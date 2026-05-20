---
name: weread-notes-export
description: |
  微信读书笔记导出工具。输入书名，自动从微信读书获取该书的划线和想法，
  按章节顺序整理为 Markdown 文件，保存到「note/《书名》/《书名》-摘抄.md」。
  触发词：导出笔记、导出划线、导出摘抄、微信读书笔记、weread notes、导出微信读书笔记。
---

# 微信读书笔记导出

输入书名，自动导出该书在微信读书中的划线和想法，按章节顺序整理为 Markdown 文件。

## 前置依赖

- 已安装微信读书 Skill（weread-skills）
- 已配置环境变量 `WEREAD_API_KEY`

## 使用方式

```bash
python3 "{SKILL_DIR}/scripts/export_notes.py <书名>" [--output <输出目录>]
```

- `<书名>`：要导出笔记的书籍名称（模糊匹配，取搜索结果第一本）
- `--output`：输出根目录，默认 `~/Workspace/lawrence-articles`

输出路径：`<输出目录>/note/《书名》/《书名》-摘抄.md`

## 输出格式

```markdown
# 书名

作者：xxx
导出时间：2026-05-20

---

## 第一章标题

> 划线内容1

*—— 2026-05-18*

> 划线内容2

*—— 2026-05-19*

**想法：** 这段话让我想到……

*—— 2026-05-19*

## 第二章标题

*（此章节无笔记）*
```

## 工作流

1. 用户提供书名
2. 运行 `python3 "{SKILL_DIR}/scripts/export_notes.py <书名>"`
3. 脚本自动：搜索书籍 → 获取章节信息 → 获取划线 → 获取想法 → 按章节排序生成 Markdown
4. 告知用户输出文件路径
