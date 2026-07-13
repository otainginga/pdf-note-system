import streamlit as st
from utils.pdf_handler import PDFHandler
from utils.note_storage import get_note_count_by_page
from components.bookmark_manager import bookmark_sidebar, add_bookmark_button
from components.note_panel import note_panel
from utils.logger import setup_logger

logger = setup_logger(__name__)


def render_page_image(pdf_handler: PDFHandler, page_num: int, note_count: int = 0):
    logger.debug(f"渲染页面图像: page={page_num}, note_count={note_count}")
    img = pdf_handler.get_page_image(page_num)
    if img is not None:
        col_img, col_badge = st.columns([10, 1])
        with col_img:
            st.image(img, width="stretch")
        with col_badge:
            if note_count > 0:
                st.markdown(f"""
                <div style="background-color: #FFD700; color: #333; border-radius: 50%; 
                            width: 24px; height: 24px; display: flex; align-items: center; 
                            justify-content: center; font-size: 12px; font-weight: bold;
                            margin-top: 8px;">
                    {note_count}
                </div>
                """, unsafe_allow_html=True)
        logger.debug(f"页面图像渲染成功: page={page_num}")
    else:
        st.info(f"无法加载第 {page_num + 1} 页")
        logger.warning(f"无法加载页面图像: page={page_num}")


