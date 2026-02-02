"""
Python代码分析模块
"""
import ast
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class FunctionInfo:
    """函数信息"""
    name: str
    line_start: int
    line_count: int
    params_count: int
    complexity: int
