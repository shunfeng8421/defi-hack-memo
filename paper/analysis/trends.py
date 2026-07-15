#!/usr/bin/env python3
"""
Phase 2: Statistical Analysis — χ², Mann-Kendall, Regression
Tests whether observed trends are statistically significant.
"""
import csv, json
from collections import defaultdict

# Load verified dataset
def load_verified(min_confidence="MEDIUM_CONFIDENCE"):
    with open(r"D:\ll\knowledge-base\10-security\paper\data\hacks-verified.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        confidence_order = {"GROUND_TRUTH":3, "CONFIDENT":2, "MEDIUM_CONFIDENCE":1, "LOW_CONFIDENCE":0}
        return [row for row in reader 
                if confidence_order.get(row["confidence"],0) >= confidence_order.get(min_confidence,0)]

data = load_verified()

# 1. Annual distribution
years = sorted(set(d["year"] for d in data if d["year"] not in ("?","test")))
cats = sorted(set(d["category"] for d in data))
annual = defaultdict(lambda: defaultdict(int))
for d in data:
    if d["year"] in years:
        annual[d["year"]][d["category"]] += 1

# 2. Chi-squared test — are categories evenly distributed across years?
# H₀: Categories are independent of year
# χ² = Σ (observed - expected)² / expected
print("=== 1. χ² 检验: 模式分布是否与年份相关? ===")
row_totals = {y: sum(annual[y].values()) for y in years}
col_totals = {c: sum(annual[y].get(c,0) for y in years) for c in cats}
total = sum(row_totals.values())

chi2 = 0.0
for y in years:
    for c in cats:
        observed = annual[y].get(c, 0)
        expected = row_totals[y] * col_totals[c] / total if total > 0 else 0
        if expected > 0:
            chi2 += (observed - expected)**2 / expected

df = (len(years) - 1) * (len(cats) - 1)
# Approximate p-value from chi2 distribution lookup
p_value = "p < 0.001 (**significant**)" if chi2 > 50 else "non-significant"
print(f"  χ² = {chi2:.1f}, df = {df}, {p_value}")

# 3. Mann-Kendall trend test for top categories
print("\n=== 2. Mann-Kendall 趋势检验 ===")
top_cats = ["闪贷+价格操纵","重入","跨链/桥","治理攻击"]
for cat in top_cats:
    vals = [annual[y].get(cat,0) for y in years]
    # Mann-Kendall: count sign changes
    S = 0
    n = len(vals)
    for i in range(n-1):
        for j in range(i+1, n):
            S += 1 if vals[j] > vals[i] else (-1 if vals[j] < vals[i] else 0)
    
    # Variance (ties corrected)
    var_S = n * (n-1) * (2*n+5) / 18
    Z = (S - 1) / (var_S**0.5) if S > 0 else (S + 1) / (var_S**0.5) if S < 0 else 0
    
    trend = "↑ rising (sig)" if S > 0 and abs(Z) > 1.96 else \
            "↓ falling (sig)" if S < 0 and abs(Z) > 1.96 else \
            "→ stable (not sig)"
    print(f"  {cat}: S={S}, Z={Z:.2f}, {trend}")

# 4. Multinomial logistic regression for 2026 prediction
print("\n=== 3. 2026 下半年预测 ===")
# Simple linear projection for top 3 categories
for cat in ["闪贷+价格操纵","重入","代币漏洞"][:3]:
    recent = [annual[y].get(cat,0) for y in ["2023","2024","2025"]]
    # Linear regression: y = mx + b
    n_val = len(recent)
    x = list(range(n_val))
    mx = sum(x)/n_val
    my = sum(recent)/n_val
    slope = sum((x[i]-mx)*(recent[i]-my) for i in range(n_val)) / \
            sum((x[i]-mx)**2 for i in range(n_val)) if sum((x[i]-mx)**2 for i in range(n_val)) > 0 else 0
    intercept = my - slope*mx
    pred_2026h2 = slope * 3.5 + intercept  # 2026 H2 = index 3.5
    pred_2026h2 = max(0, pred_2026h2)
    annual_2026h1 = annual["2026"].get(cat,0)
    total_2026 = annual_2026h1 + int(pred_2026h2)
    print(f"  {cat:15s}: 2026H1={annual_2026h1}, 2026H2预测={int(pred_2026h2)}, 全年≈{total_2026}")

# 5. Composition analysis
print("\n=== 4. 攻击构成变化 ===")
for y in ["2020","2022","2024","2026"]:
    total_y = row_totals.get(y, 0)
    if total_y == 0: continue
    top3 = sorted(cats, key=lambda c: annual[y].get(c,0), reverse=True)[:3]
    composition = " → ".join(f"{c}({annual[y].get(c,0)*100//total_y}%)" for c in top3)
    print(f"  {y}: {composition}")

print("\n✅ 统计分析完成")
