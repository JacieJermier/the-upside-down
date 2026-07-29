"""State-level cross-correlation lead times, used for the on-map annotations."""
import json, math, os

DATA = os.path.join(os.path.dirname(__file__), '..', 'data')

VARIANTS = {
    'Omicron': ('2021-11-01', '2022-04-30'),
    'BA.5':    ('2022-03-07', '2022-09-30'),
}

MAX_LAG = 6
MIN_POINTS = 10

STATE_NAMES = {
    'AL': 'Alabama', 'AZ': 'Arizona', 'CA': 'California', 'CO': 'Colorado',
    'FL': 'Florida', 'GA': 'Georgia', 'IA': 'Iowa', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky',
    'MA': 'Massachusetts', 'MD': 'Maryland', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MO': 'Missouri', 'MT': 'Montana', 'NC': 'North Carolina', 'ND': 'North Dakota',
    'NE': 'Nebraska', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NV': 'Nevada', 'NY': 'New York', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'SC': 'South Carolina', 'SD': 'South Dakota',
    'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VA': 'Virginia',
    'VT': 'Vermont', 'WA': 'Washington', 'WI': 'Wisconsin', 'WV': 'West Virginia',
    'WY': 'Wyoming',
}


def zscore(xs):
    n = len(xs)
    mu = sum(xs) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / n)
    return None if sd == 0 else [(x - mu) / sd for x in xs]


def interpolate(vals):
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
    res = []
    for lag in range(max_lag + 1):
        a = ww[:len(ww) - lag] if lag else ww[:]
        b = cl[lag:]
        n = min(len(a), len(b))
        if n < 6:
            continue
        za, zb = zscore(a[:n]), zscore(b[:n])
        if za is None or zb is None:
            continue
        res.append((lag, sum(x * y for x, y in zip(za, zb)) / n))
    return res


rows_all = json.load(open(os.path.join(DATA, 'merged_state_weekly.json')))
out = {}

for vname, (start, end) in VARIANTS.items():
    states = sorted(set(r['state'] for r in rows_all))
    results = []
    for st in states:
        rows = sorted((r for r in rows_all if r['state'] == st and start <= r['week'] <= end),
                      key=lambda r: r['week'])
        if len(rows) < MIN_POINTS:
            continue
        filled = interpolate([r.get('mean_percentile') for r in rows])
        if filled is None:
            continue
        ww, lo, hi = filled
        if len(ww) < MIN_POINTS:
            continue
        cl = [float(rows[i].get('new_cases') or 0) for i in range(lo, hi + 1)]
        res = xcorr(ww, cl, MAX_LAG)
        if not res:
            continue
        lag, r = max(res, key=lambda t: t[1])
        r0 = dict(res).get(0, 0)
        results.append(dict(state=st, name=STATE_NAMES.get(st, st), lag=lag,
                            r=round(r, 3), gain=round(r - r0, 3), n=len(ww)))

    # Defensible = real lead, strong fit, and clearly better than lag 0
    good = [d for d in results if d['lag'] >= 1 and d['r'] >= 0.65 and d['gain'] >= 0.05]
    good.sort(key=lambda d: (-d['lag'], -d['r']))
    flat = [d for d in results if d['lag'] == 0 and d['r'] >= 0.65]
    flat.sort(key=lambda d: -d['r'])

    print(f'=== {vname} ({start} .. {end}) — {len(results)} states analysed ===')
    print('  DEFENSIBLE LEAD:')
    for d in good[:10]:
        wk = 'week' if d['lag'] == 1 else 'weeks'
        print(f"    {d['name']:16} {d['lag']} {wk:5} r={d['r']:.2f} gain={d['gain']:+.2f} n={d['n']}")
    print('  NO LEAD (synchronous, high correlation):')
    for d in flat[:5]:
        print(f"    {d['name']:16} 0 weeks  r={d['r']:.2f} n={d['n']}")
    print()
    out[vname] = dict(lead=good, synchronous=flat)

with open(os.path.join(os.path.dirname(__file__), 'leadtime_states.json'), 'w') as f:
    json.dump(out, f, indent=2)
print('wrote leadtime_states.json')
