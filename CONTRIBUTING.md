# 贡献指南

感谢参与贡献。请先读 [docs/README.md](docs/README.md) 了解方法论全貌。

## 术语规范（务必遵守）

- SkillUP：**首次出现**写「SkillUP（成长模型）」，后续一律「SkillUP」
- TRAE → AI工具；TRAE-ready → AI-ready（但「如 TRAE」「TRAE 等 AI 编程助手」这类具体举例保留原名）
- 英文全名首次出现补注：Spec-Oriented Development（简称 SOD）
- 文件名 / 路径中的术语不改

## 命名规范

- **中文文档**：`NN-中文名.md`（NN 两位序号，连字符 `-` 分隔）
- **英文文档**：`NN-english-slug.md`（序号与中文版一一对应）
- 版本号不进文件名（由 git 管理）

## 提交流程

1. Fork 本仓库。
2. 新建功能分支（如 `fix/术语-xxx`）。
3. 提交前自检：术语规范 + 文档内链接有效。
4. 提交 Pull Request，说明改动意图与影响范围。

## 文档与代码的许可区分

- `docs/`、`templates/`：CC BY 4.0
- `tools/`：MIT
- 提交即视为同意按上述许可授权。
