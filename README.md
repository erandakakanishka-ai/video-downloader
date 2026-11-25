# 🎬 Video Downloader — Full-Stack Web App

වීඩියෝ ලින්ක් එකක් ඇතුළත් කළ විට **YouTube, TikTok, ok.ru, vk.ru** ඇතුළු වෙබ් අඩවි 1000කට අධික සියල්ලෙන්ම වීඩියෝ බාගත කරදෙන Full-Stack වෙබ් අඩවියකි.

- **Frontend:** සරල, ලස්සන `index.html` (HTML/CSS/JS) — URL ඇතුළත් කිරීමේ අඩඇක්ස් සහ Download බොත්තම, බාගත වේගය පෙන්වන ප්‍රොග්‍රෙස් බාර්.
- **Backend:** `Flask` API — `yt-dlp` + `FFmpeg` භාවිතයෙන් වීඩියෝ බාගත කර අඩවිය හරහා ආපසු ලබාදෙයි.
- **Deploy:** `Dockerfile` (FFmpeg ඇතුළත්) සහ `requirements.txt` ඇතුළත් නිසා **Render.com** හෝ **Hugging Face Spaces** එකෙන් නොමිලේ Deploy කළ හැක.

## 📁 ව්‍යාපෘති ගොනු (Repository structure)

```
video-downloader/
├── index.html          # Frontend (UI + ප්‍රොග්‍රෙස් පෙන්වීම, API ඇමක්ට් කිරීම)
├── app.py              # Flask backend API (yt-dlp මගින් බාගත කිරීම)
├── requirements.txt    # Python dependency සමුදාය
├── Dockerfile          # Docker image (FFmpeg ස්ථාපනය සහිතව)
├── .dockerignore
└── .gitignore
```

## ⚙️ ක්‍රියාකාරීත්වය

1. ඔබ වීඩියෝ URL ඇතුළත් කර **Download** ක්ලික් කරයි.
2. Frontend `POST /api/download` වෙත URL පිළිගනී → Backend ටහයක් (job) ආරම්භ කර දෙසින් එහි job_id ආපසු ලබාදෙයි.
3. yt-dlp වීඩියෝ බාගත කර දෙන අතර, ප්‍රොග්‍රෙස් හැඟීම් (progress hooks) හරහා පියවරෙන් පියවර ඉදිරිපත් කරයි.
4. Frontend සෑම දෙසින් එකකින් `GET /api/status/<id>` වෙත ප්‍රශ්න කර ප්‍රොග්‍රෙස් පරීක්ෂා කරයි.
5. බාගත වූ පසු, **Download** බොත්තම දිස්වෙයි — එය `GET /api/file/<id>` හරහා වීඩියෝව ඔබට බාගත කර දෙයි.

> දෝෂ ඇති ලින්ක් (වැරදි ලින්ක්, අවශ්‍යතා නොමැති වීඩියෝ, බාධිත අඩවි) වෙනුවෙන් පිටුවේ පැහැදිලි සත්‍යය මESSAGE දිස්වෙයි.

## 💻 මෙන්න (Local) දියත් කිරීම

1. **FFmpeg** ස්ථාපනය කරන්න (yt-dlp වලට අවශ්‍ය):
   - **Windows:** `winget install ffmpeg` (හෝ `choco install ffmpeg`)
   - **macOS:** `brew install ffmpeg`
   - **Linux:** `sudo apt install ffmpeg`
2. පරිග්‍රහ බලාගන්න:
   ```bash
   git clone https://github.com/<your-username>/video-downloader.git
   cd video-downloader
   ```
3. Dependencies ස්ථාපනය කරන්න:
   ```bash
   pip install -r requirements.txt
   ```
4. Server ආරම්භ කරන්න:
   ```bash
   python app.py
   ```
5. Browser වෙත හඹා යන්න: **http://127.0.0.1:5000**

## 🚀 GitHub වෙත Upload කිරීම (පියවරෙන් පියවර)

**පියවර 1 —** GitHub වෙත Repo එකක් ඇති කරන්න:
1. `https://github.com` වෙත යන්න → **Sign up / Log in** කරන්න.
2. ඉහළ දකුණු කොණයේ **`+` → New repository** ක්ලික් කරන්න.
3. Repo නම: `video-downloader` (Public තෝරන්න — නොමිලේ host කිරීම සඳහා ප්‍රශ්නයක් නැත).
4. **"Add files"** → **"Upload files"** තෝරා, මෙම ව්‍යාපෘතියේ සියලුම ගොනු (index.html, app.py, requirements.txt, Dockerfile, .gitignore) ඇක්ස් කර **Commit changes** කරන්න.

*(හෝ Terminal එකෙන් — ලොකල් දියත් කර ඇති ව්‍යාපෘතිය මත පහත කමාන්ඩ් භාවිතා කරන්න:)*
```bash
cd video-downloader
git init
git add .
git commit -m "Initial commit: video downloader app"
git branch -M main
git remote add origin https://github.com/<your-username>/video-downloader.git
git push -u origin main
```

