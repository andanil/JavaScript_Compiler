import inspect
from contextlib import suppress

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
        literal = (num | str_).setName('Literal')
        ident = ppc.identifier.setName('Ident')

        VAR_KW, FUNC_KW = pp.Keyword('var'), pp.Keyword('function')
        IF_KW, ELSE_KW = pp.Keyword('if'), pp.Keyword('else')
        FOR_KW, DO_KW, WHILE_KW = pp.Keyword('for'), pp.Keyword('do'), pp.Keyword('while')

        L_PAR, R_PAR = pp.Literal('(').suppress(), pp.Literal(')').suppress()
        L_BRACKET, R_BRACKET = pp.Literal('{').suppress(), pp.Literal('}').suppress()
        SEMICOLON, COMMA = pp.Literal(';').suppress(), pp.Literal(',').suppress()

        ASSIGN = pp.Literal('=')
        ADD, SUB, MUL, DIV, MOD = pp.Literal('+'), pp.Literal('-'), pp.Literal('*'), pp.Literal('/'), pp.Literal('%')
        LOG_AND, LOG_OR, LOG_NOT = pp.Literal('&&'), pp.Literal('||'), pp.Literal('!')
        GT, LT, GE, LE = pp.Literal('>'), pp.Literal('<'), pp.Literal('>='), pp.Literal('<=')
        NEQ, EQ = pp.Literal('!='), pp.Literal('==')
        INCR, DECR = pp.Literal('++'), pp.Literal('--')
        COMP_ADD, COMP_SUB, COMP_MUL, COMP_DIV, COMP_MOD = pp.Literal('+='), pp.Literal('-='), pp.Literal('*='), \
                                                           pp.Literal('/='), pp.Literal('%=')
        mul_op = pp.Forward()
        add_op = pp.Forward()
        expr = pp.Forward()

        call = (ident + L_PAR + pp.Optional(expr + pp.ZeroOrMore(COMMA + expr)) + R_PAR).setName('Call')

        incr_op = (ident + INCR).setName('UnaryExpr')
        decr_op = (ident + DECR).setName('UnaryExpr')

        group = (literal | call | ident | L_PAR + expr + R_PAR)

        mul_op << pp.Group(group + pp.ZeroOrMore((MUL | DIV | MOD) + group)).setName('BinExpr')
        add_op << pp.Group(mul_op + pp.ZeroOrMore((ADD | SUB) + mul_op)).setName('BinExpr')
        compare = pp.Group(add_op + pp.ZeroOrMore((GE | LE | GT | LT) + add_op)).setName('BinExpr')
        compare_eq = pp.Group(compare + pp.ZeroOrMore((EQ | NEQ) + compare)).setName('BinExpr')
        log_and_op = pp.Group(compare_eq + pp.ZeroOrMore(LOG_AND + compare_eq)).setName('BinExpr')
        log_or_op = pp.Group(log_and_op + pp.ZeroOrMore(LOG_OR + log_and_op)).setName('BinExpr')
        expr << log_or_op

        assign = (ident + ASSIGN + expr).setName('BinExpr')
        simple_assign = (ident + ASSIGN.suppress() + expr)
        var_item = simple_assign | ident
        simple_var = (VAR_KW.suppress() + var_item).setName('Declarator')
        mult_var_item = (COMMA + var_item).setName('Declarator')
        mult_var = (simple_var + pp.ZeroOrMore(mult_var_item)).setName('VarDeclaration')
        # | comp_add.suppress() | comp_sub.suppress() | comp_div.suppress() | comp_mul.suppress() | comp_mod.suppress()
        stmt = pp.Forward()
        simple_stmt = assign | call | incr_op | decr_op

        for_statement_list = pp.Optional(simple_stmt + pp.ZeroOrMore(COMMA + simple_stmt))
        for_statement = mult_var | for_statement_list
        for_test = expr | pp.Group(pp.empty)
        for_block = stmt | pp.Group(SEMICOLON).setName('BlockStatement')

        if_ = (IF_KW.suppress() + L_PAR + expr + R_PAR + stmt + pp.Optional(ELSE_KW.suppress() + stmt)).setName('If')
        for_ = (FOR_KW.suppress() + L_PAR + for_statement + SEMICOLON + for_test + SEMICOLON +
                for_statement + R_PAR + for_block).setName('For')
        while_ = (WHILE_KW.suppress() + L_PAR + expr + R_PAR + stmt).setName('While')
        block = pp.ZeroOrMore(stmt + pp.ZeroOrMore(SEMICOLON)).setName('BlockStatement')
        br_block = L_BRACKET + block + R_BRACKET
        do_while = (DO_KW + stmt + WHILE_KW + L_PAR + expr + R_PAR).setName('DoWhile')
        args = (ident + pp.ZeroOrMore(COMMA + ident)).setName("Args")
        func_decl = (FUNC_KW.suppress() + ident + L_PAR + pp.Optional(args) + R_PAR + br_block)\
            .setName('FuncDeclaration')

        stmt << (
                if_ |
                for_ |
                while_ |
                do_while |
                br_block |
                mult_var + SEMICOLON |
                simple_stmt + SEMICOLON |
                func_decl
        )

        for var_name, value in locals().copy().items():
            if isinstance(value, pp.ParserElement):
                Parser.__set_parse_action(var_name, value)
        return block.ignore(pp.cStyleComment).ignore(pp.dblSlashComment) + pp.stringEnd

    @staticmethod
    def __set_parse_action(rule_name: str, rule: pp.ParserElement):
        if rule_name == rule_name.upper():
            return
        if getattr(rule, 'name', None) and rule.name.isidentifier():
            rule_name = rule.name
        if rule_name in ('BinExpr', ):
            def bin_op_parse_action(s, loc, toks):
                node = toks[0]
                if not isinstance(node, TreeNode):
                    node = bin_op_parse_action(s, loc, node)
                for i in range(1, len(toks) - 1, 2):
                    secondNode = toks[i + 1]
                    if not isinstance(secondNode, TreeNode):
                        secondNode = bin_op_parse_action(s, loc, secondNode)
                    node = BinExprNode(Operators(toks[i]), node, secondNode)
                return node
            rule.setParseAction(bin_op_parse_action)
        elif rule_name in ('UnaryExpr', ):
            def un_op_parse_action(s, loc, toks):
                node = toks[0]
                if not isinstance(node, TreeNode):
                    node = un_op_parse_action(s, loc, node)
                for i in range(1, len(toks)):
                    node = UnaryExprNode(Operators(toks[i]), node)
                return node
            rule.setParseAction(un_op_parse_action)
        else:
            cls = rule_name + 'Node'
            with suppress(NameError):
                cls = eval(cls)
                if not inspect.isabstract(cls):
                    def parse_action(s, loc, toks):
                        return cls(*toks)
                    rule.setParseAction(parse_action)

    def parse(self, code: str) -> BlockStatementNode:
        return self.grammar.parseString(str(code))[0]
