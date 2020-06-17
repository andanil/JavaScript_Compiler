class Context:
    def __init__(self, line):
        self._variables = {}
        self._return_line = line

    def get_variable(self, name):
        try:
            return self._variables[name]
        except KeyError:
            return None

    def set_variable(self, name, value):
        self._variables[name] = value

    def get_return_address(self):
        return self._return_line
