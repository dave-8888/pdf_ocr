class PdfViewer:
    def __init__(self):
        self.resize_factor = 1  # pdf缩放比例
        self.current_page = 0  # 当前pdf页码
        self.pdf_path = None  # pdf文件路径
        self.doc = None  # 获取到的pdf文件

    class PageViewer:
        def __init__(self):
            self.page = None


pdf_viewer = PdfViewer()
page_viewer = pdf_viewer.PageViewer()
