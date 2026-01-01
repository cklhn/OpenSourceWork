"""
OSS代码分析工具 - 主程序
"""
import argparse
import os
from datetime import datetime

from src.collector import GitCollector
from src.analyzer import CodeAnalyzer
from src.storage import Database


def analyze_repository(repo_url: str, max_commits: int = 100):
    """分析仓库"""
    print(f"{'='*50}")
    print(f"OSS代码分析工具")
    print(f"{'='*50}")
    print(f"仓库:  {repo_url}")
    print(f"分析提交数: {max_commits}\n")

    # 初始化
    db = Database("data/analysis.db")
    db.init_tables()

    collector = GitCollector(repo_url, "data/repos")
    if not collector.clone():
        print("仓库克隆/打开失败!")
        return

    # 保存项目
    project_id = db.save_project(collector.repo_name, repo_url)
    print(f"项目ID: {project_id}\n")

    # 获取提交
    print("正在获取提交历史...")
    commits = list(collector.get_commits(max_count=max_commits))
    print(f"获取到 {len(commits)} 个提交\n")

    # 保存提交信息
    print("正在保存提交信息...")
    for commit in commits:
        db.save_commit(project_id, commit)
    print(f"已保存 {len(commits)} 个提交\n")

    # 分析当前代码
    print("正在分析当前代码...")
    python_files = collector.get_python_files()
    print(f"找到 {len(python_files)} 个Python文件\n")

    total_loc = 0
    total_functions = 0
    total_classes = 0
    all_smells = []

    for file_path in python_files:
        content = collector.get_current_file(file_path)
        if content:
            analyzer = CodeAnalyzer(content, file_path)
            metrics = analyzer.analyze()
            if metrics:
                db.save_file_stats(project_id, metrics)
                total_loc += metrics. loc
                total_functions += metrics.functions_count
                total_classes += metrics. classes_count
                all_smells.extend(metrics.code_smells)

    # 保存项目统计
    db.save_project_stats(project_id, {
        'total_files': len(python_files),
        'total_loc': total_loc,
        'total_functions': total_functions,
        'total_classes': total_classes,
        'total_smells': len(all_smells)
    })