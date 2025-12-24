# 🔍 Debug Guide: Image Upload with Verbose Logging

## Overview

Now you can see **exactly what's happening** when you upload an image! Both backend and frontend show detailed progress.

## 🖥️ Backend Terminal Output

When you upload an image, you'll see:

```
================================================================================
🖼️  IMAGE UPLOAD RECEIVED
================================================================================
📁 File: my-dag.png
📏 Size: 45678 bytes
🎨 Type: image/png

💾 Saving image temporarily...
✅ Saved to: /tmp/tmpxyz123.png

🤖 Starting AI extraction...
📦 Loading AI extractor module...
✅ AI extractor loaded successfully

🔑 OpenAI API key found
🚀 Using GPT-4 Vision for extraction...
📸 Sending image to GPT-4 Vision API...
⏳ This may take 2-5 seconds...
✅ GPT-4 Vision completed!
📊 Raw result: {
  "nodes": ["A", "B", "C"],
  "edges": [
    {"source": "A", "target": "B"},
    {"source": "B", "target": "C"}
  ]
}

🔍 Validating extracted graph...
✅ Graph is valid!

🔄 Converting to application format...
📊 Extracted:
   - Nodes: ['A', 'B', 'C']
   - Edges: 2
     1. A → B
     2. B → C

📤 Sending response to frontend:
   Success: True
   Method: openai
   Nodes: 3
   Edges: 2
================================================================================

INFO:     127.0.0.1:12345 - "POST /api/extract-from-image HTTP/1.1" 200 OK

🧹 Cleaning up temporary file: /tmp/tmpxyz123.png
✅ Cleanup complete
```

## 🌐 Frontend Console Output

Open browser DevTools (F12) → Console tab:

```javascript
🖼️ IMAGE UPLOAD STARTED
📁 File: my-dag.png image/png 45678 bytes
📤 Sending to backend...
📥 Response received: 200
📊 Response data: {success: true, method: 'openai', edges: Array(2), nodes: Array(3), message: '✅ Extracted 3 nodes and 2 edges'}
✅ Extraction successful!
📊 Extracted edges: [{source: 'A', target: 'B', classes: []}, {source: 'B', target: 'C', classes: []}]
📊 Extracted nodes: ['A', 'B', 'C']
🔧 Method used: openai
🔄 Setting edges in state...
✅ Edges set! Length: 2
🔄 Edges state changed! Length: 2
📊 Fetching graph stats for 2 edges
```

## 🎯 Understanding the Flow

### Step 1: Upload
```
User uploads image
   ↓
Frontend: Creates FormData
   ↓
Frontend: Sends POST request
   ↓
Backend: Receives file
```

### Step 2: AI Processing
```
Backend: Saves temp file
   ↓
Backend: Loads AI extractor
   ↓
Backend: Chooses method (OpenAI or Hugging Face)
   ↓
Backend: Sends to AI for analysis
   ↓
AI: Analyzes image, extracts nodes and edges
   ↓
Backend: Receives AI response
```

### Step 3: Validation
```
Backend: Validates graph structure
   ↓
Backend: Checks nodes and edges are valid
   ↓
Backend: Converts to app format
```

### Step 4: Response
```
Backend: Sends JSON response
   ↓
Frontend: Receives data
   ↓
Frontend: Sets edges in state
   ↓
Frontend: Updates UI with graph preview
```

## 🔍 Debugging Scenarios

### Scenario 1: No Graph Appears

**Backend shows:**
```
✅ Sending response to frontend:
   Success: True
   Edges: 2
```

**Frontend shows:**
```
📥 Response received: 200
📊 Response data: {success: true, ...}
✅ Edges set! Length: 2
```

**But no graph?**

**Check:**
1. Browser console for React errors
2. Is `setEdges()` being called?
3. Does the edges state update? (`🔄 Edges state changed`)
4. Is the preview visible? (eye icon toggle)

### Scenario 2: AI Not Installed

**Backend shows:**
```
❌ AI extractor not available: No module named 'transformers'
📤 Response: {
  "success": false,
  "error": "setup_required",
  ...
}
```

**Frontend shows:**
```
❌ Extraction failed
Error type: setup_required
```

**Solution:**
```bash
pip install transformers torch pillow
# OR
pip install openai
```

### Scenario 3: Invalid Graph Extracted

**Backend shows:**
```
❌ Validation failed: No nodes found in image
📤 Response: {
  "success": false,
  "error": "invalid_graph"
}
```