def render_page_text(pdf_handler: PDFHandler, page_num: int, note_count: int = 0):
    logger.debug(f"渲染页面正文: page={page_num}")
    text = pdf_handler.get_page_text(page_num)
    if text:
        # 在正文右上角显示笔记计数徽章
        if note_count > 0:
            col_text, col_badge = st.columns([10, 1])
            with col_text:
                st.markdown(f'<div class="pdf-text-content" style="height:400px;overflow-y:auto;padding:8px;border:1px solid #e0e0e0;border-radius:4px;background-color:#fafafa;color:#1e1e1e;font-size:14px;line-height:1.8;white-space:pre-wrap;">{text}</div>', unsafe_allow_html=True)
            with col_badge:
                st.markdown(f"""
                <div style="background-color: #FFD700; color: #333; border-radius: 50%;
                            width: 24px; height: 24px; display: flex; align-items: center;
                            justify-content: center; font-size: 12px; font-weight: bold;
                            margin-top: 8px;">
                    {note_count}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="pdf-text-content" style="height:400px;overflow-y:auto;padding:8px;border:1px solid #e0e0e0;border-radius:4px;background-color:#fafafa;color:#1e1e1e;font-size:14px;line-height:1.8;white-space:pre-wrap;">{text}</div>', unsafe_allow_html=True)
        logger.debug(f"页面正文渲染成功: page={page_num}")
    else:
        st.info(f"无法加载第 {page_num + 1} 页的正文")
        logger.warning(f"无法加载页面正文: page={page_num}")


def reader(book: dict):
    logger.info(f"进入阅读器: book_id={book['id']}, title={book['title']}")
    
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = book.get('last_page', 0)
        logger.info(f"初始化当前页码: {st.session_state['current_page']}")
    
    if 'reading_mode' not in st.session_state:
        st.session_state['reading_mode'] = 'dual'
        logger.info(f"初始化阅读模式: dual")
    
    if 'display_mode' not in st.session_state:
        st.session_state['display_mode'] = 'pdf'
        logger.info(f"初始化显示模式: pdf")
    
    if 'page_slider_value' not in st.session_state:
        st.session_state['page_slider_value'] = st.session_state['current_page'] + 1
    
    if 'page_input_dual_value' not in st.session_state:
        st.session_state['page_input_dual_value'] = st.session_state['current_page'] + 1
    
    if 'page_input_single_value' not in st.session_state:
        st.session_state['page_input_single_value'] = st.session_state['current_page'] + 1
    
    current_page = st.session_state['current_page']
    reading_mode = st.session_state['reading_mode']
    display_mode = st.session_state['display_mode']
    logger.debug(f"当前页码: {current_page}, 阅读模式: {reading_mode}, 显示模式: {display_mode}")
    
    try:
        with PDFHandler(book['file_path']) as pdf:
            total_pages = pdf.get_page_count()
            logger.debug(f"PDF总页数: {total_pages}")
            
            if total_pages == 0:
                st.error("PDF文件为空")
                logger.error(f"PDF文件为空: {book['file_path']}")
                return
            
            bookmark_sidebar(book['notes_path'], on_bookmark_click=lambda page: jump_to_page(page), toc=pdf.get_toc())
            
            col_back, col_modes, col_display = st.columns([3, 1, 1])
            with col_back:
                if st.button(f"← 返回书架 - {book['title']}", key="back_to_shelf"):
                    st.session_state['mode'] = 'shelf'
                    logger.info("返回书架")
                    st.rerun()
            with col_modes:
                mode_options = ['双页', '单页']
                mode_keys = ['dual', 'single']
                selected_mode = st.selectbox(
                    "阅读模式",
                    options=mode_keys,
                    format_func=lambda x: mode_options[mode_keys.index(x)],
                    key="reading_mode_select"
                )
                if selected_mode != reading_mode:
                    st.session_state['reading_mode'] = selected_mode
                    logger.info(f"切换阅读模式: {reading_mode} -> {selected_mode}")
                    st.rerun()
            with col_display:
                st.write("显示")
                col_pdf_btn, col_text_btn = st.columns(2)
                with col_pdf_btn:
                    pdf_active = display_mode == 'pdf'
                    if st.button("📄", key="display_pdf", help="PDF原图", type="primary" if pdf_active else "secondary"):
                        st.session_state['display_mode'] = 'pdf'
                        st.rerun()
                with col_text_btn:
                    text_active = display_mode == 'text'
                    if st.button("📝", key="display_text", help="页面正文", type="primary" if text_active else "secondary"):
                        st.session_state['display_mode'] = 'text'
                        st.rerun()
            
            st.markdown("""
            <style>
            .nav-btn {
                background-color: #E5E7EB !important;
                border: 1px solid #D1D5DB !important;
                border-radius: 6px !important;
                padding: 4px 8px !important;
                font-size: 16px !important;
                color: #374151 !important;
                width: auto !important;
            }
            .nav-btn:hover {
                background-color: #D1D5DB !important;
            }
            /* Dark mode for text content */
            [data-theme="dark"] .pdf-text-content {
                background-color: #1e1e1e !important;
                color: #e0e0e0 !important;
                border-color: #444 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if reading_mode == 'dual':
                left_page = current_page
                right_page = current_page + 1 if current_page + 1 < total_pages else None
                logger.debug(f"左右页: left={left_page}, right={right_page}")
                
                col_prev_nav, col_left, col_right, col_next_nav, col_notes = st.columns([0.2, 2, 2, 0.2, 1.5])
                
                with col_prev_nav:
                    st.markdown("<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>", unsafe_allow_html=True)
                    if st.button("◀", key="prev_page_dual", use_container_width=True):
                        if current_page > 0:
                            st.session_state['current_page'] = max(0, current_page - 1)
                            st.session_state['page_slider_value'] = st.session_state['current_page'] + 1
                            st.session_state['page_input_dual_value'] = st.session_state['current_page'] + 1
                            from utils.note_storage import update_last_page
                            update_last_page(book['id'], st.session_state['current_page'])
                            logger.info(f"翻页: 上一页 -> {st.session_state['current_page']}")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_left:
                    left_title = pdf.get_toc_for_page(left_page)
                    if left_title:
                        st.markdown(f"**{left_title}**")
                    st.subheader(f"第 {left_page + 1} 页")
                    note_count_left = get_note_count_by_page(book['notes_path'], left_page)
                    if display_mode == 'pdf':
                        render_page_image(pdf, left_page, note_count_left)
                    else:
                        render_page_text(pdf, left_page, note_count_left)
                
                with col_right:
                    if right_page is not None:
                        right_title = pdf.get_toc_for_page(right_page)
                        if right_title:
                            st.markdown(f"**{right_title}**")
                        st.subheader(f"第 {right_page + 1} 页")
                        note_count_right = get_note_count_by_page(book['notes_path'], right_page)
                        if display_mode == 'pdf':
                            render_page_image(pdf, right_page, note_count_right)
                        else:
                            render_page_text(pdf, right_page, note_count_right)
                    else:
                        st.empty()
                
                with col_next_nav:
                    st.markdown("<div style='display: flex; align-items: center; justify-content: center; height: 100%;'>", unsafe_allow_html=True)
                    if st.button("▶", key="next_page_dual", use_container_width=True):
                        if current_page < total_pages - 1:
                            st.session_state['current_page'] = min(total_pages - 1, current_page + 1)
                            st.session_state['page_slider_value'] = st.session_state['current_page'] + 1
                            st.session_state['page_input_dual_value'] = st.session_state['current_page'] + 1
                            from utils.note_storage import update_last_page
                            update_last_page(book['id'], st.session_state['current_page'])
                            logger.info(f"翻页: 下一页 -> {st.session_state['current_page']}")
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_notes:
                    current_pages = [left_page]
                    if right_page is not None:
                        current_pages.append(right_page)
                    note_panel(book['notes_path'], book['images_path'], book['id'], current_pages)
                
                page_range = f"{left_page + 1}"
                if right_page is not None:
                    page_range += f" - {right_page + 1}"
                    
                col_info, col_slider, col_input, col_bookmark = st.columns([1, 2, 1, 1])
                
                with col_info:
                    st.write(f"页码: {page_range} / {total_pages}")
                
                with col_slider:
                    new_page = st.slider("跳转", 1, total_pages, st.session_state['page_slider_value'], key="page_slider")
                    if new_page != st.session_state['page_slider_value']:
                        st.session_state['current_page'] = new_page - 1
                        st.session_state['page_slider_value'] = new_page
                        st.session_state['page_input_dual_value'] = new_page
                        from utils.note_storage import update_last_page
                        update_last_page(book['id'], st.session_state['current_page'])
                        logger.info(f"滑块跳转: {current_page + 1} -> {new_page}")
                        st.rerun()
                
                with col_input:
                    input_page = st.number_input("页码", min_value=1, max_value=total_pages, value=st.session_state['page_input_dual_value'], key="page_input_dual")
                    if input_page != st.session_state['page_input_dual_value']:
                        st.session_state['current_page'] = input_page - 1
                        st.session_state['page_slider_value'] = input_page
                        st.session_state['page_input_dual_value'] = input_page
                        from utils.note_storage import update_last_page
                        update_last_page(book['id'], st.session_state['current_page'])
                        logger.info(f"输入跳转: {current_page + 1} -> {input_page}")
                        st.rerun()
                
                with col_bookmark:
                    add_bookmark_button(book['notes_path'], current_page)
            else:
                display_page = current_page
                logger.debug(f"单页模式: page={display_page}")
                
                col_book, col_notes = st.columns([1.2, 1])
                
                with col_book:
                    display_title = pdf.get_toc_for_page(display_page)
                    if display_title:
                        st.markdown(f"**{display_title}**")
                    col_prev_top, col_page, col_next_top = st.columns([0.3, 1, 0.3])
                    with col_prev_top:
                        if st.button("◀", key="prev_page_single_top", use_container_width=True):
                            if current_page > 0:
                                st.session_state['current_page'] = max(0, current_page - 1)
                                st.session_state['page_input_single_value'] = st.session_state['current_page'] + 1
                                from utils.note_storage import update_last_page
                                update_last_page(book['id'], st.session_state['current_page'])
                                st.rerun()
                    with col_page:
                        st.subheader(f"第 {display_page + 1} 页")
                    with col_next_top:
                        if st.button("▶", key="next_page_single_top", use_container_width=True):
                            if current_page < total_pages - 1:
                                st.session_state['current_page'] = min(total_pages - 1, current_page + 1)
                                st.session_state['page_input_single_value'] = st.session_state['current_page'] + 1
                                from utils.note_storage import update_last_page
                                update_last_page(book['id'], st.session_state['current_page'])
                                st.rerun()
                    note_count = get_note_count_by_page(book['notes_path'], display_page)
                    if display_mode == 'pdf':
                        render_page_image(pdf, display_page, note_count)
                    else:
                        render_page_text(pdf, display_page, note_count)
                    
                    col_prev, col_info, col_next, col_slider, col_bookmark = st.columns([0.4, 1.5, 0.4, 2, 1])
                    
                    with col_prev:
                        if st.button("◀", key="prev_page_single", use_container_width=True):
                            if current_page > 0:
                                st.session_state['current_page'] = max(0, current_page - 1)
                                st.session_state['page_input_single_value'] = st.session_state['current_page'] + 1
                                from utils.note_storage import update_last_page
                                update_last_page(book['id'], st.session_state['current_page'])
                                logger.info(f"翻页: 上一页 -> {st.session_state['current_page']}")
                                st.rerun()
                    
                    with col_info:
                        st.write(f"{display_page + 1} / {total_pages}")
                    
                    with col_next:
                        if st.button("▶", key="next_page_single", use_container_width=True):
                            if current_page < total_pages - 1:
                                st.session_state['current_page'] = min(total_pages - 1, current_page + 1)
                                st.session_state['page_input_single_value'] = st.session_state['current_page'] + 1
                                from utils.note_storage import update_last_page
                                update_last_page(book['id'], st.session_state['current_page'])
                                logger.info(f"翻页: 下一页 -> {st.session_state['current_page']}")
                                st.rerun()
                    
                    with col_slider:
                        new_page = st.number_input("页码", min_value=1, max_value=total_pages, value=st.session_state['page_input_single_value'], key="page_input")
                        if new_page != st.session_state['page_input_single_value']:
                            st.session_state['current_page'] = new_page - 1
                            st.session_state['page_input_single_value'] = new_page
                            from utils.note_storage import update_last_page
                            update_last_page(book['id'], st.session_state['current_page'])
                            logger.info(f"输入跳转: {current_page + 1} -> {new_page}")
                            st.rerun()
                    
                    with col_bookmark:
                        add_bookmark_button(book['notes_path'], current_page)
                
                with col_notes:
                    note_panel(book['notes_path'], book['images_path'], book['id'], [display_page])
            
            st.markdown("""
            <script>
            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    return;
                }
                
                if (e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prevBtn = document.querySelector('[data-testid="stButton"] button');
                    if (prevBtn) prevBtn.click();
                } else if (e.key === 'ArrowRight') {
                    e.preventDefault();
                    const buttons = document.querySelectorAll('[data-testid="stButton"] button');
                    if (buttons.length > 0) {
                        buttons[buttons.length - 1].click();
                    }
                }
            });
            
            document.querySelectorAll('.streamlit-expanderHeader').forEach(function(header) {
                header.addEventListener('mouseenter', function(e) {
                    e.preventDefault();
                    const expander = header.parentElement;
                    const content = expander.querySelector('.streamlit-expanderContent');
                    if (content && content.style.display !== 'block') {
                        header.click();
                    }
                });
            });
            </script>
            """, unsafe_allow_html=True)
        
        logger.info(f"阅读器渲染完成")
    except Exception as e:
        logger.error(f"阅读器异常: {e}", exc_info=True)
        st.error(f"阅读器出现错误: {e}")


def jump_to_page(page_num: int):
    logger.info(f"跳转到页面: {page_num}")
    st.session_state['current_page'] = page_num
    st.session_state['page_slider_value'] = page_num + 1
    st.session_state['page_input_dual_value'] = page_num + 1
    st.session_state['page_input_single_value'] = page_num + 1
    st.rerun()