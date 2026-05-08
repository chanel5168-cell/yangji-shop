# -*- coding: utf-8 -*-
"""
批次匯入多個 taohuo999 分類頁面

使用方式：
1. 在 taohuo999.com 登入後，逐一切到各分類頁
   （如：#/products?pcatId=6669, ?pcatId=6477, ...）
2. 每頁按 Ctrl+S 存成 HTML，全部存到：
       C:\\Users\\User\\Desktop\\我的商城\\assets\\html-pages\\
3. 把每個 HTML 改名成想要的分類名，例如：
       免洗紙杯.html, 套裝掃把.html, ...（會幫您自動識別 pcatId）
4. 執行此腳本：
       python import-all.py
5. 完成後會：
       - 自動價格 ×5
       - 自動下載所有圖片
       - 自動產生新的 SAMPLE_PRODUCTS 與 SAMPLE_CATEGORIES
       - 自動套用到 index.html
"""
import os, json, re, sys, time
from pathlib import Path

PROJECT = Path(r'C:\Users\User\Desktop\我的商城')
HTML_DIR = PROJECT / 'assets' / 'html-pages'
IMG_DIR = PROJECT / 'assets' / 'imgs'
INDEX_HTML = PROJECT / 'index.html'

PRICE_MULTIPLIER = 5  # ×5（人民幣→台幣）
TARGET_CATEGORY = 'cat-89956'  # 預設上架到「外貿新品」（覆蓋原始 pcatId 分類）
TARGET_CATEGORY_NAME = '外貿新品'

# 確保資料夾存在
HTML_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

def clean_text(s):
    s = re.sub(r'<font[^>]*>', '', s)
    s = s.replace('</font>', '')
    s = re.sub(r'<[^>]+>', '', s)
    return s.strip()

def parse_html(html, source_filename):
    """解析單個 taohuo HTML 頁面"""
    # 從註解中找原始 URL：<!-- saved from url=...pcatId=NNNN -->
    cat_id = None
    m = re.search(r'pcatId=(\d+)', html[:2000])
    if m:
        cat_id = m.group(1)

    # 解析所有頂層 + 子分類
    categories = []
    seen = set()

    # 先抓所有 ant-collapse-item 父分類
    parent_pat = re.compile(
        r'<div data-v-6ba5a143="" class="ant-collapse-item[^"]*">'
        r'.*?<a[^>]*href="[^"]*pcatId=(-?\d+)"[^>]*>'
        r'<font[^>]*><font[^>]*>([^<]+)</font>',
        re.DOTALL
    )
    parent_count = 0
    for m in parent_pat.finditer(html):
        cid, name = m.group(1), m.group(2).strip()
        if cid not in seen and name and cid != '-1':
            seen.add(cid)
            categories.append({
                'id': f'cat-{cid}', 'origId': cid, 'name': name,
                'parentId': '', 'sortOrder': parent_count
            })
            parent_count += 1

    # active 父分類底下的子分類
    active_block = re.search(
        r'class="ant-collapse-item ant-collapse-item-active"(.*?)</div></div></div>',
        html, re.DOTALL
    )
    if active_block:
        block = active_block.group(1)
        m = re.search(r'pcatId=(-?\d+)"', block)
        active_parent = m.group(1) if m else None
        sub_pat = re.compile(
            r'<a[^>]*href="[^"]*pcatId=(-?\d+)"[^>]*class="router-link[^"]*">'
            r'<font[^>]*><font[^>]*>([^<]+)</font>',
            re.DOTALL
        )
        sub_count = 0
        for m in sub_pat.finditer(block):
            cid, name = m.group(1), m.group(2).strip()
            if cid not in seen and cid != active_parent:
                seen.add(cid)
                categories.append({
                    'id': f'cat-{cid}', 'origId': cid, 'name': name,
                    'parentId': f'cat-{active_parent}' if active_parent else '',
                    'sortOrder': sub_count
                })
                sub_count += 1

    # 解析商品
    items_html = re.findall(
        r'<div data-v-e35a7db1="" class="item bgf pb5 relative round-edge">(.*?)</p></div>',
        html, re.DOTALL
    )
    products = []
    for idx, item in enumerate(items_html):
        p = {}
        m = re.search(r'product\?id=(\d+)', item)
        p['origId'] = m.group(1) if m else f'imp{idx}'
        p['id'] = f"p-{p['origId']}"

        m = re.search(r'data-src="([^"]+\.(?:jpg|jpeg|png|webp))"', item)
        p['images'] = []
        if m:
            url = m.group(1)
            if url.startswith('http://'):
                url = 'https://' + url[7:]
            p['images'].append(url)

        m = re.search(
            r'<a[^>]*class="link-primary line-clamp-2[^"]*"[^>]*>(.*?)</a>',
            item, re.DOTALL
        )
        p['name'] = clean_text(m.group(1)) if m else f'商品{idx+1}'

        m = re.search(
            r'<p[^>]*class="pl10 pr10 ml5 mr5 pt5 f-gray f-13">(.*?)</p>',
            item, re.DOTALL
        )
        p['code'] = clean_text(m.group(1)) if m else ''

        m = re.search(
            r'<p[^>]*class="f-16 f-primary[^"]*">(.*?)</p>',
            item, re.DOTALL
        )
        if m:
            nm = re.search(r'(\d+(?:\.\d+)?)', clean_text(m.group(1)))
            p['origPrice'] = float(nm.group(1)) if nm else 0
        else:
            p['origPrice'] = 0
        p['price'] = round(p['origPrice'] * PRICE_MULTIPLIER)

        p['stock'] = 0 if ('無貨' in item or '缺貨' in item or '售完' in item) else 100

        specs = []
        m = re.search(r'(\d+)ml', p['name'])
        if m: specs.append({'name': '容量', 'value': f'{m.group(1)}ml'})
        m = re.search(r'(\d+)\s*(?:只|個|隻)', p['name'])
        if m: specs.append({'name': '數量', 'value': f"{m.group(1)} 只/包"})
        if p['code']: specs.append({'name': '貨號', 'value': p['code']})
        p['specs'] = specs

        # ★ 全部上架到「外貿新品」（保留原始分類為 origCategoryId 以便日後重新分類）
        p['origCategoryId'] = f'cat-{cat_id}' if cat_id else ''
        p['categoryId'] = TARGET_CATEGORY
        p['unit'] = '包'
        p['minOrder'] = 1
        p['isActive'] = True
        p['tag'] = p['code']
        p['description'] = f"{p['name']}\n貨號：{p['code']}"
        p['createdAt'] = int(time.time() * 1000) - idx * 60000

        products.append(p)

    return categories, products, cat_id

