import os
from AST.Parser import *

# строка с кодом, который в последствии будет распознаваться парсером.
prog = '''
    var d = 1, c, k, l = (5+3)**7 + 12;
    d = 5;
    b = d**5;
    function kek(a, b, c, d, e){
        var s;
    }   
    kek(3, 5, b);
    if(a < 2)
        b = 3;
    for (var i = 0; i < 10; i++){
        a--;
    }

    return d;
'''
# вызов конструктора класса Parser.
parser = Parser()
# в переменной res хранится корень графа, описывающего структуру кода из переменной prog.
res = parser.parse(prog)
# вызов функции print, в результате которого в консоли будет отображено абстрактное синтаксическое дерево.
print(*res.tree, sep=os.linesep)
