import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import pytesseract
import re

# 加载 PDF 文档
doc = None
current_page = 0  # 当前页索引
resize_factor = 0.5  # 缩放比例


def load_pdf():
    """加载 PDF 文件"""
    global doc, current_page
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if file_path:
        doc = fitz.open(file_path)
        current_page = 0
        update_image()


def update_image():
    """更新显示的 PDF 页面"""
    global tk_img, label, page_label, doc, resize_factor
    if doc is None:
        return
    page = doc[current_page]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    # 进行缩放
    new_width = int(img.width * resize_factor)
    new_height = int(img.height * resize_factor)
    img = img.resize((new_width, new_height), Image.LANCZOS)

    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    page_label.config(text=f"{current_page + 1} / {len(doc)}")


def next_page(event=None):
    """显示下一页"""
    global current_page
    if doc and current_page < len(doc) - 1:
        current_page += 1
        update_image()


def prev_page(event=None):
    """显示上一页"""
    global current_page
    if doc and current_page > 0:
        current_page -= 1
        update_image()


def go_to_page(event=None):
    """跳转到指定页码"""
    global current_page
    try:
        page_num = int(entry_page.get()) - 1  # 用户输入的是从 1 开始的页码
        if doc and 0 <= page_num < len(doc):
            current_page = page_num
            update_image()
    except ValueError:
        pass  # 处理无效输入


def zoom_in():
    """放大 PDF 页面"""
    global resize_factor
    resize_factor *= 1.2
    update_image()


def zoom_out():
    """缩小 PDF 页面"""
    global resize_factor
    resize_factor /= 1.2
    update_image()


def preprocess_image(image):
    """预处理图片，提高 OCR 识别效果"""
    image = image.convert("L")  # 转灰度
    image = image.filter(ImageFilter.MedianFilter())  # 降噪
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # 提高对比度
    image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)  # 放大 2 倍
    return image


def ocr_current_page():
    """对当前 PDF 页面进行 OCR 识别，并显示在右侧文本框中"""
    global current_page, text_box, doc
    if doc is None:
        return
    # 清空文本框并显示状态信息
    text_box.delete(1.0, tk.END)
    status_label.config(text="正在识别，请稍候...")
    root.update_idletasks()
    page = doc[current_page]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img = preprocess_image(img)

    # OCR 识别
    config = "--oem 1 --psm 3"
    text = pytesseract.image_to_string(img, lang='chi_sim+eng', config=config)
    text = re.sub(r'([\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', r'\1', text)  # 去除中文字符间的空格

    # 在文本框中显示结果
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, text)
    # 更新状态
    status_label.config(text="OCR 识别完成！")


if __name__ == "__main__":
    # 创建 Tkinter 窗口
    root = tk.Tk()
    root.title("PDF Viewer")

    # 顶部按钮栏
    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, pady=5)

    btn_zoom_in = tk.Button(top_frame, text="放大", command=zoom_in)
    btn_zoom_in.pack(side=tk.LEFT, padx=5)

    btn_zoom_out = tk.Button(top_frame, text="缩小", command=zoom_out)
    btn_zoom_out.pack(side=tk.LEFT, padx=5)

    btn_load = tk.Button(top_frame, text="导入 PDF", command=load_pdf)
    btn_load.pack(side=tk.LEFT, padx=5)

    # 状态显示标签
    status_label = tk.Label(top_frame, text="", fg="blue")
    status_label.pack(side=tk.LEFT, padx=10)
    # 创建主框架
    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.LEFT, padx=10, pady=10)

    # 显示 PDF 的 Label
    label = tk.Label(main_frame)
    label.pack()

    # 页码显示
    page_label = tk.Label(main_frame, text="")  # 先创建空文本
    page_label.pack()

    # 控件容器
    nav_frame = tk.Frame(main_frame)
    nav_frame.pack(pady=10)

    # 上一页按钮
    btn_prev = tk.Button(nav_frame, text="上一页", command=prev_page)
    btn_prev.pack(side=tk.LEFT, padx=10)

    # 输入框和跳转按钮
    entry_page = tk.Entry(nav_frame, width=5)
    entry_page.pack(side=tk.LEFT, padx=5)
    entry_page.bind("<Return>", go_to_page)  # 绑定回车键
    btn_go = tk.Button(nav_frame, text="跳转", command=go_to_page)
    btn_go.pack(side=tk.LEFT, padx=5)

    # 下一页按钮
    btn_next = tk.Button(nav_frame, text="下一页", command=next_page)
    btn_next.pack(side=tk.LEFT, padx=10)

    # OCR 按钮
    btn_ocr = tk.Button(nav_frame, text="识别页面", command=ocr_current_page)
    btn_ocr.pack(side=tk.LEFT, padx=10)

    # 右侧文本框
    text_frame = tk.Frame(root)
    text_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
    text_box = tk.Text(text_frame, wrap=tk.WORD, width=50, height=30)
    text_box.pack(fill=tk.BOTH, expand=True)

    # 运行主循环
    root.mainloop()