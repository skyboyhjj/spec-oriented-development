# -*- coding: utf-8 -*-
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT_DIR = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("MSYH", os.path.join(FONT_DIR, "msyh.ttc"), subfontIndex=0))
pdfmetrics.registerFont(TTFont("MSYHBD", os.path.join(FONT_DIR, "msyhbd.ttc"), subfontIndex=0))

DIR = r"E:\00kb-TS爱心联盟公众号\内容管理\面向规约AI合集"
FILES = [
    "00_导读_面向规约AI合集.md",
    "01_面向规约是什么.md",
    "02_规约是长出来的.md",
    "03_12处偏差教给我的.md",
    "04_四套模板.md",
    "05_模板填出来长什么样.md",
]
OUT = os.path.join(DIR, "面向规约AI合集.pdf")

MAIN = colors.HexColor("#8B1E22")
BODY = colors.HexColor("#333333")

title_style = ParagraphStyle("title", fontName="MSYHBD", fontSize=19, leading=27,
                             textColor=MAIN, spaceAfter=8)
h2_style = ParagraphStyle("h2", fontName="MSYHBD", fontSize=13.5, leading=19,
                          textColor=MAIN, spaceBefore=12, spaceAfter=6)
body_style = ParagraphStyle("body", fontName="MSYH", fontSize=10.5, leading=18,
                            textColor=BODY, spaceAfter=6, alignment=TA_LEFT)
note_style = ParagraphStyle("note", fontName="MSYH", fontSize=9.5, leading=15,
                            textColor=colors.HexColor("#8a6d3b"), spaceAfter=4)
footer_style = ParagraphStyle("footer", fontName="MSYH", fontSize=9.5, leading=15,
                              textColor=colors.HexColor("#888888"), spaceAfter=3)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    return s


def parse_md(lines):
    """Parse markdown lines into a list of reportlab flowables."""
    out = []
    i = 0
    n = len(lines)
    first_h1 = True
    while i < n:
        line = lines[i].rstrip("\n").rstrip()
        if line.strip() == "":
            i += 1
            continue
        if line.startswith("# "):
            if not first_h1:
                out.append(PageBreak())
            first_h1 = False
            out.append(Paragraph(inline(line[2:].strip()), title_style))
            out.append(HRFlowable(width="100%", thickness=1.2, color=MAIN, spaceAfter=8))
            i += 1
        elif line.startswith("## "):
            out.append(Paragraph(inline(line[3:].strip()), h2_style))
            i += 1
        elif line.startswith("---") and line.strip().replace("-", "") == "":
            out.append(Spacer(1, 6))
            out.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cccccc"), spaceAfter=6))
            i += 1
        elif line.startswith("|"):
            # collect table block
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                raw = lines[i].strip().strip("|")
                cells = [c.strip() for c in raw.split("|")]
                rows.append(cells)
                i += 1
            # drop separator row (cells all dashes)
            cleaned = []
            for r in rows:
                if all(re.fullmatch(r"-{2,}", c) for c in r):
                    continue
                cleaned.append(r)
            if cleaned:
                data = [[Paragraph(inline(c), body_style) for c in row] for row in cleaned]
                ncols = max(len(r) for r in cleaned)
                data = [row + [Paragraph("", body_style)] * (ncols - len(row)) for row in data]
                colw = (A4[0] - 2 * 2 * cm) / ncols
                t = Table(data, colWidths=[colw] * ncols, repeatRows=1)
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3e9e9")),
                    ("FONTNAME", (0, 0), (-1, 0), "MSYHBD"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d9c2c2")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                out.append(t)
                out.append(Spacer(1, 8))
        elif re.match(r"^\d+\.\s", line):
            # ordered list block
            while i < n and re.match(r"^\d+\.\s", lines[i].strip()):
                num = re.match(r"^(\d+)\.\s", lines[i].strip()).group(1)
                text = re.sub(r"^\d+\.\s", "", lines[i].strip())
                out.append(Paragraph("%s.&nbsp;%s" % (num, inline(text)), body_style))
                i += 1
        elif line.startswith("△") or line.startswith("标签"):
            out.append(Paragraph(inline(line), note_style))
            i += 1
        elif "TS爱心联盟" in line:
            out.append(Paragraph(inline(line), footer_style))
            i += 1
        else:
            out.append(Paragraph(inline(line), body_style))
            i += 1
    return out


def main():
    story = []
    for f in FILES:
        p = os.path.join(DIR, f)
        with open(p, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        story.extend(parse_md(lines))

    doc = SimpleDocTemplate(OUT, pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="面向规约AI合集", author="TS爱心联盟")
    doc.build(story)
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
