# -*- coding: utf-8 -*-
"""
圖片本地化下載工具

功能：
1. 讀取 products.json 裡所有商品圖片 URL
2. 下載到 assets/imgs/ 資料夾
3. 產出 products-local.json：把 images 改為本地相對路徑
4. 也產出可貼回 index.html 的 SAMPLE_PRODUCTS

執行方式：
  cd C:\\Users\\User\\Desktop\\我的商城\\assets
  python download-images.py

完成後：
  - 圖片會在 assets/imgs/ 內
  - 產生 products-local.json
  - 您可以選擇：
    A. 在 admin 後台編輯每個商品圖片路徑
    B. 用本腳本最後產的 SAMPLE_PRODUCTS 覆蓋 index.html
"""
import os, json, urllib.request, urllib.error, ssl, time, re, sys

PROJECT_DIR = r'C:\Users\User\Desktop\我的商城'
PRODUCTS_JSON = os.path.join(PROJECT_DIR, 'assets', 'products.json')
IMGS_DIR = os.path.join(PROJECT_DIR, 'assets', 'imgs')
OUT_JSON = os.path.join(PROJECT_DIR, 'assets', 'products-local.json')

os.makedirs(IMGS_DIR, exist_ok=True)

# SSL — 略過 cert 檢查（中國 CDN 可能用自簽憑證）
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0',
    'Referer': 'https://www.taohuo999.com/'
}

def safe_filename(url):
    """從 URL 取最後檔名作為儲存檔名"""
    name = url.split('/')[-1]
    # 去掉 ?query，限制長度
    name = name.split('?')[0]
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)[:120]
    return name

def download_one(url, target):
    if os.path.exists(target):
        return 'skip'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            data = resp.read()
            if len(data) < 200:
                return 'fail-tiny'
            with open(target, 'wb') as f:
                f.write(data)
            return f'ok ({len(data)//1024} KB)'
    except urllib.error.HTTPError as e:
        return f'fail-http-{e.code}'
    except Exception as e:
        return f'fail-{type(e).__name__}'

def main():
    with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
        products = json.load(f)

    print(f'共 {len(products)} 件商品')
    print(f'圖片目標資料夾：{IMGS_DIR}\n')

    new_products = []
    ok = fail = skip = 0
    for i, p in enumerate(products):
        new_p = dict(p)
        new_images = []
        for img_url in p.get('images', []):
            fname = safe_filename(img_url)
            target = os.path.join(IMGS_DIR, fname)
            rel_path = f'assets/imgs/{fname}'
            print(f'  [{i+1}/{len(products)}] {fname[:60]}...', end=' ')
            sys.stdout.flush()
            result = download_one(img_url, target)
            print(result)
            if result.startswith('ok'):
                new_images.append(rel_path)
                ok += 1
            elif result == 'skip':
                new_images.append(rel_path)
                skip += 1
            else:
                # 下載失敗，保留原始 URL（前台 onerror 會 fallback）
                new_images.append(img_url)
                fail += 1
            time.sleep(0.3)  # 禮貌停頓
        new_p['images'] = new_images
        new_products.append(new_p)

    # 寫出本地化版本
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(new_products, f, ensure_ascii=False, indent=2)

    print(f'\n=== 完成 ===')
    print(f'  成功下載：{ok}  ·  已存在跳過：{skip}  ·  失敗：{fail}')
    print(f'  本地化清單：{OUT_JSON}')

    # 額外輸出可貼回 index.html 的 SAMPLE_PRODUCTS 區塊
    print(f'\n=== 已產生 SAMPLE_PRODUCTS 替換片段 ===')
    out_txt = os.path.join(PROJECT_DIR, 'assets', '_local_sample.txt')
    lines = ['const SAMPLE_PRODUCTS = [']
    for p in new_products:
        clean = {
            'id': p['id'],
            'name': p['name'],
            'categoryId': p['categoryId'],
            'price': p['price'],
            'origPrice': p.get('origPrice', p['price']/5 if p['price']>10 else p['price']),
            'stock': p['stock'],
            'unit': p['unit'],
            'minOrder': p['minOrder'],
            'images': p['images'],
            'description': p['description'],
            'specs': p['specs'],
            'isActive': True,
            'tag': p.get('code', p.get('tag', '')),
            'createdAt': p['createdAt']
        }
        lines.append('  ' + json.dumps(clean, ensure_ascii=False) + ',')
    lines[-1] = lines[-1].rstrip(',')
    lines.append('];')
    with open(out_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'  片段已存：{out_txt}')
    print(f'\n下一步：')
    print(f'  1. 用文字編輯器打開 {out_txt}')
    print(f'  2. 在 index.html 找到 const SAMPLE_PRODUCTS = [...] 整個替換')
    print(f'  3. 把 DATA_VERSION 改成新的字串（例 "yangji-localimg"）強制更新')
    print(f'  4. 重整瀏覽器即可看到本地圖片')

if __name__ == '__main__':
    main()
