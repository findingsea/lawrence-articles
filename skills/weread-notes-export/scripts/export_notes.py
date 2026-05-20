#!/usr/bin/env python3
"""
微信读书笔记导出脚本
用法: python3 export_notes.py <书名> [--output <输出目录>]
"""

import json
import sys
import os
import subprocess
from datetime import datetime

API_BASE = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.3"

def get_env(key):
    val = os.environ.get(key)
    if not val:
        raise ValueError(f"未找到环境变量 {key}，请先配置微信读书 API Key")
    return val

def api_call(api_name, **params):
    api_key = get_env("WEREAD_API_KEY")
    payload = {"api_name": api_name, "skill_version": SKILL_VERSION, **params}
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", API_BASE,
         "-H", f"Authorization: Bearer {api_key}",
         "-H", "Content-Type: application/json",
         "-d", json.dumps(payload)],
        capture_output=True, text=True
    )
    resp = json.loads(result.stdout)
    # errcode 存在且非 0 才是错误
    if "errcode" in resp and resp["errcode"] != 0:
        raise Exception(f"API 错误 ({api_name}): {resp.get('message', resp)}")
    return resp

def search_book(keyword):
    resp = api_call("/store/search", keyword=keyword, scope=10, count=10)
    results = resp.get("results", [])
    if not results:
        return None
    # 遍历所有分组，找 scope=10 或 scope=17 的电子书分组
    for group in results:
        scope = group.get("scope", 0)
        if scope in (10, 17):
            books = group.get("books", [])
            if books:
                info = books[0].get("bookInfo", {})
                return {"bookId": info["bookId"], "title": info["title"], "author": info.get("author", "未知")}
    # 兜底：取第一个有 books 的分组
    for group in results:
        books = group.get("books", [])
        if books:
            info = books[0].get("bookInfo", {})
            return {"bookId": info["bookId"], "title": info["title"], "author": info.get("author", "未知")}
    return None

def find_book_in_notebooks(keyword):
    """从 notebooks 列表中找到含关键词且有多条的书籍"""
    resp = api_call("/user/notebooks", count=100)
    best_match = None
    best_count = 0
    for b in resp.get("books", []):
        book = b.get("book", {})
        title = book.get("title", "")
        note_count = b.get("noteCount", 0)
        review_count = b.get("reviewCount", 0)
        bookmark_count = b.get("bookmarkCount", 0)
        total = note_count + review_count + bookmark_count
        if keyword in title and total > best_count:
            best_match = {"bookId": book["bookId"], "title": title, "author": book.get("author", "未知")}
            best_count = total
    return best_match

def get_chapters(bookId):
    resp = api_call("/book/chapterinfo", bookId=bookId)
    chapters = resp.get("chapters", [])
    # 按 chapterIdx 排序
    chapters.sort(key=lambda c: c.get("chapterIdx", 0))
    return {c["chapterUid"]: c for c in chapters}

def get_all_bookmarks(bookId):
    """获取所有划线，按 chapterUid 分组"""
    resp = api_call("/book/bookmarklist", bookId=bookId)
    bookmarks_by_chapter = {}
    # 从返回的 chapters 中建立 uid -> title 映射
    chapters_map = {c["chapterUid"]: c["title"] for c in resp.get("chapters", [])}
    for bm in resp.get("updated", []):
        uid = bm["chapterUid"]
        if uid not in bookmarks_by_chapter:
            bookmarks_by_chapter[uid] = []
        ts = bm.get("createTime", 0)
        date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
        bookmarks_by_chapter[uid].append({
            "text": bm["markText"],
            "range": bm.get("range", ""),
            "date": date_str,
            "chapterUid": uid,
        })
    return bookmarks_by_chapter, chapters_map

def get_all_reviews(bookId):
    """获取所有想法/点评，按章节名分组"""
    reviews_by_chapter = {}
    synckey = 0
    while True:
        resp = api_call("/review/list/mine", bookid=bookId, synckey=synckey, count=50)
        reviews = resp.get("reviews", [])
        for r in reviews:
            rev = r.get("review", {})
            content = rev.get("content", "").strip()
            if not content:
                continue
            chapter_name = rev.get("chapterName", "")
            ts = rev.get("createTime", 0)
            date_str = datetime.fromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""
            if chapter_name not in reviews_by_chapter:
                reviews_by_chapter[chapter_name] = []
            reviews_by_chapter[chapter_name].append({
                "content": content,
                "chapterName": chapter_name,
                "date": date_str,
            })
        has_more = resp.get("hasMore", 0)
        synckey = resp.get("synckey", 0)
        if not has_more:
            break
    return reviews_by_chapter

