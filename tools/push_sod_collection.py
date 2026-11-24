#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量推送「面向规约AI」合集（6篇）到微信公众号草稿箱。
- 上传正文图片（media/uploadimg → mmbiz URL 替换 <img src>）
- 上传封面图（material/add_material → thumb_media_id）
- 推送草稿（draft/add）
- 验证草稿箱（draft/batchget）
"""

import os
import re
import sys
import json
import time
import requests

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prepare_sod_collection import ARTICLES, BASE_DIR

AUTHOR = 'TS爱心联盟'


def load_env():
    from dotenv import load_dotenv
    env_paths = [
        os.path.expanduser('~/.openclaw/.env'),
        os.path.join(os.path.dirname(__file__), 'TracSkill/config.env'),
    ]
    for p in env_paths:
        if os.path.exists(p):
            load_dotenv(p, override=True)


def get_access_token(app_id, app_secret):
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}'
    resp = requests.get(url, timeout=15)
    data = resp.json()
    if 'access_token' not in data:
        raise RuntimeError(f'获取token失败: {data}')
    return data['access_token']


def upload_content_image(access_token, file_path):
    """上传正文图片，返回 mmbiz URL。"""
    url = f'https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}'
    with open(file_path, 'rb') as f:
        files = {'media': (os.path.basename(file_path), f, 'image/png')}
        resp = requests.post(url, files=files, timeout=60)
    result = resp.json()
    if 'url' not in result:
        raise RuntimeError(f'正文图片上传失败 {os.path.basename(file_path)}: {result}')
    return result['url']


def upload_cover_image(access_token, file_path):
    """上传封面图，返回 media_id。"""
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    with open(file_path, 'rb') as f:
        files = {'media': (os.path.basename(file_path), f, 'image/png')}
        resp = requests.post(url, files=files, timeout=60)
    result = resp.json()
    if 'media_id' not in result:
        raise RuntimeError(f'封面图上传失败 {os.path.basename(file_path)}: {result}')
    return result['media_id']


def push_to_draft(access_token, title, content, digest, cover_media_id):
    url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}'
    article = {
        'title': title,
        'content': content,
        'author': AUTHOR,
        'digest': digest[:120],
        'show_cover_pic': 1,
        'content_source_url': '',
        'thumb_media_id': cover_media_id,
    }
    data = json.dumps({'articles': [article]}, ensure_ascii=False)
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    resp = requests.post(url, data=data.encode('utf-8'), headers=headers, timeout=60)
    result = resp.json()
    if 'media_id' not in result:
        raise RuntimeError(f'推送失败 {title}: {result}')
    return result['media_id']


def verify_drafts(access_token):
    url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}'
    resp = requests.post(url, json={'offset': 0, 'count': 20}, timeout=15)
    result = resp.json()
    if 'item' not in result:
        print(f'获取草稿列表失败: {result}')
        return
    print(f"\n草稿箱共 {result.get('total_count', '?')} 篇，最近列表：")
    for idx, item in enumerate(result['item'][:12], 1):
        articles = item.get('articles', [])
        if articles:
            print(f"  {idx}. {articles[0].get('title', 'N/A')}")


def main():
    load_env()
    app_id = os.environ.get('WECHAT_APP_ID', '')
    app_secret = os.environ.get('WECHAT_APP_SECRET', '')
    if not app_id or not app_secret:
        print('缺少 WECHAT_APP_ID / WECHAT_APP_SECRET')
        return 1

    token = get_access_token(app_id, app_secret)
    print(f'Access Token: {token[:16]}...')

    pushed = []
    for art in ARTICLES:
        html_path = os.path.join(BASE_DIR, art['md'].replace('.md', '.html'))
        cover_path = os.path.join(BASE_DIR, 'covers', art['md'].replace('.md', '.png'))

        print(f"\n===== {art['title_plain']} =====")

        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 上传并替换正文图片
        img_srcs = re.findall(r'src="(png/[^"]+\.png)"', content)
        for rel in img_srcs:
            abs_path = os.path.join(BASE_DIR, rel.replace('/', os.sep))
            mmbiz_url = upload_content_image(token, abs_path)
            content = content.replace(f'src="{rel}"', f'src="{mmbiz_url}"')
            print(f'  [正文图] {os.path.basename(rel)} -> {mmbiz_url[:50]}...')

        # 上传封面
        cover_media_id = upload_cover_image(token, cover_path)
        print(f'  [封面] {os.path.basename(cover_path)} -> {cover_media_id}')

        # 推送
        draft_id = push_to_draft(token, art['title_plain'], content, art['digest'], cover_media_id)
        pushed.append((art['title_plain'], draft_id))
        print(f'  [推送成功] draft media_id = {draft_id}')

        time.sleep(1)

    print('\n' + '=' * 60)
    print(f'共推送 {len(pushed)} 篇：')
    for t, d in pushed:
        print(f'  - {t}  ({d})')

    verify_drafts(token)
    print('\n完成。请登录微信公众平台草稿箱查看。')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'\n异常: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
