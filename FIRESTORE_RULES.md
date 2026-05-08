# 🔐 Firestore Security Rules — 暘基商城

> **必讀**:你目前用的是「**測試模式**」規則,**會在建立後 30 天自動失效**(大約 2026-06-08 左右)。失效後 Firestore 會 deny 全部讀寫 → 整個商城會壞掉。
>
> 這份文件給你 3 種規則選擇,照優先度部署。

---

## 🎯 你現在要做什麼

**最晚在測試期到期前**到 Firebase Console 部署「**方案 A**」的規則,否則系統會當掉。

部署位置:[Firebase Console → Firestore Database → 規則](https://console.firebase.google.com/project/yangji-shop/firestore/rules)

---

## ⚠️ 先理解一個關鍵限制

商城目前使用**自製帳密**(adminUsers 存在 Firestore 內),**沒有使用 Firebase Authentication**。

這代表:
- Firestore 從外部看,**沒有「使用者身份」可識別**
- 任何拿到 firebaseConfig (admin.html 公開的 API key) 的人
- 都可以**繞過你的登入畫面**,用 Firebase SDK 直接讀寫資料庫

**Firestore Rules 唯一能做的事**:限制存取的「形狀」(哪些路徑、什麼資料),但**無法區分是哪個使用者**。

要做到完整的「客戶 A 看不到客戶 B 的訂單」這種安全保護,**必須遷移到 Firebase Auth** (這是長期目標)。

---

## 📋 三個方案 (從急用到完整)

### 🟡 方案 A:短期可用版 (測試期到期前必須部署) ⭐ 推薦

**目的**:避免測試期到期商城當掉,最低限度的保護。

**保護程度**:擋住「亂試 path」的人,但拿到 firebaseConfig 的人還是能讀寫全部。

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // 商品 / 分類 / 廠商 / 設定 — 公開可讀(前台需要),登入後可寫
    match /products/{id} {
      allow read: if true;
      allow write: if request.auth != null || request.time < timestamp.date(2027, 12, 31);
    }
    match /categories/{id} {
      allow read: if true;
      allow write: if request.auth != null || request.time < timestamp.date(2027, 12, 31);
    }
    match /suppliers/{id} {
      // 廠商資料只給後台
      allow read, write: if request.time < timestamp.date(2027, 12, 31);
    }
    match /settings/{doc} {
      allow read: if true;
      allow write: if request.time < timestamp.date(2027, 12, 31);
    }

    // 訂單 / 進貨 / 客票 / 發票 / 票本 / 進項 — 內部資料,不公開
    match /orders/{id}        { allow read, write: if request.time < timestamp.date(2027, 12, 31); }
    match /purchases/{id}     { allow read, write: if request.time < timestamp.date(2027, 12, 31); }
    match /transfers/{id}     { allow read, write: if request.time < timestamp.date(2027, 12, 31); }
    match /customerChecks/{id}{ allow read, write: if request.time < timestamp.date(2027, 12, 31); }
    match /checkbooks/{id}    { allow read, write: if request.time < timestamp.date(2027, 12, 31); }
    match /invoiceBooks/{id}  { allow read, write: if request.time < timestamp.date(2027, 12, 31); }
    match /inputInvoices/{id} { allow read, write: if request.time < timestamp.date(2027, 12, 31); }

    // 會員 — 客戶可讀寫自己,但因為沒接 Auth,先全開
    match /users/{uid} {
      allow read, write: if request.time < timestamp.date(2027, 12, 31);
    }

    // 後台帳號 — 內部資料(包含密碼!)
    match /adminUsers/{id} {
      allow read, write: if request.time < timestamp.date(2027, 12, 31);
    }
  }
}
```

**部署步驟**:

1. 開 [Firebase Console Rules](https://console.firebase.google.com/project/yangji-shop/firestore/rules)
2. 把上面這段整個複製貼上(替換掉現有的)
3. 點右上「**發布**」
4. 等 5~10 秒 → 規則生效
5. 商城應該繼續正常運作(因為過期日設成 2027 年底)

---

### 🟢 方案 B:長期可用版 (Firebase Auth 接好之後)

**前提**:已經把後台登入改用 Firebase Authentication。

**保護**:沒登入的人完全不能寫,只能讀公開資料(商品/分類/設定/促銷)。

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function isAdmin() {
      return request.auth != null
          && exists(/databases/$(database)/documents/adminUsers/$(request.auth.uid))
          && get(/databases/$(database)/documents/adminUsers/$(request.auth.uid)).data.isActive == true;
    }
    function isCustomer() { return request.auth != null; }

    // 公開讀(前台展示)
    match /products/{id}     { allow read: if true; allow write: if isAdmin(); }
    match /categories/{id}   { allow read: if true; allow write: if isAdmin(); }
    match /settings/{doc}    { allow read: if true; allow write: if isAdmin(); }

    // 客戶可建訂單,只能讀自己的
    match /orders/{id} {
      allow create: if isCustomer();
      allow read:   if isAdmin() || (isCustomer() && resource.data.userId == request.auth.uid);
      allow update, delete: if isAdmin();
    }

    // 客戶會員資料 — 只能讀寫自己
    match /users/{uid} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
      allow read: if isAdmin();
    }

    // 純內部 — 只給 admin
    match /suppliers/{id}      { allow read, write: if isAdmin(); }
    match /purchases/{id}      { allow read, write: if isAdmin(); }
    match /transfers/{id}      { allow read, write: if isAdmin(); }
    match /customerChecks/{id} { allow read, write: if isAdmin(); }
    match /checkbooks/{id}     { allow read, write: if isAdmin(); }
    match /invoiceBooks/{id}   { allow read, write: if isAdmin(); }
    match /inputInvoices/{id}  { allow read, write: if isAdmin(); }
    match /adminUsers/{id}     { allow read, write: if isAdmin(); }
  }
}
```

**前提任務**:

- [ ] 後台登入接 `firebase.auth().signInWithEmailAndPassword`
- [ ] adminUsers 改用 Firebase Auth UID 當 docId
- [ ] 客戶會員也統一接 Firebase Auth (含 LIFF 登入綁 LINE userId)

---

### 🔴 方案 C:萬無一失版 (有 Cloud Functions 之後)

驗證用 Cloud Functions 處理(不再用 Firestore Rules 直接擋),客戶端只能呼叫定義好的 API。

需要付費升級到 Blaze 方案(Cloud Functions 要用)。先不做。

---

## 🚀 上線步驟總結

1. 改 admin 密碼 (4 個帳號全改)
2. 部署方案 A 規則
3. 推 GitHub + 開 Pages
4. 設 LIFF
5. **未來**:遷移到 Firebase Auth → 部署方案 B 規則
