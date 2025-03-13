class PdfViewer:
    def __init__(self):
        self.resize_factor = 1   # pdf缩放比例
        self.current_page = 0  # 当前pdf页码

    class PageViewer:
        def __init__(self):
            self.page = None
            self.rotation_angle = 0


pdf_viewer = PdfViewer()
page_viewer = pdf_viewer.PageViewer()
