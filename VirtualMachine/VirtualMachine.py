from Instructions import *
from Context import Context


class VirtualMachine:
    def __init__(self, code):
        self._code = code
        self._IP = 0
        self._stack = []
        self._contexts = [Context(0)]
        self._halted = False

    def run(self):
        while self._IP < len(self._code) and not self._halted:
            instruction = self.get_code("Ожидалась команда")
            self.execute_operation(instruction)

    def execute_operation(self, instruction):
        opcode = {
            HALT: self.halt,
            PUSH: self.push,
            POP: self.pop,
            DUP: self.dup,
            ADD: self.add,
            SUB: self.sub,
            MUL: self.mul,
            DIV: self.div,
            IDIV: self.idiv,
            MOD: self.mod,
            NOT: self._not,
            AND: self._and,
            OR: self._or,
            EQ: self.eq,
            GT: self.gt,
            LT: self.lt,
            GE: self.ge,
            LE: self.le,
            JMP: self.jmp,
            JNZ: self.jnz,
            LOAD: self.load,
            STORE: self.store,
            CALL: self.call,
            RET: self.ret
        }

        if instruction in opcode:
            opcode[instruction]()
        else:
            raise RuntimeError("Неизвестная команда: " + str(instruction))

    def halt(self):
        self._halted = True

    def push(self):
        value = int(self.get_code("Ожидалось значение после команды PUSH"))
        self._stack.append(value)

    def pop(self):
        self.is_stack_empty()
        return self._stack.pop()

    def dup(self):
        self.is_stack_empty()
        last = self._stack[len(self._stack)-1]
        self._stack.append(last)

    def add(self):
        self.check_stack("ADD")
        self._stack.append(self.pop() + self.pop())

    def sub(self):
        self.check_stack("SUB")
        last = self.pop()
        self._stack.append(self.pop() - last)

    def mul(self):
        self.check_stack("MUL")
        self._stack.append(self.pop() * self.pop())

    def div(self):
        self.check_stack("DIV")
        last = self.pop()
        self._stack.append(self.pop() / last)

    def idiv(self):
        self.check_stack("IDIV")
        last = self.pop()
        self._stack.append(self.pop() // last)

    def mod(self):
        self.check_stack("MOD")
        last = self.pop()
        self._stack.append(self.pop() % last)

    def _not(self):
        self.is_stack_empty()
        self._stack.append(int(not self.pop()))

    def _and(self):
        self.check_stack("AND")
        self._stack.append(self.pop() and self.pop())

    def _or(self):
        self.check_stack("OR")
        self._stack.append(self.pop() or self.pop())

    def eq(self):
        self.check_stack("EQ")
        self._stack.append(self.pop() == self.pop())

    def gt(self):
        self.check_stack("GT")
        last = self.pop()
        self._stack.append(self.pop() > last)

    def lt(self):
        self.check_stack("LT")
        last = self.pop()
        self._stack.append(self.pop() < last)

    def ge(self):
        self.check_stack("GE")
        last = self.pop()
        self._stack.append(self.pop() >= last)

    def le(self):
        self.check_stack("LE")
        last = self.pop()
        self._stack.append(self.pop() <= last)

    def jmp(self):
        address = self.get_code("Ожидался адрес после команды JMP")
        self.check_address(address)
        self._IP = address

    def jnz(self):
        address = self.get_code("Ожидался адрес после команды JNZ")
        self.check_address(address)
        self.is_stack_empty()
        if self.pop():
            self._IP = address

    def load(self):
        var_name = self.get_code("Ожидалось имя переменной после команды LOAD")
        self._stack.append(self.get_current_context().get_variable(var_name))

    def store(self):
        var_name = self.get_code("Ожидалось имя переменной после команды STORE")
        self.is_stack_empty()
        self.get_current_context().set_variable(var_name, self.pop())

    def call(self):
        address = self.get_code("Ожидался адрес после команды CALL")
        self.check_address(address)
        self._contexts.append(Context(self._IP))
        self._IP = address

    def ret(self):
        if len(self._contexts) == 1:
            raise RuntimeError("Недопустимая команда RET")
        else:
            ret_address = self.get_current_context().get_return_address()
            self._contexts.pop()
            self._IP = ret_address

    def get_code(self, error_message):
        if self._IP < len(self._code):
            code = self._code[self._IP]
            self._IP += 1
            return code
        else:
            raise RuntimeError(error_message)

    def check_stack(self, instruction):
        if len(self._stack) < 2:
            raise RuntimeError("Недостаточно элементов в стеке для выполнения команды" + instruction)

    def is_stack_empty(self):
        if len(self._stack) == 0:
            raise RuntimeError("Стек пустой")

    def get_current_context(self):
        return self._contexts[len(self._contexts)-1]

    def check_address(self, address):
        if address < 0 or address >= len(self._code):
            raise RuntimeError("Неверный адрес в команде JUMP")

