"""
Git仓库数据采集模块
"""
import os
import re
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Generator
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError


class GitCollector:
    """Git仓库采集器"""

    def __init__(self, repo_url: str, local_base: str = "./data/repos"):
        self.repo_url = repo_url
        self.is_local = os.path.exists(repo_url)

        if self.is_local:
            self.repo_name = os.path.basename(os.path.abspath(repo_url))
            self.local_path = repo_url
        else:
            self.repo_name = self._extract_repo_name(repo_url)
            self.local_path = os.path.join(local_base, self.repo_name)

        self.repo:  Optional[Repo] = None

    def _extract_repo_name(self, url: str) -> str:
        """从URL提取仓库名"""
        patterns = [
            r'github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$',
            r'gitee\.com[/:]([^/]+)/([^/]+?)(?:\.git)?$',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return f"{match.group(1)}_{match.group(2)}"
        raise ValueError(f"无效的仓库URL: {url}")

    def clone(self, force: bool = False) -> bool:
        """克隆或打开仓库"""
        if self.is_local:
            try:
                self.repo = Repo(self.local_path)
                return True
            except InvalidGitRepositoryError:
                return False

        if os.path.exists(self.local_path):
            if force:
                shutil.rmtree(self.local_path)
            else:
                try:
                    self.repo = Repo(self.local_path)
                    return True
                except:
                    shutil.rmtree(self. local_path)

        os.environ['GIT_HTTP_VERSION'] = 'HTTP/1.1'

        try:
            print(f"正在克隆 {self.repo_url}...")
            self.repo = Repo.clone_from(self. repo_url, self.local_path, depth=200)
            print("克隆完成!")
            return True
        except GitCommandError as e:
            print(f"克隆失败: {e}")
            return False

    def get_default_branch(self) -> str:
        """获取默认分支"""
        for branch in ['main', 'master']:
            try:
                self.repo.refs[branch]
                return branch
            except:
                continue
        return 'HEAD'

    def get_commits(self, max_count:  int = 100) -> Generator[Dict, None, None]:
        """获取提交历史"""
        if not self.repo:
            return

        branch = self.get_default_branch()
        try:
            commits = self.repo.iter_commits(branch, max_count=max_count)
        except:
            commits = self.repo.iter_commits('HEAD', max_count=max_count)

        for commit in commits:
            try:
                stats = commit.stats. total
            except:
                stats = {'files': 0, 'insertions': 0, 'deletions': 0}

            yield {
                'sha': commit.hexsha,
                'author': commit.author.name if commit.author else "Unknown",
                'email': commit.author.email if commit.author else "",
                'message': commit.message. strip()[:200],
                'date': datetime.fromtimestamp(commit. committed_date),
                'files_changed': stats.get('files', 0),
                'insertions':  stats.get('insertions', 0),
                'deletions':  stats.get('deletions', 0),
            }

    def get_python_files(self) -> List[str]:
        """获取所有Python文件"""
        if not self.repo:
            return []

        try:
            tree = self.repo.head.commit.tree
            files = []
            self._find_files(tree, '', files)
            return files
        except:
            return []

    def _find_files(self, tree, prefix: str, result: List[str]):
        """递归查找Python文件"""
        skip_dirs = {'__pycache__', 'venv', 'env', '.git', 'node_modules', '. tox', 'build', 'dist'}

        for item in tree:
            path = f"{prefix}/{item.name}" if prefix else item.name
            if item. type == 'tree':
                if item.name.lower() not in skip_dirs:
                    self._find_files(item, path, result)
            elif item.type == 'blob' and item.name.endswith('.py'):
                result.append(path)

    def get_current_file(self, file_path: str) -> Optional[str]:
        """获取当前版本的文件内容"""
        try:
            blob = self.repo.head.commit.tree / file_path
            return blob. data_stream.read().decode('utf-8', errors='ignore')
        except:
            return None

    def get_file_types_stats(self) -> Dict[str, int]:
        """统计文件类型"""
        if not self.repo:
            return {}

        stats = {}
        try:
            tree = self.repo.head.commit.tree
            self._count_file_types(tree, stats)
        except:
            pass
        return stats

    def _count_file_types(self, tree, stats:  Dict[str, int]):
        """递归统计文件类型"""
        skip_dirs = {'__pycache__', 'venv', 'env', '.git', 'node_modules'}

        for item in tree:
            if item.type == 'tree':
                if item.name.lower() not in skip_dirs:
                    self._count_file_types(item, stats)
            elif item.type == 'blob':
                ext = os.path.splitext(item. name)[1].lower() or '(无扩展名)'
                stats[ext] = stats.get(ext, 0) + 1
