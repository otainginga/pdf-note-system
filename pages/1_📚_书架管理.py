import streamlit as st
import os
import uuid
from utils.note_storage import load_shelf, add_book, DATA_DIR, get_book, sync_shelf_with_disk
from components.reader import reader
from components.bookshelf_card import render_bookshelf
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    logger.info("进入书架管理页面")
    
    if 'mode' not in st.session_state:
        st.session_state['mode'] = 'shelf'
        logger.debug("初始化模式为: shelf")
    
    if 'upload_counter' not in st.session_state:
        st.session_state['upload_counter'] = 0
    
    if st.session_state['mode'] == 'reader' and st.session_state.get('selected_book_id'):
        book = get_book(st.session_state['selected_book_id'])
        if book:
            logger.info(f"进入阅读模式: book_id={book['id']}")
            reader(book)
        else:
            st.error("书籍不存在")
            logger.error(f"书籍不存在: book_id={st.session_state['selected_book_id']}")
            st.session_state['mode'] = 'shelf'
            st.rerun()
    else:
        st.title("📚 书架管理")
        
        shelf = sync_shelf_with_disk()
        books = shelf.get("books", [])
        logger.debug(f"书架书籍数量: {len(books)}")
        
        st.subheader("上传新书籍")
        uploaded_file = st.file_uploader("选择PDF文件", type=["pdf"], key=f"upload_pdf_{st.session_state['upload_counter']}")
        
        if uploaded_file is not None:
            logger.info(f"开始上传书籍: {uploaded_file.name}")
            try:
                book_id = str(uuid.uuid4())
                book_dir = os.path.join(DATA_DIR, 'books', book_id)
                os.makedirs(book_dir, exist_ok=True)
                
                original_name = uploaded_file.name[:-4] if uploaded_file.name.endswith('.pdf') else uploaded_file.name
                book_title = st.text_input("书籍名称", value=original_name, key=f"upload_title_{st.session_state['upload_counter']}")
                
                file_path = os.path.join(book_dir, f"{book_title}.pdf")
                
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                add_book(book_title, file_path)
                st.success(f"书籍 '{book_title}' 已添加到书架")
                logger.info(f"书籍上传成功: title={book_title}, book_id={book_id}")
                st.session_state['upload_counter'] += 1
                st.rerun()
            except Exception as e:
                st.error(f"上传书籍失败: {e}")
                logger.error(f"书籍上传失败: {e}", exc_info=True)
        
        st.divider()
        
        st.subheader("我的书架")
        render_bookshelf(books)


if __name__ == "__main__":
    main()