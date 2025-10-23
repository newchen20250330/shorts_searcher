# YouTube 短影片搜尋器 📹

一個簡單易用的 YouTube Shorts 搜尋工具，支援多條件篩選、即時配額監控、CSV 匯出等功能。

## ✨ 功能特色

- 🔍 **多條件搜尋**：關鍵字、類別、地區、時間、觀看次數
- 🌍 **支援 20 個國家/地區**：台灣、美國、日本、韓國等
- 📊 **即時配額監控**：追蹤 YouTube API 每日使用量
- 💾 **CSV 匯出**：一鍵下載搜尋結果
- 🎨 **響應式介面**：手機、平板、電腦都能用

## 🚀 快速開始

### 方法一：使用安裝腳本（推薦）

1. **執行安裝**
   ```
   雙擊「安裝.bat」
   ```

2. **設定 API Key**
   - 複製 `.env.example` 為 `.env`
   - 填入你的 YouTube API Key（參考下方說明）

3. **啟動程式**
   ```
   雙擊「啟動.bat」
   ```

4. **開啟瀏覽器**
   ```
   http://127.0.0.1:5000
   ```

### 方法二：手動安裝

```bash
# 建立虛擬環境
python -m venv .venv

# 啟動虛擬環境 (Windows)
.venv\Scripts\activate

# 安裝套件
pip install -r requirements.txt

# 設定 .env 檔案
copy .env.example .env
# 編輯 .env 填入 API Key

# 啟動程式
python app.py
```

## 🔑 取得 YouTube API Key

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用「YouTube Data API v3」
4. 建立憑證 → API 金鑰
5. 複製 API Key 到 `.env` 檔案

詳細步驟請參考「使用說明.txt」

## 📦 系統需求

- Windows 10/11
- Python 3.8 或更新版本
- 網路連線

## 📋 套件需求

- Flask：網頁框架
- google-api-python-client：YouTube API 客戶端
- python-dotenv：環境變數管理
- isodate：時間格式處理
- requests：HTTP 請求

## 🎯 使用方式

### 搜尋影片
1. 輸入關鍵字（例如：cat, 料理, gaming）
2. 選擇篩選條件：
   - 影片類別（音樂、遊戲、寵物等）
   - 地區（台灣、美國、日本等）
   - 上傳時間（6/12/24 小時內）
   - 最少觀看次數
   - 影片長度上限
3. 點擊「搜尋」

### 匯出結果
- 點擊「匯出 CSV」下載搜尋結果
- 可用 Excel 或 Google 試算表開啟

### 配額監控
- 畫面上方顯示今日 API 配額使用情況
- 每日免費配額：10,000 單位
- 每次搜尋約消耗 100 單位

## 📁 檔案結構

```
youtube-shorts-search/
├── 安裝.bat              # 一鍵安裝腳本
├── 啟動.bat              # 一鍵啟動腳本
├── 使用說明.txt          # 詳細使用說明
├── requirements.txt      # Python 套件清單
├── .env.example         # 環境變數範本
├── app.py               # 主程式
└── templates/
    └── index.html       # 網頁介面
```

## ⚙️ 設定說明

### .env 檔案
```env
YOUTUBE_API_KEY=你的API金鑰
```

### 配額說明
- **搜尋 API**：100 單位/次
- **影片詳情 API**：1 單位/次（每 50 支影片）
- **類別 API**：1 單位/次
- **每日配額**：10,000 單位（約可搜尋 100 次）

## ❓ 常見問題

**Q: 顯示「API Key 無效」？**  
A: 檢查 .env 檔案中的 API Key 是否正確，並確認已在 Google Cloud Console 啟用 YouTube Data API v3

**Q: 搜尋不到結果？**  
A: 嘗試放寬篩選條件（降低觀看次數、延長時間範圍）或更換關鍵字

**Q: 配額用完了？**  
A: 等到隔天配額重置（太平洋時間午夜），或建立新的 Google Cloud 專案

**Q: CSV 匯出亂碼？**  
A: 使用 Excel 開啟時選擇 UTF-8 編碼，或使用 Google 試算表開啟

**Q: 可以分享給朋友嗎？**  
A: 可以！但每個人需要使用自己的 YouTube API Key

## 🔒 安全注意事項

- ⚠️ **不要分享你的 API Key**
- ⚠️ **不要將 .env 檔案上傳到公開網路**
- 💡 如果 API Key 外洩，請立即到 Google Cloud Console 刪除並重新建立

## 📞 支援

遇到問題？請檢查：
1. 「使用說明.txt」中的詳細說明
2. 「啟動.bat」視窗中的錯誤訊息
3. Python 和套件是否正確安裝

## 📝 版本歷史

### v1.0 (2025/10/23)
- ✅ 基本搜尋功能
- ✅ 多條件篩選
- ✅ 20 個國家/地區支援
- ✅ 即時配額監控
- ✅ CSV 匯出功能
- ✅ 響應式網頁設計

## 📜 授權

此專案僅供個人使用。使用 YouTube API 需遵守 [YouTube API 服務條款](https://developers.google.com/youtube/terms/api-services-terms-of-service)。

## 🙏 致謝

- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Flask](https://flask.palletsprojects.com/)
- [Bootstrap](https://getbootstrap.com/)

---

**祝使用愉快！** 🎉
