from abc import abstractmethod, ABC
from typing import Tuple, Callable, Optional


class TreeNode(ABC):
    """ Базовый класс для всех остальных классов. Используется для вывода дерева в консоль """
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
    """
    Класс, от которого наследуются классы,
    чьи значения можно привести к конкретному цифровому или буквенному значению.
    """
    pass


class ValueNode(EvalNode):
    """
    Класс, от которого наследуются классы LitelarNode и IdentNode,
    то есть те, которые могут содержать какие-либо значения.
    """
    pass


class ExprNode(EvalNode):
    """
    Класс, который является родительским для классов, описывающих выражения.
    """
    pass


class LiteralNode(ValueNode):
    """
    Класс, содержащий в себе какое-либо значение: число или строку
    """
    def __init__(self, value):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class IdentNode(ValueNode):
    """
    Класс, описывающий какой-либо идентификатор, то есть название переменной или функции.
    """
    def __init__(self, name):
        self.name = name

    def __str__(self) -> str:
        return str(self.name)


class BinExprNode(ExprNode):
    """
    Класс, описывающий бинарное выражение, то есть выражение, имеющее левую и правую часть, и оператор.
    """
    def __init__(self, op, left, right):
        self.left = left
        self.right = right
        self.op = op

    @property
    def children(self) -> Tuple[EvalNode, EvalNode]:
        return self.left, self.right

    def __str__(self) -> str:
        return str(self.op.value)


class UnaryExprNode(ExprNode):
    """
    Класс, описывающий унарное выражение, то есть выражение, имеющее левую часть и оператор.
    """
    def __init__(self, op, argument):
        self.op = op
        self.argument = argument

    @property
    def children(self) -> Tuple[EvalNode]:
        return (self.argument,) if self.argument else tuple()

    def __str__(self) -> str:
        return str(self.op.value)


class DeclaratorNode(TreeNode):
    """
    Класс, описывающий объявление переменной.
    """
    def __init__(self, ident: IdentNode, init: EvalNode = None):
        self.ident = ident
        self.init = init

    @property
    def children(self) -> Tuple[EvalNode]:
        return (self.init,) if self.init else tuple()

    def __str__(self) -> str:
        return str(self.ident)


class VarDeclarationNode(TreeNode):
    """
    Класс, описывающий объявления переменных. Содержит переменную declarations,
    в которой хранится множество с экземплярами класса DeclaratorNode.
    """
    def __init__(self, *declarations: DeclaratorNode):
        super().__init__()
        self.declarations = declarations

    @property
    def children(self) -> Tuple[DeclaratorNode]:
        return self.declarations

    def __str__(self) -> str:
        return 'var'


class BlockStatementNode(TreeNode):
    """
    Класс, содержащий в себе переменную nodes, описывающую множество всех узлов в этом блоке.
    В нашей реализации вся программа является блоком. Функции, if, for, while и do while также содержат в себе блоки.
    """
    def __init__(self, *nodes: TreeNode):
        self.nodes = nodes

    @property
    def children(self) -> Tuple[TreeNode]:
        return self.nodes

    def __str__(self) -> str:
        return 'block'


class ArgsNode(TreeNode):
    """
    Класс, описывающий множество аргументов функции.
    """
    def __init__(self, *params: Tuple[IdentNode]):
        self.params = params

    def __str__(self) -> str:
        return 'args: ' + ', '.join(str(p) for p in self.params)


class FuncDeclarationNode(TreeNode):
    """
    Класс, описывающий объявление функции. Содержит переменные ident, params, block.
    ident - название функции,
    params - аргументы функции,
    block - тело функции.
    """
    def __init__(self, ident: IdentNode, block: BlockStatementNode, params: Optional[ArgsNode] = ArgsNode()):
        self.ident = ident
        self.params = params
        self.block = block

    @property
    def children(self) -> Tuple[ArgsNode, BlockStatementNode]:
        return self.params, self.block

    def __str__(self) -> str:
        return 'function ' + str(self.ident)


class IfNode(TreeNode):
    """
    Класс, описывающий условный оператор if. Содержит переменные test, consequent, alternate.
    test - выражение, определяющее дальнейшее поведение,
    consequent - выполняется, если test принял истинное значение,
    alternate - выполняется, если test принял отрицательное значение.
    """
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
    """
    Класс, описывающий цикл for. Содержит переменные init, test, update, block.
    init - объявление переменной-счётчика,
    test - выражение, определяющее дальнейшее поведение, т.е. будет ли исполняться код в block,
    update - обновление значений переменной-счётчика.
    block - выполняется, если test принял истинное значение.
    """
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
    """
    Класс, описывающий цикл while. Содержит переменные test, block.
    test - выражение, определяющее дальнейшее поведение, т.е. будет ли исполняться код в block,
    block - выполняется, если test принял истинное значение.
    """
    def __init__(self, test: EvalNode, block: BlockStatementNode):
        self.test = test
        self.block = block

    @property
    def children(self) -> Tuple[EvalNode, BlockStatementNode]:
        return self.test, self.block

    def __str__(self) -> str:
        return 'while'


class DoWhileNode(TreeNode):
    """
       Класс, описывающий цикл do while. Содержит переменные test, block.
       test - выражение, определяющее дальнейшее поведение, т.е. будет ли исполняться код в block,
       block - выполняется, если test принял истинное значение.
       Отличие от while в том, что код в block выполнится как минимум однократно.
       """
    def __init__(self, block: BlockStatementNode, test: EvalNode):
        self.block = block
        self.test = test

    @property
    def children(self) -> Tuple[BlockStatementNode, EvalNode]:
        return self.block, self.test

    def __str__(self) -> str:
        return 'do while'


class CallNode(TreeNode):
    """
    Класс, описывающий вызов функции. ident - название функции, args - аргументы.
    """
    def __init__(self, ident: IdentNode, *args: EvalNode):
        self.ident = ident
        self.args = args

    @property
    def children(self) -> Tuple[IdentNode, EvalNode]:
        return (self.ident,) + self.args

    def __str__(self) -> str:
        return 'call'


class ReturnNode(TreeNode):
    """
    Класс, описывающий оператор return. Переменная argument - возвращаемое значение.
    """
    def __init__(self, argument: EvalNode):
        self.argument = argument

    @property
    def children(self) -> Tuple[EvalNode, ...]:
        return self.argument,

    def __str__(self) -> str:
        return 'return'
