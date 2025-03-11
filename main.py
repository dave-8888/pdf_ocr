import sqlite3

import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog, ttk, font
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import pytesseract
import re

# 加载 PDF 文档
doc = None
current_page = 0  # 当前页索引
resize_factor = 1  # 缩放比例


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
    global page_label, doc, resize_factor
    if doc is None:
        return
    page = doc[current_page]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    # 计算窗口高度的 80%
    window_height = root.winfo_height()  # 获取窗口当前高度
    display_height = int(window_height * 0.85)  # 计算 PDF 显示区域的目标高度
    aspect_ratio = img.width / img.height  # 计算宽高比例
    # 按比例调整宽度
    display_width = int(display_height * aspect_ratio)
    # 进行缩放
    new_width = int(display_width * resize_factor)
    new_height = int(display_height * resize_factor)
    window_width = root.winfo_width()
    paned_w_width = new_width + 10
    if paned_w_width > window_width / 2:
        paned_w_width = int(window_width / 2)
    paned_window.sash_place(0, paned_w_width, 0)  # 调整分隔线位置，使两侧更均匀
    img = img.resize((new_width, new_height))
    photo = ImageTk.PhotoImage(img)
    canvas.delete("all")
    # 更新 Canvas 大小
    canvas.create_image(0, 0, anchor="nw", image=photo)
    canvas.image = photo
    canvas.config(scrollregion=canvas.bbox("all"))
    page_label.config(text=f"{current_page + 1} / {len(doc)}")
    load_text_from_database()


def next_page(event=None):
    """显示下一页"""
    if root.focus_get() not in [entry_page, text_box]:  # 仅在非输入框时生效
        global current_page
        if doc and current_page < len(doc) - 1:
            current_page += 1
            update_image()


def prev_page(event=None):
    """显示上一页"""
    if root.focus_get() not in [entry_page, text_box]:  # 仅在非输入框时生效
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
    resize_factor *= 1.1
    update_image()


def zoom_out():
    """缩小 PDF 页面"""
    global resize_factor
    resize_factor /= 1.1
    update_image()


def preprocess_image(image):
    """预处理图片，提高 OCR 识别效果"""
    image = image.convert("L")  # 转灰度
    image = image.filter(ImageFilter.MedianFilter())  # 降噪
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0)  # 提高对比度
    image = image.resize((image.width * 2, image.height * 2))  # 放大 2 倍
    return image


def ocr_current_page():
    """对当前 PDF 页面进行 OCR 识别，并显示在右侧文本框中"""
    global current_page, text_box, doc
    if doc is None:
        return
    # 清空文本框并显示状态信息
    text_box.delete(1.0, tk.END)
    status_label.config(text="正在识别，请稍候...",fg="blue")
    root.update_idletasks()
    page = doc[current_page]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img = preprocess_image(img)

    # OCR 识别
    config = "--oem 3 --psm 3"
    text = pytesseract.image_to_string(img, lang='chi_sim+eng', config=config)
    text = re.sub(r'([\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', r'\1', text)  # 去除中文字符间的空格

    # 在文本框中显示结果
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, text)
    # 更新状态
    status_label.config(text="OCR 识别完成！" ,fg="blue")


def change_font(event=None):
    """修改文本框的字体大小"""
    try:
        new_font = font_var.get()  # 获取选择的字体
        new_size = int(font_size_entry.get())  # 获取输入框中的字体大小
        text_box.config(font=(new_font, new_size))  # 设置新的字体大小
    except ValueError:
        status_label.config(text="请输入有效的数字", fg="red")  # 错误提示


def focus_canvas(event):
    canvas.focus_set()  # 让 canvas 获取焦点


