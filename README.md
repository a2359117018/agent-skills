# Agent Skills

AI agent 技能集合。每个 skill 是一个独立的、可被 coding agent（Claude Code、opencode、Gemini CLI 等）加载的能力模块。

## 目录结构

```
agent-skills/
├── minimax-cli-skills/          # MiniMax 相关技能
│   ├── minimax-vision-describe/ # 图片视觉分析
│   └── minimax-web-search/     # 网页搜索（开发中）
└── <provider>/                  # 按工具/服务提供商组织
    └── <skill-name>/
        ├── SKILL.md             # 技能定义（必需）
        ├── scripts/             # 可执行脚本
        └── references/          # 参考文档
```

## 可用技能

### minimax-vision-describe

基于 MiniMax Vision API 的图片分析技能。支持图片描述、OCR 文字提取、截图分析、UI 元素识别等。

**前置条件：** 安装 [minimax-cli](https://github.com/GalaxyHacks/minimax-cli) 并配置 API key。

**使用方式：**

```bash
python scripts/describe.py <image-path> [--prompt "<instruction>"] [--timeout <seconds>]
```

支持的图片格式：`.jpg`、`.jpeg`、`.png`、`.webp`（本地文件或 HTTP(S) URL）。

## 安装

将目标 skill 目录复制到你的 agent 配置目录下：

```bash
# Claude Code
cp -r minimax-cli-skills/minimax-vision-describe ~/.config/claude-code/skills/

# opencode
cp -r minimax-cli-skills/minimax-vision-describe ~/.config/opencode/skills/
```

agent 会自动发现 `SKILL.md` 并在匹配场景下激活该技能。

## Skill 结构规范

每个 skill 目录必须包含一个 `SKILL.md`，结构如下：

```
<skill-name>/
├── SKILL.md          # 技能入口（必需）
├── scripts/          # 脚本文件
├── references/       # agent 可查阅的参考文档
└── evals/            # 评估用例（不提交，已在 .gitignore 中）
```

### SKILL.md 格式

```markdown
---
name: skill-name
description: >
  触发描述——说明何时应该使用此技能。
---

## Critical Rule & Usage

核心使用规则和命令示例。

## Gotchas

已知陷阱和注意事项。

## Output Contract

成功/失败时的输出格式约定。
```

`description` 字段是 agent 判断是否激活此技能的依据，应尽量涵盖典型触发场景。

## 贡献

1. 在对应的 `<provider>/` 目录下创建 `<skill-name>/` 文件夹
2. 编写 `SKILL.md`（含 frontmatter）
3. 将脚本放入 `scripts/`，参考文档放入 `references/`
4. 提交 PR

## 许可证

[MIT](LICENSE)
