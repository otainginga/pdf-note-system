import streamlit as st
from utils.note_storage import init_storage
from utils.logger import setup_logger

logger = setup_logger(__name__)


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

    # Custom navigation with ordered sidebar links
    pages = {
        "": [
            st.Page("pages/1_📚_书架管理.py", title="📚 书架管理", default=True),
            st.Page("pages/2_🔖_书签管理.py", title=" 书签管理"),
            st.Page("pages/3_📊_系统概览.py", title="📊 系统概览"),
        ]
    }

    pg = st.navigation(pages, position="sidebar")
    pg.run()


if __name__ == "__main__":
    main()
