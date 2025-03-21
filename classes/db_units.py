import sqlite3
import os
import json
import shutil
import traceback
import fitz  # PyMuPDF

from classes.components import components
from classes.pdf_viewer import pdf_viewer
from main import update_image

DB_FILE = "sources/ocr_results.db"


def init_db():
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pdf_state (
            pdf_path TEXT PRIMARY KEY,
            current_page INTEGER
        )
    ''')
    conn.commit()
    conn.close()


def save_state(pdf_path, current_page):
    """将 PDF 状态保存到数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO pdf_state (pdf_path, current_page)
        VALUES (?, ?)
        ON CONFLICT(pdf_path) DO UPDATE SET current_page=excluded.current_page
    ''', (pdf_path, current_page))
    conn.commit()
    conn.close()


def load_state(pdf_path):
    """从数据库中恢复 PDF 的上次阅读状态"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT current_page FROM pdf_state WHERE pdf_path=?', (pdf_path,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0  # 默认返回第 0 页


init_db()  # 初始化表
