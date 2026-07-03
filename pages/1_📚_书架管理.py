import streamlit as st
import os
import uuid
import json
from utils.note_storage import load_shelf, add_book, remove_book, DATA_DIR, get_book, get_all_notes
from utils.pdf_handler import PDFHandler
from components.reader import reader
from utils.logger import setup_logger

logger = setup_logger(__name__)


def export_notes_to_md(book: dict):
    logger.info(f"导出笔记为Markdown: {book['title']}")
    notes = get_all_notes(book['notes_path'])
    
    if not notes:
        st.warning("该书暂无笔记")
        return
    
    md_content = f"# {book['title']} - 读书笔记\n\n"
    md_content += f"导出时间: {book.get('added_at', '')}\n"
    md_content += f"书籍ID: {book['id']}\n\n"
    md_content += "---\n\n"
    
    notes_by_page = {}
    for note in sorted(notes, key=lambda x: x['page']):
        if note['page'] not in notes_by_page:
            notes_by_page[note['page']] = []
        notes_by_page[note['page']].append(note)
    
    for page in sorted(notes_by_page.keys()):
        md_content += f"## 第 {page + 1} 页\n\n"
        
        for i, note in enumerate(notes_by_page[page], 1):
            md_content += f"### 笔记 {i}\n\n"
            
            if note.get('text'):
                md_content += f"**选中的文本:**\n\n>{note['text']}\n\n"
            
            md_content += f"**笔记内容:**\n\n{note['content']}\n\n"
            
            md_content += f"**创建时间:** {note['created_at']}\n"
            md_content += f"**更新时间:** {note['updated_at']}\n\n"
        
        md_content += "---\n\n"
    
    filename = f"{book['title']}_笔记.md"
    st.download_button(
        label="📥 下载笔记",
        data=md_content,
        file_name=filename,
        mime="text/markdown",
        key=f"export_{book['id']}"
    )
    
    logger.info(f"笔记导出成功: {filename}")


def show_book(book):
    logger.debug(f"显示书籍信息: id={book['id']}, title={book['title']}")
    with st.expander(f"📖 {book['title']}"):
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write(f"**文件路径**: {book['file_path']}")
            st.write(f"**添加时间**: {book['added_at']}")
            st.write(f"**最后阅读**: 第 {book['last_page'] + 1} 页")
            
            with PDFHandler(book['file_path']) as pdf:
                total_pages = pdf.get_page_count()
                st.write(f"**总页数**: {total_pages}")
        
        with col2:
            col_read, col_export = st.columns(2)
            with col_read:
                if st.button("开始阅读", key=f"read_{book['id']}"):
                    st.session_state['selected_book_id'] = book['id']
                    st.session_state['mode'] = 'reader'
                    logger.info(f"开始阅读书籍: id={book['id']}, title={book['title']}")
                    st.rerun()
            
            with col_export:
                export_notes_to_md(book)
            
            col_rename, col_delete = st.columns(2)
            with col_rename:
                if st.button("重命名", key=f"rename_{book['id']}", type="secondary"):
                    st.session_state['renaming_book_id'] = book['id']
                    st.session_state['renaming_new_title'] = book['title']
                    logger.info(f"开始重命名书籍: {book['id']}")
                    st.rerun()
            
            with col_delete:
                delete_key = f"delete_{book['id']}"
                confirm_key = f"confirm_delete_{book['id']}"
                
                if confirm_key not in st.session_state:
                    st.session_state[confirm_key] = False
                
                if not st.session_state[confirm_key]:
                    if st.button("删除", key=delete_key, type="secondary"):
                        st.session_state[confirm_key] = True
                        st.rerun()
                else:
                    st.warning("⚠️ 确定要删除这本书吗？删除后所有笔记和图片将被永久删除！")
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("确认删除", key=f"do_delete_{book['id']}"):
                            remove_book(book['id'])
                            st.success(f"已删除书籍: {book['title']}")
                            logger.info(f"删除书籍: id={book['id']}, title={book['title']}")
                            del st.session_state[confirm_key]
                            st.rerun()
                    with col_cancel:
                        if st.button("取消", key=f"cancel_delete_{book['id']}"):
                            st.session_state[confirm_key] = False
                            st.rerun()


def rename_book(book):
    logger.info(f"重命名书籍: {book['id']}")
    st.subheader(f"✏️ 重命名书籍")
    
    new_title = st.text_input("新书名", value=st.session_state.get('renaming_new_title', book['title']))
    
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("保存", key=f"save_rename_{book['id']}"):
            if new_title.strip():
                shelf = load_shelf()
                for b in shelf["books"]:
                    if b["id"] == book["id"]:
                        b["title"] = new_title.strip()
                        break
                
                old_pdf_path = book["file_path"]
                new_pdf_name = f"{new_title.strip()}.pdf"
                new_pdf_path = os.path.join(os.path.dirname(old_pdf_path), new_pdf_name)
                
                if os.path.exists(old_pdf_path):
                    os.rename(old_pdf_path, new_pdf_path)
                    for b in shelf["books"]:
                        if b["id"] == book["id"]:
                            b["file_path"] = new_pdf_path
                            break
                
                from utils.note_storage import save_shelf
                save_shelf(shelf)
                
                st.success(f"书籍已重命名为: {new_title}")
                logger.info(f"书籍重命名成功: {book['title']} -> {new_title}")
                
                del st.session_state['renaming_book_id']
                del st.session_state['renaming_new_title']
                st.rerun()
            else:
                st.warning("请输入书名")
    
    with col_cancel:
        if st.button("取消", key=f"cancel_rename_{book['id']}"):
            del st.session_state['renaming_book_id']
            del st.session_state['renaming_new_title']
            logger.debug("取消重命名书籍")
            st.rerun()


def main():
    logger.info("进入书架管理页面")
    
    if 'mode' not in st.session_state:
        st.session_state['mode'] = 'shelf'
        logger.debug("初始化模式为: shelf")
    
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
        renaming_book_id = st.session_state.get('renaming_book_id')
        if renaming_book_id:
            book = get_book(renaming_book_id)
            if book:
                rename_book(book)
                return
        
        st.title("📚 书架管理")
        
        shelf = load_shelf()
        books = shelf.get("books", [])
        logger.debug(f"书架书籍数量: {len(books)}")
        
        st.subheader("上传新书籍")
        uploaded_file = st.file_uploader("选择PDF文件", type=["pdf"], key="upload_pdf")
        
        if uploaded_file is not None:
            logger.info(f"开始上传书籍: {uploaded_file.name}")
            try:
                book_id = str(uuid.uuid4())
                book_dir = os.path.join(DATA_DIR, 'books', book_id)
                os.makedirs(book_dir, exist_ok=True)
                
                original_name = uploaded_file.name[:-4] if uploaded_file.name.endswith('.pdf') else uploaded_file.name
                book_title = st.text_input("书籍名称", value=original_name, key="upload_title")
                
                file_path = os.path.join(book_dir, f"{book_title}.pdf")
                
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                add_book(book_title, file_path)
                st.success(f"书籍 '{book_title}' 已添加到书架")
                logger.info(f"书籍上传成功: title={book_title}, book_id={book_id}")
                st.rerun()
            except Exception as e:
                st.error(f"上传书籍失败: {e}")
                logger.error(f"书籍上传失败: {e}", exc_info=True)
        
        st.divider()
        
        st.subheader("我的书架")
        
        if not books:
            st.info("书架为空，请上传PDF文件开始阅读")
            logger.debug("书架为空")
        else:
            for book in sorted(books, key=lambda x: x['added_at'], reverse=True):
                show_book(book)


if __name__ == "__main__":
    main()