import json
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any

from utils.logger import setup_logger

logger = setup_logger(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
SHELF_PATH = os.path.join(DATA_DIR, 'shelf.json')


def init_storage():
    logger.info("初始化存储系统...")
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SHELF_PATH):
        with open(SHELF_PATH, 'w', encoding='utf-8') as f:
            json.dump({"books": []}, f)
        logger.info(f"创建书架文件: {SHELF_PATH}")
    logger.info("存储系统初始化完成")


def load_shelf() -> Dict:
    logger.debug("加载书架数据...")
    init_storage()
    if os.path.exists(SHELF_PATH):
        try:
            with open(SHELF_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"书架数据加载成功，共 {len(data.get('books', []))} 本书")
            return data
        except Exception as e:
            logger.error(f"加载书架数据失败: {e}")
            return {"books": []}
    logger.warning("书架文件不存在")
    return {"books": []}


def save_shelf(shelf: Dict):
    logger.debug("保存书架数据...")
    init_storage()
    try:
        with open(SHELF_PATH, 'w', encoding='utf-8') as f:
            json.dump(shelf, f, ensure_ascii=False, indent=2)
        logger.debug("书架数据保存成功")
    except Exception as e:
        logger.error(f"保存书架数据失败: {e}")


def add_book(title: str, file_path: str) -> Dict:
    logger.info(f"添加书籍: {title}, 文件路径: {file_path}")
    shelf = load_shelf()
    
    existing = next((b for b in shelf["books"] if b["file_path"] == file_path), None)
    if existing:
        logger.warning(f"书籍已存在，跳过重复添加: {file_path}")
        return existing
    
    book_id = os.path.basename(os.path.dirname(file_path))
    book_dir = os.path.dirname(file_path)
    
    book_data = {
        "id": book_id,
        "title": title,
        "file_path": file_path,
        "notes_path": os.path.join(book_dir, 'notes.json'),
        "images_path": os.path.join(book_dir, 'images'),
        "last_page": 0,
        "added_at": datetime.now().isoformat()
    }
    
    os.makedirs(book_data["images_path"], exist_ok=True)
    init_notes_file(book_data["notes_path"])
    
    shelf["books"].append(book_data)
    save_shelf(shelf)
    
    logger.info(f"书籍添加成功，ID: {book_id}")
    return book_data


def remove_book(book_id: str):
    logger.info(f"删除书籍: {book_id}")
    shelf = load_shelf()
    book = next((b for b in shelf["books"] if b["id"] == book_id), None)
    if not book:
        logger.warning(f"未找到书籍: {book_id}")
        raise ValueError(f"未找到书籍: {book_id}")
    
    shelf["books"] = [b for b in shelf["books"] if b["id"] != book_id]
    save_shelf(shelf)
    
    try:
        if os.path.exists(book["file_path"]):
            os.remove(book["file_path"])
            logger.debug(f"删除书籍文件: {book['file_path']}")
        
        if os.path.exists(book["notes_path"]):
            os.remove(book["notes_path"])
            logger.debug(f"删除笔记文件: {book['notes_path']}")
        
        if os.path.exists(book["images_path"]):
            for img in os.listdir(book["images_path"]):
                img_path = os.path.join(book["images_path"], img)
                os.remove(img_path)
                logger.debug(f"删除图片: {img_path}")
            os.rmdir(book["images_path"])
            logger.debug(f"删除图片目录: {book['images_path']}")
        
        book_dir = os.path.dirname(book["file_path"])
        if os.path.exists(book_dir):
            os.rmdir(book_dir)
            logger.debug(f"删除书籍目录: {book_dir}")
    except Exception as e:
        logger.warning(f"文件清理失败（书架条目已删除）: {e}")
    
    logger.info(f"书籍删除成功: {book_id}")


def update_last_page(book_id: str, page: int):
    logger.debug(f"更新最后阅读页码: book_id={book_id}, page={page}")
    shelf = load_shelf()
    for book in shelf["books"]:
        if book["id"] == book_id:
            book["last_page"] = page
            logger.debug(f"最后阅读页码更新成功: {book_id} -> {page}")
            break
    save_shelf(shelf)