def build_markdown(book_title, author, bookmarks_by_chapter, chapters_map, reviews_by_chapter):
    lines = []
    lines.append(f"# {book_title}\n")
    lines.append(f"作者：{author}\n")
    lines.append(f"导出时间：{datetime.now().strftime('%Y-%m-%d')}\n")
    lines.append("---\n")

    # 只输出有笔记的章节
    for chapter_uid in sorted(chapters_map.keys()):
        chapter_info = chapters_map[chapter_uid]
        chapter_title = chapter_info["title"] if isinstance(chapter_info, dict) else chapter_info

        bms = bookmarks_by_chapter.get(chapter_uid, [])
        chapter_reviews = reviews_by_chapter.get(chapter_title, [])

        # 跳过无笔记的章节
        if not bms and not chapter_reviews:
            continue

        lines.append(f"\n## {chapter_title}\n")

        # 划线
        for bm in bms:
            lines.append(f'> {bm["text"]}\n')
            lines.append(f'*—— {bm["date"]}*\n')

        # 想法（按章节名匹配）
        for r in chapter_reviews:
            lines.append(f'**想法：** {r["content"]}\n')
            lines.append(f'*—— {r["date"]}*\n')

    return "".join(lines)

def main():
    if len(sys.argv) < 2:
        print("用法: python3 export_notes.py <书名> [--output <输出目录>]")
        sys.exit(1)

    book_name = sys.argv[1]
    output_dir = None
    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_dir = sys.argv[idx + 1]

    if not output_dir:
        output_dir = os.path.expanduser("~/Workspace/lawrence-articles")

    print(f"搜索书籍：{book_name}")
    book_info = search_book(book_name)
    if not book_info:
        print("搜索未找到，尝试从书架匹配...")
        book_info = find_book_in_notebooks(book_name)
    if not book_info:
        print("未找到这本书，请确认书名是否正确")
        sys.exit(1)

    book_id = book_info["bookId"]
    title = book_info["title"]
    author = book_info["author"]
    print(f"找到：《{title}》 {author}（bookId: {book_id}）")

    print("获取章节信息...")
    chapters_map = get_chapters(book_id)

    print("获取划线笔记...")
    bookmarks_by_chapter, _ = get_all_bookmarks(book_id)
    total_bookmarks = sum(len(v) for v in bookmarks_by_chapter.values())
    print(f"共 {total_bookmarks} 条划线")

    print("获取想法点评...")
    reviews_by_chapter = get_all_reviews(book_id)
    total_reviews = sum(len(v) for v in reviews_by_chapter.values())
    print(f"共 {total_reviews} 条想法")

    # 如果没有找到笔记，尝试从 notebooks 匹配其他版本
    if total_bookmarks == 0 and total_reviews == 0:
        print("此版本无笔记，尝试从书架匹配其他版本...")
        alt_info = find_book_in_notebooks(book_name)
        if alt_info and alt_info["bookId"] != book_id:
            book_id = alt_info["bookId"]
            title = alt_info["title"]
            author = alt_info["author"]
            print(f"匹配到：《{title}》 {author}（bookId: {book_id}）")
            chapters_map = get_chapters(book_id)
            bookmarks_by_chapter, _ = get_all_bookmarks(book_id)
            total_bookmarks = sum(len(v) for v in bookmarks_by_chapter.values())
            reviews_by_chapter = get_all_reviews(book_id)
            total_reviews = sum(len(v) for v in reviews_by_chapter.values())
            print(f"共 {total_bookmarks} 条划线，{total_reviews} 条想法")

    print("生成 Markdown...")
    md_content = build_markdown(title, author, bookmarks_by_chapter, chapters_map, reviews_by_chapter)

    # 写入文件
    article_dir = os.path.join(output_dir, "note", f"《{title}》")
    os.makedirs(article_dir, exist_ok=True)
    filename = f"《{title}》-摘抄.md"
    filepath = os.path.join(article_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"✅ 已保存至：{filepath}")
    return filepath

if __name__ == "__main__":
    main()