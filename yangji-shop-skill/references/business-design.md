# 💼 商業設計 — 暘基商城

進銷存流程、稽合邏輯、會員等級設計。

---

## 進銷流程

```
廠商 → [進貨單 confirm] → 商品庫存增 + 應付帳款增
                            ↓
                      [付款給廠商]
                            ↓
                      應付帳款減 + 銀行戶頭/支票減
─────────────────────────────────────────────
客戶 → [前台下單] → 訂單建立 + 商品庫存減
                       ↓
                  [客戶付款]
                       ↓
                  訂單應收減
                  (現金/匯款 立即;客票/信用卡 延遲)
                       ↓
                  [客票兌現 OR 退票]
                       ↓
                  兌現:應收為 0 + 銀行戶頭增
                  退票:應收回沖
```

---

## 訂單狀態流轉

| 狀態 | 觸發條件 | 顯示 |
|------|---------|------|
| pending | 訂單剛建立,尚未付款 | 待處理 |
| paid | 全額付清(現金或客票收齊),但還沒出貨 | 已付款(罕用) |
| shipped | 已出貨(管理員手動點) | 已出貨 |
| completed | shipped + orderRemain == 0 (auto) | 已完成 |
| cancelled | 管理員取消(下拉選擇) | 已取消 |
| refunded | 退款(下拉選擇) | 已退款 |

**自動流轉**:
- shipped → completed: 收到全額付款 (maybeAutoComplete)
- completed → shipped: 退票讓 remain > 0 (maybeAutoRevert)

---

## 客票生命週期

```
pending (剛收到客票) ──┬→ cleared (兌現,存入我方銀行)
                       ├→ bounced (退票,訂單應收回沖)
                       └→ endorsed (背書轉讓給廠商,抵應付)
```

退票連動規則:
- 找 fromOrderId 的訂單
- 把對應 payment.checkStatus 設為 bounced
- 重算訂單應收
- 若 remain > 0 且原 status == completed → 退回 shipped

---

## 多倉庫 / 多貨架

```
warehouse {
  id, code, name, address, isActive,
  zones: ['A', 'B', ...],     // 區
  shelvesPerZone: 4,          // 每區幾個貨架
  layerLabels: ['上','中','下']  // 每架幾層
}
```

商品庫存:
```
product {
  stock: 200,                          // 總庫存(自動算)
  stockByWarehouse: {                  // 各倉庫存
    'wh-main': 150, 'wh-second': 50
  },
  shelfByWarehouse: {                  // 各倉貨架位置
    'wh-main': 'A-1-上', 'wh-second': 'B-2-中'
  }
}
```

進貨確認時(`confirmPurchase`):
- 每筆 item 必有 `targetWarehouse`
- 沒指定 → 用 purchase.defaultWarehouse → 用第一個 isActive warehouse
- newSBW[wh] += qty
- 同步寫 newSheBW[wh] = item.targetShelf

---

## 多幣別計價

每個商品有 `costCurrency` (CNY/USD/TWD/JPY/HKD)
匯率表在 `settings.pricing.exchangeRates`

```
進貨成本(原幣) × 匯率 = 採購成本 NT$
+ 運費(每 kg / 每件 / 整箱)
+ 關稅 (依 hsCode 對應 tariffPresets)
× (1 + 利潤 %)
= 建議售價 NT$
```

`computePrice(p)` 是核心函式,進貨單 / 商品編輯 / 報價單 都用。

---

## 5 種促銷活動

| 類型 | 結構 | 範例 |
|------|------|------|
| sitewide_discount | `{value: 5}` | 全館 95 折 |
| spend_discount | `{threshold: 1000, value: 10}` | 滿 1000 享 9 折 |
| bundle | `{qty: 5, fixedPrice: 800, categoryIds: [...]}` | 五金 5 件 800 |
| gift | `{tiers: [{threshold, gift, image, description}]}` | 滿額贈 |
| free_shipping | `{threshold: 1500}` | 滿 1500 免運 |

促銷套用順序(在 cartPromoResult):
1. bundle (任選 N 件 / 每分類最低件數兩種模式)
2. sitewide_discount (取最大 value)
3. spend_discount (取符合條件中最大 value)
4. gift (累贈 cumulative / 最高階 highest 兩種模式)
5. free_shipping (取最低 threshold)

---

## 4 級會員等級

```
L0 一般會員 (門檻 0)        × 1.00 (不打折)
L1 銀卡 (滿 5000)           × 0.95 (95 折)
L2 金卡 (滿 20000)          × 0.90 (9 折)
L3 白金 (滿 50000)          × 0.85 (85 折)
```

等級套用優先序(`priceFor`):
1. 商品有 vipPrice → 用 vipPrice (個別優惠)
2. 用 user.level.discount (等級折扣)
3. 都沒有 → product.price (原價)

晉級觸發:
- 客戶下單 → totalSpent 增加
- 計算 totalSpent 對應的最高 levelId
- 自動設定 user.levelId

---

## 稽合三大金額

| 名稱 | 算法 |
|------|------|
| 應收帳款 | sum(訂單未付清,排除退票) |
| 應付帳款 | sum(進貨單未付清) |
| 待兌客票 | sum(客票 status=pending) |
| 庫存價值 | sum(p.stock × p.cost × 匯率) |
| 銀行戶頭結餘 | (人工或從 cleared payments 累計) |

平衡公式:
```
本月銷售收入 = sum(訂單收款,bounced 不計)
本月採購支出 = sum(進貨付款)
庫存變化     = 進貨入庫 - 銷貨出庫
應收增加     = 銷售 - 收款
應付增加     = 進貨 - 付款
```
