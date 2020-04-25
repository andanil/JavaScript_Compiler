import pyparsing as pp
from pyparsing import pyparsing_common as ppc
from AST.Nodes import *


class Parser:
    def __init__(self):
        self.grammar = Parser.__mk_grammar()

    @staticmethod
    def __mk_grammar():
        num = pp.Regex('[+-]?\\d+\\.?\\d*([eE][+-]?\\d+)?')
        str_ = pp.QuotedString('"', escChar='\\', unquoteResults=False, convertWhitespaceEscapes=False)
        literal = num | str_
        ident = ppc.identifier

        var_kw, func_kw = pp.Keyword('var'), pp.Keyword('function')
        if_kw, else_kw = pp.Keyword('if'), pp.Keyword('else')
        for_kw, do_kw, while_kw = pp.Keyword('for'), pp.Keyword('do'), pp.Keyword('while')

        l_par, r_par = pp.Literal('(').suppress(), pp.Literal(')')
        l_bracket, r_bracket = pp.Literal('{').suppress(), pp.Literal('}')
        semicolon, comma = pp.Literal(';').suppress(), pp.Literal(',').suppress()

        assign = pp.Literal('=')
        add, sub, mul, div, mod = pp.Literal('+'), pp.Literal('-'), pp.Literal('*'), pp.Literal('/'), pp.Literal('%')
        log_and, log_or, log_not = pp.Literal('&&'), pp.Literal('||'), pp.Literal('!')
        gt, lt, ge, le = pp.Literal('>'), pp.Literal('<'), pp.Literal('>='), pp.Literal('<=')
        neq, eq = pp.Literal('!='), pp.Literal('==')

        add_op = pp.Forward()
        expr = pp.Forward()

        call = ident + l_par + pp.Optional(expr + pp.ZeroOrMore(comma + expr)) + r_par

        group = (literal | call | ident | l_par + expr + r_par)

        mul_op = pp.Group(group + pp.ZeroOrMore((mul | div | mod)) + group)
        add_op << pp.Group(mul_op + pp.ZeroOrMore((add | sub)) + mul_op)
        compare = pp.Group(add_op + pp.ZeroOrMore((gt | lt | ge | le)) + add_op)
        compare_eq = pp.Group(compare + pp.ZeroOrMore((eq | neq)) + compare)
        log_and_op = pp.Group(compare_eq + pp.ZeroOrMore(log_and + compare_eq))
        log_or_op = pp.Group(log_and_op + pp.ZeroOrMore(log_or + log_and_op))
        expr << log_or_op

        simple_assign = ident + assign.suppress() + expr
        var_item = simple_assign | ident
        simple_var = var_kw.suppress() + var_item
        mult_var = simple_var + pp.ZeroOrMore(comma + var_item)

        stmt = pp.Forward()
        simple_stmt = simple_assign | call

        for_statement_list = pp.Optional(simple_stmt + pp.ZeroOrMore(comma + simple_stmt))
        for_statement = mult_var | for_statement_list
        for_test = expr | pp.Group(pp.empty)
        for_block = stmt | pp.Group(semicolon)

        if_ = if_kw.suppress() + l_par + expr + r_par + stmt + pp.Optional(else_kw.suppress() + stmt)
        for_ = for_kw.suppress() + l_par + for_statement + semicolon + for_test + semicolon + for_statement + r_par + for_block
        while_ = while_kw.suppress() + l_par + expr + r_par + stmt
        stmt_list = pp.ZeroOrMore(stmt + pp.ZeroOrMore(semicolon))
        block = l_bracket + stmt_list + r_bracket
        do_while = do_kw + stmt + while_kw + l_par + expr + r_par
        func_decl = func_kw + ident + l_par + pp.Optional(ident + pp.ZeroOrMore(comma + ident)) + r_par + block

        stmt << (
            if_ |
            for_ |
            while_ |
            do_while |
            block |
            mult_var + semicolon |
            simple_stmt + semicolon |
            func_decl
        )

        return stmt_list.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.stringEnd

    def parse(self, code: str) -> BlockStatement:
        return self.grammar.parseString(str(code))

