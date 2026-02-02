# OSS代码分析工具

一个用于分析开源项目代码质量、贡献者统计和代码异味的工具。

##  功能特性

###  代码分析
- **代码统计**：自动分析Python文件的代码行数、函数数量、类数量
- **贡献者分析**：统计项目贡献者排名、提交次数、代码增删量
- **代码异味检测**：自动检测常见的代码质量问题

###  Web可视化界面
- **项目概览**：展示已分析的项目列表
- **详细统计**：查看每个项目的详细分析结果
- **交互式图表**：直观展示贡献者排名和代码统计

###  命令行工具
- **一键分析**：通过命令行快速分析GitHub仓库
- **批量处理**：支持批量分析多个仓库
- **数据导出**：支持将分析结果导出为JSON格式

##  安装

### 环境要求
- Python 3.8+
- Git

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/cklhn/OpenSourceWork
cd OpenSourceWork
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **初始化数据库**
```bash
python main.py init
```

##  快速开始

### 分析单个仓库
```bash
python main.py analyze https://github.com/username/repository
```

### 批量分析多个仓库
```bash
python main.py batch analyze.txt
```

### 启动Web界面
```bash
python main.py web
```
访问：http://127.0.0.1:5000

##  项目结构

```
OpenSourceWork/
├── src/                    # 源代码
│   ├── collector.py       # 数据收集器（Git操作）
│   ├── analyzer.py        # 代码分析器
│   ├── storage.py         # 数据存储（SQLite）
│   ├── visualizer.py      # 数据可视化
│   └── web_app.py         # Flask Web应用
├── templates/             # HTML模板
│   └── index.html         # 主界面
├── data/                  # 数据存储
│   ├── analysis.db       # SQLite数据库
│   └── repos/            # 克隆的仓库
├── tests/                 # 测试文件
├── requirements.txt       # Python依赖
├── main.py               # 主程序入口
└── README.md             # 说明文档
```

##  使用示例

### 示例1：分析Flask开源项目
```bash
python main.py analyze https://github.com/pallets/flask
```

### 示例2：查看分析结果
```bash
python main.py stats
```

### 示例3：导出分析数据
```bash
python main.py export output.json
```

##  分析指标

### 代码质量指标
- **代码行数**（LOC）：统计有效代码行数
- **圈复杂度**：函数复杂度分析
- **代码重复率**：检测重复代码片段
- **注释比例**：代码注释覆盖率

### 贡献者指标
- **提交次数**：每个贡献者的提交数量
- **代码增删**：新增和删除的代码行数
- **活跃度**：贡献时间分布

### 代码异味
- **过长函数**：函数行数超过阈值
- **过大类**：类行数过多
- **重复代码**：相似的代码片段
- **复杂表达式**：嵌套过深的逻辑

##  API接口

### REST API端点
- `GET /api/projects` - 获取所有项目列表
- `GET /api/project/<id>` - 获取项目详情
- `GET /api/project/<id>/contributors` - 获取贡献者统计
- `GET /api/project/<id>/files` - 获取文件统计
- `GET /api/project/<id>/commits` - 获取提交记录

### 示例响应
```json
{
  "project": {
    "id": 1,
    "name": "flask",
    "url": "https://github.com/pallets/flask",
    "total_files": 45,
    "total_loc": 12560,
    "total_functions": 320,
    "total_classes": 25
  },
  "contributors": [
    {
      "author": "user1",
      "commits": 120,
      "additions": 4500,
      "deletions": 1200
    }
  ]
}
```

##  致谢

- 感谢所有开源项目的贡献者
- 使用了以下开源库：
  - Flask - Web框架
  - SQLAlchemy - 数据库ORM
  - GitPython - Git操作库
- 对以下开源库进行了OSS代码分析
   - https://github.com/pallets/flask
   - [https://gitee.com/mirrors/flask](https://gitee.com/mirrors/flask)(gitee镜像版)
