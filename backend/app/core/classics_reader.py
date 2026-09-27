# -*- coding: utf-8 -*-
"""典籍全文阅读：把 txt 按章节标题切分，供电子书式阅读器使用。"""
import os
import re

DATA_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "data", "classics"))

_NUM = "一二三四五六七八九十百千万零两0123456789"

# 句读标点：出现在行内基本可判定为正文而非标题（标题允许 ： 、 -）
_SENT_PUNCT = set("，。；\"'“”‘’「」『』!?！？…—·")

_CHAPTER_RES = [
    re.compile(r"^【?卷之[" + _NUM + r"]+】?$"),
    re.compile(r"^卷之[" + _NUM + r"]+\s*.{1,18}章$"),
    re.compile(r"^.{1,18}章第[" + _NUM + r"]+$"),
    re.compile(r"^第[" + _NUM + r"]+[章节卷篇].{0,18}$"),
    re.compile(r"^.{1,20}章$"),
    re.compile(r"^卷[一二三四五六七八九十百\d上下]+$"),
    re.compile(r"^(乾|兑|离|震|巽|坎|艮|坤)(上|下)(乾|兑|离|震|巽|坎|艮|坤)(上|下)\s*[\u4e00-\u9fff]{0,2}：?$"),
]

# 已核实的版本说明（诚实标注，不虚构）
BOOK_NOTES = {
    "ym": "残本说明：此转录本缺末章〈占诫章第九十一〉（仅至〈道业章第九十〉），待原版补入后更新。",
}


def is_chapter_heading(line):
    s = line.strip()
    if not s or len(s) > 28:
        return False
    for c in s:
        if c in _SENT_PUNCT:
            return False
    for p in _CHAPTER_RES:
        if p.match(s):
            return True
    return False


def split_chapters(text):
    """返回 [{'title': 章标题, 'text': 正文}, ...]；无章节标记时返回单章。"""
    chapters = []
    state = {"title": None, "buf": []}

    def flush():
        body = "\n".join(state["buf"]).strip("\n")
        if state["title"] is not None or body.strip():
            chapters.append({"title": state["title"] or "全文", "text": body})
        state["title"] = None
        state["buf"] = []

    for line in text.splitlines():
        if is_chapter_heading(line):
            flush()
            state["title"] = line.strip()
        else:
            state["buf"].append(line)
    flush()
    if len(chapters) > 1 and not chapters[0]["text"].strip():
        chapters.pop(0)
    return chapters


def load_book_text(book_key, source_file):
    """读取典籍全文并分章。source_file 如 'data/classics/zengshanbuyi.txt'。"""
    path = os.path.join(DATA_DIR, os.path.basename(source_file))
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    chapters = split_chapters(text)
    return {
        "book_key": book_key,
        "chapters": chapters,
        "chapter_count": len(chapters),
        "char_count": len(text),
        "note": BOOK_NOTES.get(book_key),
    }
