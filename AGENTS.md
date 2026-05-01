# AGENTS.md — Agent 工作约定

## 项目概述

这是一个 AI agent 技能集合项目。每个 skill 是独立的能力模块，供 coding agent 加载使用。

## 目录约定

- 技能按**工具/服务提供商**组织为顶层目录（如 `minimax-cli-skills/`）
- 每个技能一个子目录，目录名即技能名
- 每个技能必须包含 `SKILL.md`

## SKILL.md 规范

- 必须包含 YAML frontmatter，含 `name` 和 `description` 字段
- `description` 是 agent 自动匹配的依据，需覆盖典型触发场景
- 正文包含：核心规则（Critical Rule）、陷阱（Gotchas）、输出约定（Output Contract）
- 引用脚本使用相对路径（如 `scripts/describe.py`），绝不使用绝对路径

## 脚本约定

- 所有可执行脚本放在 `scripts/` 目录
- 脚本需有明确的退出码规范（0=成功，非零=错误）
- 错误输出使用结构化 JSON（含 `error` 和 `message` 字段）
- 脚本应自行处理前置检查（如 CLI 安装、认证状态），不依赖 agent 预先运行

## 参考文档

- 放在 `references/` 目录
- 仅用于 agent 运行时查阅的辅助信息（如错误码说明）
- 不要放冗余内容，保持精简

## 禁止事项

- 不要提交 `evals/` 或 `evals-workspace/` 目录（已在 .gitignore 中）
- 不要在 SKILL.md 中硬编码绝对路径
- 不要在脚本中暴露或日志记录 API key
