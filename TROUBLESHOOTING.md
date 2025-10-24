# Troubleshooting Guide 疑難排解

## Common Installation Issues 常見安裝問題

### ❌ ERROR: Could not open requirements file

**Problem 問題:**
```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
[ERROR] Package installation failed
```

**Solutions 解決方案:**

1. **Make sure you're in the correct folder**
   ```
   確認你在正確的資料夾中執行 install.bat
   
   資料夾應包含以下檔案:
   - install.bat
   - requirements.txt
   - app.py
   - templates/ (folder)
   ```

2. **Check if you downloaded all files**
   ```
   如果是從 GitHub 下載:
   - 點擊綠色 "Code" 按鈕
   - 選擇 "Download ZIP"
   - 解壓縮完整的資料夾
   - 進入解壓後的資料夾
   - 在該資料夾中執行 install.bat
   ```

3. **Right-click and "Run as administrator"**
   ```
   有時需要管理員權限
   ```

---

### ❌ Python not found

**Problem:**
```
[ERROR] Python not found
```

**Solutions:**

1. **Install Python**
   - Download from: https://www.python.org/downloads/
   - Install Python 3.8 or newer
   - ⚠️ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Restart your computer**
   - After installing Python, restart before trying again

3. **Check Python installation**
   - Open Command Prompt
   - Type: `python --version`
   - Should show: `Python 3.x.x`

---

### ❌ Virtual environment creation failed

**Problem:**
```
[ERROR] Failed to create virtual environment
```

**Solutions:**

1. **Try running as administrator**
2. **Check disk space** (need at least 500MB)
3. **Try manual installation:**
   ```bash
   python -m pip install --user virtualenv
   python -m venv .venv
   ```

---

### ❌ Package installation failed

**Problem:**
```
[ERROR] Package installation failed
```

**Solutions:**

1. **Check internet connection**
   - Installation requires internet to download packages

2. **Update pip first:**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **Install packages one by one:**
   ```bash
   .venv\Scripts\activate
   pip install flask
   pip install google-api-python-client
   pip install python-dotenv
   pip install isodate
   pip install requests
   ```

---

### ❌ Application won't start

**Problem:**
```
程式啟動後立即關閉
或顯示錯誤訊息
```

**Solutions:**

1. **Run diagnose.bat**
   - This will check your system

2. **Check .env file exists**
   - Run `setup_api_key.bat`
   - Or manually copy `.env.example` to `.env`

3. **Verify API Key**
   - Open `.env` file
   - Make sure `YOUTUBE_API_KEY` is set
   - API Key should start with `AIzaSy` and be 39 characters long

4. **Check port 5000**
   - Another program might be using port 5000
   - Close other applications and try again

---

## Quick Fix Checklist 快速檢查清單

Before asking for help, try these:

□ 1. Are you in the correct folder?
     (Should contain install.bat, requirements.txt, app.py)

□ 2. Is Python installed and added to PATH?
     (Run: `python --version`)

□ 3. Did installation complete successfully?
     (No red [ERROR] messages)

□ 4. Does .env file exist?
     (Run setup_api_key.bat if not)

□ 5. Is your API Key correct?
     (39 characters, starts with AIzaSy)

□ 6. Run diagnose.bat
     (Check for any issues)

---

## Getting Help 取得協助

If problems persist:

1. Run `diagnose.bat`
2. Take a screenshot of the output
3. Open an issue on GitHub with:
   - Screenshot
   - Your Windows version
   - Python version
   - What you were trying to do

GitHub Issues: https://github.com/newchen20250330/shorts_searcher/issues

---

## Platform-Specific Issues 特定平台問題

### Windows 7/8
- May need to install Visual C++ Redistributable
- Download from Microsoft website

### Windows 11
- No known issues

### Using PowerShell instead of CMD
- All batch files should work
- If not, try running from regular Command Prompt
