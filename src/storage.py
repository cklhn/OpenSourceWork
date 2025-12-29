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

            # 文件统计表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    loc INTEGER DEFAULT 0,
                    sloc INTEGER DEFAULT 0,
                    functions_count INTEGER DEFAULT 0,
                    classes_count INTEGER DEFAULT 0,
                    imports_count INTEGER DEFAULT 0,
                    code_smells TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects(id)
                )
            ''')

    def save_project(self, name: str, url: str) -> int:
        """保存项目"""
        with self. get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM projects WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                # 清除旧数据
                cursor. execute("DELETE FROM commits WHERE project_id = ?", (row['id'],))
                cursor.execute("DELETE FROM file_stats WHERE project_id = ?", (row['id'],))
                return row['id']
            cursor.execute("INSERT INTO projects (name, url) VALUES (?, ?)", (name, url))
            return cursor.lastrowid

    def save_commit(self, project_id: int, commit:  Dict):
        """保存提交"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO commits (project_id, sha, author, email, message,
                                    committed_at, files_changed, insertions, deletions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id, commit['sha'], commit['author'], commit['email'],
                commit['message'], commit['date']. isoformat(),
                commit['files_changed'], commit['insertions'], commit['deletions']
            ))

    def save_file_stats(self, project_id: int, metrics):
        """保存文件统计"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            data = metrics.to_dict()
            cursor.execute('''
                INSERT INTO file_stats (project_id, file_path, loc, sloc,
                                       functions_count, classes_count, imports_count, code_smells)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id, data['file_path'], data['loc'], data['sloc'],
                data['functions_count'], data['classes_count'],
                data['imports_count'], data['code_smells']
            ))

    def save_project_stats(self, project_id: int, stats:  Dict):
        """保存项目统计"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE projects SET 
                    total_files = ?, total_loc = ?, total_functions = ?,
                    total_classes = ?, total_smells = ? 
                WHERE id = ?
            ''', (
                stats['total_files'], stats['total_loc'], stats['total_functions'],
                stats['total_classes'], stats['total_smells'], project_id
            ))

    def get_all_projects(self) -> List[Dict]:
        """获取所有项目"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def get_project(self, project_id:  int) -> Optional[Dict]:
        """获取项目详情"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_commits(self, project_id: int, limit: int = 100) -> List[Dict]:
        """获取提交列表"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM commits WHERE project_id = ? 
                ORDER BY committed_at DESC LIMIT ?
            ''', (project_id, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_contributor_stats(self, project_id: int) -> List[Dict]:
        """获取贡献者统计"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT author, COUNT(*) as commits,
                       SUM(insertions) as additions, 
                       SUM(deletions) as deletions
                FROM commits WHERE project_id = ? 
                GROUP BY author ORDER BY commits DESC
            ''', (project_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_file_stats(self, project_id: int) -> List[Dict]:
        """获取文件统计"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM file_stats WHERE project_id = ?
                ORDER BY loc DESC
            ''', (project_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_code_smells(self, project_id: int) -> List[str]:
        """获取所有代码异味"""
        with self.get_conn() as conn:
            cursor = conn. cursor()
            cursor.execute('''
                SELECT code_smells FROM file_stats 
                WHERE project_id = ?  AND code_smells != ''
            ''', (project_id,))

            smells = []
            for row in cursor.fetchall():
                if row['code_smells']:
                    smells.extend(row['code_smells']. split(','))
            return smells

    def get_commit_activity(self, project_id: int) -> Dict[str, int]:
        """获取提交活动统计(按日期)"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DATE(committed_at) as date, COUNT(*) as count
                FROM commits WHERE project_id = ? 
                GROUP BY DATE(committed_at)
                ORDER BY date DESC LIMIT 30
            ''', (project_id,))
            return {row['date']: row['count'] for row in cursor.fetchall()}

    def close(self):
        pass
