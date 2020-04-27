from AST.Parser import *

prog = '''
    var i = 1, b = 2;
    var c = i <= b;
'''

parser = Parser()
res = parser.parse(prog)
a = 1
