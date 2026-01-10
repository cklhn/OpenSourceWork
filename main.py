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
      # 输出结果
    print(f"{'='*50}")
    print("分析结果")
    print(f"{'='*50}")
    print(f"Python文件数: {len(python_files)}")
    print(f"总代码行数:  {total_loc}")
    print(f"函数总数: {total_functions}")
    print(f"类总数: {total_classes}")
    print(f"代码异味数: {len(all_smells)}")

    if all_smells:
        print(f"\n代码异味详情 (前10个):")
        for smell in all_smells[:10]:
            print(f"  - {smell}")

    # 贡献者统计
    contributors = db.get_contributor_stats(project_id)
    print(f"\n贡献者排名 (前5名):")
    for i, c in enumerate(contributors[:5], 1):
        print(f"  {i}. {c['author']}: {c['commits']} 次提交")

    print(f"\n{'='*50}")
    print("分析完成!  运行 'python main.py web' 查看Web界面")
    print(f"{'='*50}")

    db.close()


def run_web(port: int = 5000):
    """启动Web"""
    from src.web_app import create_app
    app = create_app("data/analysis.db")
    print(f"启动Web:  http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)


def clear_data():
    """清除数据"""
    if os.path.exists("data/analysis.db"):
        os.remove("data/analysis.db")
        print("已清除数据库")
    print("完成!")


def main():
    parser = argparse.ArgumentParser(description="OSS代码分析工具")
    subparsers = parser.add_subparsers(dest="command")

    # analyze命令
    p1 = subparsers. add_parser("analyze", help="分析仓库")
    p1.add_argument("repo_url", help="仓库URL或本地路径")
    p1.add_argument("-n", "--max-commits", type=int, default=100, help="最大提交数")

    # web命令
    p2 = subparsers. add_parser("web", help="启动Web界面")
    p2.add_argument("-p", "--port", type=int, default=5000, help="端口号")

    # clear命令
    subparsers.add_parser("clear", help="清除数据")

    args = parser.parse_args()
    os.makedirs("data/repos", exist_ok=True)

    if args.command == "analyze":
        analyze_repository(args.repo_url, args. max_commits)
    elif args.command == "web":
        run_web(args.port)
    elif args.command == "clear":
        clear_data()
    else:
        parser. print_help()


if __name__ == "__main__":
    main()