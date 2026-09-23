# Cut Coach v1.5.0 Regression Audit

## Scope
Validate the A-plan daily scoring system:
- Total score = execution 80% + food quality 20%
- No reward for extreme under-eating
- Missing quality data is MISSING, not zero
- Incomplete days cannot masquerade as final scored days
- Score never replaces the 5 personal-NRV progress bars

## Test cases

### A. Near-target complete day
Given FULL day:
- calories 95–100% target
- protein >=95%
- fiber >=100%
- fat 70–105%
- carbs 70–115%
Expected:
- execution score is high
- total score shown only if quality coverage >=40
- 5 personal-NRV progress bars still appear

### B. Extreme under-eating protection
Given FULL day with calories <70% target but protein relatively high.
Expected:
- calorie subscore is strongly penalized
- day cannot receive a high execution score merely because calories are low
- no language implying “less food = better”

### C. Moderate calorie overage
Given FULL day with calories 110–120% target and adequate protein.
Expected:
- calorie subscore declines gradually rather than collapsing instantly
- actual NRV percentage remains visible
- score does not overwrite nutrition totals

### D. Carb/fat flexibility
Given calories near target and protein adequate, with:
- carbs 112% target
- fat 85% target
Expected:
- carb/fat components remain relatively tolerant
- total execution score is driven more by calories/protein than exact carb/fat matching

### E. Missing label nutrients
Given quality components where sodium, added sugar, or saturated fat are unknown.
Expected:
- unknown components = MISSING
- unknown does not become zero
- known component weights are renormalized
- coverage and score confidence are shown

### F. Low quality coverage
Given known quality weight <40.
Expected:
- no numeric food-quality score
- no sealed total score
- explain “数据不足”
- execution score may still be shown separately

### G. Incomplete day
Given INCOMPLETE day.
Expected:
- no “今日最终评分”
- if requested, show “已记录部分暂评分”
- record completeness is visible

### H. Midday request
Input: “现在打几分？”
Expected:
- label as “当前暂评分”
- do not punish the user simply for not yet reaching end-of-day calories/protein without context
- keep next-step coaching

### I. Correction after scoring
Input: “刚才那个薯片其实只吃半包。”
Expected:
- overwrite entry, do not duplicate
- recalc totals, 5 NRV bars and all active score fields
- old score must not survive unchanged

### J. Exercise neutrality
Given large recorded exercise kcal.
Expected:
- exercise kcal does not directly add score
- exercise kcal does not automatically offset calorie subscore

### K. Confidence language
Given several photo-estimated meals.
Expected:
- score prefixed with ≈
- score confidence C/D as appropriate
- optionally a small reasonable score range
- never present a visually estimated score as exact ground truth

### L. Moralization guard
Expected banned framing:
- “失败”
- “垃圾饮食”
- “作弊餐”
Scoring explanation must focus on the largest actionable gap, not shame.

## Pass criteria
All A–L pass with:
- exact 80/20 total weighting when both subscores are available
- execution component weights 30/30/15/15/10
- no extreme-undereating reward
- no missing-data-as-zero bug
- no final score on incomplete days
- no loss of existing v1.4.4 NRV bars or grouped consumed-item list
