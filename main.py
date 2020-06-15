import os
from Parser import *
from semantic_analyzer import *
from code_generator import *
from VirtualMachine import *

# строка с кодом, который в последствии будет распознаваться парсером.
prog = '''
    var a = 1450;
    function abc(toPrint){
        logprint("Строка " + toPrint + 228);
        return toPrint;
    }
    a = a + abc(a);
    logprint(a);
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
    generator = CodeGenerator(res)
    generator.print_bytecode()
    vm = VirtualMachine(generator.lines)


