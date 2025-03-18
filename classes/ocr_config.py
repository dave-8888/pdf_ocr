import tkinter as tk


class OcrConfig:
    def __init__(self):
        self.oem = 1  # OCR 引擎模式
        self.psm = 3  # 页面分割模式


ocr_cf = OcrConfig()
