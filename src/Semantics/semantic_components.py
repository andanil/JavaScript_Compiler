from enum import Enum


class LabelType(Enum):
    """Тип элемента в области видимости."""
    FUNC = "function"
    VAR = "variable"


class Label:
    """Класс, описывающий элемент области видимости."""
    def __init__(self, label_type: LabelType, name, val):
        self.label_type = label_type
        self.name = name
        self.val = val


class Scope:
    """Класс, описывающий область видимости."""
    def __init__(self, prev_scope):
        self._labels = []
        self.children_scopes = []
        self.prev_scope = prev_scope

    def add_label(self, label: Label, loc):
        """Этот метод добавляет функцию или переменную."""
        label_names = [lbl.name for lbl in self._labels]
        # Если эл-т не существует в области видимости, мы его добавляем в неё
        if label.name not in label_names:
            self._labels.append(label)
            return True
        else:
            # В противном случае мы проверяем, не существует ли функции с таким же именем.
            index = label_names.index(label)
            if label.label_type is LabelType.FUNC or self._labels[index].label_type is LabelType.FUNC:
                # Если она существует, выводим ошибку.
                raise SemanticException("Объект с именем {} уже существует.".format(label.name), loc[0], loc[1])
            else:
                # Если существует переменная с таким же именем, мы переопределяем её значение.
                self._labels[index] = label

    def get_label(self, name, loc):
        """Метод, возвращающий переменную из текущей области видимости или из её родительской области видимости."""
        result = [lbl for lbl in self._labels if lbl.name == name]
        if len(result) > 0:
            # Если переменная или функция с таким именем существует, возвращаем её.
            return result[0]
        else:
            if self.prev_scope is not None:
                # Если она не существует в текущей области видимости, ищем её в родительской области видимости.
                return self.prev_scope.get_label(name, loc)
            else:
                # Если такой переменной или функции нет, то выводим ошибку.
                raise SemanticException("Объекта с именем {} не существует. ".format(name), loc[0], loc[1])


class SemanticException(Exception):
    """Исключения в семантическом анализе."""
    def __init__(self, message, row: int = None, col: int = None) -> None:
        if row or col:
            message += " ("
            if row:
                message += "строка: {}".format(row)
                if col:
                    message += ", "
            if row:
                message += "символ: {}".format(col)
            message += ")"
        self.message = message