def save_to_database():
    """将 OCR 识别的文本保存到 SQLite 数据库"""
    global doc
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        status_label.config(text="没有可保存的文本！", fg="red")
        return
    try:
        conn = sqlite3.connect("ocr_results.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocr_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT,
                page INTEGER,
                text TEXT,
                UNIQUE(filename, page)  -- 确保 filename 和 page 组合是唯一的
            )
        """)
        filename = doc.name if doc else "Unknown"
        cursor.execute("""
            INSERT INTO ocr_data (filename, page, text)
            VALUES (?, ?, ?)
            ON CONFLICT(filename, page) DO UPDATE SET text = excluded.text
        """, (filename, current_page + 1, text))
        conn.commit()
        conn.close()
        status_label.config(text="OCR 结果已保存或更新！", fg="green")
    except Exception as e:
        status_label.config(text=f"保存失败: {e}", fg="red")
def load_text_from_database():
    """根据当前文件名和页码，从数据库中加载 OCR 识别的文本并显示"""
    global doc, text_box, current_page
    if doc is None:
        return
    try:
        conn = sqlite3.connect("ocr_results.db")
        cursor = conn.cursor()
        filename = doc.name if doc else "Unknown"
        cursor.execute("SELECT text FROM ocr_data WHERE filename = ? AND page = ?", (filename, current_page + 1))
        result = cursor.fetchone()
        conn.close()
        text_box.delete(1.0, tk.END)  # 清空文本框
        if result:
            text_box.insert(tk.END, result[0])  # 显示查询到的文本
            status_label.config(text="已加载 OCR 结果", fg="blue")
        else:
            status_label.config(text="无 OCR 结果", fg="red")
    except Exception as e:
        status_label.config(text=f"查询失败: {e}", fg="red")


def show_menu(event):
    menu.post(event.x_root, event.y_root)  # 在鼠标点击处弹出菜单


if __name__ == "__main__":
    # 创建 Tkinter 窗口
    root = tk.Tk()
    root.title("pdf 识别")
    root.geometry("1000x800")  # 设置窗口默认大小
    # 创建自定义菜单栏
    menu_frame = tk.Frame(root, height=12)  # 这里可以控制高度
    menu_frame.pack(fill="x")

    # 创建菜单按钮（点击后弹出菜单）
    menu_label = tk.Label(menu_frame, text="文件", padx=5, pady=5,bg="lightgray")
    menu_label.pack(side="left")
    menu_label.bind("<Button-1>", show_menu)  # 绑定鼠标左键点击事件

    # 创建弹出菜单
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="导入 PDF", command=load_pdf)

    # 顶部按钮栏
    top_frame = tk.Frame(root)
    top_frame.pack(fill=tk.X, pady=5)

    btn_zoom_in = tk.Button(top_frame, text="放大", command=zoom_in)
    btn_zoom_in.pack(side=tk.LEFT, padx=5)

    btn_zoom_out = tk.Button(top_frame, text="缩小", command=zoom_out)
    btn_zoom_out.pack(side=tk.LEFT, padx=5)

    # 状态显示标签
    status_label = tk.Label(top_frame, text="", fg="blue")
    status_label.pack(side=tk.LEFT, padx=10)
    # 创建一个可调节的 PanedWindow
    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    paned_window.pack(fill=tk.BOTH, expand=True)
    paned_window.configure(sashrelief=tk.RIDGE, sashwidth=0)
    # 创建主框架（左侧 PDF 显示区域）
    main_frame = tk.Frame(paned_window, bg="lightgray")
    paned_window.add(main_frame, stretch="always")
    # 创建 Canvas 用于显示 PDF
    canvas = tk.Canvas(main_frame, bg="white")
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.bind("<Button-1>", focus_canvas)

    # 滚动条
    v_scroll = tk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
    v_scroll.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
    canvas.config(yscrollcommand=v_scroll.set)

    h_scroll = tk.Scrollbar(canvas, orient=tk.HORIZONTAL, command=canvas.xview)
    h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    canvas.config(xscrollcommand=h_scroll.set)

    # 页码显示
    page_label = tk.Label(canvas, text="")  # 先创建空文本
    page_label.pack(side=tk.BOTTOM)

    # 控件容器
    nav_frame = tk.Frame(main_frame)
    # 让按钮栏固定在 main_frame 底部
    nav_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, anchor="s")

    # 上一页按钮
    btn_prev = tk.Button(nav_frame, text="上一页", command=prev_page)
    btn_prev.pack(side=tk.LEFT, padx=10)
    root.bind("<Left>", prev_page)  # 绑定左箭头键

    # 输入框和跳转按钮
    entry_page = tk.Entry(nav_frame, width=5)
    entry_page.pack(side=tk.LEFT, padx=5)
    entry_page.bind("<Return>", go_to_page)  # 绑定回车键
    btn_go = tk.Button(nav_frame, text="跳转", command=go_to_page)
    btn_go.pack(side=tk.LEFT, padx=5)

    # 下一页按钮
    btn_next = tk.Button(nav_frame, text="下一页", command=next_page)
    btn_next.pack(side=tk.LEFT, padx=10)
    root.bind("<Right>", next_page)  # 绑定右箭头键

    # OCR 按钮
    btn_ocr = tk.Button(nav_frame, text="识别页面", command=ocr_current_page)
    btn_ocr.pack(side=tk.LEFT, padx=10)
    root.bind("<Control-Return>", lambda event: ocr_current_page())
    # 创建右侧文本框
    text_frame = tk.Frame(paned_window, bg="lightblue")
    paned_window.add(text_frame, stretch="always")

    # 默认字体
    default_font = "微软雅黑"
    text_font = (default_font, 12)  # 初始字体大小 12
    text_box = tk.Text(text_frame, wrap=tk.WORD, width=50, height=30, font=text_font)
    text_box.configure(bg="#F5F5D5", fg="blue")
    text_box.pack(fill=tk.BOTH, expand=True)

    # 控制字体大小的输入框和按钮
    font_control_frame = tk.Frame(text_frame)
    font_control_frame.pack(fill=tk.X, pady=5)

    tk.Label(font_control_frame, text="字体:").pack(side=tk.LEFT, padx=5)

    font_var = tk.StringVar(value=default_font)
    font_options = ["宋体", "黑体", "楷体", "微软雅黑", "仿宋", "Arial", "Times New Roman", "Courier", "Verdana"]
    font_dropdown = ttk.Combobox(font_control_frame, textvariable=font_var, values=font_options, state="readonly")
    font_dropdown.pack(side=tk.LEFT, padx=5)
    font_dropdown.bind("<<ComboboxSelected>>", change_font)

    tk.Label(font_control_frame, text="大小:").pack(side=tk.LEFT, padx=5)

    font_size_entry = tk.Entry(font_control_frame, width=5)
    font_size_entry.pack(side=tk.LEFT, padx=5)
    font_size_entry.insert(0, "12")  # 默认字体大小 12
    font_size_entry.bind("<Return>", change_font)  # 绑定回车键

    btn_set_font = tk.Button(font_control_frame, text="设置", command=change_font)
    btn_set_font.pack(side=tk.LEFT, padx=5)
    # 在文本框下方添加保存按钮
    btn_save = tk.Button(font_control_frame, text="保存文本", command=save_to_database)
    btn_save.pack(side=tk.LEFT,padx=5,pady=5)
    # 绑定 Ctrl + S 快捷键到保存功能
    root.bind("<Control-s>", lambda event: save_to_database())
    # 让 PanedWindow 在初始时平均分配宽度
    root.update_idletasks()  # 确保 UI 元素已经初始化
    # 运行主循环
    root.mainloop()
