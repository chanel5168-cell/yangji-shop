# 暘基五金有限公司

> 仿 taohuo999.com 的單檔 HTML + Firebase 商城系統

---

## 📋 專案內容

| 檔案 | 用途 |
|------|------|
| `index.html` | 前台商城 — 顧客瀏覽商品、加入購物車、下單、會員登入、訂單查詢 |
| `admin.html` | 後台管理 — 商品/分類/訂單/會員 CRUD、批次匯入、系統設定 |
| `CLAUDE.md` | 給未來 Claude AI 接手用的開發手冊 |
| `README.md` | 本檔（給人看的安裝說明）|

---

## 🚀 5 分鐘上手

### 立刻試用（不需要 Firebase）

直接用瀏覽器打開 `index.html`，就能看到示範商城。資料會存在瀏覽器的 localStorage。

打開 `admin.html` 後，用以下帳密登入示範後台：
- 帳號：`admin@shop.local`
- 密碼：`admin123`

---

## ⚙️ 上線部署（接 Firebase 雲端）

### 步驟 1：建立 Firebase 專案

1. 前往 https://console.firebase.google.com/
2. 點「新增專案」→ 取個名字（例 `my-shop`）→ 建立
3. 進入專案 → 左側選單 → **Authentication** → 開始使用 → 啟用「電子郵件/密碼」
4. 左側選單 → **Firestore Database** → 建立資料庫（選擇生產模式）

### 步驟 2：取得 Firebase 設定

1. 在專案首頁點 `</>` 圖示新增 Web 應用
2. 取得 `firebaseConfig` 物件，看起來像這樣：
   ```js
   const firebaseConfig = {
     apiKey: "AIzaSy...",
     authDomain: "my-shop.firebaseapp.com",
     projectId: "my-shop",
     storageBucket: "my-shop.appspot.com",
     messagingSenderId: "1234567890",
     appId: "1:1234567890:web:abc123"
   };
   ```

### 步驟 3：替換到兩個 HTML 檔

打開 `index.html` 和 `admin.html`，找到這段：
```js
const firebaseConfig = {
  apiKey: "REPLACE_WITH_YOUR_API_KEY",
  ...
};
```
把整個物件用您剛才複製的取代。**兩個檔案都要改**。

### 步驟 4：建立第一個管理員

1. 開瀏覽器打開 `index.html`
2. 點右上角「註冊」，用您的 Email 註冊一個帳號
3. 回到 Firebase Console → Firestore → `users` collection → 找到您的帳號
4. 把 `role` 欄位的值改成 `admin`
5. 重新整理 `admin.html`，用同個 Email/密碼登入後台

### 步驟 5：（可選）部署到 GitHub Pages

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<您的帳號>/my-shop.git
git push -u origin main
```

到 GitHub repo → Settings → Pages → Source 選 `main` 分支，1-2 分鐘後即可在 `https://<您的帳號>.github.io/my-shop/` 訪問。

---

## 📥 從 taohuo999 匯入商品

1. 用您的帳號登入 https://www.taohuo999.com/
2. 進入 https://www.taohuo999.com/#/products?pcatId=6669
3. 按 **F12** 打開開發者工具 → 切到 **Network** 分頁
4. 重新整理頁面，找到一個 `process.aspx` 的請求（通常是 POST）
5. 點該請求 → Response → 把 JSON 全選複製
6. 開啟您的 `admin.html` → 左側選單「批次匯入」→ 貼上 JSON → 「分析並匯入」
7. 預覽欄位對應沒問題後，按「確認匯入」

⚠ 若無法取得 JSON，您也可以：
- 在 Excel 或 Google 試算表整理商品（欄位：name, price, stock, unit, categoryId, description）
- 另存成 CSV → 用記事本打開 → 全選複製 → 貼到批次匯入框
- 第一行需要是欄位名稱

---

## 🗂 資料模型（Firestore Collections）

```
products      商品（id, name, categoryId, price, stock, images, ...）
categories    分類（id, name, parentId, sortOrder）
orders        訂單（id, orderNo, userId, items, total, status, ...）
users         會員（uid, name, email, phone, role, level, ...）
settings/main 全域設定（shopName, contactPhone, shippingFee, ...）
```

---

## 🎨 自訂外觀

### 改顏色

在 `index.html` 與 `admin.html` 開頭的 `:root` 區塊調整：
```css
:root{
  --primary:#d92626;     /* 主色 — 商城紅 */
  --primary-dark:#a81818;
  --accent:#ff8800;      /* 強調色 */
}
```

### 改商城名稱與聯絡資訊

進入 `admin.html` → 系統設定，在後台修改即可（無需動 code）。

---

## 🔒 安全提醒

⚠ 上線前必做：

1. **替換 Firebase Config**：`REPLACE_WITH_YOUR_API_KEY` 不能留著
2. **修改示範管理員帳密**：`admin.html` 裡的 `DEMO_ADMIN` 常數請改掉或移除
3. **設定 Firestore Rules**：在 Firebase Console → Firestore → Rules，貼上以下範例：
   ```
   rules_version = '2';
   service cloud.firestore {
     match /databases/{database}/documents {
       // 商品、分類、設定：所有人可讀，僅管理員可寫
       match /products/{doc} {
         allow read: if true;
         allow write: if request.auth != null &&
           get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
       }
       match /categories/{doc} {
         allow read: if true;
         allow write: if request.auth != null &&
           get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
       }
       match /settings/{doc} {
         allow read: if true;
         allow write: if request.auth != null &&
           get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
       }
       // 訂單：本人或管理員可讀，建立後不可改（除管理員）
       match /orders/{doc} {
         allow create: if request.auth != null;
         allow read: if request.auth != null &&
           (resource.data.userId == request.auth.uid ||
            get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
         allow update: if request.auth != null &&
           get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
       }
       // 會員：本人或管理員可讀寫
       match /users/{uid} {
         allow read, write: if request.auth != null &&
           (request.auth.uid == uid ||
            get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin');
       }
     }
   }
   ```

---

## ❓ 常見問題

**Q：我沒設定 Firebase，可以用嗎？**
A：可以。前台、後台都有 localStorage 備援，但資料只存在當前瀏覽器，不能多裝置同步。適合先試玩。

**Q：商品圖片怎麼放？**
A：目前是用網址直連方式（每行一個網址）。可以用 imgur、Cloudinary 或 Firebase Storage 來託管圖片。

**Q：怎麼批量匯出/備份資料？**
A：後台「批次匯入」頁底部有「匯出商品/分類/訂單 JSON」按鈕。

**Q：可以做 LINE 登入或 LIFF 整合嗎？**
A：可以，照著您現有薪資系統的做法接 LIFF 即可。如需協助，告訴 Claude 您要整合 LIFF。

---

*專案版本：v1.0 · 建立於 2026-05-02*
