# 🚀 Quick Start - AI-Powered DAG Optimization

## ✅ Setup Complete!

Your OpenRouter API is already configured with:
- **API Key:** Securely stored in `backend/.env` ✅
- **Model:** Google Gemini 2.0 Flash (FREE, recommended) ✅

---

## 🎯 Start the Application

### 1. Start Backend (Terminal 1)

```cmd
cd backend
python main.py
```

**You should see:**
```
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend (Terminal 2)

```cmd
cd frontend
npm run dev
```

**You should see:**
```
Local: http://localhost:5173
```

### 3. Open App

Open browser: **http://localhost:5173**

---

## 🖼️ Upload a DAG Image

1. Click **"Upload Image"** tab
2. Drop your DAG image
3. AI extracts nodes & edges automatically! ✨
4. See interactive graph preview
5. Click **"Optimize"** to optimize the DAG
6. Export to Neo4j if needed

---

## 🤖 Change AI Model

Want to try a different model?

```cmd
cd backend
python setup_api_key.py
```

**Choose from 4 FREE models:**
1. Google Gemini 2.0 Flash ⭐ (current, recommended)
2. NVIDIA Nemotron Nano (fastest)
3. Meta Llama 3.2 Vision (most accurate)
4. Qwen 2 VL (best for photos)

See `FREE_AI_MODELS_GUIDE.md` for detailed comparison.

---

## 📁 Project Structure

```
backend/
  ├── .env              # API key (NEVER commit to Git!)
  ├── main.py           # FastAPI backend
  └── setup_api_key.py  # Model selection tool

frontend/
  ├── src/              # React components
  └── package.json      # Dependencies

*.md                    # Documentation
```

---

## 🔒 Security Note

**`.env` file is in `.gitignore`** - Your API key is safe!

Never commit API keys to Git. The `.env` file stays local only.

---

## 🆘 Troubleshooting

### Backend won't start?

```cmd
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend won't start?

```cmd
cd frontend
npm install
npm run dev
```

### Image upload not working?

Check backend terminal - should show:
```
🔑 OpenRouter API key found
🤖 Using model: google/gemini-2.0-flash-exp:free
```

If not, check `backend/.env` file exists with your API key.

---

## 📚 More Info

- **Model Guide:** `FREE_AI_MODELS_GUIDE.md`
- **OpenRouter Setup:** `OPENROUTER_SETUP.md`
- **Migration Details:** `OPENROUTER_MIGRATION_SUMMARY.md`

---

## 🎉 You're Ready!

1. ✅ Backend running on port 8000
2. ✅ Frontend running on port 5173
3. ✅ OpenRouter API configured
4. ✅ Free AI model selected

**Start uploading DAG images!** 🚀
