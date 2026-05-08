# 🚨 踩雷大全 — 暘基商城

12 個歷史踩過的雷,每個都記得避開。

---

## 1. file:// 雙擊開檔 vs http://localhost

**症狀**: localStorage 不互通,商品資料「不見」(其實在另一個 origin)

**修法**: 一律用 `http://localhost:8000/admin.html`,不雙擊檔案

---

## 2. 簡體字辨識(Excel 匯入)

**症狀**: doImport 只認繁體欄名(「貨號」「價格」),簡體 Excel(「货号」「价格」) 全部 0

**修法**: 已加雙語對照,doImport 同時支援繁/簡。如果有新欄位記得兩邊都要支援

---

## 3. base64 圖片爆 localStorage

**症狀**: 161 件商品 × 80KB base64 = 9.6 MB → 超過 5-10MB 限制

**修法**: `/upload` 端點存成檔案,product.images 只存路徑

---

## 4. DATA_VERSION 遷移會覆蓋使用者資料

**症狀**: index.html 的 `migrateDefaults` 版本不符時用 SAMPLE_PRODUCTS 覆蓋

**修法**: bumping DATA_VERSION 要加保護(檢查現有 products 數量)

---

## 5. Vue.mount() 只能掛到一個元素

**症狀**: admin.html 有 login + admin 兩個 view,不能用 mount('#a, #b')

**修法**: 用單一 #app + v-if 切換子視圖

---

## 6. 瀏覽器快取嚴重

**症狀**: 改了 code 但瀏覽器跑舊版

**修法**:
- start-server.py 強制送 `Cache-Control: no-store`
- 客戶端: F12 Network 勾「Disable cache」
- 終極: 網址加 query string `?v=1`、`?v=2`

---

## 7. ★ Vue 3 method vs computed 語意陷阱

**症狀**: template 用 `licenseStatus.kind` 直接讀,但 licenseStatus 寫在 methods → 拿到 function 物件的 `.kind`(永遠 undefined)

**修法**: **屬性訪問用 computed,事件處理才用 method**

```js
// ❌ 錯誤 - 在 methods 裡
methods: {
  licenseStatus() { return { kind: 'licensed' }; }
}
// template 用 {{ licenseStatus.kind }} → undefined

// ✅ 正確 - 在 computed 裡
computed: {
  licenseStatus() { return { kind: 'licensed' }; }
}
// template 用 {{ licenseStatus.kind }} → 'licensed'
```

**已修**: licenseStatus / isReadOnly / licenseDebugInfo 都搬到 computed

---

## 8. ★ Firestore onSnapshot 不能 `length > 0` 過濾

**症狀**: 雲端清空時,本地不會更新(跟薪資系統同樣的雷)

**修法**:
```js
// ❌ 錯誤
db.collection('xxx').onSnapshot(snap => {
  const list = snap.docs.map(d => d.data());
  if (list.length > 0) {  // 雲端清空 → 跳過
    this.xxx = list;
    save(STORE.xxx, list);
  }
});

// ✅ 正確
db.collection('xxx').onSnapshot(snap => {
  this.xxx = snap.docs.map(d => ({id: d.id, ...d.data()}));
  save(STORE.xxx, this.xxx);
});
```

**例外**: adminUsers 可保留 length > 0 (避免空雲清掉本地預設帳號)

---

## 9. ★ GitHub Pages 子目錄絕對路徑會 404

**症狀**: `<img src="/assets/imgs/xxx.jpg">` 在 `chanel5168-cell.github.io/yangji-shop/` 下找不到圖

**修法**: 用相對路徑 `assets/imgs/xxx.jpg` (去掉開頭 `/`)

**已修**: `migrateImagePaths()` 一次性遷移函式自動修

---

## 10. ★ Firebase 首次連線用空雲覆蓋本地

**症狀**: 設定好 firebaseConfig 重整 → 本地 seed 資料被空雲清掉

**修法**: `bootstrapFirebaseFromLocal()` 在訂閱前先把本地推上去

```js
this.bootstrapFirebaseFromLocal()
  .then(() => this.migrateImagePaths())
  .then(() => this.subscribeAll());
```

flag `shop_firebase_bootstrapped_v1` 確保只跑一次

---

## 11. ★ Bash 環境 SSL 憑證問題

**症狀**: Claude Bash 工具 curl/git push GitHub 失敗 (`CRYPT_E_NO_REVOCATION_CHECK`)

**修法**: git push 必須在使用者的 PowerShell 跑

```powershell
PS C:\Users\User\Desktop\我的商城> git push
```

如果跳出瀏覽器登入 → 點 Authorize 即可

---

## 12. ★ LINE 設定欄位不能貼整段 HTML

**症狀**: 把 LINE Official Account 給的 `<a href="..."><img></a>` 整段貼進去,系統把整串當 LINE ID,組到網址後面 404

**修法**:
- LINE 官方帳號 ID: 只填 `@305xxlkn` (8-9 碼)
- 加好友連結: 只填 `https://lin.ee/wx8M7bNt` (短網址)
