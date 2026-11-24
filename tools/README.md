# tools · 公众号自动化脚本

「面向规约AI」合集从 Markdown 到公众号草稿的一站式脚本。仅在 Windows + Python 3 环境验证。

## 脚本清单

| 脚本 | 用途 |
|:---|:---|
| `prepare_sod_collection.py` | .md → 公众号 HTML（第07期金色样式）+ 封面图 |
| `convert_sod_collection_pdf.py` | HTML → PDF 合集 |
| `push_sod_collection.py` | `draft/add`：首次新建公众号草稿 |
| `update_sod_collection.py` | `draft/update`：覆盖已有草稿 |
| `check_sod_drafts.py` | 查草稿箱最近草稿列表 |

## 依赖

见 `requirements.txt`。核心：`requests`、`python-dotenv`、`reportlab`。

## 凭证配置

AppID / Secret 从 `.env` 加载，**勿硬编码**。脚本会依次尝试：

1. `~/.openclaw/.env`
2. `E:\Trac Project\TracSkill\config.env`

复制 `.env.example` 为 `.env` 并填入真实值（`.env` 已被 `.gitignore` 忽略）。

## 运行

```bash
python prepare_sod_collection.py   # 生成 HTML + 封面
python convert_sod_collection_pdf.py
python push_sod_collection.py      # 首次新建草稿
python update_sod_collection.py    # 覆盖草稿
python check_sod_drafts.py         # 查草稿箱
```

## 已知硬编码点（待工程化）

- `prepare_sod_collection.py` 的 `BASE_DIR` 指向个人目录 `E:\00kb-TS爱心联盟公众号\内容管理\面向规约AI合集`，需参数化。
- 各脚本 `.env` 路径为个人路径，需改为环境变量读取。
- `push` / `update` 依赖 `prepare_sod_collection` 的 `ARTICLES` / `BASE_DIR`。

## 注意

- 公众号 IP 白名单可能变化，接口报错先查白名单。
- 修改已推送文章前必须人工确认。
