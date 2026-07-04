import streamlit as st
from utils.note_storage import get_all_notes, remove_book, load_shelf, save_shelf, DATA_DIR
from utils.logger import setup_logger

logger = setup_logger(__name__)


def compute_note_counts(books):
    counts = {}
    for book in books:
        try:
            notes = get_all_notes(book["notes_path"])
            counts[book["id"]] = len(notes)
        except Exception as e:
            logger.warning(f"获取笔记数失败: book_id={book['id']}, error={e}")
            counts[book["id"]] = 0
    return counts


def render_book_card(index, book, note_count=0):
    book_id = book["id"]
    title = book["title"]
    last_page = book.get("last_page", 0)

    with st.container(border=True):
        cols = st.columns([0.6, 0.6, 2.2, 0.8, 0.8, 1.0, 0.8])

        with cols[0]:
            st.markdown(f"**{index}**")

        with cols[1]:
            st.markdown("##### 📖")

        with cols[2]:
            st.markdown(f"**{title}**")
            last_page_text = f"第 {last_page + 1} 页" if isinstance(last_page, (int, float)) else "--"
            st.caption(f"读到 {last_page_text}")

        with cols[3]:
            if st.button("👁️", key=f"read_{book_id}", help="开始阅读此书"):
                st.session_state["selected_book_id"] = book_id
                st.session_state["mode"] = "reader"
                st.toast(f"📖 正在打开《{title}》...")
                st.rerun()

        with cols[4]:
            with st.popover("✏️", help="重命名此书"):
                st.caption("输入新书名")
                new_title = st.text_input(
                    "新书名", value=title,
                    key=f"rename_inp_{book_id}",
                    label_visibility="collapsed"
                )
                if st.button("确认", key=f"rename_ok_{book_id}", type="primary", use_container_width=True):
                    if new_title.strip():
                        shelf = load_shelf()
                        for b in shelf["books"]:
                            if b["id"] == book_id:
                                b["title"] = new_title.strip()
                                break
                        save_shelf(shelf)
                        st.toast(f"✏️ 已重命名为《{new_title.strip()}》")
                        st.rerun()

        with cols[5]:
            label = f"📝 {note_count}" if note_count > 0 else "📝"
            help_text = f"共 {note_count} 条笔记" if note_count > 0 else "暂无笔记"
            if st.button(label, key=f"notes_{book_id}", help=help_text):
                st.toast(f"📝 《{title}》共有 {note_count} 条笔记")

        with cols[6]:
            with st.popover("🗑️", help="删除此书"):
                st.warning("⚠️ 确认删除？所有笔记和图片将永久丢失！")
                col_yes, col_no = st.columns(2)
                with col_yes:
                    if st.button("确认删除", key=f"del_yes_{book_id}", type="primary", use_container_width=True):
                        try:
                            remove_book(book_id)
                            st.toast(f"🗑️ 已删除《{title}》")
                            st.rerun()
                        except Exception as del_err:
                            st.error(f"删除失败: {del_err}")
                with col_no:
                    if st.button("取消", key=f"del_no_{book_id}", use_container_width=True):
                        st.rerun()


def render_bookshelf(books, note_counts=None):
    if not books:
        st.info("📚 书架为空，请上传PDF文件开始阅读")
        return

    if note_counts is None:
        note_counts = compute_note_counts(books)

    sorted_books = sorted(books, key=lambda x: x.get("added_at", ""), reverse=True)
    for i, book in enumerate(sorted_books, start=1):
        render_book_card(i, book, note_counts.get(book["id"], 0))


DEMO_BOOKS = [
    {"name": "深入理解计算机系统", "notes": 3},
    {"name": "算法导论", "notes": 0},
    {"name": "设计模式", "notes": 5},
]


def _demo_main():
    st.set_page_config(page_title="书架卡片组件演示", layout="centered")
    st.title("📚 我的书架")
    st.caption("书架卡片组件演示 — 使用示例数据")

    import os
    import json
    seed_key = "_demo_seeded"
    if seed_key not in st.session_state:
        shelf = load_shelf()
        shelf["books"] = []
        for i, b in enumerate(DEMO_BOOKS):
            book_id = f"demo_{i}"
            book_dir = os.path.join(DATA_DIR, "books", book_id)
            os.makedirs(book_dir, exist_ok=True)
            shelf["books"].append({
                "id": book_id,
                "title": b["name"],
                "file_path": os.path.join(book_dir, f"{b['name']}.pdf"),
                "notes_path": os.path.join(book_dir, "notes.json"),
                "images_path": os.path.join(book_dir, "images"),
                "last_page": 0,
                "added_at": "2026-01-01T00:00:00",
            })
            os.makedirs(os.path.join(book_dir, "images"), exist_ok=True)
            sample_notes = []
            for ni in range(b["notes"]):
                sample_notes.append({
                    "id": f"note_{i}_{ni}",
                    "page": ni,
                    "text": f"笔记示例 {ni + 1}",
                    "content": f"这是《{b['name']}》的第 {ni + 1} 条笔记",
                    "images": [],
                    "created_at": "2026-01-01T00:00:00",
                    "updated_at": "2026-01-01T00:00:00",
                    "position": {},
                })
            with open(os.path.join(book_dir, "notes.json"), "w") as f:
                f.write(json.dumps({"notes": sample_notes, "bookmarks": []}))
        save_shelf(shelf)
        st.session_state[seed_key] = True

    shelf = load_shelf()
    render_bookshelf(shelf.get("books", []))


if __name__ == "__main__":
    _demo_main()
