from abc import abstractmethod, ABC
from typing import Tuple


class TreeNode(ABC):
    def __init__(self):
        pass

    @property
    def children(self):
        return ()

    @property
    def tree(self) -> [str, ...]:
        res = [str(self)]
        children_temp = self.children
        for i, child in enumerate(children_temp):
            ch0, ch = '├', '│'
            if i == len(children_temp) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree)))
        return res

    @abstractmethod
    def __str__(self):
        pass


class EvalNode(TreeNode):
    pass


class ValueNode(EvalNode):
    pass


class ExprNode(EvalNode):
    pass


class LiteralNode(ValueNode):
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class IdentNode(ValueNode):
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return str(self.name)


class BinExpr(ExprNode):
    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

    @property
    def children(self):
        return self.left, self.right

    def __str__(self) -> str:
        return str(self.op)


class UnaryExpr(ExprNode):
    def __init__(self, op, argument):
        self.op = op
        self.argument = argument

    @property
    def children(self):
        return self.argument

    def __str__(self) -> str:
        return str(self.op)


class VarDeclaration(TreeNode):
    def __init__(self, declarations):
        self.declarations = declarations

    @property
    def children(self):
        return self.declarations

    def __str__(self) -> str:
        return 'var'


class Declarator(TreeNode):
    def __init__(self, ident, init):
        self.ident = ident
        self.init = init

    @property
    def children(self):
        return self.init

    def __str__(self) -> str:
        return str(self.ident)


class BlockStatement(TreeNode):
    def __init__(self, nodes):
        self.nodes = nodes

    @property
    def children(self):
        return self.nodes

    def __str__(self) -> str:
        return 'block'


class FuncDeclaration(TreeNode):
    def __init__(self, ident: IdentNode, params: Tuple[IdentNode], block: BlockStatement):
        self.ident = ident
        self.params = params
        self.block = block

    @property
    def children(self):
        return self.block

    def __str__(self) -> str:
        return str(self.ident) + '(' + str([str(p) for p in enumerate(self.params)]) + ')'


class IfNode(TreeNode):
    def __init(self, test: EvalNode, consequent: TreeNode, alternate: TreeNode):
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

    @property
    def children(self):
        return self.test, self.consequent, self.alternate

    def __str__(self) -> str:
        return 'if'


class ForNode(TreeNode):
    def __init(self, init: VarDeclaration, test: EvalNode, update: EvalNode, block: BlockStatement):
        self.init = init
        self.test = test
        self.update = update
        self.block = block

    @property
    def children(self):
        return self.init, self.test, self.update, self.block

    def __str__(self) -> str:
        return 'for'


class WhileNode(TreeNode):
    def __init(self, test: EvalNode, block: BlockStatement):
        self.test = test
        self.block = block

    @property
    def children(self):
        return self.test, self.block

    def __str__(self) -> str:
        return 'while'


class DoWhileNode(TreeNode):
    def __init(self, block: BlockStatement, test: EvalNode):
        self.block = block
        self.test = test

    @property
    def children(self):
        return self.block, self.test

    def __str__(self) -> str:
        return 'do while'


class CallNode(TreeNode):
    def __init(self, ident: IdentNode, args: Tuple[EvalNode]):
        self.ident = ident
        self.args = args

    @property
    def children(self):
        return self.args

    def __str__(self) -> str:
        return 'call'
