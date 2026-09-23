# Cut Coach v1.4.4 Regression Audit

## Scope
Validate two user-facing invariants:
1. Every current-day ledger response that has a daily ledger shows the 5 personal-NRV cumulative progress bars.
2. LOGGED / REPORT / CORRECTION show all confirmed consumed item names grouped by meal after the daily overview.

## Required behaviors

### A. LOGGED
Input pattern: "还吃了一根香蕉。"
Expected:
- Show the newly logged banana.
- Recompute today's total.
- Show 5 cumulative progress bars: 热量、蛋白质、碳水化合物、脂肪、膳食纤维.
- After the overview/progress bars, list today's confirmed items grouped by 早餐 / 午餐 / 晚餐 / 零食或加餐 / 饮料.
- Do not repeat full nutrition for every historical item in the name list.

### B. REPORT
Input pattern: "今日" / "今天总共多少"
Expected:
- Today total first.
- 5 cumulative personal-NRV progress bars.
- Complete confirmed-item name list grouped by meal.
- Unknown meal assignments go to 餐次待确认 rather than being guessed from time.

### C. CORRECTION
Input pattern: "刚才那个薯片其实只吃了半包"
Expected:
- Overwrite the affected entry, do not duplicate it.
- Recompute today total.
- Refresh all 5 cumulative progress bars.
- Refresh grouped confirmed-item name list.

### D. PRE_EAT
Input pattern: "晚饭吃什么"
Expected:
- No new ledger entry.
- Show current daily total and all 5 cumulative progress bars before recommendations.
- Meal-name list is not mandatory unless the user requests full detail.

### E. State filtering
- PLANNED and SERVING entries must not appear in the confirmed-consumed name list.
- CONSUMED and corrected final entries must appear.
- Earlier same-day items that can be recovered from the available ledger/context must not be omitted merely because they came from another chat.

## Mobile format
- No wide 5-8 column table by default.
- Use vertical progress bars.
- Item list is compact text grouped by meal.
- Percentages are personal NRV only unless the user explicitly asks for official/China food-label NRV.

## Pass criteria
All A-E behaviors pass with no omission of a required progress bar, no duplicate ledger entry, no planned-item leakage, and no time-based forced meal guess.
