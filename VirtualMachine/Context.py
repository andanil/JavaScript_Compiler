class Context:
    def __init__(self, address):
        self._variables = []
        self._return_address = address

    def get_variable(self, name):
        return self._variables[name]

    def set_variable(self, name, value):
        self._variables[name] = value

    def get_return_address(self):
        return self._return_address
