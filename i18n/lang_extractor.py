# extract_i18n.py
import re
import json
from pathlib import Path

# 向上找，直到找到包含 'view' 和 'controller' 的目录
def find_project_root(start_path: Path) -> Path:
    current = start_path.resolve()
    while current.parent != current:  # 防止无限循环到根目录
        if (current / "view").is_dir() and (current / "controller").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("未找到项目根目录（需包含 view/ 和 controller/）")

# 扫描根目录（当前项目）
PROJECT_ROOT = find_project_root(Path(__file__).parent)
I18N_DIR = PROJECT_ROOT / "i18n"
OUTPUT_FILE = I18N_DIR / "messages.json"


# 排除目录
EXCLUDE_DIRS = {"venv", "__pycache__", ".git", "build", "dist"}

def find_tr_calls_in_file(file_path: Path):
    """从 .py 文件中提取 tr("...") 中的字符串"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️ 无法读取 {file_path}: {e}")
        return set()

    # 正则匹配 tr("...") 或 _("...")
    # 支持多行、转义引号（简化版）
    pattern = r'''(?:\btr|_)\(\s*["']((?:[^"']|\\["'])*?)["']\s*\)'''
    matches = re.findall(pattern, content)
    # 去掉转义（如 \" → "）
    cleaned = [s.replace('\\"', '"').replace("\\'", "'") for s in matches]
    return set(cleaned)

def main():
    all_strings = set()

    for py_file in PROJECT_ROOT.rglob("*.py"):
        # 跳过排除目录
        if any(part in EXCLUDE_DIRS for part in py_file.parts):
            continue
        # 跳过自己
        if py_file.name == "extract_i18n.py":
            continue

        strings = find_tr_calls_in_file(py_file)
        if strings:
            rel_path = py_file.relative_to(PROJECT_ROOT)
            print(f"🔍 {rel_path} → {len(strings)} 条")
            all_strings.update(strings)

    # 排序并保存
    sorted_strings = sorted(all_strings)
    messages = {text: "" for text in sorted_strings}  # value 留空供翻译

    I18N_DIR.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 提取完成！共 {len(messages)} 条文本")
    print(f"📄 模板文件已保存至: {OUTPUT_FILE}")
    print("\n📝 下一步：")
    print("1. 复制 messages.json 为 zh.json（默认语言可直接用原文）")
    print("2. 复制 messages.json 为 en.json，并填写英文翻译")
    print("3. 在代码中确保已导入: from i18n import tr")

if __name__ == "__main__":
    main()