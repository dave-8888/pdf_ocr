from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
import os


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
    cleaned_text = re.sub(r'([\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', r'\1', text)
    return cleaned_text


def image_to_text(image_path, output_folder, lang='chi_sim+eng'):
    """处理单张图片并输出文本"""
    os.makedirs(output_folder, exist_ok=True)

    print(f"正在处理图片: {image_path}...")

    # OCR 识别
    text = ocr_image(image_path, lang)

    # 去除中文字符之间的空格
    text = remove_spaces_between_chinese(text)

    # 保存结果
    output_txt_path = os.path.join(output_folder, os.path.splitext(os.path.basename(image_path))[0] + ".txt")
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"OCR 处理完成，结果已保存至 {output_txt_path}")


if __name__ == "__main__":
    image_path = "input.jpeg"  # 输入图片文件路径
    output_folder = "output_text"  # 输出文本文件夹
    image_to_text(image_path, output_folder, lang='chi_sim+eng')  # 进行 OCR 识别