from Semantics.semantic_components import *
from AST.Nodes import *


class Analyzer:
    """Класс, производящий семантический анализ."""
    def __init__(self):
        self.root_scope = Scope(None)
        self.__current_scope = self.root_scope
        self.errors = []

    def analyze(self, root_node: TreeNode):
        """Метод, производящий семантический анализ абстрактного синтаксичесткого дерева."""
        for child in root_node.children:
            try:
                # Проверяем различные типы узлов АСД и проверяем необходимые условия.
                if child.__class__.__name__ in ["VarDeclarationNode"]:
                    for decl in child.children:
                        if decl.init.__class__.__name__ in ["LiteralNode"]:
                            self.__current_scope.add_label(Label(LabelType.VAR, decl.ident.name, decl.init.value),
                                                           [decl.row, decl.col])
                        else:
                            lbl = self.__current_scope.get_label(decl.init.name, [decl.row, decl.col])
                            self.__current_scope.add_label(Label(LabelType.VAR, decl.ident.name, lbl.val),
                                                           [decl.row, decl.col])
                elif child.__class__.__name__ in ["IdentNode"]:
                    self.__current_scope.get_label(child.name, [child.row, child.col])
                elif child.__class__.__name__ in ["FuncDeclarationNode"]:
                    self.__current_scope.add_label(Label(LabelType.FUNC, child.ident.name, len(child.params.params)),
                                                   [child.row, child.col])
                    newScope = Scope(self.__current_scope)
                    self.__current_scope.children_scopes.append(newScope)
                    self.__current_scope = newScope
                    self.analyze(child.block)
                    self.__current_scope = newScope.prev_scope
                elif child.__class__.__name__ in ["CallNode"]:
                    lbl = self.__current_scope.get_label(child.ident.name, [child.row, child.col])
                    req_args = len(child.args)
                    if lbl.val != req_args:
                        raise SemanticException("Неверное количество аргументов функции. "
                                                "Передано {}, необходимо {}".format(req_args, lbl.val),
                                                child.row, child.col)
                else:
                    self.analyze(child)
            except SemanticException as e:
                self.errors.append(e)
