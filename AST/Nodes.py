from abc import abstractmethod, ABC
from enum import Enum
from typing import Tuple, Callable, Optional


class TreeNode(ABC):
    def __init__(self):
        super().__init__()

    @property
    def children(self) -> Tuple['TreeNode', ...]:
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

    def visit(self, func: Callable[['TreeNode'], None]) -> None:
        func(self)
        map(func, self.children)

    def __getitem__(self, index):
        return self.children[index] if index < len(self.children) else None


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


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    INCR = '++'
    DECR = '--'
    ASSIGN = '='
    GE = '>='
    LE = '<='
    NEQ = '!='
    EQ = '=='
    GT = '>'
    LT = '<'
    LOG_AND = '&&'
    LOG_OR = '||'


class BinExprNode(ExprNode):
    def __init__(self, op, left, right):
        self.left = left
        self.right = right
        self.op = op

    @property
    def children(self) -> Tuple[EvalNode, EvalNode]:
        return self.left, self.right

    def __str__(self) -> str:
        return str(self.op.value)


class UnaryExpr(ExprNode):
    def __init__(self, op, argument):
        self.op = op
        self.argument = argument

    @property
    def children(self) -> Tuple[EvalNode]:
        return self.argument

    def __str__(self) -> str:
        return str(self.op.value)


class DeclaratorNode(TreeNode):
    def __init__(self, ident: IdentNode, init: EvalNode = None):
        self.ident = ident
        self.init = init

    @property
    def children(self) -> Tuple[EvalNode]:
        return (self.init,) if self.init else tuple()

    def __str__(self) -> str:
        return str(self.ident)


class VarDeclarationNode(TreeNode):
    def __init__(self, *declarations: DeclaratorNode):
        super().__init__()
        self.declarations = declarations

    @property
    def children(self) -> Tuple[DeclaratorNode]:
        return self.declarations

    def __str__(self) -> str:
        return 'var'


class BlockStatementNode(TreeNode):
    def __init__(self, *nodes: TreeNode):
        self.nodes = nodes

    @property
    def children(self) -> Tuple[TreeNode]:
        return self.nodes

    def __str__(self) -> str:
        return 'block'


class FuncDeclarationNode(TreeNode):
    def __init__(self, ident: IdentNode, *block: BlockStatementNode, params: Tuple[IdentNode] = None):
        self.ident = ident
        self.params = params
        self.block = block

    @property
    def children(self) -> Tuple[BlockStatementNode]:
        return self.block

    def __str__(self) -> str:
        return str(self.ident) + '(' + (str([str(p) for p in enumerate(self.params)]) if self.params else "") + ')'


class IfNode(TreeNode):
    def __init__(self, test: EvalNode, consequent: BlockStatementNode, alternate: BlockStatementNode = None):
        self.test = test
        self.consequent = consequent
        self.alternate = alternate

    @property
    def children(self) -> Tuple[EvalNode, ...]:
        return (self.test, self.consequent) + ((self.alternate,) if self.alternate else tuple())

    def __str__(self) -> str:
        return 'if'


class ForNode(TreeNode):
    def __init__(self, init: VarDeclarationNode, test: EvalNode, update: EvalNode, block: BlockStatementNode):
        self.init = init
        self.test = test
        self.update = update
        self.block = block

    @property
    def children(self) -> Tuple[VarDeclarationNode, EvalNode, EvalNode, BlockStatementNode]:
        return self.init, self.test, self.update, self.block

    def __str__(self) -> str:
        return 'for'


class WhileNode(TreeNode):
    def __init__(self, test: EvalNode, block: BlockStatementNode):
        self.test = test
        self.block = block

    @property
    def children(self) -> Tuple[EvalNode, BlockStatementNode]:
        return self.test, self.block

    def __str__(self) -> str:
        return 'while'


class DoWhileNode(TreeNode):
    def __init__(self, block: BlockStatementNode, test: EvalNode):
        self.block = block
        self.test = test

    @property
    def children(self) -> Tuple[BlockStatementNode, EvalNode]:
        return self.block, self.test

    def __str__(self) -> str:
        return 'do while'


class CallNode(TreeNode):
    def __init__(self, ident: IdentNode, *args: EvalNode):
        self.ident = ident
        self.args = args

    @property
    def children(self) -> Tuple[IdentNode, EvalNode]:
        return (self.ident,) + self.args

    def __str__(self) -> str:
        return 'call'
