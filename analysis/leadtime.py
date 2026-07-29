"""Cross-correlation lead time: wastewater signal vs clinical cases, per region per variant."""
import json, math, os

DATA = os.path.expanduser('~/projects/HCI/project/data')

VARIANTS = {
    'Delta':   ('2021-06-15', '2021-11-30'),
    'Omicron': ('2021-11-01', '2022-04-30'),
    'BA.5':    ('2022-05-01', '2022-10-31'),
}

REGIONS = ['Pacific NW', 'Mountain', 'Upper Midwest', 'Lower Midwest',
           'Northeast', 'Appalachian', 'Southeast', 'Southwest']

MAX_LAG = 8  # weeks


def zscore(xs):
    n = len(xs)
    mu = sum(xs) / n
    var = sum((x - mu) ** 2 for x in xs) / n
    sd = math.sqrt(var)
    if sd == 0:
        return None
    return [(x - mu) / sd for x in xs]


def interpolate(vals):
    """Fill interior Nones by linear interpolation; drop leading/trailing Nones."""
    idx = [i for i, v in enumerate(vals) if v is not None]
    if len(idx) < 2:
        return None
    lo, hi = idx[0], idx[-1]
    out = []
    for i in range(lo, hi + 1):
        if vals[i] is not None:
            out.append(float(vals[i]))
        else:
            prev = max(j for j in idx if j < i)
            nxt = min(j for j in idx if j > i)
            f = (i - prev) / (nxt - prev)
            out.append(float(vals[prev]) + f * (float(vals[nxt]) - float(vals[prev])))
    return out, lo, hi


def xcorr(ww, cl, max_lag):
    """Correlation of ww[t] with cl[t+lag]. Positive lag => wastewater leads."""
    results = []
    for lag in range(0, max_lag + 1):
        a = ww[:len(ww) - lag] if lag else ww[:]
        b = cl[lag:]
        n = min(len(a), len(b))
        if n < 6:
            continue
        a, b = a[:n], b[:n]
        za, zb = zscore(a), zscore(b)
        if za is None or zb is None:
            continue
        r = sum(x * y for x, y in zip(za, zb)) / n
        results.append((lag, r, n))
    return results


def peak_gap(weeks, ww, cl):
    """Weeks between wastewater peak and clinical peak."""
    iw = max(range(len(ww)), key=lambda i: ww[i])
    ic = max(range(len(cl)), key=lambda i: cl[i])
    return ic - iw, weeks[iw], weeks[ic]


rw = json.load(open(os.path.join(DATA, 'region_weekly.json')))

print(f"{'variant':9} {'region':15} {'lag*':>5} {'r':>7} {'n':>4} {'peak-gap':>9}  quality")
print('-' * 74)

summary = {}
for vname, (start, end) in VARIANTS.items():
    for reg in REGIONS:
        rows = sorted((r for r in rw if r['region'] == reg and start <= r['week'] <= end),
                      key=lambda r: r['week'])
        if len(rows) < 8:
            print(f"{vname:9} {reg:15} {'--':>5} {'--':>7} {len(rows):>4} {'--':>9}  insufficient data")
            continue

        ww_raw = [r.get('mean_percentile') for r in rows]
        filled = interpolate(ww_raw)
        if filled is None:
            print(f"{vname:9} {reg:15} {'--':>5} {'--':>7} {len(rows):>4} {'--':>9}  no wastewater signal")
            continue
        ww, lo, hi = filled
        cl = [float(rows[i].get('total_cases') or 0) for i in range(lo, hi + 1)]
        weeks = [rows[i]['week'] for i in range(lo, hi + 1)]

        res = xcorr(ww, cl, MAX_LAG)
        if not res:
            print(f"{vname:9} {reg:15} {'--':>5} {'--':>7} {len(ww):>4} {'--':>9}  series too short")
            continue

        best_lag, best_r, n = max(res, key=lambda t: t[1])
        gap, wpk, cpk = peak_gap(weeks, ww, cl)

        r0 = next((r for (l, r, _) in res if l == 0), 0)
        margin = best_r - r0

        if best_lag >= 1 and best_r >= 0.6 and margin >= 0.05:
            quality = 'STRONG'
        elif best_lag >= 1 and best_r >= 0.4:
            quality = 'moderate'
        elif best_lag == 0:
            quality = 'no lead (synchronous)'
        else:
            quality = 'weak'

        print(f"{vname:9} {reg:15} {best_lag:>5} {best_r:>7.3f} {n:>4} {gap:>9} weeks  {quality}")
        summary[(vname, reg)] = dict(lag=best_lag, r=round(best_r, 3), n=n,
                                     peak_gap=gap, quality=quality,
                                     ww_peak=wpk, cl_peak=cpk,
                                     curve=[(l, round(r, 3)) for l, r, _ in res])

    print()

with open(os.path.join(os.path.dirname(__file__), 'leadtime_results.json'), 'w') as f:
    json.dump({f'{k[0]}|{k[1]}': v for k, v in summary.items()}, f, indent=2)
print('wrote leadtime_results.json')
