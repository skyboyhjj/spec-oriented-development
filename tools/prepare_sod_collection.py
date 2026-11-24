#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
准备「面向规约AI」合集：生成 6 篇公众号 HTML（第07期金色样式）+ 6 张封面图。
"""

import os
import re
import sys

BASE_DIR = r"E:\00kb-TS爱心联盟公众号\内容管理\面向规约AI合集"
PNG_DIR = os.path.join(BASE_DIR, "png")
COVER_DIR = os.path.join(BASE_DIR, "covers")

# ---------------- 样式常量（第07期金色样式） ----------------
WRAPPER_OPEN = '''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>{title_plain}</title></head>
<body style="margin:0;background:#fff;">
<div style="font-size:16px;line-height:1.9;color:#3f3f3f;letter-spacing:.5px;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif;max-width:677px;margin:0 auto;padding:24px 16px 48px;">
'''

H1 = '<h1 style="font-size:22px;font-weight:700;color:#1a1a1a;line-height:1.5;margin:0 0 6px;letter-spacing:1px;text-align:center;">{title_html}</h1>\n'

BLOCKQUOTE_OPEN = '<blockquote style="margin:0 0 22px;padding:16px 18px;background:#f7f5f1;border-left:3px solid #d8cfbe;color:#5a5a5a;font-size:15px;line-height:1.85;">\n'
BLOCKQUOTE_CLOSE = '</blockquote>\n'

H2 = '<h2 style="font-size:18px;font-weight:700;color:#1a1a1a;line-height:1.6;margin:40px 0 18px;padding-left:12px;border-left:4px solid #b08d57;">{text}</h2>\n'

P = '<p style="margin:0 0 20px;text-align:justify;">{text}</p>\n'

HR = '<hr style="border:none;border-top:1px solid #e8e4dc;margin:36px 0;">\n'

IMG = '<p style="margin:0 0 6px;"><img src="{src}" alt="{alt}" style="max-width:100%;height:auto;display:block;margin:0 auto 8px;border-radius:2px;"></p>\n<p style="margin:0 0 26px;font-size:13px;color:#9a9a9a;text-align:center;">{caption}</p>\n'

TABLE_OPEN = '<table style="width:100%;border-collapse:collapse;margin:0 0 22px;font-size:14px;line-height:1.7;">\n'
THEAD_OPEN = '<thead><tr>\n'
TH = '<th style="border:1px solid #e2ddd3;padding:8px 10px;background:#f7f5f1;font-weight:700;color:#3f3f3f;text-align:left;">{text}</th>\n'
THEAD_CLOSE = '</tr></thead>\n'
TBODY_OPEN = '<tbody>\n'
TR_OPEN = '<tr>\n'
TD = '<td style="border:1px solid #e2ddd3;padding:8px 10px;text-align:left;">{text}</td>\n'
TR_CLOSE = '</tr>\n'
TBODY_CLOSE = '</tbody>\n'
TABLE_CLOSE = '</table>\n'

WRAPPER_CLOSE = '</div></body></html>\n'


def escape(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_inline(text):
    text = escape(text)
    text = re.sub(
        r'`([^`]+)`',
        r'<code style="font-family:Consolas,Monaco,monospace;background:#f6f4ef;padding:2px 6px;border-radius:3px;font-size:14px;color:#8a6d3b;">\1</code>',
        text,
    )
    return text


def render_blockquote(paras):
    out = BLOCKQUOTE_OPEN
    for idx, p in enumerate(paras):
        style = 'margin:0 0 14px;text-align:justify;' if idx < len(paras) - 1 else 'margin:0;text-align:justify;'
        out += f'<p style="{style}">{escape(p)}</p>\n'
    out += BLOCKQUOTE_CLOSE
    return out


def render_table(table_lines):
    def parse_row(line):
        line = line.strip().strip('|')
        return [c.strip() for c in line.split('|')]

    rows = [parse_row(l) for l in table_lines]
    rows = [r for r in rows if not all(re.match(r'^-+$', c) for c in r)]
    if not rows:
        return ''
    header = rows[0]
    body = rows[1:]
    out = TABLE_OPEN + THEAD_OPEN
    for c in header:
        out += TH.format(text=render_inline(c))
    out += THEAD_CLOSE + TBODY_OPEN
    for row in body:
        out += TR_OPEN
        for c in row:
            out += TD.format(text=render_inline(c))
        out += TR_CLOSE
    out += TBODY_CLOSE + TABLE_CLOSE
    return out


def render_numbered_list(items):
    out = []
    for item in items:
        m = re.match(r'^(\d+)\.\s+(.*)$', item)
        if not m:
            continue
        num, rest = m.group(1), m.group(2)
        if '。' in rest:
            lead, tail = rest.split('。', 1)
            lead += '。'
            out.append(
                f'<p style="margin:0 0 12px;text-align:justify;">'
                f'<strong style="font-weight:700;color:#8a6d3b;">{num}. {render_inline(lead)}</strong>{render_inline(tail)}</p>\n'
            )
        else:
            out.append(
                f'<p style="margin:0 0 12px;text-align:justify;">'
                f'<strong style="font-weight:700;color:#8a6d3b;">{num}. {render_inline(rest)}</strong></p>\n'
            )
    return ''.join(out)


def render_ending(stripped):
    if stripped.startswith('△'):
        return '<p style="margin:0 0 20px;text-align:justify;">△ <strong style="font-weight:700;color:#8a6d3b;">原创声明</strong>：本文原创，转载请注明出处。</p>\n'
    if stripped.startswith('TS爱心联盟'):
        return '<p style="margin:0 0 20px;text-align:justify;"><strong style="font-weight:700;color:#8a6d3b;">TS爱心联盟 · 探索爱的真谛，让爱自由表达</strong></p>\n'
    if stripped.startswith('标签'):
        return '<p style="margin:0 0 20px;text-align:justify;">' + escape(stripped) + '</p>\n'
    return P.format(text=escape(stripped))


def convert_markdown(md_text, title_html, title_plain, png_files):
    """将 markdown 转为第07期金色样式 HTML。"""
    lines = md_text.split('\n')

    # 第一步：把 mermaid 代码块（及其紧邻上方的说明句）替换成 @@IMAGE@@ 占位符
    result = []
    png_idx = 0
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped == '```mermaid':
            j = i + 1
            while j < len(lines) and lines[j].strip() != '```':
                j += 1
            # 取最近的非空行作为图注
            while result and result[-1].strip() == '':
                result.pop()
            caption = result.pop().strip() if result else ''
            png = png_files[png_idx] if png_idx < len(png_files) else ''
            png_idx += 1
            result.append(f'@@IMAGE@@{png}||{caption}')
            i = j + 1
        else:
            result.append(lines[i])
            i += 1

    # 第二步：逐行转 HTML
    html = []
    in_intro = True  # H1 之后、首个 ## 之前的内容作为导语引文块
    intro_paras = []
    i = 0
    while i < len(result):
        line = result[i]
        stripped = line.strip()

        if stripped.startswith('@@IMAGE@@'):
            if intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
                in_intro = False
            payload = stripped[len('@@IMAGE@@'):]
            png, caption = payload.split('||', 1)
            html.append(IMG.format(src=png, alt=escape(caption), caption=escape(caption)))
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped.startswith('# '):
            if intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
            html.append(H1.format(title_html=title_html))
            in_intro = True
            i += 1
            continue

        if stripped.startswith('## '):
            if in_intro and intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
                in_intro = False
            html.append(H2.format(text=escape(stripped[3:])))
            i += 1
            continue

        if stripped == '---':
            if in_intro and intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
                in_intro = False
            html.append(HR)
            i += 1
            continue

        if stripped.startswith('|'):
            table_lines = []
            while i < len(result) and result[i].strip().startswith('|'):
                table_lines.append(result[i].strip())
                i += 1
            if in_intro and intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
                in_intro = False
            html.append(render_table(table_lines))
            continue

        if stripped.startswith('△') or stripped.startswith('TS爱心联盟') or stripped.startswith('标签'):
            if in_intro and intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
                in_intro = False
            html.append(render_ending(stripped))
            i += 1
            continue

        if re.match(r'^\d+\.\s', stripped):
            items = []
            while i < len(result) and re.match(r'^\d+\.\s', result[i].strip()):
                items.append(result[i].strip())
                i += 1
            if in_intro and intro_paras:
                html.append(render_blockquote(intro_paras))
                intro_paras = []
                in_intro = False
            html.append(render_numbered_list(items))
            continue

        # 普通段落
        if in_intro:
            intro_paras.append(stripped)
        else:
            html.append(P.format(text=render_inline(stripped)))
        i += 1

    if intro_paras:
        html.append(render_blockquote(intro_paras))

    body = ''.join(html)
    return WRAPPER_OPEN.format(title_plain=title_plain) + body + WRAPPER_CLOSE


# ---------------- 文章元数据 ----------------
ARTICLES = [
    {
        'md': '00_导读_面向规约AI合集.md',
        'title_html': '面向规约AI · 合集导读',
        'title_plain': '面向规约AI · 合集导读',
        'cover_label': '导读',
        'cover_lines': ['面向规约AI · 合集导读'],
        'digest': '和 AI 结对一年悟出：它聪明，但不一定听话。这个合集，讲怎么把 AI 的一次性聪明变成稳定可靠——方法叫「面向规约」。',
        'images': ['png/00_导读_阅读路径.png', 'png/00_导读_理念到实践.png'],
    },
    {
        'md': '01_面向规约是什么.md',
        'title_html': '面向规约是什么<br>让 AI 从「一次聪明」到「稳定可靠」',
        'title_plain': '面向规约是什么：让 AI 从「一次聪明」到「稳定可靠」',
        'cover_label': '第 1 篇',
        'cover_lines': ['面向规约是什么', '让 AI 从「一次聪明」', '到「稳定可靠」'],
        'digest': '换会话就忘约定、功能越做越跑偏、难题下次还得重来。面向规约，用规约四层加五步闭环，填上这三个坑。',
        'images': ['png/01_规约四层.png', 'png/01_五步闭环.png'],
    },
    {
        'md': '02_规约是长出来的.md',
        'title_html': '规约是长出来的，不是写出来的',
        'title_plain': '规约是长出来的，不是写出来的',
        'cover_label': '第 2 篇',
        'cover_lines': ['规约是长出来的，不是写出来的'],
        'digest': '规约不是先设计完美再照做，而是一路偏差、一路复审长出来的。这篇讲它怎么诞生、怎么运营、怎么自我修正。',
        'images': ['png/02_六步启动清单.png', 'png/02_宪法演进.png'],
    },
    {
        'md': '03_12处偏差教给我的.md',
        'title_html': '12 处偏差<br>教给了这套方法最重要的一课',
        'title_plain': '12 处偏差，教给了这套方法最重要的一课',
        'cover_label': '第 3 篇',
        'cover_lines': ['12 处偏差', '教给了这套方法最重要的一课'],
        'digest': '功能能跑，不等于做对了。12 处偏差教给这套方法最重要的一课：有规约，不等于按规约做。',
        'images': ['png/03_偏差闭环.png', 'png/03_26条禁止行为.png'],
    },
    {
        'md': '04_四套模板.md',
        'title_html': '四套模板<br>把方法套用到你的项目',
        'title_plain': '四套模板：把方法套用到你的项目',
        'cover_label': '第 4 篇',
        'cover_lines': ['四套模板', '把方法套用到你的项目'],
        'digest': '面向规约不是理念，是四张可以抄的表。接到需求、写完功能、收尾复盘、发现跑偏，各填一张。',
        'images': ['png/04_四模板闭环.png', 'png/04_八阶段流程.png'],
    },
    {
        'md': '05_模板填出来长什么样.md',
        'title_html': '四套模板<br>填出来长什么样',
        'title_plain': '四套模板，填出来长什么样',
        'cover_label': '第 5 篇',
        'cover_lines': ['四套模板', '填出来长什么样'],
        'digest': '上一篇给了空白模板，这一篇拿真实项目填给你看，照着抄就行。',
        'images': ['png/05_模板A转译.png'],
    },
]


# ---------------- 封面图生成 ----------------
def load_font(size, bold=False):
    from PIL import ImageFont
    candidates = []
    if bold:
        candidates = [
            r'C:\Windows\Fonts\msyhbd.ttc',
            r'C:\Windows\Fonts\msyh.ttc',
            r'C:\Windows\Fonts\simhei.ttf',
        ]
    else:
        candidates = [
            r'C:\Windows\Fonts\msyh.ttc',
            r'C:\Windows\Fonts\simhei.ttf',
            r'C:\Windows\Fonts\msyhbd.ttc',
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def wrap_text(draw, text, font, max_width):
    lines = []
    current = ''
    for ch in text:
        test = current + ch
        bbox = draw.textbbox((0, 0), test, font=font)
        w = bbox[2] - bbox[0]
        if w > max_width and current:
            lines.append(current)
            current = ch
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def generate_cover(title_lines, cover_label, out_path):
    from PIL import Image, ImageDraw
    W, H = 900, 500
    img = Image.new('RGB', (W, H), '#f7f5f1')
    draw = ImageDraw.Draw(img)

    # 内边框
    draw.rectangle([36, 36, W - 36, H - 36], outline='#d8cfbe', width=2)

    font_label = load_font(30, bold=True)
    font_rule_title = load_font(48, bold=True)
    font_footer = load_font(24, bold=False)

    # 顶部标签
    label = f'面向规约AI · {cover_label}'
    lbbox = draw.textbbox((0, 0), label, font=font_label)
    lw = lbbox[2] - lbbox[0]
    draw.text(((W - lw) / 2, 92), label, font=font_label, fill='#b08d57')

    # 金色短横线
    draw.rectangle([(W - 120) / 2, 140, (W + 120) / 2, 143], fill='#b08d57')

    # 标题（按给定分行，每行仍自动换行兜底）
    wrapped_all = []
    for seg in title_lines:
        wrapped_all.extend(wrap_text(draw, seg, font_rule_title, 760))

    line_height = 64
    total_h = line_height * len(wrapped_all)
    start_y = (H - total_h) / 2 + 20
    for idx, line in enumerate(wrapped_all):
        bbox = draw.textbbox((0, 0), line, font=font_rule_title)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2, start_y + idx * line_height), line, font=font_rule_title, fill='#1a1a1a')

    # 底部
    footer = 'TS爱心联盟 · 探索爱的真谛，让爱自由表达'
    fbbox = draw.textbbox((0, 0), footer, font=font_footer)
    fw = fbbox[2] - fbbox[0]
    draw.text(((W - fw) / 2, H - 76), footer, font=font_footer, fill='#9a9a9a')

    img.save(out_path, 'PNG')
    return out_path


def main():
    os.makedirs(COVER_DIR, exist_ok=True)

    for art in ARTICLES:
        md_path = os.path.join(BASE_DIR, art['md'])
        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        html = convert_markdown(md_text, art['title_html'], art['title_plain'], art['images'])

        html_name = os.path.splitext(art['md'])[0] + '.html'
        html_path = os.path.join(BASE_DIR, html_name)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'[HTML] {html_name}  ({len(html)} 字符)')

        cover_name = os.path.splitext(art['md'])[0] + '.png'
        cover_path = os.path.join(COVER_DIR, cover_name)
        generate_cover(art['cover_lines'], art['cover_label'], cover_path)
        print(f'[封面] {cover_name}')

    print('\n全部完成。')


if __name__ == '__main__':
    main()
