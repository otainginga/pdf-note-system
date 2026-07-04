import streamlit as st
from utils.note_storage import add_bookmark, delete_bookmark, get_all_bookmarks
from utils.logger import setup_logger

logger = setup_logger(__name__)


def bookmark_sidebar(notes_path: str, on_bookmark_click=None, toc=None):
    logger.debug("初始化书签侧边栏")
    
    # TOC 列表样式
    st.markdown("""
    <style>
    .toc-list button {
        background: transparent !important;
        border: none !important;
        text-align: left !important;
        padding: 3px 8px !important;
        font-size: 14px !important;
        color: inherit !important;
        cursor: pointer !important;
        width: 100% !important;
        font-weight: normal !important;
        border-radius: 4px !important;
    }
    .toc-list button:hover {
        background: rgba(128,128,128,0.15) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # PDF 目录结构
    if toc:
        with st.sidebar.expander("📑 目录", expanded=False):
            st.markdown('<div class="toc-list">', unsafe_allow_html=True)
            for level, title, page in toc:
                indent = "&nbsp;&nbsp;" * (level - 1)
                icon = "▸" if level == 1 else "&nbsp;"
                label = f"{indent}{icon} {title}"
                if st.button(
                    label,
                    key=f"toc_{level}_{page}_{hash(title)}",
                    help=f"跳转到第 {page} 页",
                    use_container_width=True
                ):
                    if on_bookmark_click:
                        on_bookmark_click(page - 1)
            st.markdown('</div>', unsafe_allow_html=True)

    bookmarks = get_all_bookmarks(notes_path)
    bookmark_count = len(bookmarks)
    
    with st.sidebar.expander(f"🔖 书签列表 ({bookmark_count})", expanded=False):
        if not bookmarks:
            st.info("暂无书签，点击页面添加")
            logger.debug("暂无书签")
        else:
            logger.debug(f"获取到 {bookmark_count} 个书签")
            for bookmark in bookmarks:
                logger.debug(f"处理书签: id={bookmark['id']}, page={bookmark['page']}")
                col1, col2 = st.columns([4, 1])
                with col1:
                    page_info = f"第 {bookmark['page'] + 1} 页"
                    if bookmark['note']:
                        page_info += f" - {bookmark['note']}"
                    if st.button(page_info, key=f"bookmark_{bookmark['id']}"):
                        if on_bookmark_click:
                            on_bookmark_click(bookmark['page'])
                            logger.info(f"点击书签跳转: page={bookmark['page']}")
                with col2:
                    delete_key = f"del_bookmark_{bookmark['id']}"
                    if delete_key not in st.session_state:
                        st.session_state[delete_key] = False
                    
                    if not st.session_state[delete_key]:
                        if st.button("🗑️", key=delete_key + "_btn", help="删除书签"):
                            st.session_state[delete_key] = True
                    else:
                        if st.button("确认删除", key=delete_key + "_confirm"):
                            delete_bookmark(notes_path, bookmark['id'])
                            st.success("书签已删除")
                            logger.info(f"书签删除成功: {bookmark['id']}")
                            del st.session_state[delete_key]
                            st.rerun()
                        if st.button("取消", key=delete_key + "_cancel"):
                            st.session_state[delete_key] = False


def add_bookmark_button(notes_path: str, current_page: int):
    logger.debug(f"添加书签按钮: current_page={current_page}")
    st.markdown(f"""
    <style>
    .bookmark-expander {{
        background-color: #10B981 !important;
        border-radius: 8px;
        padding: 4px;
    }}
    .bookmark-expander:hover {{
        background-color: #059669 !important;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    with st.expander("添加书签", expanded=False):
        note = st.text_input("书签备注（可选）", key="bookmark_note")
        if st.button("添加到书签", key="add_bookmark_btn"):
            add_bookmark(notes_path, current_page, note)
            st.success(f"已添加书签到第 {current_page + 1} 页")
            logger.info(f"添加书签: page={current_page}, note={note}")
            st.rerun()


def bookmark_list(notes_path: str, book_title: str = ""):
    logger.info(f"书签列表页面: book_title={book_title}")
    st.header(f"🔖 {book_title} 的书签")
    
    bookmarks = get_all_bookmarks(notes_path)
    
    if not bookmarks:
        st.info("暂无书签")
        logger.debug("暂无书签")
        return
    
    logger.debug(f"获取到 {len(bookmarks)} 个书签")
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
                if st.button("删除", key=f"delete_bookmark_{bookmark['id']}"):
                    delete_bookmark(notes_path, bookmark['id'])
                    st.success("书签已删除")
                    logger.info(f"书签删除成功: {bookmark['id']}")
                    st.rerun()