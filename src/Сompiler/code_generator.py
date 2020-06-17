import inspect
from typing import List
from pyparsing import ParseResults
from Nodes import *
import custom_builtins
op_cmd = {
    '+': 'ADD',
    '-': 'SUB',
    '*': 'MUL',
    '/': 'DIV',
    '%': 'MOD',
    '>=': 'GE',
    '<=': 'LE',
    '!=': 'NEQ',
    '==': 'EQ',
    '>': 'GT',
    '<': 'LT',
    '&&': 'AND',
    '||': 'OR',
    '**': 'PWR'
}
builtin_funcs = [f for f in dir(custom_builtins) if inspect.isfunction(getattr(custom_builtins, f))]


class CodeGenerator:
    def __init__(self, ast: BlockStatementNode):
        self.__ast = ast
        self.lines: List[CodeLine] = []
        self.__funcs = {}
        self.__compile_functions()
        self.__generate_code(self.__ast)
        self.__add_line(CodeLine('HALT'))

    def __compile_functions(self):
        for child in self.__ast.children:
            if child.__class__.__name__ in ["FuncDeclarationNode"]:
                self.__funcs[child.ident.name] = len(self.lines) + 1
                if not isinstance(child.params.params[0], ParseResults):
                    for param in child.params.params[::-1]:
                        self.__add_line(CodeLine('STORE', param.name))
                self.__generate_code(child.block)
                if self.lines[len(self.lines) - 1].cmd not in ['RET']:
                    self.__add_line(CodeLine('RET'))
        self.__add_line_at(CodeLine('JMP', len(self.lines) + 1), 0)

    def __generate_code(self, node: TreeNode):
        if node.__class__.__name__ in ["BinExprNode"]:
            self.__compile_binexpr(node)
        elif node.__class__.__name__ in ["UnaryExprNode"]:
            self.__compile_unexpr(node)
        elif node.__class__.__name__ in ["LiteralNode"]:
            self.__add_line(CodeLine('PUSH', node.value))
        elif node.__class__.__name__ in ["IdentNode"]:
            self.__add_line(CodeLine('LOAD', node.name))
        elif node.__class__.__name__ in ["ReturnNode"]:
            self.__generate_code(node.argument)
            self.__add_line(CodeLine('RET'))
        elif node.__class__.__name__ in ["DeclaratorNode"]:
            if node.init is not None:
                self.__generate_code(node.init)
                self.__add_line(CodeLine('STORE', node.ident.name))
        elif node.__class__.__name__ in ["CallNode"]:
            for param in node.args:
                self.__generate_code(param)
            if node.ident.name in builtin_funcs:
                self.__add_line(CodeLine('CBLTN', node.ident.name))
            else:
                self.__add_line(CodeLine('CALL', self.__funcs[node.ident.name]))
        elif node.__class__.__name__ in ["BlockStatementNode", "VarDeclarationNode"]:
            for child in node.children:
                self.__generate_code(child)
        elif node.__class__.__name__ in ["IfNode"]:
            self.__compile_if(node)
        elif node.__class__.__name__ in ["WhileNode"]:
            self.__compile_while(node)
        elif node.__class__.__name__ in ["DoWhileNode"]:
            self.__compile_dowhile(node)
        elif node.__class__.__name__ in ["ForNode"]:
            self.__compile_for(node)

    def __compile_binexpr(self, node: BinExprNode):
        if node.op.value == '=':
            self.__generate_code(node.right)
            self.__add_line(CodeLine('STORE', node.left.name))
        else:
            self.__generate_code(node.left)
            self.__generate_code(node.right)
            self.__add_line(CodeLine(op_cmd[node.op.value]))

    def __compile_unexpr(self, node: UnaryExprNode):
        if node.op.value == '++':
            self.__add_line(CodeLine('PUSH', 1))
            self.__add_line(CodeLine('LOAD', node.argument.name))
            self.__add_line(CodeLine('ADD'))
            self.__add_line(CodeLine('STORE', node.argument.name))
        elif node.op.value == '--':
            self.__add_line(CodeLine('LOAD', node.argument.name))
            self.__add_line(CodeLine('PUSH', 1))
            self.__add_line(CodeLine('SUB'))
            self.__add_line(CodeLine('STORE', node.argument.name))
        elif node.op.value == '!':
            self.__add_line(CodeLine('LOAD', node.argument.name))
            self.__add_line(CodeLine('NOT'))

    def __compile_if(self, node: IfNode):
        self.__generate_code(node.test)
        start_false = len(self.lines)
        self.__generate_code(node.alternate)
        start_true = len(self.lines)
        self.__generate_code(node.consequent)
        self.__add_line_at(CodeLine('JNZ', start_true + 2), start_false)
        self.__add_line_at(CodeLine('JMP', len(self.lines) + 1), start_true + 1)

    def __compile_while(self, node: WhileNode):
        start_test = len(self.lines)
        self.__generate_code(node.test)
        self.__add_line(CodeLine('NOT'))
        start_true = len(self.lines)
        self.__generate_code(node.block)
        self.__add_line_at(CodeLine('JNZ', len(self.lines) + 2), start_true)
        self.__add_line(CodeLine('JMP', start_test))

    def __compile_dowhile(self, node: DoWhileNode):
        start_block = len(self.lines)
        self.__generate_code(node.block)
        self.__generate_code(node.test)
        self.__add_line(CodeLine('JNZ', start_block))

    def __compile_for(self, node: ForNode):
        self.__generate_code(node.init)
        start_test = len(self.lines)
        if node.test.__class__.__name__ not in ["BinExprNode"]:
            self.__add_line(CodeLine('PUSH', 1))
        else:
            self.__generate_code(node.test)
        self.__add_line(CodeLine('NOT'))
        start_block = len(self.lines)
        self.__generate_code(node.block)
        self.__generate_code(node.update)
        self.__add_line(CodeLine('JMP', start_test))
        self.__add_line_at(CodeLine('JNZ', len(self.lines) + 1), start_block)

    def __add_line(self, line):
        self.lines.append(line)

    def __add_line_at(self, line, index):
        self.lines.insert(index, line)

    def print_bytecode(self):
        id = 0
        for line in self.lines:
            print(str(id) + '. ' + str(line))
            id += 1


class CodeLine:
    def __init__(self, cmd: str, value: Optional = None):
        self.cmd = cmd
        self.value = value

    def __str__(self):
        return self.cmd + ' ' + (str(self.value) if self.value else '')

