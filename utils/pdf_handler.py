import fitz
from PIL import Image
import io
from typing import Tuple, Optional

from utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFHandler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.doc = None
        logger.info(f"创建PDFHandler实例: {file_path}")
    
    def open(self):
        if self.doc is None:
            logger.debug(f"打开PDF文件: {self.file_path}")
            try:
                self.doc = fitz.open(self.file_path)
                logger.debug(f"PDF文件打开成功，页数: {len(self.doc)}")
            except Exception as e:
                logger.error(f"打开PDF文件失败: {e}")
                raise
    
    def close(self):
        if self.doc is not None:
            logger.debug(f"关闭PDF文件: {self.file_path}")
            self.doc.close()
            self.doc = None
    
    def get_page_count(self) -> int:
        logger.debug(f"获取PDF页数: {self.file_path}")
        self.open()
        count = len(self.doc)
        logger.debug(f"PDF页数: {count}")
        return count
    
    def get_page_text(self, page_num: int) -> str:
        logger.debug(f"获取页面文本: page={page_num}")
        self.open()
        if page_num < 0 or page_num >= len(self.doc):
            logger.warning(f"页码超出范围: {page_num}")
            return ""
        try:
            page = self.doc[page_num]
            text = page.get_text()
            logger.debug(f"页面文本获取成功，长度: {len(text)}")
            return text
        except Exception as e:
            logger.error(f"获取页面文本失败: {e}")
            return ""
    
    def get_page_image(self, page_num: int, dpi: int = 150) -> Optional[Image.Image]:
        logger.debug(f"获取页面图像: page={page_num}, dpi={dpi}")
        self.open()
        if page_num < 0 or page_num >= len(self.doc):
            logger.warning(f"页码超出范围: {page_num}")
            return None
        
        try:
            page = self.doc[page_num]
            zoom = dpi / 72
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            logger.debug(f"页面图像获取成功，尺寸: {img.size}")
            return img
        except Exception as e:
            logger.error(f"获取页面图像失败: {e}")
            return None
    
    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        logger.debug(f"获取页面尺寸: page={page_num}")
        self.open()
        if page_num < 0 or page_num >= len(self.doc):
            logger.warning(f"页码超出范围: {page_num}")
            return (0, 0)
        
        try:
            page = self.doc[page_num]
            dimensions = (page.rect.width, page.rect.height)
            logger.debug(f"页面尺寸: {dimensions}")
            return dimensions
        except Exception as e:
            logger.error(f"获取页面尺寸失败: {e}")
            return (0, 0)
    
    def extract_text_blocks(self, page_num: int) -> list:
        logger.debug(f"提取文本块: page={page_num}")
        self.open()
        if page_num < 0 or page_num >= len(self.doc):
            logger.warning(f"页码超出范围: {page_num}")
            return []
        
        try:
            page = self.doc[page_num]
            blocks = page.get_text("blocks")
            logger.debug(f"文本块提取成功，数量: {len(blocks)}")
            return blocks
        except Exception as e:
            logger.error(f"提取文本块失败: {e}")
            return []
    
    def get_metadata(self) -> dict:
        logger.debug(f"获取PDF元数据: {self.file_path}")
        self.open()
        try:
            metadata = self.doc.metadata
            logger.debug(f"PDF元数据获取成功: {metadata}")
            return metadata
        except Exception as e:
            logger.error(f"获取PDF元数据失败: {e}")
            return {}
    
    def get_toc(self) -> list:
        """获取PDF目录结构
        返回格式: [[level, title, page], ...]，其中page是从1开始的页码
        """
        logger.debug(f"获取PDF目录: {self.file_path}")
        self.open()
        try:
            toc = self.doc.get_toc()
            logger.debug(f"PDF目录获取成功，条目数: {len(toc)}")
            return toc
        except Exception as e:
            logger.error(f"获取PDF目录失败: {e}")
            return []
    
    def get_toc_for_page(self, page_num: int) -> Optional[str]:
        """获取指定页面的目录标题（page_num是从0开始的页码）
        返回最接近该页面的目录标题
        """
        toc = self.get_toc()
        if not toc:
            return None
        
        # 转换为从0开始的页码进行比较
        target_page = page_num + 1  # PDF目录中的页码是从1开始的
        
        # 找到最后一个页码小于等于当前页面的目录项
        found_title = None
        for item in toc:
            level, title, page = item
            if page <= target_page:
                found_title = title
            else:
                break
        
        return found_title
    
    def __enter__(self):
        logger.debug(f"进入PDFHandler上下文: {self.file_path}")
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug(f"退出PDFHandler上下文: {self.file_path}")
        if exc_type:
            logger.error(f"PDFHandler上下文异常: {exc_type}, {exc_val}")
        self.close()