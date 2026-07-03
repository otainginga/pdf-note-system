import streamlit as st
import os
from utils.note_storage import get_book, init_storage, load_shelf
from components.reader import reader
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_file_size(filepath: str) -> str:
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"
    return "0 B"


def calculate_storage_stats():
    shelf = load_shelf()
    books = shelf.get("books", [])
    
    total_images_size = 0
    total_notes_size = 0
    total_books = len(books)
    total_notes = 0
    total_bookmarks = 0
    
    for book in books:
        if os.path.exists(book['notes_path']):
            total_notes_size += os.path.getsize(book['notes_path'])
            
            import json
            with open(book['notes_path'], 'r', encoding='utf-8') as f:
                notes_data = json.load(f)
                total_notes += len(notes_data.get('notes', []))
                total_bookmarks += len(notes_data.get('bookmarks', []))
        
        if os.path.exists(book['images_path']):
            for img_file in os.listdir(book['images_path']):
                img_path = os.path.join(book['images_path'], img_file)
                if os.path.isfile(img_path):
                    total_images_size += os.path.getsize(img_path)
    
    def format_size(size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        else:
            return f"{size / (1024 * 1024):.2f} MB"
    
    return {
        'total_books': total_books,
        'total_notes': total_notes,
        'total_bookmarks': total_bookmarks,
        'notes_size': format_size(total_notes_size),
        'images_size': format_size(total_images_size),
        'total_size': format_size(total_notes_size + total_images_size)
    }


def main():
    logger.info("=" * 50)
    logger.info("PDF双页阅读笔记系统启动")
    logger.info("=" * 50)
    
    init_storage()
    
    st.set_page_config(
        page_title="PDF双页阅读笔记系统",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if 'page' not in st.session_state:
        st.session_state['page'] = 'shelf'
        logger.debug("初始化page状态: shelf")
    
    if 'selected_book_id' not in st.session_state:
        st.session_state['selected_book_id'] = None
        logger.debug("初始化selected_book_id状态: None")
    
    if st.session_state['page'] == 'reader' and st.session_state['selected_book_id']:
        book = get_book(st.session_state['selected_book_id'])
        if book:
            reader(book)
        else:
            st.error("书籍不存在")
            logger.error(f"书籍不存在: book_id={st.session_state['selected_book_id']}")
            st.session_state['page'] = 'shelf'
            st.rerun()
    else:
        st.title("📖 PDF双页阅读笔记系统")
        st.markdown("""
        欢迎使用PDF双页阅读笔记系统！
        
        **功能特点：**
        - 📚 **书架管理**：上传和管理您的PDF书籍
        - 📖 **双页阅读**：仿实体书的双页阅读体验
        - 📝 **富文本笔记**：支持Markdown格式和图片插入
        - 🔖 **书签导航**：快速跳转到重要页面
        - 💾 **自动保存**：所有笔记和阅读进度自动保存
        
        **使用方法：**
        1. 点击左侧"书架管理"上传PDF文件
        2. 点击"开始阅读"进入阅读器
        3. 在右侧笔记面板添加和管理笔记
        4. 使用书签功能标记重要页面
        
        开始您的阅读之旅吧！
        """)
        
        stats = calculate_storage_stats()
        
        st.subheader("📊 系统统计")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("书籍数量", stats['total_books'])
        with col2:
            st.metric("笔记数量", stats['total_notes'])
        with col3:
            st.metric("书签数量", stats['total_bookmarks'])
        with col4:
            st.metric("笔记文件大小", stats['notes_size'])
        with col5:
            st.metric("图片文件大小", stats['images_size'])
        with col6:
            st.metric("总数据大小", stats['total_size'])


if __name__ == "__main__":
    main()