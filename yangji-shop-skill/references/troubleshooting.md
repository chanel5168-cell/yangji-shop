# 🩺 故障排除 — 暘基商城

客戶或業主回報問題時的快速診斷流程。

---

## 圖片

### 症狀: 商品圖片不顯示(破圖)

**診斷流程**:

1. 開 F12 Network 分頁,看 jpg 請求是 200 還是 404
2. 看請求網址:
   - `https://chanel5168-cell.github.io/assets/...` → ❌ 路徑錯了(子目錄消失)
   - `https://chanel5168-cell.github.io/yangji-shop/assets/...` → ✓ 路徑對
3. 如果 404 路徑錯了 → 檢查 product.images:
   - `/assets/imgs/xxx.jpg` (絕對) → ❌ GH Pages 子目錄會 404
   - `assets/imgs/xxx.jpg` (相對) → ✓
4. 修法: 開後台讓 `migrateImagePaths()` 自動跑(看 console 訊息)

### 症狀: 上傳圖片後不見

- 用本地 `/upload` 端點還是 base64?
- base64 超過 5-10MB 會爆 localStorage
- 用 `/upload` 存成檔案,products.images 只存路徑

---

## 跑馬燈

### 症狀: 跑馬燈沒跑

1. 後台 系統設定 → 「啟用頂部跑馬燈」勾選有打勾嗎?
2. `settings.announcement` 有填字嗎? 或有 enabled 促銷活動嗎?
3. 沒有任何文字 → marqueeText 為空 → v-if 不渲染 → 沒跑馬燈
4. 加一段文字到 announcement 即可顯示

### 症狀: 跑馬燈在跑但跑超快/超慢

- CSS `.marquee-track { animation:marqueeScroll 38s linear infinite; }` 改 38s
- 改成 60s 會慢點,改成 20s 會快點

---

## 授權碼

### 症狀: 紅色 banner「系統處於唯讀模式 — 授權失效」

1. 看 banner 第二行「失效原因」:
   - `format` → 授權碼格式錯
   - `decode` → base64 解不開
   - `sig` → 校驗碼錯(被改過 / 偽造)
   - `expired` → 真的過期
2. 點 banner 內「🔧 一鍵修復」按鈕
3. 還不行 → 開 fix.html 看完整診斷
4. 還不行 → console 看 `[license boot-fix]` 訊息
5. 終極: 用 _gen_keys.js 重新產一張(僅限賣家本人)

### 症狀: 啟用成功重整又失效

- 看 [踩雷大全 #7 Vue 3 method vs computed]
- licenseStatus 必須在 computed 不能在 methods

---

## Firebase 同步

### 症狀: A 改 B 不同步

1. F12 console 看是否有 [Firebase Bootstrap] 訊息
2. 看是否有 `Permission denied` 紅字 → 是的話 Firestore Rules 鎖死了,看 FIRESTORE_RULES.md
3. 看 Network 分頁是否有 `channel?VER=8` 長連線 → 沒有 = Firebase 沒連上
4. 看 admin.html 有沒有 `firebase.initializeApp` 訊息

### 症狀: 雲端有資料但本地空的

- 開 admin.html 觸發 onSnapshot → 應自動拉雲端資料覆蓋本地
- 沒覆蓋 → 看是否該 collection 有 onSnapshot 監聽器(可能漏掉)
- 商城已加 12 個 collection 監聽器

### 症狀: 雲端是空的把本地也清掉了

- 第 10 雷! `bootstrapFirebaseFromLocal()` 應該保護
- 檢查 localStorage `shop_firebase_bootstrapped_v1` flag
- 沒 flag 但 onSnapshot 已經跑 → bootstrap 沒跑成功
- 還原: `seed-test.html` 還原最後備份

---

## LINE 按鈕

### 症狀: LINE 浮動按鈕點下去 404

- 看 [踩雷大全 #12]
- LINE 官方帳號 ID 欄位被貼了整段 HTML
- 修: 系統設定 → 💬 LINE 連動 → 兩個欄位重填:
  - 帳號 ID: `@xxxxxxxx`
  - 加好友連結: `https://lin.ee/xxxxx`

### 症狀: LIFF 自動登入沒啟動

- `settings.liffId` 有填嗎?
- 開 F12 console 看是否有 `[商城] LIFF 自動登入:` 訊息
- 沒訊息 = 不在 LINE 內開(必須從 LINE app 內開連結才會 LIFF)

---

## GitHub Pages

### 症狀: 推完 git push 但 Pages 還是舊版

- 部署需要 1~2 分鐘,先等
- Settings → Pages → 看是否顯示「Your site is live at ...」
- 如果黃色「Your site is being built」一直在 = 還在建

### 症狀: 推 git push 失敗

- 看是否在 PowerShell 跑(Bash 環境會 SSL 失敗)
- 跳出瀏覽器登入 → 點 Authorize
- 還不行 → Personal Access Token (PAT)

---

## 多裝置

### 症狀: 手機跟電腦看到不同資料

1. 都連同一個 Firebase 專案?
2. 都登入相同的後台帳號?
3. F12 console 看 `[Firebase Bootstrap]` 訊息(應該只在第一裝置出現)
4. 強制重整(Ctrl+Shift+R)清快取

### 症狀: 公網跟本地看到不同資料

- 兩邊都連同一個 Firebase
- 但快取 / 鎖定模式可能差異
- 公網清空快取重整看看
