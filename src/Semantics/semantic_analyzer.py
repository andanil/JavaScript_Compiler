import inspect

from pyparsing import ParseResults

import custom_builtins
from semantic_components import *
from Nodes import *

builtin_funcs = [f for f in dir(custom_builtins) if inspect.isfunction(getattr(custom_builtins, f))]


class Analyzer:
    """Класс, производящий семантический анализ."""

    def __init__(self):
        self.root_scope = Scope(None)
        self.__current_scope = self.root_scope
        for func in builtin_funcs:
            self.__current_scope.add_label(Label(LabelType.FUNC, str(func),
                                                 len(inspect.signature(getattr(custom_builtins, func)).parameters)), [])
        self.errors = []

    def analyze(self, root_node: TreeNode):
        """Метод, производящий семантический анализ абстрактного синтаксичесткого дерева."""
        for child in root_node.children:
            self.analyze_node(child)

    def analyze_node(self, node):
        """Метод, производящий семантический анализ узла дерева."""
        try:
            # Проверяем различные типы узлов АСД и проверяем необходимые условия.
            if node.__class__.__name__ in ["VarDeclarationNode"]:
                for decl in node.children:
                    if decl.init.__class__.__name__ in ["LiteralNode"]:
                        self.__current_scope.add_label(Label(LabelType.VAR, decl.ident.name, decl.init.value),
                                                       [decl.row, decl.col])
                    else:
                        self.__current_scope.add_label(Label(LabelType.VAR, decl.ident.name, None),
                                                       [decl.row, decl.col])
                        self.analyze_node(decl.init)
            elif node.__class__.__name__ in ["IdentNode"]:
                self.__current_scope.get_label(node.name, [node.row, node.col])
            elif node.__class__.__name__ in ["FuncDeclarationNode"]:
                self.__current_scope.add_label(Label(LabelType.FUNC, node.ident.name,
                                                     0 if isinstance(node.params.params[0], ParseResults) else len(
                                                         node.params.params)), [node.row, node.col])
                newScope = Scope(self.__current_scope)
                self.__current_scope.children_scopes.append(newScope)
                self.__current_scope = newScope
                for param in node.params.params:
                    if param.__class__.__name__ in ["IdentNode"]:
                        self.__current_scope.add_label(Label(LabelType.VAR, param.name, None), [param.row, param.col])
                self.analyze(node.block)
                self.__current_scope = newScope.prev_scope
            elif node.__class__.__name__ in ["CallNode"]:
                lbl = self.__current_scope.get_label(node.ident.name, [node.row, node.col])
                req_args = len(node.args)
                if lbl.val != req_args:
                    raise SemanticException("Неверное количество аргументов функции. "
                                            "Передано {}, необходимо {}".format(req_args, lbl.val),
                                            node.row, node.col)
            elif node.__class__.__name__ not in ["NoneType"]:
                self.analyze(node)
        except SemanticException as e:
            self.errors.append(e)
