from AST.Parser import *

prog = '''
    var bb, c;
    bb = c;
'''

parser = Parser()
res = parser.parse(prog)
a = 1
