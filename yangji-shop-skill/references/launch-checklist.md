# 🚀 上線檢核清單 — 暘基商城

從目前 v3.2 → 真正可賣可收錢的清單。按優先序勾選。

---

## 🔥 必做(沒做會出事)

- [ ] **改 4 個後台預設密碼**
  - admin@shop.local / acc / pick / sales
  - 後台「帳號管理」改,或 Firebase Console 直接編 adminUsers collection
  - 改完密碼會自動同步到 Firebase

- [ ] **部署 Firestore Rules 方案 A** (大約 6/8 前)
  - 看 [FIRESTORE_RULES.md](../../FIRESTORE_RULES.md) 方案 A 整段複製
  - 貼到 [Firebase Console Rules](https://console.firebase.google.com/project/yangji-shop/firestore/rules) → 發布
  - 不做的話 6/8 後 Firestore 拒絕全部讀寫,商城會當

- [ ] **L2 LIFF 自動登入**
  - LINE Developer Console 建 Channel(LINE Login) + LIFF App
  - LIFF Endpoint URL: `https://chanel5168-cell.github.io/yangji-shop/index.html`
  - LIFF Size: Full,Scope: profile + openid,Bot link feature: On(Aggressive)
  - 拿 LIFF ID → 後台 系統設定 → 💬 LINE 連動 → LIFF ID 貼上 → 儲存
  - 驗證: 在 LINE 內傳訊息給自己 → 點 LIFF URL → 應該自動登入並進商城

- [ ] **重設清空測試資料**(整合測試 seed 留著很怪)
  - 後台「資料管理 → 清空資料」全部勾 → 確認
  - 或 seed-test.html 改用真實營運資料重新 seed

- [ ] **真實商品上架**
  - 從 taohuo999.com 抓商品(parse-taohuo.py)
  - 或 Excel 匯入
  - 改 product.cost / price / vipPrice / images 為真實值

---

## 🟡 強烈建議(可上線後做但越早越好)

- [ ] **公司資料完整填寫**
  - 後台 系統設定 → 公司資訊
  - 統編 / 電話 / Email / 地址 / Slogan / Logo URL

- [ ] **銀行戶頭資訊**
  - 系統設定 → 銀行戶頭管理
  - 至少設 1 個主帳 + 1 個備援

- [ ] **促銷活動實際內容**
  - 目前是 4 個整合測試用的 (95 折 / 滿 1500 免運 / 五金 5 件 800 / 滿額贈)
  - 改成你真的想跑的活動

- [ ] **商品分類整理**
  - 預設 10 類 (鐵線製品 / 彎折成型 / ...)
  - 改成真實商品結構

- [ ] **首頁 Banner 與宣傳圖**
  - assets/imgs/ 加首頁 hero image
  - 系統設定 → 關於我們 → bannerImage / galleryImages

---

## 🟢 次優先(收尾完美)

- [ ] **訂單通知 LINE**(L3)
  - 需要 Firebase Functions(Blaze 付費方案,最低用量免費)
  - 客戶下單後自動推 LINE 訊息「訂單已收到 / 已出貨 / 票期提醒」

- [ ] **LINE Pay 整合**(L4)
  - 申請 LINE Pay 商家帳號(審核 1~2 週)
  - 結帳時直接刷 LINE Pay

- [ ] **LICENSE_SECRET 移後端**
  - 目前 admin.html 公開,可被偽造授權
  - SaaS 規模化前要改 Firebase Functions

- [ ] **商品評價系統**

- [ ] **物流追蹤 API**(黑貓 / 7-11 / 全家)

- [ ] **電子發票**

---

## 🔬 上線當天/前一天驗證

開公網網址做這 10 項驗證:

1. [ ] 前台首頁 30 商品圖片都顯示
2. [ ] 跑馬燈在跑
3. [ ] 點 LINE 浮動按鈕跳對加好友頁
4. [ ] 加 5 件「五金扣件」到購物車 → 顯示「五金扣件 5 件 NT$ 800」自動套用
5. [ ] 全館 95 折 + 滿額免運 + 滿額贈 都正確顯示
6. [ ] 結帳填會員資料 → 下單成功
7. [ ] 後台訂單管理看到剛才的訂單
8. [ ] 後台改商品價格 → 重整前台看是否同步
9. [ ] 在另一個瀏覽器開後台 → 應同步看到剛剛改的價格
10. [ ] 後台「會員管理」看到剛才下單的客戶

10 項全 ✓ → 可以開幹。

---

## 🎬 上線後第一週

- 每天看 Firebase Console → Firestore 文件成長
- 看 GitHub Pages 流量(但 Pages 不給流量數據,要靠 GA)
- 收到第一個真實訂單 → 截圖紀念

開幕快樂! 🎉
