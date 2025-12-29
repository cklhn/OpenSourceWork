"""
单元测试
运行:  pytest tests/test_Database.py -v
"""
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.storage import Database

class TestDatabase:
    """数据库测试"""

    @pytest.fixture
    def db(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            path = f.name
        db = Database(path)
        db.init_tables()
        yield db
        os.unlink(path)

    def test_save_project(self, db):
        pid = db.save_project("test", "https://github.com/test/test")
        assert pid > 0

        project = db.get_project(pid)
        assert project['name'] == "test"

    def test_save_commit(self, db):
        from datetime import datetime
        pid = db.save_project("test", "https://github.com/test/test")

        db.save_commit(pid, {
            'sha': 'abc123',
            'author': 'Test',
            'email': 'test@test.com',
            'message':  'Test commit',
            'date': datetime.now(),
            'files_changed': 1,
            'insertions': 10,
            'deletions': 5
        })

        commits = db.get_commits(pid)
        assert len(commits) == 1
        assert commits[0]['author'] == 'Test'

    def test_contributor_stats(self, db):
        from datetime import datetime
        pid = db.save_project("test", "https://github.com/test/test")

        for i in range(5):
            db.save_commit(pid, {
                'sha': f'sha{i}',
                'author': 'Alice' if i < 3 else 'Bob',
                'email': 'test@test.com',
                'message': f'Commit {i}',
                'date': datetime.now(),
                'files_changed': 1,
                'insertions':  10,
                'deletions': 5
            })

        stats = db.get_contributor_stats(pid)
        assert len(stats) == 2
        assert stats[0]['author'] == 'Alice'
        assert stats[0]['commits'] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])