#!/usr/bin/env python3
"""
يمسح مجلدات على جهازك ويولّد ملف catalog.json لموقع المحتويات.

أمثلة:
    python scan_catalog.py D:\\Library E:\\Movies
    python scan_catalog.py ~/Media --out catalog.json
    python scan_catalog.py D:\\Library --no-root-folder      # يعرض محتويات المجلد مباشرة بدون مجلد الجذر
    python scan_catalog.py D:\\Library --exclude "*.tmp" "Backup*"
"""
import argparse
import fnmatch
import json
import os
import sys
import unicodedata

DEFAULT_EXCLUDES = [
    "System Volume Information", "$RECYCLE.BIN", "$Recycle.Bin", "Recovery",
    "Thumbs.db", "desktop.ini", ".DS_Store", ".git", ".Trash*", "__MACOSX",
    "*.part", "*.crdownload", "*.tmp",
]


def norm(name: str) -> str:
    # توحيد الترميز (NFC) حتى لا تختلف الحروف العربية بين الأنظمة
    return unicodedata.normalize("NFC", name)


def is_excluded(name: str, patterns) -> bool:
    return any(fnmatch.fnmatch(name.lower(), p.lower()) for p in patterns)


def scan_dir(path: str, patterns, errors: list):
    """يعيد (children, total_size)."""
    children = []
    total = 0
    try:
        entries = list(os.scandir(path))
    except (PermissionError, FileNotFoundError, OSError) as exc:
        errors.append(f"{path}: {exc}")
        return children, total

    for entry in entries:
        name = entry.name
        if name.startswith(".") or is_excluded(name, patterns):
            continue
        try:
            if entry.is_symlink():
                continue  # تجاهل الروابط الرمزية لتفادي التكرار والحلقات
            st = entry.stat(follow_symlinks=False)
            if entry.is_dir(follow_symlinks=False):
                sub, sub_size = scan_dir(entry.path, patterns, errors)
                children.append({
                    "name": norm(name),
                    "type": "folder",
                    "size": sub_size,
                    "count": len(sub),
                    "modified": int(st.st_mtime),
                    "children": sub,
                })
                total += sub_size
            elif entry.is_file(follow_symlinks=False):
                ext = os.path.splitext(name)[1].lstrip(".").lower()
                item = {
                    "name": norm(name),
                    "type": "file",
                    "size": st.st_size,
                    "modified": int(st.st_mtime),
                }
                if ext:
                    item["ext"] = ext
                children.append(item)
                total += st.st_size
        except (PermissionError, FileNotFoundError, OSError) as exc:
            errors.append(f"{entry.path}: {exc}")
    return children, total


def main():
    ap = argparse.ArgumentParser(description="توليد catalog.json لمستعرض المحتويات")
    ap.add_argument("roots", nargs="+", help="مجلد أو أكثر للمسح")
    ap.add_argument("-o", "--out", default="catalog.json", help="ملف الإخراج (الافتراضي catalog.json)")
    ap.add_argument("--exclude", nargs="*", default=[], help="أنماط إضافية للاستثناء (مثل *.tmp Backup*)")
    ap.add_argument("--no-root-folder", action="store_true",
                    help="عرض محتويات كل مجلد جذر مباشرة بدل عرض المجلد نفسه")
    args = ap.parse_args()

    patterns = DEFAULT_EXCLUDES + args.exclude
    errors = []
    catalog = []

    for root in args.roots:
        root = os.path.abspath(os.path.expanduser(root))
        if not os.path.isdir(root):
            print(f"تخطّي (ليس مجلداً): {root}", file=sys.stderr)
            continue
        children, size = scan_dir(root, patterns, errors)
        if args.no_root_folder:
            catalog.extend(children)
        else:
            catalog.append({
                "name": norm(os.path.basename(root.rstrip("\\/")) or root),
                "type": "folder",
                "size": size,
                "count": len(children),
                "modified": int(os.stat(root).st_mtime),
                "children": children,
            })

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, separators=(",", ":"))

    def count(nodes):
        folders = files = 0
        for n in nodes:
            if n["type"] == "folder":
                folders += 1
                a, b = count(n["children"])
                folders += a
                files += b
            else:
                files += 1
        return folders, files

    folders, files = count(catalog)
    print(f"تم: {folders} مجلد، {files} ملف  ->  {args.out}")
    if errors:
        print(f"تعذّرت قراءة {len(errors)} عنصر (صلاحيات أو ملفات مفقودة)، أول 5:", file=sys.stderr)
        for e in errors[:5]:
            print("  ", e, file=sys.stderr)


if __name__ == "__main__":
    main()