**පියවර 2 —** GitHub Repo එක සම්පූර්ණ වී පෙනෙන බව තහවුරු කරන්න (දත්ත මේසේ පෙන්න).

## ☁️ Render.com හි නොමිලේ Deploy කිරීම (පියවරෙන් පියවර)

**පියවර 1** — `https://render.com` වෙත යන්න → **Sign Up** කරන්න (GitHub හරහා ලොග් ඇතුළත් කළ හැක).

**පියවර 2** — Dashboard හි **New → Web Service** ක්ලික් කරන්න.

**පියවර 3** — **Connect GitHub** ක්ලික් කරන්න → ඔබේ `video-downloader` repo තෝරා **Import** කරන්න.

**පියවර 4** — Render **නිවැරදිවම Dockerfile ස්වයංක්‍රීයව හඳුනාගනී** (Service type: **Container**). මෙහිදී ඔබට අවශ්‍ය වන්නේ:
- **Name:** `video-downloader` (හෝ ඔබ කැමති නමක්)
- **Region:** ඔබ ජීවත් වන ප්‍රදේශය (හෝ පහසු එකක්) තෝරන්න
- **Disk:** Free tier ට 512 MB පැමිණෙන අතර, මෙම ව්‍යාපෘතිය සඳහා ඒත් පොරසපාන අවශ්‍යයි.

**පියවර 5** — **Create Web Service** ක්ලික් කරන්න. Render build ආරම්භ කරනවා — මෙය භාගික මිනිත්තු කිහිපයක් පුරා සිදුවේ.

**පියවර 6** — Status පෙන්වන **"Live"** වූ පසු, මැයි ඉහළ **Web Service URL** එක (`https://video-downloader.onrender.com`) ක්ලික් කරන්න. ඔබගේ වීඩියෝ බාගතකරන අඩවිය දැන් සජීවීව ඇත!

## 🤗 Hugging Face Spaces හි Deploy කිරීම (විකල්පය)

1. `https://huggingface.co/spaces` වෙත යන්න → **Create new Space**.
2. නම දබා **Docker** සැකයක් (framework) තෝරන්න.
3. **GitHub** හරහා repo සම්බන්ධ කරන්න (මෙම ව්‍යාපෘතියේ Dockerfile තිබෙන නිසා Space එක එය ස්වයංක්‍රීයව භාවිතා කරයි).
4. **Create Space** කරන්න → build වූ පසු Space එකේ URL එක (`https://<your-name>.hf.space`) හරහා භාවිතා කළ හැක.

## ⚠️ වැදගත් සටහන් (Free tier සඳහා)

- Render නොමිලේ ටයරයේ **සකසන තැන නිරන්තරයෙන් වෙනස් වන දත්ත** ආකෘතියක් ඇත — නැවත restart/redeploy වන විට `downloads/` තුළ ඇති ගොනු අහිමි වේ. එබැවින් බාගත වූ වීඩියෝ **ඒ වේලාවේම** ඔබට බාගත කරගන්න.
- නොමිලේ ටයරයේ ඉහළ මට්ටමේ වීඩියෝ (දිගු, ඉහළ රිසෙලුසන් වල) බාගත කිරීමට **request timeout** හේතුවෙන් අසාර්ථක විය හැක. කුඩා-මදක් වීඩියෝ සඳහා වඩාත් සුදුසුය.
- බාධිත අඩවි හෝ දෝෂ සහිත ලින්ක් සඳහා yt-dlp දෝෂ පෙන්වන අතර, පිටුවේ ඊට අදාළ පණිවිඩය දිස්වේ.
- **yt-dlp** unpinned ආකාරයෙන් තිබෙන නිසා නැවත build කිරීමේදී නවතම විද්‍යුත් භාරගන්නා (extractors) ලබාගනී — ok.ru/vk/TikTok වැනි අඩවිවලට මෙය වැදගත් වේ.

## 🛠 ගැටලු විසඳුම් (Troubleshooting)

- **Render build අසාර්ථක වේ නම්:** `Dockerfile` සහ `requirements.txt` repo එකේ ඇති බවත්, path වැරදි නැති බවත් තහවුරු කරන්න. Build logs Render dashboard හි පරීක්ෂා කරන්න.
- **"ffmpeg not found" යන දෝෂය පෙනේ නම්:** ඔබ Docker නොවෙන විට local දියත් කර ඇති නිසා, FFmpeg ඔබේ මෙන්න එකේ ස්ථාපනය කර ඇති බව තහවුරු කරන්න (Dockerfile හි එය ස්ථාපනය කර ඇත).
- **බාගත අසාර්ථක වේ නම්:** අඩවිය yt-dlp ට අයත් නැතිද, ලින්ක් වැරදිද යන්න පරීක්ෂා කරන්න. yt-dlp වැනි අඩවි නිතර අඩවි ක්‍රියාකාරීත්වය වෙනස් කරන නිසා, නැවත deploy කිරීමෙන් යාවත්කාලීන yt-dlp ලබාගත හැක.
