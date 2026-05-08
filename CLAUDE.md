# CLAUDE.md — 暘基五金商城 AI 開發手冊

> 這份檔案會被 Claude Code 自動讀取。
> **第一次接手請先讀完，再看 [暘基商城操作手冊.md](./暘基商城操作手冊.md)。**

---

## 🎯 一句話

**暘基五金的 B2B 批發商城。單檔 HTML SPA + Firebase 雲端 + LINE LIFF + 工業金屬風 UI。內建批次匯入/分類管理/會員等級折扣/統計分析。已上 GitHub Pages 公網。**

- 業主：黃司瑩(司瑩 / chanel) / 暘基五金有限公司
- 主檔：[index.html](./index.html)（前台）+ [admin.html](./admin.html)（後台）
- 部署：本地 `start-server.py` Python 伺服器 + GitHub Pages 公網
- 公網網址：**https://chanel5168-cell.github.io/yangji-shop/**
- Firebase 專案：`yangji-shop` ([Console](https://console.firebase.google.com/project/yangji-shop))
- 完整功能說明：[暘基商城操作手冊.md](./暘基商城操作手冊.md)

---

## 🏃 接手第一動作

1. 讀完本檔（5 分鐘）
2. **看最新 [WIP_狀態_2026-05-08.md](./WIP_狀態_2026-05-08.md) 知道最新進度與待辦**
3. 掃過 [暘基商城操作手冊.md](./暘基商城操作手冊.md)（10 分鐘）

### 啟動伺服器

```powershell
cd C:\Users\User\Desktop\我的商城
python -X utf8 start-server.py
```

打開 http://localhost:8000/admin.html，登入 `admin@shop.local` / `admin123`。

⚠ **絕對不要雙擊檔案開**（file:// 會出問題）。

---

## 🏗 架構

```
🎨 表現層    index.html / admin.html（Vue 3 + 工業金屬風 CSS）
💾 儲存層    localStorage（離線備援）+ Firebase Firestore（雲端可選）
🖼 圖片儲存  assets/imgs/{md5}.jpg（透過 /upload 端點）
🔐 認證層    Firebase Auth（Email/密碼）+ LINE LIFF（可選）
🌐 伺服器    start-server.py（Python http.server，含 _proxy + upload + no-cache）
```

### 載入的 CDN

- Vue 3 prod
- Firebase 9 compat (app/auth/firestore)
- SheetJS（xlsx 解析）
- JSZip（xlsx 內嵌圖片抽取）
- OpenCC.js（簡 → 繁）
- LINE LIFF SDK

### Collections（localStorage / Firestore 同名）

```
products      商品（含 images: [本地路徑陣列]）
categories    分類（支援父子兩層 + sortOrder）
orders        訂單
purchases     進貨單
users         會員（含 level, role, blocked, note）
settings/main 系統設定（含 memberLevels 陣列）
```

---

## 🚨 已踩雷紀錄（必看）

詳見 [WIP_狀態_2026-05-08.md](./WIP_狀態_2026-05-08.md) 的「踩雷紀錄」章節。最關鍵的：

1. **file:// vs http://localhost localStorage 不互通** — 一律用 http://localhost
2. **簡體字辨識**（doImport 同時支援繁/簡欄名）
3. **base64 圖片會爆 localStorage** — 改用 `/upload` 存成檔案
4. **DATA_VERSION 遷移要小心覆蓋資料**
5. **Vue.mount() 只能掛到一個元素** — admin.html 用 #app + v-if 切換 login/admin
6. **start-server.py 強制 no-cache** — 解決瀏覽器快取問題
7. ★ **Vue 3 method vs computed 語意陷阱** — 屬性訪問 (`xxx.kind`) 必須用 computed,method 在 template 直接讀屬性會拿到 function 物件的 `.kind`(永遠 undefined)。licenseStatus / isReadOnly / licenseDebugInfo 都已搬到 computed
8. ★ **Firestore onSnapshot 不能 `length > 0` 過濾** — 雲端清空時本地不會更新。直接覆蓋本地,雲端是真相來源(adminUsers 例外保留 length 檢查避免空雲清掉預設帳號)
9. ★ **GitHub Pages 子目錄絕對路徑會 404** — `/assets/...` 在子目錄下會 404,要用相對路徑 `assets/...`。`migrateImagePaths()` 自動修
10. ★ **Firebase 首次連線會用空雲覆蓋本地** — `bootstrapFirebaseFromLocal()` 在訂閱前先把本地推上去,flag `shop_firebase_bootstrapped_v1` 確保只跑一次
11. ★ **Bash 環境 SSL 憑證問題** — Claude 的 Bash 工具 curl/git push GitHub 會失敗。指令需在使用者的 PowerShell 跑
12. ★ **LINE 設定欄位不能貼整段 HTML** — 「LINE 官方帳號 ID」只填 @xxx,「加好友連結」只填 https://lin.ee/xxx

---

## 📐 程式慣例

### Vue 風格
- Options API（不用 Composition API，相容性高）
- 不用 build 步驟，CDN 引入

### 命名
- camelCase: 變數、函式、物件 key
- UPPER_SNAKE: 常數（如 `STORE`, `DEFAULT_SETTINGS`, `FALLBACK_CATEGORIES`）
- HTML id: camelCase（`app`, `loginApp`）
- CSS class: kebab-case（`product-card`, `btn-primary`）

### 顏色
- `--primary: #1a2a4a`（鋼鐵深藍）
- `--accent: #c9a95c`（黃銅金）
- `--steel: #4a5568`（鋼鐵灰）
- 全站工業金屬風 — **絕對不要改成紅白風**（薪資系統那種）

### 字型
- `-apple-system, "PingFang TC", "Microsoft JhengHei"`
- 全繁體中文 UI（顧客資料若是簡體會自動轉繁）

### 程式風格
- `let`/`const`，不用 `var`
- 非同步用 `async/await`
- localStorage 用 `load()` / `save()` 包裝

---

## 🔧 常見任務

### 任務 A：使用者說「商品圖看不到」

```
1. 商品 images 欄位是什麼？
   - 'assets/imgs/xxx.jpg' → 本地檔，看 assets/imgs/ 下是否真有此檔
   - 'data:image/...' → base64，超大會卡瀏覽器
   - 'https://...' → 外部 URL，可能 CORS 問題
2. F12 Network 看圖片請求是 200 還是 404
3. 對應修復：
   - 404 → 重新匯入（會走 /upload 自動本地化）
   - CORS → 用「系統設定 → 圖片本地化」按鈕
```

### 任務 B：使用者說「會員等級不對」

```
1. 確認累積消費（未取消訂單的 total 加總）
2. 確認 settings.memberLevels 的 threshold 設定
3. 點「↻ 全站重算等級」
4. F5 前台 → 看會員中心顯示的等級
```

### 任務 C：批次匯入卡住

```
1. F12 Console 看「[商城匯入]」訊息
2. 看是哪一步卡：解析？圖片下載？儲存？
3. 圖片下載卡：可能某張圖 timeout，看 Network 哪個 /_proxy 請求慢
4. 儲存失敗：通常 localStorage 容量不足，看 Console 「[商城匯入] 預計新資料 XX MB」
```

### 任務 D：新增功能流程

```
1. 先讀 [暘基商城操作手冊.md] 確認功能不存在
2. 規劃資料 schema：要不要加 settings 欄位？要不要加 collection？
3. admin 加 UI（form + 按鈕 + modal）
4. admin 加 method（CRUD + Firebase 同步）
5. 如果前台要用，index.html 同步加（注意：index 跟 admin 要同步 settings 結構）
6. 改 [操作手冊] 與 [WIP] 留紀錄
7. 用 node --check 驗證 JS 語法
```

---

## 📂 重要檔案

| 檔案 | 用途 |
|------|------|
| [暘基商城操作手冊.md](./暘基商城操作手冊.md) | **完整功能說明**（最重要的文件）|
| [WIP_狀態_2026-05-04.md](./WIP_狀態_2026-05-04.md) | 每日交接，含待辦與雷區 |
| [README.md](./README.md) | 給業主看的部署說明 |
| [index.html](./index.html) | 前台主檔 |
| [admin.html](./admin.html) | 後台主檔 |
| [start-server.py](./start-server.py) | Python 本地伺服器 |
| [assets/import-all.py](./assets/import-all.py) | 批次匯入多頁 HTML |
| [assets/download-images.py](./assets/download-images.py) | 圖片本地化下載 |

---

## 🤝 業主溝通

`chanel`（黃司瑩）是業主，**不是工程師**。請：

1. **繁體中文回應**
2. **解釋每個改動的「為什麼」**，不要只說「已修正」
3. **提供具體步驟**（點哪裡 → 看到什麼）
4. **避免技術黑話**（除非她明確問）
5. **bug 嚴重時致歉**
6. 業主期待「Cowork + Claude Code 雙邊進行」流程

---

## 💡 給未來 Claude 的話

商城經過密集開發已具規模（~3000 行 admin.html、~1500 行 index.html）。**請尊重已存在的設計**：

- 不要因為「重複」就把欄位辨識邏輯合併（繁簡欄名同時支援是必要的）
- 不要因為「精簡」拿掉自救邏輯（FALLBACK_CATEGORIES 防護 origin 切換）
- 不要因為「現代化」就改用 Composition API（業主接手難度會變高）
- 不要動 [暘基商城操作手冊.md] 的核心架構說明（除非有重大重構）

如有疑問先讀 [暘基商城操作手冊.md] 與 WIP，再動手。

---

*本檔最後更新：2026-05-04*
*專案版本：v2.0*
