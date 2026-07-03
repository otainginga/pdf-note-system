import streamlit as st
from utils.image_handler import save_image, validate_image


def image_uploader(book_id: str, page_num: int, images_path: str, key: str = "image_uploader"):
    uploaded_file = st.file_uploader(
        "上传图片",
        type=["png", "jpg", "jpeg", "gif", "bmp"],
        key=key,
        help="拖拽或点击上传图片"
    )
    
    if uploaded_file is not None:
        if validate_image(uploaded_file):
            filename = save_image(uploaded_file, images_path, book_id, page_num)
            st.success(f"图片上传成功: {filename}")
            return filename
        else:
            st.error("无效的图片文件")
            return None
    
    return None


def multiple_image_uploader(book_id: str, page_num: int, images_path: str, 
                            existing_images: list = None, key: str = "multi_image_uploader"):
    existing_images = existing_images or []
    
    st.subheader("图片管理")
    
    uploaded_file = st.file_uploader(
        "上传新图片",
        type=["png", "jpg", "jpeg", "gif", "bmp"],
        key=f"{key}_upload",
        help="拖拽或点击上传图片"
    )
    
    if uploaded_file is not None:
        if validate_image(uploaded_file):
            filename = save_image(uploaded_file, images_path, book_id, page_num)
            existing_images.append(filename)
            st.success(f"图片上传成功: {filename}")
    
    if existing_images:
        st.write("已上传的图片:")
        for i, img_name in enumerate(existing_images):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.image(f"{images_path}/{img_name}", caption=img_name, width=100)
            with col2:
                if st.button("删除", key=f"{key}_delete_{i}"):
                    existing_images.remove(img_name)
                    from utils.image_handler import delete_image
                    delete_image(images_path, img_name)
                    st.success(f"图片已删除")
                    st.rerun()
    
    return existing_images