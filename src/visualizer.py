"""
数据可视化模块
"""
import os
from typing import List, Dict
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """可视化生成器"""

    def __init__(self, db):
        self.db = db

    def plot_complexity_trend(self, project_id: int, save_path: str):
        """绘制复杂度变化趋势图"""
        data = self.db.get_complexity_trend(project_id)
        if not data:
            print("无复杂度数据")
            return

        df = pd.DataFrame(data)
        df['committed_at'] = pd.to_datetime(df['committed_at'])

        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(df['committed_at'], df['avg_complexity'],
                'b-o', label='平均复杂度', markersize=4)
        ax.plot(df['committed_at'], df['max_complexity'],
                'r-s', label='最大复杂度', markersize=4)

        ax.set_xlabel('日期')
        ax.set_ylabel('圈复杂度')
        ax.set_title('代码复杂度演化趋势')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 添加阈值线
        ax.axhline(y=10, color='orange', linestyle='--', label='复杂度阈值(10)')

        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"复杂度趋势图已保存:  {save_path}")

    def plot_code_growth(self, project_id: int, save_path: str):
        """绘制代码增长趋势图"""
        data = self.db.get_code_growth(project_id)
        if not data:
            print("无代码增长数据")
            return

        df = pd.DataFrame(data)
        df['committed_at'] = pd.to_datetime(df['committed_at'])

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

        # 代码行数
        ax1.fill_between(df['committed_at'], df['total_loc'], alpha=0.3, label='总行数')
        ax1.fill_between(df['committed_at'], df['total_sloc'], alpha=0.5, label='有效代码行')
        ax1.plot(df['committed_at'], df['total_loc'], 'b-', linewidth=2)
        ax1.plot(df['committed_at'], df['total_sloc'], 'g-', linewidth=2)
        ax1.set_xlabel('日期')
        ax1.set_ylabel('代码行数')
        ax1.set_title('代码规模增长趋势')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 函数数量
        ax2.plot(df['committed_at'], df['total_functions'], 'purple',
                 linewidth=2, marker='o', markersize=4)
        ax2.fill_between(df['committed_at'], df['total_functions'], alpha=0.3, color='purple')
        ax2.set_xlabel('日期')
        ax2.set_ylabel('函数数量')
        ax2.set_title('函数数量增长趋势')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"代码增长图已保存: {save_path}")

    def plot_contributor_stats(self, project_id: int, save_path: str):
        """绘制贡献者统计图"""
        data = self.db.get_contributor_stats(project_id)
        if not data:
            print("无贡献者数据")
            return

        df = pd.DataFrame(data)

        # 只显示前10名贡献者
        df = df.head(10)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 提交次数柱状图
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(df)))
        bars = ax1.barh(df['author'], df['commits'], color=colors)
        ax1.set_xlabel('提交次数')
        ax1.set_title('贡献者提交次数排名 (Top 10)')
        ax1.invert_yaxis()

        # 在柱状图上显示数值
        for bar, val in zip(bars, df['commits']):
            ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                     f'{val}', va='center', fontsize=9)

        # 代码增删饼图（所有贡献者总计）
        total_additions = df['additions'].sum()
        total_deletions = df['deletions'].sum()

        if total_additions + total_deletions > 0:
            sizes = [total_additions, total_deletions]
            labels = [f'新增 ({total_additions: ,})', f'删除 ({total_deletions:,})']
            colors = ['#4CAF50', '#f44336']
            ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                    startangle=90, explode=(0.05, 0))
            ax2.set_title('代码变更统计')

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"贡献者统计图已保存: {save_path}")

    def plot_code_smells(self, project_id: int, save_path: str):
        """绘制代码异味分布图"""
        smells = self.db.get_code_smells_summary(project_id)
        if not smells:
            print("无代码异味数据")
            return

        fig, ax = plt.subplots(figsize=(10, 6))

        labels = list(smells.keys())
        values = list(smells.values())

        colors = plt.cm.Reds(pd.np.linspace(0.3, 0.8, len(labels)))
        bars = ax.bar(labels, values, color=colors)

        ax.set_xlabel('异味类型')
        ax.set_ylabel('出现次数')
        ax.set_title('代码异味分布')
        plt.xticks(rotation=45, ha='right')

        # 添加数值标签
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    str(val), ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        plt.savefig(save_path, dpi=150)
        plt.close()
        print(f"代码异味分布图已保存: {save_path}")

    def generate_report(self, project_id: int, output_dir: str = "data"):
        """生成完整报告"""
        os.makedirs(output_dir, exist_ok=True)

        project = self.db.get_project(project_id)
        if not project:
            print(f"项目 {project_id} 不存在")
            return

        print(f"\n=== 生成项目报告:  {project['name']} ===\n")

        self.plot_complexity_trend(project_id, f"{output_dir}/complexity_trend.png")
        self.plot_code_growth(project_id, f"{output_dir}/code_growth.png")
        self.plot_contributor_stats(project_id, f"{output_dir}/contributors.png")
        self.plot_code_smells(project_id, f"{output_dir}/code_smells.png")

        print(f"\n报告生成完成，保存在 {output_dir}/ 目录")
