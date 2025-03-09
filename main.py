import fitz
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import os
import re


def extract_images(pdf_path, output_folder):
    """从 PDF 提取图片，保持原始方向"""
    doc = fitz.open(pdf_path)
    os.makedirs(output_folder, exist_ok=True)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_path = os.path.join(output_folder, f"page{page_num}_img{img_index}.{image_ext}")
            with open(image_path, "wb") as f:
                f.write(image_bytes)

    doc.close()


def preprocess_image(image_path):
    """预处理图片，提高 OCR 识别效果"""
    image = Image.open(image_path).convert("L")  # 转灰度
    image = image.filter(ImageFilter.MedianFilter())  # 降噪
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # 提高对比度
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)  # 放大 2 倍
    return image


def ocr_image(image_path, lang='chi_sim+eng'):
    """对单张图片进行 OCR 识别"""
    image = preprocess_image(image_path)
    config = "--oem 1 --psm 3"  # 选择 OCR 引擎和页面分割模式
    text = pytesseract.image_to_string(image, lang=lang, config=config)
    return text


def remove_spaces_between_chinese(text):
    """去除中文字符之间的空格，保留英文单词之间的空格"""
    # 使用正则表达式匹配中文字符之间的空格并去除
    # 正则表达式解释：([\u4e00-\u9fff]) 匹配一个中文字符，\s+ 匹配一个或多个空格，(?=[\u4e00-\u9fff]) 确保空格后面也是中文字符
    cleaned_text = re.sub(r'([\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', r'\1', text)
    return cleaned_text


def pdf_to_text(pdf_path, output_folder, lang='chi_sim+eng'):
    """将 PDF 转换为文本，逐页处理并输出"""
    temp_folder = "temp_images"
    os.makedirs(output_folder, exist_ok=True)
    extract_images(pdf_path, temp_folder)

    image_files = sorted(os.listdir(temp_folder))  # 按文件名排序，确保顺序一致

    for img_file in image_files:
        img_path = os.path.join(temp_folder, img_file)
        if img_path.lower().endswith(('png', 'jpg', 'jpeg')):
            page_num = int(img_file.split("_")[0].replace("page", ""))  # 获取页码
            print(f"正在处理第 {page_num + 1} 页...")

            # OCR 识别
            text = ocr_image(img_path, lang)

            # 去除中文字符之间的空格
            text = remove_spaces_between_chinese(text)

            # 逐页保存结果
            page_txt_path = os.path.join(output_folder, f"page{page_num + 1}.txt")
            with open(page_txt_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"第 {page_num + 1} 页 OCR 处理完成，结果已保存至 {page_txt_path}")

    print("所有页面处理完成！")


if __name__ == "__main__":
    pdf_path = "input.pdf"  # 输入 PDF 文件路径
    output_folder = "output_text"  # 输出文本文件夹
    pdf_to_text(pdf_path, output_folder, lang='chi_sim+eng')  # 进行 OCR 识别