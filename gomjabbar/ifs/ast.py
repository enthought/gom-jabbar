
class AstNode(object):
    def get_children(self):
        return ()

    def __iter__(self):
        for c in self.get_children():
            yield c


class CType(AstNode):
    def __init__(self, value, lineno=None):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return 'CType({})'.format(self.value)


class Dash(AstNode):
    def __init__(self, lineno=None):
        self.lineno = lineno

    def __repr__(self):
        return 'Dash'


class Direction(AstNode):
    def __init__(self, value, lineno=None):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return 'Direction({})'.format(self.value)


class DType(AstNode):
    def __init__(self, value, lineno=None):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return 'DType({})'.format(self.value)


class Identifier(AstNode):
    def __init__(self, value, lineno=None):
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return 'Identifier({})'.format(self.value)


class Ifs(AstNode):
    def __init__(self, nodes, name_table=None, parameter_table=None,
                 port_table=None, static_var_table=None):
        self.nodes = nodes
        self.name_table = name_table
        self.parameter_table = parameter_table
        self.port_table = port_table
        self.static_var_table = static_var_table
        self.lineno = 1

    def get_children(self):
        return self.nodes

    def __repr__(self):
        nodes = '\n'.join('{!r}'.format(n) for n in self)
        if nodes:
            nodes = '\n' + nodes + '\n'
        return 'Ifs({})'.format(nodes)


class Range(AstNode):
    def __init__(self, low=None, high=None, lineno=None):
        self.low = Dash(lineno=lineno) if low is None else low
        self.high = Dash(lineno=lineno) if high is None else high
        self.lineno = lineno

    def __repr__(self):
        return 'Range({!r}, {!r})'.format(self.low, self.high)


class Table(AstNode):
    def __init__(self, type_, nodes, lineno=None):
        self.type = type_
        self.nodes = nodes
        self.lineno = lineno

    def get_children(self):
        return self.nodes

    def __repr__(self):
        nodes = '\n'.join('\t{!r}'.format(n) for n in self)
        if nodes:
            nodes = '\n' + nodes + '\n'
        return '{}({})'.format(self.type, nodes)


class TableRow(AstNode):
    def __init__(self, type_, value, lineno=None):
        self.type = type_
        self.value = value
        self.lineno = lineno

    def __repr__(self):
        return '{}({!r})'.format(self.type, self.value)
