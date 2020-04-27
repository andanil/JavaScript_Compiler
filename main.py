import os
from AST.Parser import *

prog = '''
    var a = 1, b = 2;
    /*if(a < 2)
        b = 4;*/
    /*for (var i = 0; i < 10; i++){
        a--;
    }*/
'''

parser = Parser()
res = parser.parse(prog)
print(*res.tree, sep=os.linesep)
