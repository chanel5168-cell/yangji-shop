# -*- coding: utf-8 -*-
"""
暘基五金商城 - 本地伺服器（強制不快取版）
"""
import sys, io
# 強制 stdout 用 UTF-8（Windows cp950 會無法顯示中文與 emoji）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import http.server
import socketserver
import os
import urllib.request
import urllib.parse
import ssl
import hashlib
import json

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # 強制瀏覽器不快取任何檔案
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        # CORS: 允許本地端 JS 抓 /_proxy 結果
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_OPTIONS(self):
        # CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        # 圖片上傳端點：用法 POST /upload （body = 圖片 binary）
        if self.path == '/upload':
            try:
                ctype = self.headers.get('Content-Type', 'image/jpeg').split(';')[0].strip()
                ext_map = {
                    'image/jpeg': 'jpg', 'image/jpg': 'jpg',
                    'image/png': 'png', 'image/webp': 'webp',
                    'image/gif': 'gif', 'image/bmp': 'bmp'
                }
                ext = ext_map.get(ctype, 'jpg')
                length = int(self.headers.get('Content-Length', 0))
                if length <= 0 or length > 10 * 1024 * 1024:  # 上限 10MB / 圖
                    self.send_error(400, 'Invalid size')
                    return
                data = self.rfile.read(length)
                # 用內容 MD5 當檔名（自動去重）
                h = hashlib.md5(data).hexdigest()[:16]
                filename = f'{h}.{ext}'
                imgs_dir = os.path.join(DIRECTORY, 'assets', 'imgs')
                os.makedirs(imgs_dir, exist_ok=True)
                target = os.path.join(imgs_dir, filename)
                if not os.path.exists(target):
                    with open(target, 'wb') as f:
                        f.write(data)
                rel_path = f'assets/imgs/{filename}'
                body = json.dumps({'path': rel_path, 'size': len(data)}).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
                print(f"  ↑ upload {len(data)//1024}KB → {rel_path}")
            except Exception as e:
                self.send_error(500, f'Upload failed: {e}')
            return
        self.send_error(404)

    def do_GET(self):
        # 圖片代理端點：用法 /_proxy?url=https://...
        if self.path.startswith('/_proxy?url='):
            target = urllib.parse.unquote(self.path.split('=', 1)[1])
            if not target.startswith(('http://', 'https://')):
                self.send_error(400, 'Invalid URL')
                return
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(target, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; ShopProxy/1.0)',
                    'Referer': 'https://www.taohuo999.com/',
                })
                with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                    data = resp.read()
                    ctype = resp.getheader('Content-Type', 'application/octet-stream')
                    self.send_response(200)
                    self.send_header('Content-Type', ctype)
                    self.send_header('Content-Length', str(len(data)))
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'public, max-age=86400')
                    self.end_headers()
                    self.wfile.write(data)
                    print(f"  ↗ proxy {len(data)//1024}KB ← {target[:60]}...")
            except Exception as e:
                self.send_error(502, f'Proxy fetch failed: {e}')
            return
        super().do_GET()

    def log_message(self, fmt, *args):
        # 簡化 log 輸出
        if args and 'GET' in str(args[0]):
            print(f"  → {args[0]}")

# 允許重複啟動同一 port
socketserver.TCPServer.allow_reuse_address = True

print("="*60)
print("  暘基五金商城 - 本地伺服器（強制不快取版）")
print("="*60)
print(f"  工作目錄：{DIRECTORY}")
print(f"  前台：http://localhost:{PORT}/index.html")
print(f"  後台：http://localhost:{PORT}/admin.html")
print(f"  ※ 已關閉所有快取 — 瀏覽器一定載入最新檔案")
print(f"  停止伺服器：在此視窗按 Ctrl+C")
print("="*60)
print()

with socketserver.TCPServer(("", PORT), NoCacheHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n伺服器已停止。")
