# 🚀 Local LLM Setup Guide

## Quick Start - 3 Easy Steps

### Step 1: Choose Your Backend

#### Option A: Ollama (Recommended - Easiest)
```powershell
# Install Ollama
winget install Ollama.Ollama

# Pull a model (first time only, ~4GB download)
ollama pull mistral

# Verify it's running
ollama list
```

#### Option B: GPT4All (Good for CPU)
```powershell
# Install
pip install gpt4all

# Models download automatically on first use
```

#### Option C: Llama.cpp (Advanced)
```powershell
# Install
pip install llama-cpp-python

# Download a GGUF model manually
# Place in: backend/models/
```

---

### Step 2: Configure the App

```powershell
# Edit your .env file
notepad .env
```

Add these settings:
```env
# Enable Local LLM
USE_LOCAL_LLM=true

# Choose backend: ollama, gpt4all, or llama-cpp
LOCAL_LLM_BACKEND=ollama

# Ollama settings
LOCAL_MODEL_NAME=mistral:7b
OLLAMA_HOST=http://localhost:11434

# OR for GPT4All
# LOCAL_MODEL_NAME=mistral-7b-openorca.Q4_0.gguf

# Performance settings
LOCAL_MODEL_MAX_TOKENS=500
LOCAL_MODEL_TEMPERATURE=0.7
LOCAL_MODEL_THREADS=4

# Optional: Keep API keys empty to force local mode
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
```

---

### Step 3: Install Dependencies

```powershell
cd backend

# For Ollama
pip install ollama

# OR for GPT4All
pip install gpt4all

# OR for Llama.cpp
pip install llama-cpp-python
```

---

### Step 4: Run the App

```powershell
# If using Ollama, make sure it's running
ollama serve  # In a separate terminal

# Start your app normally
cd ..
docker-compose up
# OR
.\start-backend.bat
```

---

## 🎯 Model Recommendations for Windows 11

### For 8GB RAM Laptop
```env
LOCAL_MODEL_NAME=mistral:7b-instruct-q4_K_M
```
- Size: ~4GB
- Speed: Fast
- Quality: Good

### For 16GB RAM Laptop (Best Balance)
```env
LOCAL_MODEL_NAME=mistral:7b
```
- Size: ~4.7GB
- Speed: Medium
- Quality: Very Good

### For 32GB RAM Laptop (Best Quality)
```env
LOCAL_MODEL_NAME=mixtral:8x7b
```
- Size: ~26GB
- Speed: Slower
- Quality: Excellent

---

## 🔍 Verify Local LLM is Working

### Test Ollama
```powershell
# Test generation
ollama run mistral "Hello, how are you?"
```

### Test in Your App
```powershell
# Start backend
cd backend
python -c "from app.core.local_llm import get_local_llm; llm = get_local_llm(); print(llm.generate('Hello!'))"
```

You should see a response generated locally!

---

## 📊 Performance Comparison

| Mode | Speed | Cost | Privacy | Offline |
|------|-------|------|---------|---------|
| **OpenAI GPT-4** | Fast | $$$$ | ❌ | ❌ |
| **Local Mistral 7B** | Medium | FREE | ✅ | ✅ |
| **Local Mixtral 8x7B** | Slow | FREE | ✅ | ✅ |

---

## 💡 Tips & Tricks

### Speed Optimization
```env
# Use quantized models (Q4, Q5)
LOCAL_MODEL_NAME=mistral:7b-instruct-q4_K_M

# Reduce max tokens for faster responses
LOCAL_MODEL_MAX_TOKENS=300

# Use more CPU threads
LOCAL_MODEL_THREADS=8
```

### GPU Acceleration (if you have NVIDIA GPU)
```powershell
# Install CUDA-enabled version
pip install llama-cpp-python --force-reinstall --no-cache-dir --config-settings="--extra-index-url=https://abetlen.github.io/llama-cpp-python/whl/cu121"
```

### Hybrid Mode (Local + API Fallback)
```env
# Try local first, fallback to API if needed
USE_LOCAL_LLM=true
OPENAI_API_KEY=sk-your-key  # Keep as backup
```

---

## 🐛 Troubleshooting

### "Ollama not found"
```powershell
# Make sure Ollama is running
ollama serve
```

### "Model not found"
```powershell
# Pull the model first
ollama pull mistral
```

### "Too slow"
- Use a smaller model (7B instead of 13B)
- Use quantized models (Q4 versions)
- Reduce max_tokens
- Increase CPU threads

### "Out of memory"
- Use smaller model
- Close other applications
- Use Q4 quantization

---

## 🎉 Success!

Your app now runs **100% locally**:
- ✅ No API costs
- ✅ Complete privacy
- ✅ Works offline
- ✅ Unlimited usage

The agents work exactly the same, but everything runs on your laptop!

---

## 🔄 Switching Modes

### Switch to Local Mode
```env
USE_LOCAL_LLM=true
```

### Switch to API Mode
```env
USE_LOCAL_LLM=false
OPENAI_API_KEY=sk-your-key
```

### Hybrid Mode (Smart Fallback)
```python
# App automatically falls back to API if local fails
USE_LOCAL_LLM=true
OPENAI_API_KEY=sk-your-backup-key
```

---

## 📚 Available Models (Ollama)

```powershell
# List popular models
ollama list

# Popular choices:
ollama pull mistral       # Best balance
ollama pull llama2        # Meta's model
ollama pull codellama     # For code tasks
ollama pull phi           # Tiny but capable
ollama pull neural-chat   # Good conversations
```

**Your app works with any Ollama model!**
