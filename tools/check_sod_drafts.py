#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""核对草稿箱最近的草稿（正确解析 news_item 结构）。"""
import os, sys, requests, json
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
for p in [os.path.expanduser('~/.openclaw/.env'), r'E:\Trac Project\TracSkill\config.env']:
    if os.path.exists(p):
        load_dotenv(p, override=True)

app_id = os.environ['WECHAT_APP_ID']
app_secret = os.environ['WECHAT_APP_SECRET']
t = requests.get(f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}', timeout=15).json()['access_token']
r = requests.post(f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={t}', json={'offset': 0, 'count': 20}, timeout=15).json()

print(f"total_count = {r.get('total_count')}, item_count = {r.get('item_count')}")
for idx, item in enumerate(r.get('item', [])[:10], 1):
    news = (item.get('content') or {}).get('news_item') or []
    title = news[0].get('title', 'N/A') if news else 'N/A'
    print(f"  {idx}. {title}")
