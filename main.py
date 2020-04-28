import os
from AST.Parser import *

prog = '''
    function kek(b, c){
        var s;
    }   
    kek(3, 5);
    if(a < 2)
        b = 3;
    for (var i = 0; i < 10; i++){
        a--;
    }
'''

parser = Parser()
res = parser.parse(prog)
print(*res.tree, sep=os.linesep)
