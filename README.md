# 🔐 Image Steganography — Web App

A school project web app that hides secret messages inside images using **LSB (Least Significant Bit) steganography**.

---

## ▶ Run Locally (on your computer)

### 1. Install dependencies
```bash
pip install streamlit Pillow
```

### 2. Run the app
```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## 🌐 Host Online for Free (Streamlit Cloud)

Anyone in the world can visit your app with a link — perfect for a school project.

### Step 1 — Put your files on GitHub
1. Go to [github.com](https://github.com) and create a free account
2. Click **New repository** → name it `steganography-app` → click **Create**
3. Upload these 3 files:
   - `app.py`
   - `steg_core.py`
   - `requirements.txt`

### Step 2 — Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **New app**
4. Select your repository → set **Main file** to `app.py`
5. Click **Deploy**

✅ In about 60 seconds you get a **public link** like:
`https://your-name-steganography-app.streamlit.app`

---

## 📁 Files

| File | Purpose |
|------|---------|
| `app.py` | Streamlit web interface |
| `steg_core.py` | Steganography logic (encode / decode) |
| `requirements.txt` | Python packages (for Streamlit Cloud) |

---

## 🧠 How It Works

LSB steganography hides data by replacing the **least significant bit** of each colour channel (R, G, B) in every pixel with one bit of the secret message.

- A 1000×1000 image = 1,000,000 pixels × 3 channels = **~375,000 characters** can be hidden
- The visual change is invisible to the human eye (1-bit change per channel)
- JPEG files are **not used for output** because JPEG compression destroys the hidden bits — output is always saved as PNG

---

## 🔑 Features

- ✅ Encode a message into PNG, BMP, TIFF, WebP, or JPG
- ✅ Decode a message from any encoded image
- ✅ Optional password protection (XOR encryption)
- ✅ Live character counter with capacity limit
- ✅ Side-by-side original vs encoded preview
- ✅ Download encoded image directly from browser
