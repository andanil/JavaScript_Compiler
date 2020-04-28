import os
from AST.Parser import *

prog = '''
    var d = 1, c, k, l = (5+3)*7 + 12;
    d = 5;
    d++;
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
