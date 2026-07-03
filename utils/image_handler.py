import os
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO

from utils.logger import setup_logger

logger = setup_logger(__name__)


def save_image(uploaded_file, images_path: str, book_id: str, page_num: int) -> str:
    logger.info(f"保存图片: book_id={book_id}, page={page_num}, filename={uploaded_file.name}")
    os.makedirs(images_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext not in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
        ext = 'png'
    
    filename = f"{book_id}_page{page_num}_{timestamp}.{ext}"
    filepath = os.path.join(images_path, filename)
    
    try:
        image = Image.open(uploaded_file)
        image.save(filepath)
        logger.info(f"图片保存成功: {filepath}")
        return filename
    except Exception as e:
        logger.error(f"保存图片失败: {e}")
        raise


def save_image_from_bytes(image_bytes: bytes, images_path: str, book_id: str, page_num: int) -> str:
    logger.info(f"从字节保存图片: book_id={book_id}, page={page_num}, bytes_size={len(image_bytes)}")
    os.makedirs(images_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{book_id}_page{page_num}_{timestamp}.png"
    filepath = os.path.join(images_path, filename)
    
    try:
        image = Image.open(BytesIO(image_bytes))
        image.save(filepath)
        logger.info(f"图片保存成功: {filepath}")
        return filename
    except Exception as e:
        logger.error(f"从字节保存图片失败: {e}")
        raise


def delete_image(images_path: str, filename: str):
    logger.info(f"删除图片: {filename}")
    filepath = os.path.join(images_path, filename)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.info(f"图片删除成功: {filepath}")
        except Exception as e:
            logger.error(f"删除图片失败: {e}")
    else:
        logger.warning(f"图片文件不存在: {filepath}")


def get_image_path(images_path: str, filename: str) -> str:
    path = os.path.join(images_path, filename)
    logger.debug(f"获取图片路径: {path}")
    return path


def resize_image(image: Image.Image, max_width: int = 800, max_height: int = 600) -> Image.Image:
    logger.debug(f"调整图片尺寸: original={image.size}, max={max_width}x{max_height}")
    width, height = image.size
    if width > max_width or height > max_height:
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        resized = image.resize((new_width, new_height), Image.LANCZOS)
        logger.debug(f"图片尺寸调整完成: {image.size} -> {resized.size}")
        return resized
    logger.debug(f"图片尺寸无需调整")
    return image


def image_to_bytes(image: Image.Image, format: str = 'PNG') -> bytes:
    logger.debug(f"图片转字节: format={format}, size={image.size}")
    buffer = BytesIO()
    image.save(buffer, format=format)
    logger.debug(f"图片转字节完成，大小: {len(buffer.getvalue())}")
    return buffer.getvalue()


def validate_image(file) -> bool:
    logger.debug(f"验证图片文件: {file.name}")
    try:
        image = Image.open(file)
        image.verify()
        logger.debug(f"图片验证成功")
        return True
    except Exception as e:
        logger.warning(f"图片验证失败: {e}")
        return False