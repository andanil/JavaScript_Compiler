import os
from AST.Parser import *

prog = '''
    //a + 2;
    var a, b;
    if(a < 2)
        b = 3;
    /*for (var i = 0; i < 10; i++){
        a--;
    }*/
'''

parser = Parser()
res = parser.parse(prog)
print(*res.tree, sep=os.linesep)
