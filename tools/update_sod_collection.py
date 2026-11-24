#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 draft/update 覆盖草稿箱里已有的 6 篇「面向规约AI」合集（旧版 → 术语修正版）。

流程：
1. draft/batchget 按标题匹配取回每篇 media_id
2. 重新上传正文图片（media/uploadimg → mmbiz URL）与封面（material/add_material → thumb_media_id）
3. draft/update 逐篇覆盖
4. draft/batchget 验证
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


def _json(resp):
    """微信部分接口 Content-Type 为 text/plain，requests 会按 ISO-8859-1 误解码，
    必须显式按 UTF-8 解析响应体。"""
    return json.loads(resp.content.decode('utf-8'))


def load_env():
    from dotenv import load_dotenv
    env_paths = [
        os.path.expanduser('~/.openclaw/.env'),
        os.path.join(r'E:\Trac Project', 'TracSkill', 'config.env'),
    ]
    for p in env_paths:
        if os.path.exists(p):
            load_dotenv(p, override=True)


def get_access_token(app_id, app_secret):
    url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={app_id}&secret={app_secret}'
    resp = requests.get(url, timeout=15)
    data = _json(resp)
    if 'access_token' not in data:
        raise RuntimeError(f'获取token失败: {data}')
    return data['access_token']


def fetch_drafts(access_token):
    """返回 [{media_id, title}] 列表（分页取回全部）。"""
    url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={access_token}'
    result = []
    offset = 0
    count = 20
    while True:
        resp = requests.post(url, json={'offset': offset, 'count': count}, timeout=15)
        data = _json(resp)
        if 'item' not in data:
            raise RuntimeError(f'获取草稿列表失败: {data}')
        for item in data['item']:
            news = (item.get('content') or {}).get('news_item') or []
            title = news[0].get('title', '') if news else ''
            result.append({'media_id': item['media_id'], 'title': title})
        total = data.get('total_count', 0)
        offset += len(data['item'])
        if offset >= total or len(data['item']) < count:
            break
    return result


def upload_content_image(access_token, file_path):
    """上传正文图片，返回 mmbiz URL。"""
    url = f'https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}'
    with open(file_path, 'rb') as f:
        files = {'media': (os.path.basename(file_path), f, 'image/png')}
        resp = requests.post(url, files=files, timeout=60)
    result = _json(resp)
    if 'url' not in result:
        raise RuntimeError(f'正文图片上传失败 {os.path.basename(file_path)}: {result}')
    return result['url']


def upload_cover_image(access_token, file_path):
    """上传封面图，返回 media_id。"""
    url = f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image'
    with open(file_path, 'rb') as f:
        files = {'media': (os.path.basename(file_path), f, 'image/png')}
        resp = requests.post(url, files=files, timeout=60)
    result = _json(resp)
    if 'media_id' not in result:
        raise RuntimeError(f'封面图上传失败 {os.path.basename(file_path)}: {result}')
    return result['media_id']


def update_draft(access_token, media_id, title, content, digest, cover_media_id):
    url = f'https://api.weixin.qq.com/cgi-bin/draft/update?access_token={access_token}'
    article = {
        'title': title,
        'content': content,
        'author': AUTHOR,
        'digest': digest[:120],
        'show_cover_pic': 1,
        'content_source_url': '',
        'thumb_media_id': cover_media_id,
    }
    data = json.dumps({'media_id': media_id, 'index': 0, 'articles': article}, ensure_ascii=False)
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    resp = requests.post(url, data=data.encode('utf-8'), headers=headers, timeout=60)
    result = _json(resp)
    if result.get('errcode', 0) != 0:
        raise RuntimeError(f'更新失败 {title}: {result}')
    return media_id


def main():
    load_env()
    app_id = os.environ.get('WECHAT_APP_ID', '')
    app_secret = os.environ.get('WECHAT_APP_SECRET', '')
    if not app_id or not app_secret:
        print('缺少 WECHAT_APP_ID / WECHAT_APP_SECRET')
        return 1

    token = get_access_token(app_id, app_secret)
    print(f'Access Token: {token[:16]}...')

    # 取回草稿箱全部草稿
    drafts = fetch_drafts(token)
    print(f'\n草稿箱共 {len(drafts)} 篇：')
    for d in drafts:
        print(f"  - [{d['media_id']}] {d['title']}")

    # 按标题精确匹配
    updated = []
    for art in ARTICLES:
        target = art['title_plain']
        match = next((d for d in drafts if d['title'] == target), None)
        if match is None:
            print(f'\n!! 未在草稿箱找到标题「{target}」，跳过')
            continue

        html_path = os.path.join(BASE_DIR, art['md'].replace('.md', '.html'))
        cover_path = os.path.join(BASE_DIR, 'covers', art['md'].replace('.md', '.png'))

        print(f"\n===== {target} =====")
        print(f"  media_id = {match['media_id']}")

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

        # 覆盖更新
        update_draft(token, match['media_id'], art['title_plain'], content, art['digest'], cover_media_id)
        updated.append(target)
        print(f'  [更新成功] {target}')

        time.sleep(1)

    print('\n' + '=' * 60)
    print(f'共更新 {len(updated)} / {len(ARTICLES)} 篇：')
    for t in updated:
        print(f'  - {t}')

    # 验证
    print('\n更新后草稿箱：')
    drafts_after = fetch_drafts(token)
    for d in drafts_after:
        print(f"  - {d['title']}")

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
