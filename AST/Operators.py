from enum import Enum


class Operators(Enum):
    """
    Вспомогательный класс, дающий удобный доступ к операторам
    """
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    INCR = '++'
    DECR = '--'
    EXP = '**'
    ASSIGN = '='
    GE = '>='
    LE = '<='
    NEQ = '!='
    EQ = '=='
    GT = '>'
    LT = '<'
    LOG_AND = '&&'
    LOG_OR = '||'
    COMP_ADD = '+='
    COMP_SUB = '-='
    COMP_MUL = '*='
    COMP_DIV = '/='
    COMP_MOD = '%='
