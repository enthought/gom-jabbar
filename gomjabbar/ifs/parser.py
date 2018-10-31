from __future__ import print_function

import os.path as op

import ply.yacc as yacc

from .ast import Dash, Ifs, Range, Table, TableRow
from .lexer import IfsLexer


def _handle_list_reduction(p):
    items = p[1]
    if not isinstance(items, list):
        items = [items]
    p[0] = items


def _handle_list_or_empty_reduction(p):
    if len(p) > 2:
        items = p[2]
        if items is None:
            items = []
        elif not isinstance(items, list):
            items = [items]
        head = p[1]
        if head is None:
            head = []
        p[0] = head + items


class IfsParser(object):
    """ Parser for .ifs files
    """
    tokens = IfsLexer.tokens

    def p_ifs_table(self, p):
        """ ifs_file : list_of_tables """
        p[0] = Ifs(p[1])

    def p_list_of_tables1(self, p):
        """ list_of_tables : list_of_tables table """
        items = p[2]
        if not isinstance(items, list):
            items = [items]
        p[0] = p[1] + items

    def p_list_of_tables2(self, p):
        """ list_of_tables : table """
        _handle_list_reduction(p)

    def p_table(self, p):
        """ table : NAME_TABLE name_table
                  | PORT_TABLE port_table
                  | PARAMETER_TABLE parameter_table
                  | STATIC_VAR_TABLE static_var_table """
        p[0] = Table(p[1], p[2], lineno=p.lineno(1))

    def p_name_table(self, p):
        """ name_table : name_table name_table_item
                       | empty """
        _handle_list_or_empty_reduction(p)

    def p_name_table_item(self, p):
        """ name_table_item : C_FUNCTION_NAME identifier
                            | SPICE_MODEL_NAME identifier
                            | DESCRIPTION string """
        p[0] = TableRow(p[1], p[2], lineno=p.lineno(1))

    def p_port_table(self, p):
        """ port_table : port_table port_table_item
                       | empty """
        _handle_list_or_empty_reduction(p)

    def p_port_table_item(self, p):
        """ port_table_item : PORT_NAME list_of_ids
                            | DESCRIPTION list_of_strings
                            | DIRECTION list_of_directions
                            | DEFAULT_TYPE list_of_ctypes
                            | ALLOWED_TYPES list_of_ctype_lists
                            | ARRAY list_of_bool
                            | ARRAY_BOUNDS list_of_array_bounds
                            | NULL_ALLOWED list_of_bool """
        p[0] = TableRow(p[1], p[2], lineno=p.lineno(1))

    def p_parameter_table(self, p):
        """ parameter_table : parameter_table parameter_table_item
                            | empty """
        _handle_list_or_empty_reduction(p)

    def p_parameter_table_item(self, p):
        """ parameter_table_item : PARAMETER_NAME list_of_ids
                                 | DESCRIPTION list_of_strings
                                 | DATA_TYPE list_of_dtypes
                                 | DEFAULT_VALUE list_of_values
                                 | LIMITS list_of_ranges
                                 | ARRAY list_of_bool
                                 | ARRAY_BOUNDS list_of_array_bounds
                                 | NULL_ALLOWED list_of_bool """
        p[0] = TableRow(p[1], p[2], lineno=p.lineno(1))

    def p_static_var_table(self, p):
        """ static_var_table : static_var_table static_var_table_item
                             | empty """
        _handle_list_or_empty_reduction(p)

    def p_static_var_table_item(self, p):
        """ static_var_table_item : STATIC_VAR_NAME list_of_ids
                                  | DESCRIPTION list_of_strings
                                  | DATA_TYPE list_of_dtypes
                                  | ARRAY list_of_bool """
        p[0] = TableRow(p[1], p[2], lineno=p.lineno(1))

    def p_list_of_ids(self, p):
        """ list_of_ids : list_of_ids identifier
                        | empty """
        _handle_list_or_empty_reduction(p)

    def p_list_of_array_bounds(self, p):
        """ list_of_array_bounds : list_of_array_bounds int_range
                                 | list_of_array_bounds identifier
                                 | empty """
        _handle_list_or_empty_reduction(p)

    def p_list_of_strings(self, p):
        """ list_of_strings : list_of_strings string
                            | empty """
        _handle_list_or_empty_reduction(p)

    def p_list_of_directions(self, p):
        """ list_of_directions : list_of_directions direction
                               | empty """
        _handle_list_or_empty_reduction(p)

    def p_direction(self, p):
        """ direction : DIR_IN
                      | DIR_OUT
                      | DIR_INOUT """
        p[0] = p[1]

    def p_list_of_bool(self, p):
        """ list_of_bool : list_of_bool bool
                         | empty """
        _handle_list_or_empty_reduction(p)

    def p_list_of_ctypes(self, p):
        """ list_of_ctypes : list_of_ctypes ctype
                           | empty """
        _handle_list_or_empty_reduction(p)

    def p_ctype(self, p):
        """ ctype : CTYPE_V
                  | CTYPE_VD
                  | CTYPE_VNAM
                  | CTYPE_I
                  | CTYPE_ID
                  | CTYPE_G
                  | CTYPE_GD
                  | CTYPE_H
                  | CTYPE_HD
                  | CTYPE_D
                  | identifier """
        p[0] = p[1]

    def p_list_of_dtypes(self, p):
        """ list_of_dtypes : list_of_dtypes dtype
                           | empty """
        _handle_list_or_empty_reduction(p)

    def p_dtype(self, p):
        """ dtype : DTYPE_REAL
                  | DTYPE_INT
                  | DTYPE_BOOLEAN
                  | DTYPE_COMPLEX
                  | DTYPE_STRING
                  | DTYPE_POINTER """
        p[0] = p[1]

    def p_list_of_ranges(self, p):
        """ list_of_ranges : list_of_ranges range
                           | empty """
        _handle_list_or_empty_reduction(p)

    def p_int_range1(self, p):
        """ int_range : DASH """
        p[0] = Range(lineno=p.lineno(1))

    def p_int_range2(self, p):
        """ int_range : LBRACKET int_or_dash maybe_comma int_or_dash RBRACKET
        """
        p[0] = Range(p[2], p[4], lineno=p.lineno(1))

    def p_maybe_comma(self, p):
        """ maybe_comma : COMMA
                        | empty """
        pass

    def p_int_or_dash1(self, p):
        """ int_or_dash : DASH """
        p[0] = Dash(lineno=p.lineno(1))

    def p_int_or_dash2(self, p):
        """ int_or_dash : integer_value """
        p[0] = p[1]

    def p_range1(self, p):
        """ range : DASH """
        p[0] = Range(lineno=p.lineno(1))

    def p_range2(self, p):
        """ range : LBRACKET number_or_dash maybe_comma number_or_dash RBRACKET
        """
        p[0] = Range(p[2], p[4], lineno=p.lineno(1))

    def p_number_or_dash1(self, p):
        """ number_or_dash : DASH """
        p[0] = Dash(lineno=p.lineno(1))

    def p_number_or_dash2(self, p):
        """ number_or_dash : number """
        p[0] = p[1]

    def p_list_of_values(self, p):
        """ list_of_values : list_of_values value_or_dash
                           | empty """
        _handle_list_or_empty_reduction(p)

    def p_value_or_dash1(self, p):
        """ value_or_dash : DASH """
        p[0] = Dash(lineno=p.lineno(1))

    def p_value_or_dash2(self, p):
        """ value_or_dash : value """
        p[0] = p[1]

    def p_value(self, p):
        """ value : string
                  | bool
                  | complex
                  | number """
        p[0] = p[1]

    def p_complex(self, p):
        """ complex : LANGLE real maybe_comma real RANGLE """
        p[0] = complex(p[2], p[4])

    def p_list_of_ctype_lists(self, p):
        """ list_of_ctype_lists : list_of_ctype_lists delimited_ctype_list
                                | empty """
        _handle_list_or_empty_reduction(p)

    def p_delimited_ctype_list(self, p):
        """ delimited_ctype_list : LBRACKET ctype_list RBRACKET """
        p[0] = [p[2]]

    def p_ctype_list1(self, p):
        """ ctype_list : ctype """
        _handle_list_reduction(p)

    def p_ctype_list2(self, p):
        """ ctype_list : ctype_list maybe_comma ctype """
        items = p[3]
        if not isinstance(items, list):
            items = [items]
        p[0] = p[1] + items

    def p_bool(self, p):
        """ bool : BOOL_YES
                 | BOOL_NO """
        p[0] = p[1]

    def p_string(self, p):
        """ string : STRING_LITERAL """
        p[0] = p[1]

    def p_identifier(self, p):
        """ identifier : IDENTIFIER """
        p[0] = p[1]

    def p_number(self, p):
        """ number : real
                   | integer_value """
        p[0] = p[1]

    def p_integer_value(self, p):
        """ integer_value : integer """
        p[0] = p[1]

    def p_real(self, p):
        """ real : REAL_LITERAL """
        p[0] = p[1]

    def p_integer(self, p):
        """ integer : INT_LITERAL """
        p[0] = p[1]

    def p_empty(self, p):
        """ empty : """
        pass

    def p_error(self, t):
        msg = 'invalid syntax: {} ({})'
        raise RuntimeError(msg.format(t, t.lineno))

    def __init__(self):
        parse_dir = op.join(op.dirname(__file__), 'tables')
        parse_mod = 'gomjabbar.ifs.tables.parsetab'

        self.parser = yacc.yacc(
            module=self,
            method='LALR',
            start='ifs_file',
            tabmodule=parse_mod,
            outputdir=parse_dir,
            optimize=1,
            debug=0
        )

    def parse(self, source, filename='ifspec.ifs'):
        """ Parse source string and create abstract syntax tree (AST).
        """
        self.lexer = IfsLexer(filename)
        return self.parser.parse(source, debug=0, lexer=self.lexer.lexer)
