from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def ocr_scanned_page(image: Image.Image, page_num: int) -> str:
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, lang='eng', config=custom_config)