import streamlit as st
import re
import os
from utils.note_storage import add_note, update_note, delete_note, get_notes_by_page, get_all_notes
from utils.image_handler import delete_image, save_image, validate_image
from utils.logger import setup_logger

logger = setup_logger(__name__)


def render_markdown_with_images(content: str, images_path: str):
    logger.debug(f"渲染Markdown内容，长度: {len(content)}")
    content = content.replace('\r\n', '\n')
    
    image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    parts = re.split(image_pattern, content)
    
    for i in range(0, len(parts), 3):
        if parts[i].strip():
            st.markdown(parts[i], unsafe_allow_html=True)
        if i + 2 < len(parts):
            alt_text = parts[i + 1]
            img_path = parts[i + 2]
            full_path = f"{images_path}/{img_path.split('/')[-1]}"
            if os.path.exists(full_path):
                st.image(full_path, caption=alt_text, width=300)
            else:
                st.warning(f"图片不存在: {full_path}")
    
    logger.debug(f"Markdown渲染完成")


@st.fragment
def note_panel(notes_path: str, images_path: str, book_id: str, current_pages: list):
    logger.info(f"初始化笔记面板: current_pages={current_pages}")
    
    all_notes = []
    for page in current_pages:
        notes = get_notes_by_page(notes_path, page)
        all_notes.extend(notes)
    
    logger.debug(f"获取到 {len(all_notes)} 条笔记")
    
    has_notes = len(all_notes) > 0
    
    if 'note_panel_tab' not in st.session_state:
        st.session_state['note_panel_tab'] = 'notes' if has_notes else 'add'
    
    col_notes, col_add = st.columns(2)
    
    with col_notes:
        if st.button(f"📝 笔记列表 ({len(all_notes)})", 
                     key="tab_notes",
                     use_container_width=True,
                     type="primary" if st.session_state['note_panel_tab'] == 'notes' else "secondary"):
            st.session_state['note_panel_tab'] = 'notes'
            logger.info("切换到笔记列表")
    
    with col_add:
        if st.button("➕ 添加笔记", 
                     key="tab_add",
                     use_container_width=True,
                     type="primary" if st.session_state['note_panel_tab'] == 'add' else "secondary"):
            st.session_state['note_panel_tab'] = 'add'
            logger.info("切换到添加笔记")
    
    st.divider()
    
    if st.session_state['note_panel_tab'] == 'notes':
        if not all_notes:
            st.info("当前页面暂无笔记，点击上方「添加笔记」创建")
            logger.debug("当前页面无笔记")
        else:
            for note in sorted(all_notes, key=lambda x: x['created_at']):
                logger.debug(f"处理笔记: id={note['id']}, page={note['page']}")
                text_preview = note.get('text', '')[:15] + ('...' if len(note.get('text', '')) > 15 else '')
                expander_label = f"📌 第 {note['page'] + 1} 页"
                if text_preview:
                    expander_label += f" - {text_preview}"
                
                expand_key = f"expand_{note['id']}"
                if expand_key not in st.session_state:
                    st.session_state[expand_key] = False
                
                st.markdown(f"""
                <div id="{expand_key}" style="margin-bottom: 8px;">
                <script>
                document.getElementById('{expand_key}').addEventListener('mouseenter', function() {{
                    window.parent.postMessage({{type: 'expand_note', noteId: '{note['id']}'}}, '*');
                }});
                </script>
                <style>
                #{expand_key}:hover {{
                    background-color: rgba(255, 215, 0, 0.1);
                    border-left: 4px solid #FFD700;
                    border-radius: 4px;
                }}
                </style>
                """, unsafe_allow_html=True)
                
                expanded = st.session_state[expand_key]
                with st.expander(expander_label, expanded=expanded):
                    if note['text']:
                        st.markdown(f"**选中的文本:**\n\n>{note['text']}")
                    
                    st.markdown("**笔记内容:**")
                    render_markdown_with_images(note['content'], images_path)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<p style="font-size:0.5em;color:#888;margin:0;">创建: {note["created_at"]}</p>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<p style="font-size:0.5em;color:#888;margin:0;">更新: {note["updated_at"]}</p>', unsafe_allow_html=True)
                    
                    edit_key = f"edit_{note['id']}"
                    delete_key = f"delete_{note['id']}"
                    
                    col_edit, col_delete = st.columns(2)
                    with col_edit:
                        if st.button("编辑", key=edit_key):
                            st.session_state['editing_note_id'] = note['id']
                            st.session_state['editing_content'] = note['content']
                            st.session_state['editing_text'] = note.get('text', '')
                            st.session_state['editing_images'] = note['images'].copy()
                            logger.info(f"开始编辑笔记: {note['id']}")
                            st.rerun(scope="fragment")
                    with col_delete:
                        if st.button("删除", key=delete_key):
                            deleted = delete_note(notes_path, note['id'])
                            if deleted and deleted.get('images'):
                                for img in deleted['images']:
                                    delete_image(images_path, img)
                            st.success("笔记已删除")
                            logger.info(f"笔记删除成功: {note['id']}")
                            st.rerun(scope="fragment")
            
                    st.markdown("</div>", unsafe_allow_html=True)
        
        if 'editing_note_id' in st.session_state:
            st.divider()
            st.subheader("✏️ 编辑笔记")
            edit_note(notes_path, images_path, book_id)
    else:
        if 'editing_note_id' in st.session_state:
            st.subheader("✏️ 编辑笔记")
            edit_note(notes_path, images_path, book_id)
        else:
            add_new_note(notes_path, images_path, book_id, current_pages)


