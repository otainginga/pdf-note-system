import streamlit as st
from utils.note_storage import load_shelf, get_all_bookmarks, delete_bookmark
from utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    logger.info("进入书签管理页面")
    st.title("🔖 书签管理")
    
    shelf = load_shelf()
    books = shelf.get("books", [])
    logger.debug(f"书架书籍数量: {len(books)}")
    
    if not books:
        st.info("书架为空，请先添加书籍")
        logger.debug("书架为空")
        return
    
    selected_book_id = st.selectbox(
        "选择书籍",
        options=[book['id'] for book in books],
        format_func=lambda x: next(book['title'] for book in books if book['id'] == x)
    )
    
    selected_book = next(book for book in books if book['id'] == selected_book_id)
    logger.debug(f"选中书籍: {selected_book['title']}")
    
    st.subheader(f"{selected_book['title']} 的书签")
    
    bookmarks = get_all_bookmarks(selected_book['notes_path'])
    logger.debug(f"获取到 {len(bookmarks)} 个书签")
    
    if not bookmarks:
        st.info("该书暂无书签")
        logger.debug("该书暂无书签")
        return
    
    for i, bookmark in enumerate(bookmarks, 1):
        logger.debug(f"处理书签 {i}: id={bookmark['id']}, page={bookmark['page']}")
        with st.expander(f"书签 {i}: 第 {bookmark['page'] + 1} 页"):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**页码**: {bookmark['page'] + 1}")
                if bookmark['note']:
                    st.write(f"**备注**: {bookmark['note']}")
                st.write(f"**添加时间**: {bookmark['created_at']}")
            with col2:
                if st.button("跳转到阅读", key=f"goto_{bookmark['id']}"):
                    st.session_state['selected_book_id'] = selected_book_id
                    st.session_state['current_page'] = bookmark['page']
                    st.session_state['mode'] = 'reader'
                    logger.info(f"跳转到阅读: book_id={selected_book_id}, page={bookmark['page']}")
                    st.rerun()
                
                if st.button("删除", key=f"del_{bookmark['id']}", type="secondary"):
                    delete_bookmark(selected_book['notes_path'], bookmark['id'])
                    st.success("书签已删除")
                    logger.info(f"书签删除成功: {bookmark['id']}")
                    st.rerun()


if __name__ == "__main__":
    main()