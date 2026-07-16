import csv, collections, re, json

rows = []
with open(r'D:\ll\knowledge-base\10-security\zenodo-check\hacks_fixed.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for r in reader:
        if r['year'] == 'test' or not r['year'].isdigit():
            continue
        rows.append(r)

cats = collections.Counter()
years = collections.Counter()
for r in rows:
    cats[r['category']] += 1
    years[r['year']] += 1

def parse_loss(text):
    if not text or text.strip() == '':
        return None
    t = text.strip()
    eth_match = re.search(r'([\d,]+\.?\d*)\s*(?:~|about|around)?\s*ETH', t, re.IGNORECASE)
    if eth_match:
        return float(eth_match.group(1).replace(',','')) * 3000
    bnb_match = re.search(r'([\d,]+\.?\d*)\s*(?:~)?\s*(?:W?BNB)', t, re.IGNORECASE)
    if bnb_match:
        return float(bnb_match.group(1).replace(',','')) * 600
    m_match = re.search(r'([\d,]+\.?\d*)\s*(?:~)?\s*(?:million|M)\b', t, re.IGNORECASE)
    if m_match:
        val = float(m_match.group(1).replace(',',''))
        return val * 1e6 if val < 10000 else val
    b_match = re.search(r'([\d,]+\.?\d*)\s*(?:~)?\s*(?:billion|B)\b', t, re.IGNORECASE)
    if b_match:
        return float(b_match.group(1).replace(',','')) * 1e9
    k_match = re.search(r'([\d,]+\.?\d*)\s*(?:~)?\s*[Kk]', t)
    if k_match:
        return float(k_match.group(1).replace(',','')) * 1e3
    num_match = re.search(r'([\d,]+\.?\d*)', t)
    if num_match:
        return float(num_match.group(1).replace(',',''))
    return None

losses = []
for r in rows:
    l = parse_loss(r['loss'])
    if l and l > 0 and l < 1e12:
        losses.append((r['year'], r['category'], l))

losses_by_year = collections.defaultdict(float)
losses_by_cat = collections.defaultdict(float)
for year, cat, l in losses:
    losses_by_year[year] += l
    losses_by_cat[cat] += l

total = sum(l for _,_,l in losses)
volume = []
for r in reversed(range(len(rows))):
    y = rows[r]['year']
    yr_loss = losses_by_year.get(y, 0)
    n = years[y]
    avg = yr_loss / n if n > 0 else 0
    volume.append((y, n, round(yr_loss/1e6, 1), round(avg/1e6, 1)))

result = {
    'total_records': len(rows),
    'records_with_loss': len(losses),
    'total_loss_b': round(total/1e9, 2),
    'year_range': f'{min(years.keys())}-{max(years.keys())}',
    'num_categories': len(cats),
    'yearly': {y: {'attacks': years[y], 'loss_m': round(losses_by_year.get(y,0)/1e6, 1)} for y in sorted(years.keys())},
    'categories': {c: {'count': n, 'pct': round(n/len(rows)*100, 1), 'loss_m': round(losses_by_cat.get(c,0)/1e6, 1)} for c, n in cats.most_common()},
    'chi_square': round(sum((n - len(rows)/len(cats))**2 / (len(rows)/len(cats)) for n in cats.values()), 1),
    'chi_df': len(cats) - 1,
    'top3_pct': round(sum(n for _,n in cats.most_common(3))/len(rows)*100, 1),
    'top1': cats.most_common(1)[0][0],
    'top1_pct': round(cats.most_common(1)[0][1]/len(rows)*100, 1)
}

with open(r'D:\ll\knowledge-base\10-security\paper\stats.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f'Total: {result["total_records"]} records')
print(f'With loss: {result["records_with_loss"]}')
print(f'Total loss: {result["total_loss_b"]}B')
for y in sorted(years.keys()):
    print(f"  {y}: {years[y]} attacks")
for c, n in cats.most_common():
    print(f"  {c}: {n} ({round(n/len(rows)*100,1)}%)")
print(f'Chi2: {result["chi_square"]}, df={result["chi_df"]}')
print(f'Top3: {result["top3_pct"]}%')