def add_new_note(notes_path: str, images_path: str, book_id: str, current_pages: list):
    logger.debug("添加新笔记")
    selected_page = st.selectbox("选择页码", current_pages, format_func=lambda x: f"第 {x + 1} 页")
    
    selected_text = st.text_area("选中的文本（可选）", key="new_note_text", 
                                 placeholder="在此粘贴从PDF中选中的文本...")
    
    content = st.text_area("笔记内容（支持Markdown）", key="new_note_content", 
                           placeholder="在此输入笔记内容，支持Markdown格式...", height=200)
    
    uploaded_file = st.file_uploader("上传图片（可选）", type=["png", "jpg", "jpeg", "gif", "bmp"], 
                                     key="new_note_image")
    
    images = []
    if uploaded_file is not None:
        if validate_image(uploaded_file):
            filename = save_image(uploaded_file, images_path, book_id, selected_page)
            images.append(filename)
            st.success(f"图片上传成功: {filename}")
            content += f"\n\n![图片]({filename})"
            logger.info(f"图片上传并添加到笔记: {filename}")
        else:
            st.error("无效的图片文件")
            logger.warning("无效的图片文件")
    
    if st.button("保存笔记", key="save_new_note"):
        if content.strip():
            add_note(notes_path, selected_page, selected_text, content, images)
            st.success("笔记已保存")
            logger.info(f"笔记添加成功: page={selected_page}")
            st.session_state['note_panel_tab'] = 'notes'
            st.rerun(scope="fragment")
        else:
            st.warning("请输入笔记内容")
            logger.warning("笔记内容为空")


def edit_note(notes_path: str, images_path: str, book_id: str):
    note_id = st.session_state['editing_note_id']
    content = st.session_state['editing_content']
    selected_text = st.session_state.get('editing_text', '')
    images = st.session_state.get('editing_images', [])
    
    logger.info(f"编辑笔记: {note_id}")
    
    new_text = st.text_area("选中的文本（可选）", value=selected_text, key="edit_note_text", 
                            placeholder="在此粘贴从PDF中选中的文本...")
    
    new_content = st.text_area("笔记内容", value=content, key="edit_note_content", height=200)
    
    uploaded_file = st.file_uploader("上传新图片", type=["png", "jpg", "jpeg", "gif", "bmp"], 
                                     key="edit_note_image")
    
    if uploaded_file is not None:
        if validate_image(uploaded_file):
            note = next((n for n in get_all_notes(notes_path) if n['id'] == note_id), None)
            if note:
                filename = save_image(uploaded_file, images_path, book_id, note['page'])
                images.append(filename)
                new_content += f"\n\n![图片]({filename})"
                st.success(f"图片上传成功")
                logger.info(f"图片上传并添加到笔记: {filename}")
        else:
            st.error("无效的图片文件")
            logger.warning("无效的图片文件")
    
    if images:
        st.write("已添加的图片:")
        for i, img_name in enumerate(images):
            col1, col2 = st.columns([4, 1])
            with col1:
                img_full_path = os.path.join(images_path, img_name)
                if os.path.exists(img_full_path):
                    st.image(img_full_path, caption=img_name, width=100)
                else:
                    st.warning(f"图片不存在: {img_name}")
            with col2:
                if st.button("删除图片", key=f"delete_img_{i}"):
                    delete_image(images_path, img_name)
                    images.remove(img_name)
                    new_content = new_content.replace(f"![图片]({img_name})", "")
                    st.session_state['editing_images'] = images
                    st.session_state['editing_content'] = new_content
                    logger.info(f"删除笔记中的图片: {img_name}")
                    st.rerun(scope="fragment")
    
    col_save, col_cancel = st.columns(2)
    with col_save:
        if st.button("保存修改", key="save_edit_note"):
            update_note(notes_path, note_id, new_content, images, new_text)
            st.success("笔记已更新")
            logger.info(f"笔记更新成功: {note_id}")
            del st.session_state['editing_note_id']
            del st.session_state['editing_content']
            del st.session_state['editing_text']
            del st.session_state['editing_images']
            st.session_state['note_panel_tab'] = 'notes'
            st.rerun(scope="fragment")
    with col_cancel:
        if st.button("取消", key="cancel_edit_note"):
            del st.session_state['editing_note_id']
            del st.session_state['editing_content']
            del st.session_state['editing_text']
            del st.session_state['editing_images']
            logger.debug("取消编辑笔记")
            st.session_state['note_panel_tab'] = 'notes'