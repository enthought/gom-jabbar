
NAME_TABLE = 'NAME_TABLE'
PARAMETER_TABLE = 'PARAMETER_TABLE'
PORT_TABLE = 'PORT_TABLE'
STATIC_VAR_TABLE = 'STATIC_VAR_TABLE'

ALLOWED_TYPES = 'ALLOWED_TYPES'
ARRAY = 'ARRAY'
ARRAY_BOUNDS = 'ARRAY_BOUNDS'
C_FUNCTION_NAME = 'C_FUNCTION_NAME'
DATA_TYPE = 'DATA_TYPE'
DEFAULT_TYPE = 'DEFAULT_TYPE'
DEFAULT_VALUE = 'DEFAULT_VALUE'
DESCRIPTION = 'DESCRIPTION'
DIRECTION = 'DIRECTION'
LIMITS = 'LIMITS'
NULL_ALLOWED = 'NULL_ALLOWED'
PARAMETER_NAME = 'PARAMETER_NAME'
PORT_NAME = 'PORT_NAME'
SPICE_MODEL_NAME = 'SPICE_MODEL_NAME'
STATIC_VAR_NAME = 'STATIC_VAR_NAME'


class BaseType(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '{}({})'.format(type(self).__name__, self.value)


class CType(BaseType):
    pass


class Dash(object):
    def __repr__(self):
        return 'Dash'


class Direction(BaseType):
    pass


class DType(BaseType):
    pass


class Identifier(BaseType):
    pass


class Ifs(object):
    def __init__(self, tables, name_table=None, parameter_table=None,
                 port_table=None, static_var_table=None):
        self.tables = tables
        self.name_table = name_table
        self.parameter_table = parameter_table
        self.port_table = port_table
        self.static_var_table = static_var_table

    def __repr__(self):
        tabs = '\n'.join('{!r}'.format(t) for t in self.tables)
        if tabs:
            tabs = '\n' + tabs + '\n'
        return 'Ifs({})'.format(tabs)


class Range(object):
    def __init__(self, low=None, high=None):
        self.low = Dash() if low is None else low
        self.high = Dash() if high is None else high

    def __repr__(self):
        return 'Range({!r}, {!r})'.format(self.low, self.high)


class Table(object):
    def __init__(self, _type, rows):
        self.type = _type
        self.rows = rows

    def __repr__(self):
        rows = '\n'.join('\t{!r}'.format(r) for r in self.rows)
        if rows:
            rows = '\n' + rows + '\n'
        return '{}({})'.format(self.type, rows)


class TableRow(object):
    def __init__(self, _type, value):
        self.type = _type
        self.value = value

    def __repr__(self):
        return '{}({!r})'.format(self.type, self.value)