**Solution:**
- Use clearer image
- Make sure nodes are labeled
- Check arrows are visible

### Scenario 4: Extraction Timeout

**Backend shows:**
```
🚀 Using GPT-4 Vision...
📸 Sending image to GPT-4 Vision API...
⏳ This may take 2-5 seconds...
(hangs...)
```

**Frontend shows:**
```
❌ Request timed out
```

**Solution:**
- Check internet connection (for GPT-4)
- Try smaller image
- Increase timeout in frontend

## 📋 Checklist for Troubleshooting

### Before Upload:
- [ ] Backend running and showing "Uvicorn running"
- [ ] Frontend running on port 5173
- [ ] Browser console open (F12)
- [ ] Backend terminal visible

### During Upload:
- [ ] Backend shows "IMAGE UPLOAD RECEIVED"
- [ ] AI method detected (OpenAI or Hugging Face)
- [ ] Processing starts (loading messages)
- [ ] No error messages in backend

### After Upload:
- [ ] Backend shows "Sending response to frontend"
- [ ] Response has `success: true`
- [ ] Frontend receives 200 status
- [ ] Frontend sets edges in state
- [ ] Graph preview appears

## 🎯 Expected Timeline

### With GPT-4 Vision:
```
0s   - Upload starts
0.5s - Backend receives file
1s   - Sending to GPT-4 API
2-5s - GPT-4 processing
5s   - Validation complete
5.5s - Frontend receives response
6s   - Graph appears!
```

### With Local Models (First Time):
```
0s     - Upload starts
0.5s   - Backend receives file
1s     - Loading model (downloading if first time)
1-120s - Model download (only first time!)
5-10s  - Model processing
15s    - Validation complete
15.5s  - Frontend receives response
16s    - Graph appears!
```

### With Local Models (Subsequent):
```
0s    - Upload starts
0.5s  - Backend receives file
1s    - Loading cached model
5-10s - Model processing
11s   - Validation complete
11.5s - Frontend receives response
12s   - Graph appears!
```

## 💡 Pro Tips

### 1. Watch Both Terminals

Keep both backend and frontend terminals visible side-by-side to see the full flow.

### 2. Check Browser Console

Always have DevTools open (F12) to see frontend logs.

### 3. Look for Error Patterns

Common error indicators:
- `❌` emoji - something failed
- `⚠️` emoji - warning
- `✅` emoji - success step
- `⏳` emoji - waiting/processing

### 4. Trace the Numbers

Follow the edge count through the pipeline:
- Backend extracts: "Edges: 2"
- Frontend receives: "edges: Array(2)"
- State updates: "Length: 2"
- Graph shows: 2 edges

### 5. Verify Response Format

Backend should send:
```json
{
  "success": true,
  "method": "openai",
  "edges": [{source, target, classes}],
  "nodes": ["A", "B"],
  "message": "..."
}
```

## 🐛 Common Issues

### Issue: "Backend shows 200 but no graph"

**Debug Steps:**
1. Check frontend console - is data received?
2. Check if `setEdges()` is called
3. Check if edges state updates
4. Check if preview is visible (toggle eye icon)
5. Check browser React DevTools

### Issue: "Extraction takes forever"

**Possible Causes:**
- First-time model download (Hugging Face)
- Slow internet (GPT-4 API)
- Large image file
- Complex image

**Solutions:**
- Wait for first download to complete
- Use smaller images
- Use GPT-4 Vision (faster)
- Check internet speed

### Issue: "Wrong nodes/edges extracted"

**Debug:**
1. Look at backend "Raw result" output
2. Compare with your image
3. Check if image has clear labels
4. Try with simpler image first

## ✅ Success Indicators

You know it's working when you see:

**Backend:**
- `✅ Extracted: Nodes: ['A', 'B'] Edges: 1`
- `📤 Sending response to frontend: Success: True`
- `200 OK`

**Frontend:**
- `✅ Extraction successful!`
- `✅ Edges set! Length: X`
- `🔄 Edges state changed! Length: X`
- Toast notification appears
- Graph preview renders

## 🎉 Now You Can See Everything!

With verbose logging, you can:
- ✅ Track every step of the process
- ✅ See exactly what AI extracts
- ✅ Debug issues instantly
- ✅ Understand the data flow
- ✅ Verify everything works

**Happy debugging!** 🚀🔍

