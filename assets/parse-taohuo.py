# -*- coding: utf-8 -*-
"""
解析 taohuo999 存檔的 HTML，抽出商品 + 分類資料，
產出可貼到「我的商城」的 JSON。

對應關係：
- pcatId=6669 (active) = 免洗紙杯
- pcatId=6434 = 01 日用百貨 (父分類)
- 20 個一次性紙杯/塑杯商品
"""
import re, json, os, sys, time

HTML_PATH = r'C:\Users\User\Desktop\我的商城\assets\商品搜索.html'
OUT_PRODUCTS = r'C:\Users\User\Desktop\我的商城\assets\products.json'
OUT_CATEGORIES = r'C:\Users\User\Desktop\我的商城\assets\categories.json'

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

def clean_text(s):
    s = re.sub(r'<font[^>]*>', '', s)
    s = s.replace('</font>', '')
    s = re.sub(r'<[^>]+>', '', s)
    return s.strip()

# ============ 解析分類 ============
# 找出 active 的父分類（01 日用百貨）區塊
active_block = re.search(
    r'class="ant-collapse-item ant-collapse-item-active"(.*?)</div></div></div>',
    html, re.DOTALL
)

categories = []
seen = set()

active_parent_id = None
active_parent_name = None

if active_block:
    block = active_block.group(1)
    # 父分類資訊
    m = re.search(
        r'<a[^>]*href="[^"]*pcatId=(-?\d+)"[^>]*class="router-link[^"]*">'
        r'<font[^>]*><font[^>]*>([^<]+)</font>',
        block
    )
    if m:
        active_parent_id = m.group(1)
        active_parent_name = m.group(2).strip()
        seen.add(active_parent_id)
        categories.append({
            'id': f'cat-{active_parent_id}',
            'origId': active_parent_id,
            'name': active_parent_name,
            'parentId': '',
            'sortOrder': 0,
            'isActive': True
        })
        print(f'[Parent] {active_parent_id}: {active_parent_name}')

    # 子分類（pcat-sub-item 內）
    sub_pat = re.compile(
        r'<a[^>]*href="[^"]*pcatId=(-?\d+)"[^>]*class="router-link[^"]*">'
        r'<font[^>]*><font[^>]*>([^<]+)</font>',
        re.DOTALL
    )
    sub_count = 0
    for m in sub_pat.finditer(block):
        cid = m.group(1)
        name = m.group(2).strip()
        if cid not in seen and cid != active_parent_id:
            seen.add(cid)
            categories.append({
                'id': f'cat-{cid}',
                'origId': cid,
                'name': name,
                'parentId': f'cat-{active_parent_id}',
                'sortOrder': sub_count,
                'isActive': True
            })
            sub_count += 1
    print(f'[Sub] {sub_count} 個子分類在「{active_parent_name}」之下')

# 加入其他頂層父分類（節點上架、節點、外貿新品 等，這些在側邊欄顯示但未展開）
other_top_pat = re.compile(
    r'<div data-v-6ba5a143="" class="ant-collapse-item">'
    r'<div class="ant-collapse-header"[^>]*>.*?'
    r'<a[^>]*href="[^"]*pcatId=(-?\d+)"[^>]*>'
    r'<font[^>]*><font[^>]*>([^<]+)</font>',
    re.DOTALL
)
other_count = 0
for m in other_top_pat.finditer(html):
    cid = m.group(1)
    name = m.group(2).strip()
    if cid not in seen and name and cid not in ('-1',):  # 排除「節點上架」這種特殊分類
        seen.add(cid)
        categories.append({
            'id': f'cat-{cid}',
            'origId': cid,
            'name': name,
            'parentId': '',
            'sortOrder': 100 + other_count,
            'isActive': False
        })
        other_count += 1

print(f'[Other top] {other_count} 個其他頂層分類')
print(f'[Total] {len(categories)} 個分類')

# ============ 解析商品 ============
items_html = re.findall(
    r'<div data-v-e35a7db1="" class="item bgf pb5 relative round-edge">(.*?)</p></div>',
    html, re.DOTALL
)

current_cat_id = '6669'  # 免洗紙杯（從 URL 得知）
products = []

for idx, item in enumerate(items_html):
    p = {}

    m = re.search(r'product\?id=(\d+)', item)
    p['origId'] = m.group(1) if m else ''
    p['id'] = f"p-{p['origId']}" if p['origId'] else f"p-imp-{idx}"

    # 圖片：data-src 是真實 URL
    images = []
    m = re.search(r'data-src="([^"]+\.(?:jpg|jpeg|png|webp))"', item)
    if m:
        url = m.group(1)
        # 補 https://
        if url.startswith('http://'):
            url = 'https://' + url[7:]
        images.append(url)
    p['images'] = images

    # 商品名稱
    m = re.search(
        r'<a[^>]*class="link-primary line-clamp-2[^"]*"[^>]*>(.*?)</a>',
        item, re.DOTALL
    )
    p['name'] = clean_text(m.group(1)) if m else f'商品{idx+1}'

    # 商品貨號
    m = re.search(
        r'<p[^>]*class="pl10 pr10 ml5 mr5 pt5 f-gray f-13">(.*?)</p>',
        item, re.DOTALL
    )
    p['code'] = clean_text(m.group(1)) if m else ''

    # 價格
    m = re.search(
        r'<p[^>]*class="f-16 f-primary[^"]*">(.*?)</p>',
        item, re.DOTALL
    )
    if m:
        nm = re.search(r'(\d+(?:\.\d+)?)', clean_text(m.group(1)))
        p['price'] = float(nm.group(1)) if nm else 0
    else:
        p['price'] = 0

    # 庫存
    if '無貨' in item or '缺貨' in item or '售完' in item:
        p['stock'] = 0
    else:
        p['stock'] = 100

    # 規格資訊（從商品名稱抽取容量/數量）
    specs = []
    m = re.search(r'(\d+)ml', p['name'])
    if m:
        specs.append({'name': '容量', 'value': f'{m.group(1)}ml'})
    m = re.search(r'(\d+)\s*(?:只|個|隻)', p['name'])
    if m:
        specs.append({'name': '數量', 'value': f"{m.group(1)} 只/包"})
    if p['code']:
        specs.append({'name': '貨號', 'value': p['code']})
    p['specs'] = specs

    p['categoryId'] = f'cat-{current_cat_id}'
    p['unit'] = '包'
    p['minOrder'] = 1
    p['isActive'] = True
    p['description'] = f"{p['name']}\n貨號：{p['code']}\n適用：批發、零售、聚會、辦公室"
    p['createdAt'] = int(time.time() * 1000) - idx * 60000

    products.append(p)

# ============ 確保 6669 分類已存在 ============
if not any(c['origId'] == current_cat_id for c in categories):
    categories.append({
        'id': f'cat-{current_cat_id}',
        'origId': current_cat_id,
        'name': '免洗紙杯',
        'parentId': f'cat-{active_parent_id}' if active_parent_id else '',
        'sortOrder': 0,
        'isActive': True
    })

# ============ 輸出 ============
with open(OUT_PRODUCTS, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)
with open(OUT_CATEGORIES, 'w', encoding='utf-8') as f:
    json.dump(categories, f, ensure_ascii=False, indent=2)

print(f'\n[OK] {len(products)} 商品 → products.json')
print(f'[OK] {len(categories)} 分類 → categories.json')
print('\n--- 商品預覽 ---')
for p in products:
    print(f"  {p['code']:>8} | {p['name'][:30]:<30} | {p['price']:>5} 元 | {p['stock']}")
