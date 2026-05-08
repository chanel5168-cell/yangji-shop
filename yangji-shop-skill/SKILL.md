---
name: 暘基五金商城技能包
description: 接手 暘基商城 專案前的速查手冊。涵蓋架構、踩雷、上線檢核、修 bug 流程
---

# 🛒 暘基五金商城 — 技能包

> 🎯 接手第一動作: 讀完本檔(5 分鐘) → 跑伺服器 → 看 [WIP_狀態](../WIP_狀態_2026-05-08.md)

---

## 🏗 架構速覽

```
單檔 HTML SPA (admin.html ~15500 行 + index.html ~3000 行)
   ↓ Vue 3 (Options API, CDN 引入,無 build)
   ↓
localStorage (本地永遠的副本) ⇄ Firebase Firestore (雲端真相)
   ↓
GitHub Pages 公網部署 (https://chanel5168-cell.github.io/yangji-shop/)
```

關鍵 collection (Firestore):
```
products / categories / suppliers / orders / purchases / settings
transfers / customerChecks / checkbooks / invoiceBooks / inputInvoices
users / adminUsers
```

---

## 🚀 啟動 / 部署

| 動作 | 指令 |
|------|------|
| 啟動本地 | `cd C:\Users\User\Desktop\我的商城; python -X utf8 start-server.py` |
| 推 GitHub | `git push` (必須在使用者的 PowerShell) |
| 拉 GitHub | `git pull` |
| 看 commit | `git log --oneline -10` |
| 進 Firebase Console | https://console.firebase.google.com/project/yangji-shop |
| 進 GitHub Repo | https://github.com/chanel5168-cell/yangji-shop |
| 公網前台 | https://chanel5168-cell.github.io/yangji-shop/index.html |
| 公網後台 | https://chanel5168-cell.github.io/yangji-shop/admin.html |

---

## 🚨 12 個踩過的雷(必讀)

詳見 [踩雷大全](references/common-pitfalls.md)。最常踩的:

1. file:// 不能跑 — 一律 http://localhost
2. Vue 3 method vs computed — 屬性訪問必須用 computed
3. Firestore onSnapshot 不能 length>0 過濾
4. GitHub Pages 子目錄絕對路徑會 404 — 用相對路徑
5. Firebase 首次連線會用空雲覆蓋本地 — `bootstrapFirebaseFromLocal()`
6. Bash 環境 SSL 不能 push GitHub — 必須用 PowerShell
7. LINE 設定欄位不能貼整段 HTML

---

## 🔧 常見任務 SOP

| 任務 | 看哪 |
|------|------|
| 客戶說圖片看不到 | [圖片故障排除](references/troubleshooting.md#圖片) |
| 加新商品 | [操作手冊](../暘基商城操作手冊.md) → 商品管理 |
| 加新促銷活動 | [操作手冊](../暘基商城操作手冊.md) → 促銷活動 5 種類型 |
| 重置測試環境 | seed-test.html → ① 全清並注入 |
| 跑完整流程驗證 | seed-test.html → ②③④⑤⑥⑦⑧ 依序按 |
| 修授權碼問題 | fix.html (一鍵修復) |
| 改 Firestore 規則 | [FIRESTORE_RULES.md](../FIRESTORE_RULES.md) |
| 多裝置同步壞掉 | F12 console 看 [Firebase Bootstrap] 訊息 |

---

## 📐 程式風格

- Vue 3 Options API,**屬性用 computed,事件處理用 method**
- 工業金屬風: 鋼藍 #1a2a4a + 黃銅 #c9a95c (不要紅白)
- 全繁體 UI (簡體匯入會自動 OpenCC 轉繁)
- localStorage: 用 `load(STORE.xxx)` / `save(STORE.xxx, data)`
- Firebase: `cloudSave('xxx', item)` 寫;`db.collection().onSnapshot(...)` 讀

---

## 📂 References (深入閱讀)

- [踩雷大全](references/common-pitfalls.md) — 12 個歷史踩過的雷
- [商業設計](references/business-design.md) — 進銷存流程、稽合邏輯、會員等級
- [上線檢核](references/launch-checklist.md) — 上線前必做事項
- [故障排除](references/troubleshooting.md) — 常見問題

---

## 🤝 業主習慣 (per memory)

- 繁體中文回覆、具體步驟、不愛技術黑話
- 大改動: 分段做 + 每段先驗證 + 先備份
- 要求主動品質驗證 (不只做被指派的範圍)
- 工業金屬風視覺 (per feedback_hardware_shop_visual)
- 改 code 前 `git status`,改完立刻 commit + push
