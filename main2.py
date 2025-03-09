import fitz  # PyMuPDF
import tkinter as tk
from PIL import Image, ImageTk

# 加载 PDF 文档
doc = fitz.open("input.pdf")
current_page = 0  # 当前页索引

def update_image():
    """更新显示的 PDF 页面"""
    global tk_img, label, page_label
    page = doc[current_page]
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    tk_img = ImageTk.PhotoImage(img)
    label.config(image=tk_img)
    page_label.config(text=f"{current_page + 1} / {len(doc)}")

def next_page(event=None):
    """显示下一页"""
    global current_page
    if current_page < len(doc) - 1:
        current_page += 1
        update_image()

def prev_page(event=None):
    """显示上一页"""
    global current_page
    if current_page > 0:
        current_page -= 1
        update_image()

def go_to_page(event=None):
    """跳转到指定页码"""
    global current_page
    try:
        page_num = int(entry_page.get()) - 1  # 用户输入的是从 1 开始的页码
        if 0 <= page_num < len(doc):
            current_page = page_num
            update_image()
    except ValueError:
        pass  # 处理无效输入

if __name__ == "__main__":
    # 创建 Tkinter 窗口
    root = tk.Tk()
    root.title("PDF Viewer")

    # 绑定键盘事件
    root.bind("<Right>", next_page)  # 右箭头翻到下一页
    root.bind("<Left>", prev_page)   # 左箭头翻到上一页

    # 显示第一页
    label = tk.Label(root)
    label.pack()

    # 页码显示
    page_label = tk.Label(root, text="")  # 先创建空文本
    page_label.pack()

    # 控件容器
    nav_frame = tk.Frame(root)
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

    # 先初始化界面，再更新页面内容
    update_image()

    # 运行主循环
    root.mainloop()