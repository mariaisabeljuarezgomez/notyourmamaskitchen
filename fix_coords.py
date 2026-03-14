"""
Apply EXACT values from indexexample.html for SIDES and DESSERTS.
This is the authoritative reference file.
"""
import json

data = json.load(open('raw_coords.json', encoding='utf-8'))
spans = data['text_data']

# ====== SIDES: Exact X, Y from indexexample.html, font-size=17px ======
# Left col X=601.5, Right col X=735.2-736.1
# Y rows: 799.7, 823.4, 848.7, 873.5, 896.7
sides_exact = {
    'Candied Yams':       {'x': 601.5, 'y': 799.7, 'size': 17.0},
    'Cabbage':            {'x': 736.1, 'y': 799.7, 'size': 17.0},
    'Mac N Cheese':       {'x': 601.5, 'y': 823.4, 'size': 17.0},
    'Red Beans & Rice':   {'x': 736.0, 'y': 823.4, 'size': 17.0},
    'Rice & Gravy':       {'x': 601.5, 'y': 848.7, 'size': 17.0},
    'Collard Greens':     {'x': 735.2, 'y': 848.7, 'size': 17.0},
    'Potato Salad':       {'x': 601.5, 'y': 873.5, 'size': 17.0},
    'French Fries':       {'x': 735.2, 'y': 873.5, 'size': 17.0},
    'French Fries (Lrg)': {'x': 602.3, 'y': 896.7, 'size': 17.0},
    '$7.99':              {'x': 882.8, 'y': 896.7, 'size': 17.0},
}

for i, s in enumerate(spans):
    t = s['text']
    if t in sides_exact and s['bbox'][0] > 580 and s['bbox'][1] > 790:
        spec = sides_exact[t]
        w = s['bbox'][2] - s['bbox'][0]
        h = s['bbox'][3] - s['bbox'][1]
        s['bbox'][0] = spec['x']
        s['bbox'][2] = spec['x'] + w
        s['bbox'][1] = spec['y']
        s['bbox'][3] = spec['y'] + h
        s['size'] = spec['size']
        print('[{}] SIDES {!r:22s} -> x={}, y={}, size={}'.format(i, t, spec['x'], spec['y'], spec['size']))

# ====== DESSERTS: Exact X, Y from indexexample.html ======
# Peach Cobbler Y=985.4, Banana Pudding Y=1011.2, Coffee Cake Y=1034.5
# $6.00 prices all at X=882.8, matching their item's Y
desserts_exact = {
    'Peach Cobbler':  {'x': 601.5, 'y': 985.4,  'size': 17.0},
    'Banana Pudding': {'x': 601.5, 'y': 1011.2, 'size': 17.0},
    'Coffee Cake':    {'x': 601.5, 'y': 1034.5, 'size': 17.0},
}

dessert_ys = {}
for i, s in enumerate(spans):
    t = s['text']
    if t in desserts_exact:
        spec = desserts_exact[t]
        w = s['bbox'][2] - s['bbox'][0]
        h = s['bbox'][3] - s['bbox'][1]
        s['bbox'][0] = spec['x']
        s['bbox'][2] = spec['x'] + w
        s['bbox'][1] = spec['y']
        s['bbox'][3] = spec['y'] + h
        s['size'] = spec['size']
        dessert_ys[t] = spec['y']
        print('[{}] DESSERT {!r:22s} -> x={}, y={}'.format(i, t, spec['x'], spec['y']))

# Fix $6.00 prices: X=882.8, Y matches their corresponding dessert item
order = ['Peach Cobbler', 'Banana Pudding', 'Coffee Cake']
price_spans = sorted(
    [(i, s) for i, s in enumerate(spans) if s['text'] == '$6.00' and s['bbox'][0] > 800],
    key=lambda x: x[1]['bbox'][1]
)
for idx, (i, s) in enumerate(price_spans):
    if idx < len(order):
        target_y = dessert_ys.get(order[idx], s['bbox'][1])
        h = s['bbox'][3] - s['bbox'][1]
        s['bbox'][0] = 882.8
        s['bbox'][2] = 882.8 + (s['bbox'][2] - s['bbox'][0])
        s['bbox'][1] = target_y
        s['bbox'][3] = target_y + h
        s['size'] = 17.0
        print('[{}] $6.00 for {} -> x=882.8, y={}'.format(i, order[idx], round(target_y, 1)))

print()
json.dump(data, open('raw_coords.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('Done. Saved raw_coords.json')
