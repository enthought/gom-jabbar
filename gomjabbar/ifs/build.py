from __future__ import print_function

from gomjabbar.const import (
    NAME_TABLE, PARAMETER_TABLE, PORT_TABLE, STATIC_VAR_TABLE,
    ALLOWED_TYPES, ARRAY, ARRAY_BOUNDS, DATA_TYPE, DEFAULT_TYPE, DEFAULT_VALUE,
    DESCRIPTION, DIRECTION, LIMITS, NULL_ALLOWED, PARAMETER_NAME, PORT_NAME,
    STATIC_VAR_NAME
)
from .ast import Dash, Ifs, Table, TableRow
from .lexer import IfsLexer
from .parser import IfsParser

PORT_TYPES = {
    'v': 'MIF_VOLTAGE',
    'vd': 'MIF_DIFF_VOLTAGE',
    'i': 'MIF_CURRENT',
    'id': 'MIF_DIFF_CURRENT',
    'vnam': 'MIF_VSOURCE_CURRENT',
    'g': 'MIF_CONDUCTANCE',
    'gd': 'MIF_DIFF_CONDUCTANCE',
    'h': 'MIF_RESISTANCE',
    'hd': 'MIF_DIFF_RESISTANCE',
    'd': 'MIF_DIGITAL',
}
VALUE_UNION_NAMES = {
    'boolean': (bool, 'bvalue'),
    'int': (int, 'ivalue'),
    'real': (float, 'rvalue'),
    'complex': (lambda x: x, 'cvalue'),
    'string': (lambda x: '"{}"'.format(x), 'svalue'),
    'pointer': (lambda x: x, 'pvalue'),
}


class _Namespace(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def build_connections_list(port_table):
    """ Convert the PORT_TABLE items into a list which can supply data to the
    connections code template.
    """
    connections = []
    for item in transpose_table(port_table):
        conn = {
            'name': item.PORT_NAME.value,
            'is_input': item.DIRECTION.value in ('in', 'inout'),
            'is_output': item.DIRECTION.value in ('out', 'inout'),
            'ports': [
                {'type': PORT_TYPES.get(item.DEFAULT_TYPE.value,
                                        'MIF_USER_DEFINED')}
            ],
        }
        connections.append(conn)
    return connections


def build_parameters_list(parameter_table, parameter_values):
    """ Convert the PARAMETER_TABLE items into a list which can supply data to
    the params code template.
    """
    parameters = []
    for item in transpose_table(parameter_table):
        param_name = item.PARAMETER_NAME.value
        cast, unionmember = VALUE_UNION_NAMES[item.DATA_TYPE.value]
        param = {
            'name': param_name,
            'unionmember': unionmember,
        }
        value = parameter_values.get(param_name, item.DEFAULT_VALUE)
        if not isinstance(value, Dash):
            if isinstance(value, list):
                value = [cast(v) for v in value]
            else:
                value = [cast(value)]
            param['values'] = value
        parameters.append(param)
    return parameters


def compact_ast(ifs_ast):
    """ Group all tables in an `Ifs` object by their type.

    NOTE: If there is more than one NAME_TABLE, only the final one given in
    the .ifs source file will be kept.
    """
    tables = {}
    compacted = []
    ifs_kwargs = {}

    for tab in ifs_ast:
        tables.setdefault(tab.type, []).append(tab)

    # The last NAME_TABLE is the one which is used
    name_tabs = tables.get(NAME_TABLE, [])
    if name_tabs:
        compacted.append(name_tabs[-1])
        ifs_kwargs['name_table'] = name_tabs[-1]

    compaction_data = {
        PARAMETER_TABLE: {ARRAY, ARRAY_BOUNDS, DATA_TYPE, DEFAULT_VALUE,
                          DESCRIPTION, LIMITS, NULL_ALLOWED, PARAMETER_NAME},
        PORT_TABLE: {ALLOWED_TYPES, ARRAY, ARRAY_BOUNDS, DEFAULT_TYPE,
                     DESCRIPTION, DIRECTION, NULL_ALLOWED, PORT_NAME},
        STATIC_VAR_TABLE: {ARRAY, DATA_TYPE, DESCRIPTION, STATIC_VAR_NAME},
    }
    for name, expected_rows in compaction_data.items():
        if name in tables:
            table = compact_tables(name, tables[name], expected_rows)
            compacted.append(table)
            ifs_kwargs[name.lower()] = table

    return Ifs(compacted, **ifs_kwargs)


def compact_tables(table_type, tables, expected_row_names):
    """ Collapse a list of tables of the same type into a single table
    """
    rows = {}
    for tab in tables:
        expected_rows = expected_row_names.copy()
        col_count = len(tab.nodes[0].value)
        for row in tab:
            rows.setdefault(row.type, []).extend(row.value)
            expected_rows.remove(row.type)

        for typename in expected_rows:
            value = [None] * col_count
            rows.setdefault(row.type, []).extend(value)

    return Table(table_type, [TableRow(k, v) for k, v in rows.items()])


def count_static_vars(static_vars_table):
    """ Count the number of variables defined in the STATIC_VARS_TABLE
    """
    return len(static_vars_table.nodes[0].value)


def parse_file(path):
    """ Parse a single .ifs file and return its AST
    """
    parser = IfsParser()
    with open(path, 'r') as fp:
        ast = parser.parse(fp.read())
    return compact_ast(ast)


def tokenize_file(path):
    """ Show the result of running the IfsLexer on a file.
    """
    lexer = IfsLexer()
    with open(path, 'r') as fp:
        lexer.lexer.input(fp.read())

    while True:
        tok = lexer.lexer.token()
        if tok is None:
            break
        print(tok)


def transpose_table(table):
    """ Convert a `Table` to a list of objects which represent the "columns".
    """
    items = [{} for _ in range(len(table.nodes[0].value))]
    for row in table:
        for i, value in enumerate(row.value):
            items[i][row.type] = value
    return [_Namespace(**d) for d in items]


if __name__ == '__main__':
    import argparse

    argparser = argparse.ArgumentParser()
    argparser.add_argument('-l', '--lex', type=str, default='')
    argparser.add_argument('-p', '--parse', type=str, default='')
    args = argparser.parse_args()

    if args.lex:
        tokenize_file(args.lex)
    elif args.parse:
        print(parse_file(args.parse))
