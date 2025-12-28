"""
基于Z3的代码检查模块
检测潜在的除零、越界等问题
"""
import ast
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

try:
    from z3 import Solver, Int, And, Or, Not, sat, unsat

    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False


@dataclass
class CodeIssue:
    """代码问题"""
    issue_type: str
    function_name: str
    line_number: int
    description: str


class Z3Checker:
    """Z3代码检查器"""

    def __init__(self, source_code: str):
        self.source_code = source_code
        self.issues: List[CodeIssue] = []
        self._tree = None

    def check(self) -> List[CodeIssue]:
        """执行检查"""
        if not Z3_AVAILABLE:
            return []

        try:
            self._tree = ast.parse(self.source_code)
        except SyntaxError:
            return []

        self.issues = []

        for node in ast.walk(self._tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._check_function(node)

        return self.issues

    def _check_function(self, func_node):
        """检查单个函数"""
        func_name = func_node.name

        for node in ast.walk(func_node):
            # 检查除法
            if isinstance(node, ast.BinOp):
                if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                    self._check_division(node, func_name)

            # 检查条件分支
            if isinstance(node, ast.If):
                self._check_condition(node, func_name)

    def _check_division(self, node: ast.BinOp, func_name: str):
        """检查除零风险"""
        divisor = node.right

        # 如果除数是常量0
        if isinstance(divisor, ast.Constant) and divisor.value == 0:
            self.issues.append(CodeIssue(
                issue_type="除零错误",
                function_name=func_name,
                line_number=node.lineno,
                description="除数为常量0"
            ))
            return

        # 如果除数是变量，使用Z3检查是否可能为0
        if isinstance(divisor, ast.Name):
            solver = Solver()
            var = Int(divisor.id)
            solver.add(var == 0)

            if solver.check() == sat:
                self.issues.append(CodeIssue(
                    issue_type="潜在除零风险",
                    function_name=func_name,
                    line_number=node.lineno,
                    description=f"变量 {divisor.id} 可能为0"
                ))

    def _check_condition(self, node: ast.If, func_name: str):
        """检查条件分支"""
        # 检查恒真/恒假条件
        test = node.test

        if isinstance(test, ast.Constant):
            if test.value is True:
                self.issues.append(CodeIssue(
                    issue_type="恒真条件",
                    function_name=func_name,
                    line_number=node.lineno,
                    description="条件恒为True，else分支不可达"
                ))
            elif test.value is False:
                self.issues.append(CodeIssue(
                    issue_type="恒假条件",
                    function_name=func_name,
                    line_number=node.lineno,
                    description="条件恒为False，if分支不可达"
                ))

        # 使用Z3检查比较表达式
        if isinstance(test, ast.Compare):
            self._check_compare_with_z3(test, node, func_name)

    def _check_compare_with_z3(self, compare: ast.Compare, if_node: ast.If, func_name: str):
        """使用Z3检查比较表达式"""
        if len(compare.ops) != 1 or len(compare.comparators) != 1:
            return

        left = compare.left
        op = compare.ops[0]
        right = compare.comparators[0]

        # 简单情况：变量与常量比较
        if isinstance(left, ast.Name) and isinstance(right, ast.Constant):
            solver = Solver()
            var = Int(left.id)
            val = right.value

            if not isinstance(val, (int, float)):
                return

            # 构建Z3约束
            if isinstance(op, ast.Eq):
                constraint = var == val
            elif isinstance(op, ast.NotEq):
                constraint = var != val
            elif isinstance(op, ast.Lt):
                constraint = var < val
            elif isinstance(op, ast.LtE):
                constraint = var <= val
            elif isinstance(op, ast.Gt):
                constraint = var > val
            elif isinstance(op, ast.GtE):
                constraint = var >= val
            else:
                return

            # 检查是否恒真
            solver.push()
            solver.add(Not(constraint))
            if solver.check() == unsat:
                self.issues.append(CodeIssue(
                    issue_type="恒真条件",
                    function_name=func_name,
                    line_number=if_node.lineno,
                    description=f"条件 {left.id} {type(op).__name__} {val} 可能恒为真"
                ))
            solver.pop()


def check_code(source_code: str) -> List[Dict]:
    """便捷函数：检查代码"""
    checker = Z3Checker(source_code)
    issues = checker.check()
    return [{'type': i.issue_type, 'function': i.function_name,
             'line': i.line_number, 'desc': i.description} for i in issues]