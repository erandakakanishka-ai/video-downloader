"""
Video Downloader — Flask backend.

Takes a video URL (YouTube, TikTok, ok.ru, vk.ru and 1000+ other sites
supported by yt-dlp), downloads it with yt-dlp + FFmpeg, and serves the
result back to the browser.

Optional cookies can be passed to bypass site bot-checks (needed for some
YouTube videos from datacenter IPs).

Job flow (async, so big videos don't hit request timeouts):
    POST /api/download     -> creates a job, starts download in a thread, returns job_id
    GET  /api/status/<id>  -> job status + progress (polled by the frontend)
    GET  /api/file/<id>    -> streams the downloaded file as a download
"""

import glob
import os
import tempfile
import threading
import uuid

from flask import Flask, jsonify, request, send_file, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

app = Flask(__name__)

# job_id -> job dict (status, progress, title, filename, error)
jobs = {}
jobs_lock = threading.Lock()


def create_job(url, cookies=None):
    job_id = uuid.uuid4().hex[:12]
    job = {
        "id": job_id,
        "url": url,
        "cookies": cookies,       # optional cookie string (Netscape format or raw "a=b; c=d")
        "status": "queued",      # queued -> downloading -> processing -> completed / error
        "progress": 0.0,
        "title": None,
        "filename": None,
        "error": None,
    }
    with jobs_lock:
        jobs[job_id] = job
    return job


def write_cookie_file(cookies_string):
    """Write a cookie string to a temp Netscape-format cookie file for yt-dlp.

    Accepts either raw "name=value; name2=value2" or full Netscape cookie.txt
    content. Returns the path to the temp file, or None if not needed.
    """
    cookies_string = cookies_string.strip()
    if not cookies_string:
        return None

    path = os.path.join(tempfile.gettempdir(), f"cookies_{uuid.uuid4().hex}.txt")
    with open(path, "w", encoding="utf-8") as f:
        # Netscape cookie.txt format: header line + "domain flag path secure expires name value"
        # (the header is REQUIRED by http.cookiejar / yt-dlp to accept the file)
        lines = cookies_string.splitlines()
        first = lines[0].strip() if lines else ""
        if "\t" in first and "=" in first:
            # Already in Netscape format (tab-separated domain/flag/path/...)
            f.write("# Netscape HTTP Cookie File\n")
            f.write(cookies_string)
        else:
            # Convert raw "name=value; name2=value2" into Netscape lines
            f.write("# Netscape HTTP Cookie File\n")
            pairs = [p.strip() for p in cookies_string.split(";") if "=" in p]
            for pair in pairs:
                name, _, value = pair.partition("=")
                f.write(".youtube.com\tTRUE\t/\tTRUE\t1999999999\t" + name + "\t" + value + "\n")
    return path


def progress_hook_factory(job):
    """yt-dlp progress hook: keeps the job's progress up to date."""
    def hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            if total:
                job["progress"] = round(d.get("downloaded_bytes", 0) / total * 100, 1)
            job["status"] = "downloading"
        elif d.get("status") == "finished":
            job["status"] = "processing"   # merging video + audio now
            job["progress"] = 100.0
            job["filename"] = d.get("filename")
    return hook


def run_download(job):
    """Download a video in a background thread using yt-dlp."""
    from yt_dlp import YoutubeDL

    # All downloaded files are prefixed with the job id -> easy to locate later
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{job['id']}.%(ext)s")

    cookie_file = write_cookie_file(job.get("cookies") or "")

    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "bestvideo*+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "writethumbnail": False,
        "writesubtitles": False,
        "progress_hooks": [progress_hook_factory(job)],
        "quiet": False,
        "no_warnings": False,
    }
    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(job["url"], download=True)
            job["title"] = info.get("title") or job["url"]

        # Find the downloaded file (prefixed with the job id)
        matches = glob.glob(os.path.join(DOWNLOAD_DIR, f"{job['id']}.*"))
        if matches:
            job["filename"] = os.path.basename(matches[0])
            job["status"] = "completed"
            job["progress"] = 100.0
    except Exception as exc:  # yt-dlp raises DownloadError for unsupported/dead links
        job["status"] = "error"
        job["error"] = str(exc) or type(exc).__name__
    finally:
        if cookie_file and os.path.exists(cookie_file):
            os.remove(cookie_file)  # temp cookies are used only for this download


# ----------------------------------------------------------------------------
# Routes
# ----------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/download", methods=["POST"])
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    cookies = (data.get("cookies") or "").strip()
    if not url:
        return jsonify({"error": "URL ඇතුළත් කරන්න"}), 400

    job = create_job(url, cookies)
    threading.Thread(target=run_download, args=(job,), daemon=True).start()
    return jsonify({"job_id": job["id"], "status": "queued"})


@app.route("/api/status/<job_id>")
def status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job නොමැත"}), 404
    return jsonify({
        "status": job["status"],
        "progress": job["progress"],
        "title": job["title"],
        "filename": job["filename"],
        "error": job["error"],
    })


@app.route("/api/file/<job_id>")
def download_file(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job නොමැත"}), 404
    if job["status"] != "completed" or not job["filename"]:
        return jsonify({"error": "බාගත කිරීම තවම සම්පූර්ණ වී නැත"}), 400

    path = os.path.join(DOWNLOAD_DIR, job["filename"])
    if not os.path.exists(path):
        return jsonify({"error": "ගොනුව නොමැත"}), 404

    # Serve the file as a download, named after the video title
    download_name = f"{job['title']}.mp4" if job.get("title") else job["filename"]
    return send_file(path, as_attachment=True, download_name=download_name)


if __name__ == "__main__":
    # PORT env var is set automatically by Render.com / most PaaS providers
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
