# ---- Video Downloader: Flask + yt-dlp + FFmpeg ----
FROM python:3.12-slim

WORKDIR /app

# FFmpeg is REQUIRED by yt-dlp to merge video + audio streams and convert to mp4
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

RUN mkdir -p /app/downloads

# Render.com / PaaS providers set the PORT env var automatically
EXPOSE 5000

# Production WSGI server via gunicorn.
# IMPORTANT: 1 worker + threads, so all requests share the same in-memory job
# state (multiple workers would each have a separate job dict and break polling).
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-5000} -w 1 --threads 8 --timeout 300 app:app"]
