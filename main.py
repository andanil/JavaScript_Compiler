import os
from AST.Parser import *
from Semantics.semantic_analyzer import *
from Compiler.code_generator import CodeGenerator

# строка с кодом, который в последствии будет распознаваться парсером.
prog = '''
    1;
    a;
'''
# вызов конструктора класса Parser.
parser = Parser()
# вызов конструктора класса Analyzer.
analyzer = Analyzer()
# в переменной res хранится корень графа, описывающего структуру кода из переменной prog.
res = parser.parse(prog)
print(*res.tree, sep=os.linesep)

# вызов метода analyze, который производит семантический анализ
analyzer.analyze(res)
if len(analyzer.errors) > 0:
    for e in analyzer.errors:
        print("Ошибка: {}".format(e.message))
else:
    print("Ошибок не обнаружено.")

''' """"# вызов функции print, в результате которого в консоли будет отображено абстрактное синтаксическое дерево.
print(*res.tree, sep=os.linesep)'''