def sync_shelf_with_disk():
    logger.info("开始同步书架与磁盘...")
    shelf = load_shelf()
    books_dir = os.path.join(DATA_DIR, 'books')
    os.makedirs(books_dir, exist_ok=True)

    disk_ids = set()
    try:
        for entry in os.listdir(books_dir):
            entry_path = os.path.join(books_dir, entry)
            if os.path.isdir(entry_path) and len(entry) == 36:
                disk_ids.add(entry)
    except Exception as e:
        logger.warning(f"扫描 books 目录失败: {e}")

    shelf_ids = {b["id"] for b in shelf["books"]}
    changed = False

    valid_books = []
    for book in shelf["books"]:
        bid = book["id"]
        book_dir = os.path.join(books_dir, bid)

        if not os.path.isdir(book_dir):
            logger.warning(f"书架条目 {bid} 磁盘目录已丢失，移除: {book['title']}")
            changed = True
            continue

        if not os.path.exists(book.get("notes_path", "")):
            book["notes_path"] = os.path.join(book_dir, "notes.json")
            init_notes_file(book["notes_path"])
            changed = True

        if not os.path.exists(book.get("images_path", "")):
            book["images_path"] = os.path.join(book_dir, "images")
            os.makedirs(book["images_path"], exist_ok=True)
            changed = True

        valid_books.append(book)

    shelf["books"] = valid_books

    orphaned_disk_ids = disk_ids - shelf_ids
    for bid in orphaned_disk_ids:
        book_dir = os.path.join(books_dir, bid)
        pdf_files = [f for f in os.listdir(book_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            logger.warning(f"磁盘目录 {bid} 中无 PDF 文件，跳过恢复")
            continue

        pdf_name = pdf_files[0]
        title = pdf_name[:-4]
        file_path = os.path.join(book_dir, pdf_name)
        notes_path = os.path.join(book_dir, "notes.json")
        images_path = os.path.join(book_dir, "images")

        book_data = {
            "id": bid,
            "title": title,
            "file_path": file_path,
            "notes_path": notes_path,
            "images_path": images_path,
            "last_page": 0,
            "added_at": datetime.now().isoformat(),
        }
        os.makedirs(images_path, exist_ok=True)
        init_notes_file(notes_path)
        shelf["books"].append(book_data)
        logger.info(f"从磁盘恢复书籍: {title}")
        changed = True

    if changed:
        save_shelf(shelf)
        logger.info("书架同步完成（有变更）")
    else:
        logger.info("书架同步完成（无变更）")

    return shelf


def get_book(book_id: str) -> Optional[Dict]:
    logger.debug(f"获取书籍信息: {book_id}")
    shelf = load_shelf()
    book = next((b for b in shelf["books"] if b["id"] == book_id), None)
    if book:
        logger.debug(f"找到书籍: {book['title']}")
    else:
        logger.warning(f"未找到书籍: {book_id}")
    return book


def init_notes_file(notes_path: str):
    if not os.path.exists(notes_path):
        with open(notes_path, 'w', encoding='utf-8') as f:
            json.dump({"notes": [], "bookmarks": []}, f)
        logger.debug(f"创建笔记文件: {notes_path}")


def load_notes(notes_path: str) -> Dict:
    logger.debug(f"加载笔记数据: {notes_path}")
    if os.path.exists(notes_path):
        try:
            with open(notes_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"笔记数据加载成功，笔记数: {len(data.get('notes', []))}, 书签数: {len(data.get('bookmarks', []))}")
            return data
        except Exception as e:
            logger.error(f"加载笔记数据失败: {e}")
            return {"notes": [], "bookmarks": []}
    logger.warning(f"笔记文件不存在: {notes_path}")
    return {"notes": [], "bookmarks": []}


def save_notes(notes_path: str, notes_data: Dict):
    logger.debug(f"保存笔记数据: {notes_path}")
    try:
        with open(notes_path, 'w', encoding='utf-8') as f:
            json.dump(notes_data, f, ensure_ascii=False, indent=2)
        logger.debug("笔记数据保存成功")
    except Exception as e:
        logger.error(f"保存笔记数据失败: {e}")


def add_note(notes_path: str, page: int, text: str, content: str, 
             images: List[str] = None, position: Dict = None) -> Dict:
    logger.info(f"添加笔记: page={page}, text_length={len(text)}, content_length={len(content)}")
    notes_data = load_notes(notes_path)
    
    note_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    note = {
        "id": note_id,
        "page": page,
        "text": text,
        "content": content,
        "images": images or [],
        "created_at": now,
        "updated_at": now,
        "position": position or {}
    }
    
    notes_data["notes"].append(note)
    save_notes(notes_path, notes_data)
    
    logger.info(f"笔记添加成功: {note_id}")
    return note


def update_note(notes_path: str, note_id: str, content: str, images: List[str] = None, text: str = None):
    logger.info(f"更新笔记: {note_id}")
    notes_data = load_notes(notes_path)
    for note in notes_data["notes"]:
        if note["id"] == note_id:
            note["content"] = content
            if images is not None:
                note["images"] = images
            if text is not None:
                note["text"] = text
            note["updated_at"] = datetime.now().isoformat()
            logger.info(f"笔记更新成功: {note_id}")
            break
    save_notes(notes_path, notes_data)


def delete_note(notes_path: str, note_id: str) -> Dict:
    logger.info(f"删除笔记: {note_id}")
    notes_data = load_notes(notes_path)
    deleted_note = None
    
    notes_data["notes"] = [n for n in notes_data["notes"] if n["id"] != note_id or (deleted_note := n)]
    
    save_notes(notes_path, notes_data)
    if deleted_note:
        logger.info(f"笔记删除成功: {note_id}")
    else:
        logger.warning(f"未找到笔记: {note_id}")
    return deleted_note


def get_notes_by_page(notes_path: str, page: int) -> List[Dict]:
    logger.debug(f"获取页面笔记: page={page}")
    notes_data = load_notes(notes_path)
    notes = [n for n in notes_data["notes"] if n["page"] == page]
    logger.debug(f"找到 {len(notes)} 条笔记")
    return notes


def get_all_notes(notes_path: str) -> List[Dict]:
    logger.debug(f"获取所有笔记: {notes_path}")
    notes_data = load_notes(notes_path)
    return notes_data["notes"]


def add_bookmark(notes_path: str, page: int, note: str = "") -> Dict:
    logger.info(f"添加书签: page={page}, note={note}")
    notes_data = load_notes(notes_path)
    
    bookmark_id = str(uuid.uuid4())
    bookmark = {
        "id": bookmark_id,
        "page": page,
        "note": note,
        "created_at": datetime.now().isoformat()
    }
    
    notes_data["bookmarks"].append(bookmark)
    save_notes(notes_path, notes_data)
    
    logger.info(f"书签添加成功: {bookmark_id}")
    return bookmark


def delete_bookmark(notes_path: str, bookmark_id: str):
    logger.info(f"删除书签: {bookmark_id}")
    notes_data = load_notes(notes_path)
    original_count = len(notes_data["bookmarks"])
    notes_data["bookmarks"] = [b for b in notes_data["bookmarks"] if b["id"] != bookmark_id]
    if len(notes_data["bookmarks"]) < original_count:
        save_notes(notes_path, notes_data)
        logger.info(f"书签删除成功: {bookmark_id}")
    else:
        logger.warning(f"未找到书签: {bookmark_id}")


def get_all_bookmarks(notes_path: str) -> List[Dict]:
    logger.debug(f"获取所有书签: {notes_path}")
    notes_data = load_notes(notes_path)
    bookmarks = sorted(notes_data["bookmarks"], key=lambda x: x["page"])
    logger.debug(f"找到 {len(bookmarks)} 个书签")
    return bookmarks


def get_bookmark_count(notes_path: str) -> int:
    notes_data = load_notes(notes_path)
    return len(notes_data["bookmarks"])


def get_note_count_by_page(notes_path: str, page: int) -> int:
    return len(get_notes_by_page(notes_path, page))