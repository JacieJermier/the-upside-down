"""Lead times, filtered to places where wastewater coverage is actually meaningful.

The first pass ranked states purely on correlation, which surfaced Idaho (one plant,
50k people served, 2.7% of the state) above Illinois (71 plants, 63% of the state).
This version requires a state to have a real share of its population under
surveillance before its lead time is reported.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data')

VARIANTS = {
    'Omicron': ('2021-11-01', '2022-04-30'),
    'BA.5':    ('2022-03-07', '2022-09-30'),
}

MAX_LAG = 6
MIN_POINTS = 14        # weekly observations before any lag is applied
MIN_COVERAGE = 0.15    # share of state population served by sampled plants
MIN_SITES = 5          # a single plant is an anecdote, not a state signal

# 2020 census populations, used only to express coverage as a share.
STATE_POP = {
    'AL': 5024279, 'AZ': 7151502, 'CO': 5773714, 'FL': 21538187, 'GA': 10711908,
    'IA': 3190369, 'ID': 1839106, 'IL': 12812508, 'IN': 6785528, 'KS': 2937880,
    'KY': 4505836, 'MA': 7029917, 'MD': 6177224, 'ME': 1362359, 'MN': 5706494,
    'MO': 6154913, 'MT': 1084225, 'NC': 10439388, 'NH': 1377529, 'NJ': 9288994,
    'NV': 3104614, 'NY': 20201249, 'OR': 4237256, 'PA': 13002700, 'TX': 29145505,
    'UT': 3271616, 'WI': 5893718, 'WV': 1793716,
}

STATE_NAMES = {
    'AL': 'Alabama', 'AZ': 'Arizona', 'CO': 'Colorado', 'FL': 'Florida',
    'GA': 'Georgia', 'IA': 'Iowa', 'ID': 'Idaho', 'IL': 'Illinois',
    'IN': 'Indiana', 'KS': 'Kansas', 'KY': 'Kentucky', 'MA': 'Massachusetts',
    'MD': 'Maryland', 'ME': 'Maine', 'MN': 'Minnesota', 'MO': 'Missouri',
    'MT': 'Montana', 'NC': 'North Carolina', 'NH': 'New Hampshire',
    'NJ': 'New Jersey', 'NV': 'Nevada', 'NY': 'New York', 'OR': 'Oregon',
    'PA': 'Pennsylvania', 'TX': 'Texas', 'UT': 'Utah', 'WI': 'Wisconsin',
    'WV': 'West Virginia',
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
        if n < 10:
            continue
        za, zb = zscore(a[:n]), zscore(b[:n])
        if za is None or zb is None:
            continue
        res.append((lag, sum(x * y for x, y in zip(za, zb)) / n, n))
    return res


sites = json.load(open(os.path.join(DATA, 'sites.json')))
coverage, nsites = {}, {}
for st, pop in STATE_POP.items():
    sub = [s for s in sites if s.get('state') == st]
    nsites[st] = len(sub)
    coverage[st] = sum(s.get('population_served') or 0 for s in sub) / pop

rows_all = json.load(open(os.path.join(DATA, 'merged_state_weekly.json')))
out = {}

print('COVERAGE (share of state population served by sampled plants)')
print(f'  {"st":3} {"sites":>5} {"coverage":>9}   status')
for st in sorted(coverage, key=lambda s: -coverage[s]):
    ok = coverage[st] >= MIN_COVERAGE and nsites[st] >= MIN_SITES
    print(f'  {st:3} {nsites[st]:>5} {coverage[st]*100:>8.1f}%   {"included" if ok else "EXCLUDED"}')
print()

for vname, (start, end) in VARIANTS.items():
    kept, dropped = [], []
    for st in sorted(STATE_POP):
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
        lag, r, n = max(res, key=lambda t: t[1])
        r0 = next((rr for (l, rr, _) in res if l == 0), 0)
        rec = dict(state=st, name=STATE_NAMES[st], lag=lag, r=round(r, 3),
                   gain=round(r - r0, 3), n=n, sites=nsites[st],
                   coverage=round(coverage[st] * 100, 1))
        if coverage[st] >= MIN_COVERAGE and nsites[st] >= MIN_SITES:
            kept.append(rec)
        else:
            dropped.append(rec)

    kept.sort(key=lambda d: (-d['lag'], -d['r']))
    lead = [d for d in kept if d['lag'] >= 1 and d['r'] >= 0.65 and d['gain'] >= 0.03]
    flat = [d for d in kept if d['lag'] == 0 and d['r'] >= 0.65]

    print(f'=== {vname} ===')
    print('  REPORTABLE LEAD (adequate coverage):')
    for d in lead:
        wk = 'week' if d['lag'] == 1 else 'weeks'
        print(f"    {d['name']:15} {d['lag']} {wk:5} r={d['r']:.2f} gain={d['gain']:+.2f} "
              f"n={d['n']:>2} sites={d['sites']:>2} cov={d['coverage']}%")
    print('  NO LEAD (adequate coverage, peaks at lag 0):')
    for d in flat:
        print(f"    {d['name']:15} 0 weeks  r={d['r']:.2f} n={d['n']:>2} "
              f"sites={d['sites']:>2} cov={d['coverage']}%")
    print('  DROPPED for thin coverage (would have been reported before):')
    for d in sorted(dropped, key=lambda x: -x['lag']):
        if d['lag'] >= 1 and d['r'] >= 0.65:
            wk = 'week' if d['lag'] == 1 else 'weeks'
            print(f"    {d['name']:15} {d['lag']} {wk:5} r={d['r']:.2f} "
                  f"sites={d['sites']:>2} cov={d['coverage']}%")
    print()
    out[vname] = dict(lead=lead, synchronous=flat, dropped=dropped)

with open(os.path.join(HERE, 'leadtime_v2.json'), 'w') as f:
    json.dump({'coverage': {k: round(v * 100, 1) for k, v in coverage.items()},
               'sites': nsites, 'results': out}, f, indent=2)
print('wrote leadtime_v2.json')
