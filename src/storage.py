"""
SQLite数据存储模块
"""
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager


class Database:
    """数据库管理"""

    def __init__(self, db_path: str = "data/analysis.db"):
        self.db_path = db_path

    @contextmanager
    def get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_tables(self):
        """初始化表"""
        with self.get_conn() as conn:
            cursor = conn.cursor()

            # 项目表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    total_files INTEGER DEFAULT 0,
                    total_loc INTEGER DEFAULT 0,
                    total_functions INTEGER DEFAULT 0,
                    total_classes INTEGER DEFAULT 0,
                    total_smells INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # 提交表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS commits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    sha TEXT NOT NULL,
                    author TEXT,
                    email TEXT,
                    message TEXT,
                    committed_at TIMESTAMP,
                    files_changed INTEGER DEFAULT 0,
                    insertions INTEGER DEFAULT 0,
                    deletions INTEGER DEFAULT 0,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            ''')
