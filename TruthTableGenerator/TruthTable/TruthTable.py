import copy
import pandas as pd
from pandas import DataFrame
from typing import List
from AlgebraicExpressionParser import Expression
from TruthTableGenerator.exceptions.Exceptions import *


class TruthTable:

    def __init__(self, expression: str) -> None:
        """
        expression: the logic expression that the truth table will be generated from it
        expression type: str
        """

        self.expression = expression

    @property
    def expression(self) -> Expression:
        return self._expression

    @expression.setter
    def expression(self, expression: str) -> None:
        expression = self._remove_spaces_from_string(expression)
        expression = self._reformat_expression(expression)
        self._expression = Expression(expression=expression, operators={
            '|', '&', '~', '->', '<->'}, operators_info={'|': (2, 3), '&': (2, 4), '~': (1, 5), '->': (2, 2), '<->': (2, 1)}, operators_associativity={'|': 'LR', '&': 'LR', '~': 'RL', '->': 'LR', '<->': 'LR'}, variables={'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'})
        self._validate()
        self._generate_truth_table()

    def __str__(self) -> str:
        return f"{self.table()}"

    def __repr__(self) -> str:
        return f"TruthTable('{self.expression.expression}')"

    @staticmethod
    def _remove_spaces_from_string(string: str) -> str:
        string = string.replace("\n", "").replace(" ", "")
        return string

    @staticmethod
    def _reformat_expression(expression: str) -> set:
        expression = expression.replace('!', '~').replace('and', '&').replace('or', '|').replace(
            'True', 'T').replace('False', 'F').replace('∧', '&').replace('/\\', '&')
        return expression

    def _validate(self) -> None:
        """Raise an error if one of the expression variables is not valid"""
        for c in self.expression.expression:
            if c.isdigit():
                raise InvalidVariavleException(f"{c} is not valid variable")

    @staticmethod
    def Not(varibale1: List[bool]) -> List[bool]:
        result = []
        for i in varibale1:
            result.append(not i)
        return result

    @staticmethod
    def And(varibale1: List[bool], varibale2: List[bool]) -> List[bool]:
        result = []
        for i, j in zip(varibale1, varibale2):
            result.append(i and j)
        return result

    @staticmethod
    def Or(varibale1: List[bool], varibale2: List[bool]) -> List[bool]:
        result = []
        for i, j in zip(varibale1, varibale2):
            result.append(i or j)
        return result

    @staticmethod
    def Implication(varibale1: List[bool], varibale2: List[bool]) -> List[bool]:
        result = []
        for i, j in zip(varibale1, varibale2):
            result.append(not i or j)
        return result

    @staticmethod
    def Xor(varibale1: List[bool], varibale2: List[bool]) -> List[bool]:
        result = []
        for i, j in zip(varibale1, varibale2):
            result.append((not i or j) and (i or not j))
        return result

    def _select_binary_operation(self, varibale1: List[bool], varibale2: List[bool], operator: str) -> List[bool]:
        """Select which operation will be done based on the operator"""
        if operator == '&':
            return self.And(varibale1, varibale2)
        elif operator == '|':
            return self.Or(varibale1, varibale2)
        elif operator == '->':
            return self.Implication(varibale1, varibale2)
        elif operator == '<->':
            return self.Xor(varibale1, varibale2)
        return []

    def _generate_truth_table(self) -> None:
        """Generate the truth table from the logical expression"""
        postfix = self.expression.postfix()
        stack = []
        self.variables = {}
        operands = sorted(self.expression.get_operands())
        if 'T' in operands:
            operands.remove('T')
        if 'F' in operands:
            operands.remove('F')
        table_rows_count = 2**len(operands)
        revert_boolen = table_rows_count
        boolen = True
        for variable in operands:
            revert_boolen /= 2
            self.variables[variable] = []
            for i in range(table_rows_count):
                if i % revert_boolen == 0:
                    boolen = not boolen
                self.variables[variable].append(boolen)
        for token in postfix:
            if self.expression.is_operand(token):
                if token == 'T':
                    stack.append([True for i in range(table_rows_count)])
                elif token == 'F':
                    stack.append([False for i in range(table_rows_count)])
                else:
                    stack.append(self.variables[token])
            else:
                if self.expression.is_binary_operator(token):
                    op2 = stack.pop()
                    op1 = stack.pop()
                    stack.append(
                        self._select_binary_operation(op1, op2, token))
                else:
                    op1 = stack.pop()
                    stack.append(self.Not(op1))
        self.result = stack.pop()

    def table(self) -> DataFrame:
        """Return the truth table as DataFrame"""
        table = copy.deepcopy(self.variables)
        table[self.expression.expression] = self.result
        return pd.DataFrame.from_dict(table)
