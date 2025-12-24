# 🔧 Quick Fix: Image Upload Connection Error

## Problem

Getting `ECONNRESET` error when uploading images? Backend is crashing because AI models aren't installed yet.

## ✅ Quick Solution

### Option 1: Skip Image Upload (Fastest)

**Don't need image upload?** Just use the other 3 input methods:
- ✅ Upload CSV
- ✅ Paste Edges  
- ✅ Random DAG

The app works perfectly without the image feature!

### Option 2: Enable Image Upload (5 minutes)

Choose ONE option:

#### A) Use GPT-4 Vision (Best Quality) ⭐

```bash
# 1. Install OpenAI
pip install openai

# 2. Get API key from https://platform.openai.com/api-keys

# 3. Set environment variable
# Windows:
set OPENAI_API_KEY=sk-your-key-here

# Linux/Mac:
export OPENAI_API_KEY=sk-your-key-here

# 4. Restart backend
cd backend
python main.py
```

#### B) Use Free Local Models 🆓

```bash
# 1. Install AI libraries (~2GB download first time)
pip install transformers torch pillow

# 2. Restart backend
cd backend
python main.py

# 3. First upload will download models (wait ~5 minutes)
```

## 🎯 Step-by-Step Fix

### 1. Stop the Backend

In the backend terminal, press `Ctrl+C`

### 2. Install Dependencies

**Choose GPT-4 (recommended):**
```bash
pip install openai
set OPENAI_API_KEY=sk-your-actual-key
```

**OR choose Free models:**
```bash
pip install transformers torch pillow
```

### 3. Restart Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Keep Frontend Running

Frontend should still be running. If not:
```bash
cd frontend  
npm run dev
```

### 5. Try Upload Again!

1. Refresh browser
2. Click "Upload Image" tab
3. Drop an image
4. Should work now! 🎉

## 🐛 Still Not Working?

### Check Backend Logs

Look for errors in the backend terminal. Common issues:

**"ModuleNotFoundError: No module named 'transformers'"**
```bash
pip install transformers torch pillow
```

**"openai.error.AuthenticationError"**
```bash
# Check your API key
echo %OPENAI_API_KEY%  # Windows
echo $OPENAI_API_KEY   # Linux/Mac
```

**"CUDA error" or "GPU"**
```bash
# Use CPU instead (add to backend code)
# Or install CPU-only PyTorch:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Check Frontend Logs

Open browser DevTools (F12) → Console tab

**"Failed to fetch" or "Network Error"**
- Backend isn't running
- Start it: `cd backend && python main.py`

**"timeout"**
- Image too large or complex
- Try smaller/simpler image

## 💡 Pro Tips

### If You Don't Want Image Upload:

The image upload feature is **completely optional**! You can:

1. Remove the "Upload Image" tab by commenting out the mode in the frontend
2. Or just ignore it and use the other 3 input methods
3. Everything else works perfectly without AI models

### If You Want It:

- **GPT-4 Vision**: Best accuracy (95%+), cheap ($0.001/image)
- **Local Models**: Free, private, but requires ~2GB disk space

## 📋 Verify Setup

### Test Backend Health:

```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"..."}
```

### Test Image Extraction Status:

```bash
curl http://localhost:8000/api/image-extraction/status
# Shows which AI methods are available
```

### Test Frontend:

Open: http://localhost:5173
- Should see the app
- All tabs should be visible
- Can test other input methods

## 🎉 Success Checklist

After fixing, you should be able to:

- ✅ Backend running without crashes
- ✅ Frontend connects successfully  
- ✅ Upload CSV files (works)
- ✅ Paste edges (works)
- ✅ Generate random DAG (works)
- ✅ Upload images (works if AI installed)

## 📞 Need More Help?

1. Check backend terminal for error messages
2. Check browser console (F12) for frontend errors
3. Try the other input methods first
4. Image upload is optional - app works great without it!

---

**TL;DR:** Install `pip install openai` (or `transformers torch pillow`), set API key if using OpenAI, restart backend. Done! 🚀

