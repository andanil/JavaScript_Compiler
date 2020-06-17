from typing import List
from Instructions import *
from Context import Context
from code_generator import CodeLine
import custom_builtins
import inspect


class VirtualMachine:
    def __init__(self, code: List[CodeLine]):
        self._code = code
        self._cur_line_id = 0
        self._stack = []
        self._contexts = [Context(0)]
        self._halted = False
        self.__run()

    def __run(self):
        while self._cur_line_id < len(self._code) and not self._halted:
            instruction = self.get_code("Ожидалась команда")
            self.execute_operation(instruction)

    def execute_operation(self, instruction):
        opcode = {
            HALT: self.halt,
            POP: self.pop,
            DUP: self.dup,
            ADD: self.add,
            SUB: self.sub,
            MUL: self.mul,
            DIV: self.div,
            MOD: self.mod,
            NOT: self._not,
            AND: self._and,
            OR: self._or,
            EQ: self.eq,
            NEQ: self.neq,
            GT: self.gt,
            LT: self.lt,
            GE: self.ge,
            LE: self.le,
            RET: self.ret
        }
        opcode_with_val = {
            PUSH: self.push,
            JMP: self.jmp,
            JNZ: self.jnz,
            LOAD: self.load,
            STORE: self.store,
            CALL: self.call,
            CBLTN: self.call_builtin
        }

        if instruction.cmd in opcode:
            opcode[instruction.cmd]()
        elif instruction.cmd in opcode_with_val:
            opcode_with_val[instruction.cmd](instruction.value)
        else:
            raise RuntimeError("Неизвестная команда: " + str(instruction))

    def halt(self):
        self._halted = True

    def push(self, value):
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
        right = self.pop()
        left = self.pop()
        if isinstance(right, str) or isinstance(left, str):
            left = str(left)
            right = str(right)
        self._stack.append(left + right)

    def sub(self):
        self.check_stack("SUB")
        right = self.pop()
        left = self.pop()
        if isinstance(right, str) or isinstance(left, str):
            self._stack.append('NaN')
        else:
            self._stack.append(right - left)

    def mul(self):
        self.check_stack("MUL")
        right = self.pop()
        left = self.pop()
        if isinstance(right, str) or isinstance(left, str):
            self._stack.append('NaN')
        else:
            self._stack.append(left * right)

    def div(self):
        self.check_stack("DIV")
        right = self.pop()
        left = self.pop()
        if isinstance(right, str) or isinstance(left, str):
            self._stack.append('NaN')
        else:
            self._stack.append(right / left)

    def mod(self):
        self.check_stack("MOD")
        right = self.pop()
        left = self.pop()
        if isinstance(right, str) or isinstance(left, str):
            self._stack.append('NaN')
        else:
            self._stack.append(right % left)

    def _not(self):
        self.is_stack_empty()
        left = self.pop()
        if isinstance(left, str):
            self._stack.append(False)
        else:
            self._stack.append(int(not left))

    def _and(self):
        self.check_stack("AND")
        right = self.pop()
        left = self.pop()
        if isinstance(left, bool) and isinstance(right, bool):
            self._stack.append(left and right)
        elif isinstance(left, bool):
            self._stack.append(left)
        else:
            self._stack.append(right)

    def _or(self):
        self.check_stack("OR")
        right = self.pop()
        left = self.pop()
        if isinstance(left, bool) and isinstance(right, bool):
            self._stack.append(left or right)
        elif isinstance(left, bool):
            self._stack.append(right)
        else:
            self._stack.append(left)

    def eq(self):
        self.check_stack("EQ")
        right = self.pop()
        left = self.pop()
        if (isinstance(right, str) and not isinstance(left, str))\
                or (not isinstance(right, str) and isinstance(left, str)):
            self._stack.append(False)
        else:
            self._stack.append(left == right)

    def neq(self):
        self.check_stack("NEQ")
        self.eq()
        self._stack.append(not self.pop())

    def gt(self):
        self.check_stack("GT")
        right = self.pop()
        left = self.pop()
        if (isinstance(right, str) and not isinstance(left, str)) \
                or (not isinstance(right, str) and isinstance(left, str)):
            self._stack.append(False)
        else:
            self._stack.append(left > right)

    def lt(self):
        self.check_stack("LT")
        right = self.pop()
        left = self.pop()
        if (isinstance(right, str) and not isinstance(left, str)) \
                or (not isinstance(right, str) and isinstance(left, str)):
            self._stack.append(False)
        else:
            self._stack.append(left < right)

    def ge(self):
        self.check_stack("GE")
        right = self.pop()
        left = self.pop()
        if (isinstance(right, str) and not isinstance(left, str)) \
                or (not isinstance(right, str) and isinstance(left, str)):
            self._stack.append(False)
        else:
            self._stack.append(left >= right)

    def le(self):
        self.check_stack("LE")
        right = self.pop()
        left = self.pop()
        if (isinstance(right, str) and not isinstance(left, str)) \
                or (not isinstance(right, str) and isinstance(left, str)):
            self._stack.append(False)
        else:
            self._stack.append(left <= right)

    def pwr(self):
        self.check_stack("PWR")
        right = self.pop()
        left = self.pop()
        if isinstance(right, str) or isinstance(left, str):
            self._stack.append('NaN')
        else:
            self._stack.append(left ** right)

    def jmp(self, address):
        self.check_address(address)
        self._cur_line_id = address

    def jnz(self, address):
        self.check_address(address)
        self.is_stack_empty()
        if self.pop():
            self._cur_line_id = address

    def load(self, var_name):
        self._stack.append(self.get_current_context().get_variable(var_name))

    def store(self, var_name):
        self.is_stack_empty()
        self.get_current_context().set_variable(var_name, self.pop())

    def call(self, address):
        self.check_address(address)
        self._contexts.append(Context(self._cur_line_id))
        self._cur_line_id = address

    def call_builtin(self, func_name):
        method_to_call = getattr(custom_builtins, func_name)
        args = []
        for param in inspect.signature(method_to_call).parameters:
            args.append(self._stack.pop())
        res = method_to_call(*args)
        if res is not None:
            self._stack.append(res)

    def ret(self):
        if len(self._contexts) == 1:
            raise RuntimeError("Недопустимая команда RET")
        else:
            ret_address = self.get_current_context().get_return_address()
            self._contexts.pop()
            self._cur_line_id = ret_address

    def get_code(self, error_message):
        if self._cur_line_id < len(self._code):
            code = self._code[self._cur_line_id]
            self._cur_line_id += 1
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

