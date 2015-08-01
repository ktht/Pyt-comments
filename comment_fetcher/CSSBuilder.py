class CSSBuilder:
    
    def __init__(self, name, indent="   "):
        self.__name = name
        self.__indent = indent
        self.__keyvals = []
        self.__string = None
    
    def add(self, key, val):
        self.__keyvals.append((key, val))
    
    def __create_string(self):
        self.__string = self.__name + " {\n"
        for kv in self.__keyvals:
            self.__string += self.__indent
            self.__string += kv[0]
            self.__string += ": "
            self.__string += kv[1]
            self.__string += ";\n"
        self.__string += "}\n"
    
    def to_string(self):
        if self.__string is None:
            self.__create_string()
        return self.__string