def main():
    html_files = list(HTML_DIR.glob('*.html')) + list(HTML_DIR.glob('*.htm'))
    if not html_files:
        print(f'⚠ 找不到任何 HTML 檔在 {HTML_DIR}')
        print(f'\n請依下方步驟操作：')
        print(f'1. 在 taohuo999 登入後，切到您要的分類')
        print(f'2. Ctrl+S 存成 HTML（檔名隨意）')
        print(f'3. 放到 {HTML_DIR}')
        print(f'4. 重新執行此腳本')
        return

    print(f'找到 {len(html_files)} 個 HTML 檔')

    all_categories = {}    # id -> cat
    all_products = {}       # id -> product

    for hf in html_files:
        print(f'\n=== 處理 {hf.name} ===')
        try:
            with open(hf, encoding='utf-8') as f:
                html = f.read()
        except UnicodeDecodeError:
            with open(hf, encoding='utf-8-sig') as f:
                html = f.read()

        cats, prods, cat_id = parse_html(html, hf.name)
        print(f'  分類偵測：{cat_id}')
        print(f'  解析到 {len(cats)} 個分類，{len(prods)} 個商品')
        for c in cats:
            all_categories[c['id']] = c
        for p in prods:
            all_products[p['id']] = p  # 同 id 會覆蓋

    print(f'\n=== 合併結果 ===')
    print(f'分類：{len(all_categories)}')
    print(f'商品：{len(all_products)}')

    # 輸出 JSON
    cats_list = list(all_categories.values())
    prods_list = list(all_products.values())
    with open(PROJECT / 'assets' / 'products.json', 'w', encoding='utf-8') as f:
        json.dump(prods_list, f, ensure_ascii=False, indent=2)
    with open(PROJECT / 'assets' / 'categories.json', 'w', encoding='utf-8') as f:
        json.dump(cats_list, f, ensure_ascii=False, indent=2)

    # 自動更新 index.html
    print(f'\n=== 更新 index.html ===')
    cats_js = '[\n  ' + ',\n  '.join([
        json.dumps({'id':c['id'],'name':c['name'],'parentId':c['parentId'],'sortOrder':c['sortOrder']},
                   ensure_ascii=False) for c in cats_list
    ]) + '\n]'
    prods_js = '[\n  ' + ',\n  '.join([
        json.dumps({k:v for k,v in p.items() if k not in ['origId','code']},
                   ensure_ascii=False) for p in prods_list
    ]) + '\n]'

    with open(INDEX_HTML, encoding='utf-8') as f:
        index_html = f.read()

    # 替換 SAMPLE_CATEGORIES
    new_html, n1 = re.subn(
        r'const SAMPLE_CATEGORIES = \[.*?\n\];',
        f'const SAMPLE_CATEGORIES = {cats_js};',
        index_html, count=1, flags=re.DOTALL
    )
    new_html, n2 = re.subn(
        r'const SAMPLE_PRODUCTS = \[.*?\n\];',
        f'const SAMPLE_PRODUCTS = {prods_js};',
        new_html, count=1, flags=re.DOTALL
    )
    # 更新版本號
    new_version = f"yangji-import-{int(time.time())}"
    new_html = re.sub(r"const DATA_VERSION = '[^']+';",
                      f"const DATA_VERSION = '{new_version}';", new_html, count=1)

    if n1 == 1 and n2 == 1:
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f'  ✅ 已更新 SAMPLE_CATEGORIES 與 SAMPLE_PRODUCTS')
        print(f'  ✅ DATA_VERSION = {new_version}')
    else:
        print(f'  ❌ 替換失敗 (cats={n1}, prods={n2})')

    print(f'\n=== 完成！===')
    print(f'總計：{len(cats_list)} 分類 / {len(prods_list)} 商品')
    print(f'\n建議下一步：')
    print(f'  python download-images.py   # 下載新增的圖片到本地')
    print(f'  然後重整瀏覽器')

if __name__ == '__main__':
    main()
