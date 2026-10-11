#!/usr/bin/env python3
"""去 AI 味机械扫描器。

用法:
    python3 scan.py posts/2026-10-工作主义/工作主义.md

只读，不修改任何文件。输出：分段字数 + 各类病灶命中（行号 + 原文片段）。
判据与条号参见 ../../SKILL.md 与项目 AGENTS.md。
"""

import re
import sys
from pathlib import Path

PATTERNS = {
    "§59 宣布感受/观察(我)":
        r"我记[得了]|我印象|我一直在想|我在想|我读的时候|我这边看到的|我看到的|我注意到|让我|值得思考的是",
    "§60 宣布论证动作(他/文章)":
        r"再往下|往下推|往下一层|问题在这儿|分界是|关键在|这里有个|他的判断是|文章里有个比方|"
        r"具体的样子|值得守住|会有一个后果|值得注意|需要说明|更难的一层",
    "§52 路标/元叙述":
        r"^(为什么是现在|麻烦在于|让我们|下面|接下来|总之|关键在于)|核心判断就在这里|"
        r"用他(自己)的话说|真正要问的是|最微妙的地方在|我的判断是",
    "§1 不是A是B":
        r"不是.{1,20}[，,；;].{0,14}(是|而是)|不在.{1,10}[，,].{0,8}在|不在于",
    "§13 拔高":
        r"泡沫|扎破|本质上|意味着|标志着",
    "§5 跟空气辩论":
        r"我对用.{0,6}没有意见|不是要|并不是说|倒不是",
    "§22 客服腔":
        r"希望这|值得注意的是|需要说明|值得一提的是",
}

CJK = r"[\u4e00-\u9fff]"


def scan(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # 跳过 frontmatter
    body = text.split("---", 2)[2] if text.startswith("---") else text

    print("=== 字数 ===")
    print("  全文:", len("".join(body.split())))
    for sec in re.split(r"\n(?=## )", body):
        head = sec.split("\n")[0][:28] or "(引子)"
        print(f"    {len(''.join(sec.split())):>5}  {head}")
    print()
    print("--- 小节 ---")
    for sec in re.split(r"\n(?=### )", body):
        head = sec.split("\n")[0]
        if head.startswith("###"):
            print(f"    {len(''.join(sec.split())):>5}  {head[:30]}")
    print()

    for name, pat in PATTERNS.items():
        hits = [(i, l.strip()[:64]) for i, l in enumerate(lines, 1) if re.search(pat, l)]
        print(f"{name}: {hits if hits else '✓ 无'}")
    print()

    # 冒号前空预告
    print("=== 冒号前半句（逐条判断：删掉后意思不变→删）===")
    for i, l in enumerate(lines, 1):
        s = l.strip()
        m = re.match(r"^(.{0,16}?)[：:](.*)$", s)
        if m and len(m.group(1)) <= 16 and m.group(1) and not m.group(1).startswith("#"):
            print(f"  {i}  [{m.group(1)}] {m.group(2)[:46]}")
    print()

    # 三连排比（顿号≥3项）
    print("=== 顿号列举≥3项（检查是否凑数/同构）===")
    for i, l in enumerate(lines, 1):
        if l.count("、") >= 2 and re.search(r"、.{1,12}、", l):
            print(f"  {i} [{l.count('、') + 1}项] {l.strip()[:60]}")
    print()

    # 硬性错误
    space = [(i, l.strip()[:40]) for i, l in enumerate(lines, 1)
             if re.search(rf"{CJK}[A-Za-z0-9]|[A-Za-z0-9]{CJK}", l)]
    quote = [(i, l.strip()[:40]) for i, l in enumerate(lines, 1)
             if '"' in l or "\u201c" in l or "\u201d" in l]
    print("中英空格:", space if space else "✓ 无缺失")
    print("引号(应为「」):", quote if quote else "✓ 全为「」")

    # 一节内同词重复
    print()
    print("=== 一节内同词重复 ≥4 次 ===")
    for sec in re.split(r"\n(?=### )", body):
        head = sec.split("\n")[0]
        words = re.findall(rf"{CJK}{{2,3}}", sec)
        cnt: dict[str, int] = {}
        for w in words:
            cnt[w] = cnt.get(w, 0) + 1
        dup = [(w, n) for w, n in cnt.items() if n >= 4]
        if dup:
            print(f"  {head[:26]}: {dup}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"文件不存在: {p}")
        sys.exit(1)
    scan(p)


if __name__ == "__main__":
    main()
