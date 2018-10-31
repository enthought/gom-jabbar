from __future__ import print_function

import os.path as op
import re

import ply.lex as lex

from .ast import CType, Direction, DType, Identifier


class IfsLexer(object):
    """ Lexer for .ifs files
    """
    states = (
        ('bool', 'inclusive'),
        ('ctype', 'inclusive'),
        ('dir', 'inclusive'),
        ('dtype', 'inclusive'),
        ('comment', 'exclusive'),
        ('stringl', 'exclusive'),
    )
    tokens = (
        'STRING_LITERAL',
        'ALLOWED_TYPES',
        'ARRAY',
        'ARRAY_BOUNDS',
        'C_FUNCTION_NAME',
        'PORT_NAME',
        'PORT_TABLE',
        'DATA_TYPE',
        'DEFAULT_TYPE',
        'DEFAULT_VALUE',
        'DESCRIPTION',
        'DIRECTION',
        'STATIC_VAR_NAME',
        'STATIC_VAR_TABLE',
        'LIMITS',
        'NAME_TABLE',
        'NULL_ALLOWED',
        'PARAMETER_NAME',
        'PARAMETER_TABLE',
        'SPICE_MODEL_NAME',

        'BOOL_YES',
        'BOOL_NO',

        'CTYPE_V',
        'CTYPE_VD',
        'CTYPE_VNAM',
        'CTYPE_I',
        'CTYPE_ID',
        'CTYPE_G',
        'CTYPE_GD',
        'CTYPE_H',
        'CTYPE_HD',
        'CTYPE_D',

        'DIR_IN',
        'DIR_OUT',
        'DIR_INOUT',

        'DTYPE_REAL',
        'DTYPE_INT',
        'DTYPE_BOOLEAN',
        'DTYPE_COMPLEX',
        'DTYPE_STRING',
        'DTYPE_POINTER',

        'LANGLE',
        'RANGLE',
        'LBRACKET',
        'RBRACKET',
        'COMMA',
        'DASH',

        'IDENTIFIER',
        'INT_LITERAL',
        'REAL_LITERAL',
    )

    def t_start_comment_state(self, t):
        r'/\*'
        t.lexer.push_state('comment')

    def t_comment_non_star(self, t):
        r'[^*\n]+'
        # eat anything that's not a '*'
        pass

    def t_comment_stars(self, t):
        r'\*(?!/)'
        # eat up '*'s not followed by '/'s
        pass

    def t_comment_nl(self, t):
        r'\n'
        # new line
        t.lexer.lineno += 1

    def t_comment_end(self, t):
        r'\*+/'
        t.lexer.pop_state()

    # supress PLY warning
    t_comment_ignore = ''

    def t_comment_error(self, t):
        raise RuntimeError('Error while scanning comment')

    def t_start_stringl_state(self, t):
        r'"'
        t.lexer.push_state('stringl')

    def t_stringl_content(self, t):
        r'[^"]+'
        t.type = 'STRING_LITERAL'
        return t

    def t_stringl_end(self, t):
        r'"'
        t.lexer.pop_state()

    # supress PLY warning
    t_stringl_ignore = ''

    def t_stringl_error(self, t):
        raise RuntimeError('Error while scanning string literal')

    def t_ARRAY_BOUNDS(self, t):
        r'vector_bounds[ \t\n]*:'
        t.value = t.type
        return t

    def t_C_FUNCTION_NAME(self, t):
        r'c_function_name[ \t\n]*:'
        t.value = t.type
        return t

    def t_PORT_NAME(self, t):
        r'port_name[ \t\n]*:'
        t.value = t.type
        return t

    def t_PORT_TABLE(self, t):
        r'port_table[ \t\n]*:'
        t.value = t.type
        return t

    def t_DEFAULT_VALUE(self, t):
        r'default_value[ \t\n]*:'
        t.value = t.type
        return t

    def t_DESCRIPTION(self, t):
        r'description[ \t\n]*:'
        t.value = t.type
        return t

    def t_STATIC_VAR_NAME(self, t):
        r'static_var_name[ \t\n]*:'
        t.value = t.type
        return t

    def t_STATIC_VAR_TABLE(self, t):
        r'static_var_table[ \t\n]*:'
        t.value = t.type
        return t

    def t_LIMITS(self, t):
        r'limits[ \t\n]*:'
        t.value = t.type
        return t

    def t_NAME_TABLE(self, t):
        r'name_table[ \t\n]*:'
        t.value = t.type
        return t

    def t_PARAMETER_NAME(self, t):
        r'parameter_name[ \t\n]*:'
        t.value = t.type
        return t

    def t_PARAMETER_TABLE(self, t):
        r'parameter_table[ \t\n]*:'
        t.value = t.type
        return t

    def t_SPICE_MODEL_NAME(self, t):
        r'spice_model_name[ \t\n]*:'
        t.value = t.type
        return t

    def t_ALLOWED_TYPES(self, t):
        r'allowed_types[ \t\n]*:'
        t.value = t.type
        t.lexer.push_state('ctype')
        return t

    def t_ARRAY(self, t):
        r'vector[ \t\n]*:'
        t.value = t.type
        t.lexer.push_state('bool')
        return t

    def t_DATA_TYPE(self, t):
        r'data_type[ \t\n]*:'
        t.value = t.type
        t.lexer.push_state('dtype')
        return t

    def t_DEFAULT_TYPE(self, t):
        r'default_type[ \t\n]*:'
        t.value = t.type
        t.lexer.push_state('ctype')
        return t

    def t_DIRECTION(self, t):
        r'direction[ \t\n]*:'
        t.value = t.type
        t.lexer.push_state('dir')
        return t

    def t_NULL_ALLOWED(self, t):
        r'null_allowed[ \t\n]*:'
        t.value = t.type
        t.lexer.push_state('bool')
        return t

    def t_BOOL_YES(self, t):
        r'true'
        t.value = True
        return t

    def t_BOOL_NO(self, t):
        r'false'
        t.value = False
        return t

    def t_bool_BOOL_YES(self, t):
        r'yes'
        t.value = True
        return t

    def t_bool_BOOL_NO(self, t):
        r'no'
        t.value = False
        return t

    def t_bool_end(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.pop_state()

    def t_ctype_CTYPE_V(self, t):
        r'v(?!d|nam)'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_VD(self, t):
        r'vd'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_VNAM(self, t):
        r'vnam'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_I(self, t):
        r'i(?!d)'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_ID(self, t):
        r'id'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_G(self, t):
        r'g(?!d)'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_GD(self, t):
        r'gd'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_H(self, t):
        r'h(?!d)'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_HD(self, t):
        r'hd'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_CTYPE_D(self, t):
        r'd'
        t.value = CType(t.value, lineno=t.lexer.lineno)
        return t

    def t_ctype_end(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.pop_state()

    def t_dir_DIR_IN(self, t):
        r'in(?!out)'
        t.value = Direction(t.value)
        return t

    def t_dir_DIR_OUT(self, t):
        r'out'
        t.value = Direction(t.value)
        return t

    def t_dir_DIR_INOUT(self, t):
        r'inout'
        t.value = Direction(t.value)
        return t

    def t_dir_end(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.pop_state()

    def t_dtype_DTYPE_REAL(self, t):
        r'real'
        t.value = DType(t.value, lineno=t.lexer.lineno)
        return t

    def t_dtype_DTYPE_INT(self, t):
        r'int'
        t.value = DType(t.value, lineno=t.lexer.lineno)
        return t

    def t_dtype_DTYPE_BOOLEAN(self, t):
        r'boolean'
        t.value = DType(t.value, lineno=t.lexer.lineno)
        return t

    def t_dtype_DTYPE_COMPLEX(self, t):
        r'complex'
        t.value = DType(t.value, lineno=t.lexer.lineno)
        return t

    def t_dtype_DTYPE_STRING(self, t):
        r'string'
        t.value = DType(t.value, lineno=t.lexer.lineno)
        return t

    def t_dtype_DTYPE_POINTER(self, t):
        r'pointer'
        t.value = DType(t.value, lineno=t.lexer.lineno)
        return t

    def t_dtype_end(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.lexer.pop_state()

    t_LANGLE = r'<'
    t_RANGLE = r'>'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COMMA = r','
    t_DASH = r'-'

    def t_IDENTIFIER(self, t):
        r'[a-z_]+\w*'
        t.value = Identifier(t.value, lineno=t.lexer.lineno)
        return t

    def t_REAL_LITERAL(self, t):
        r'''[+-]?\d+\.\d*(e[+-]?\d+)?|
            [+-]?\d*\.\d+(e[+-]?\d+)?|
            [+-]?\d+(e[+-]?\d+)'''
        t.value = float(t.value)
        return t

    def t_INT_LITERAL(self, t):
        r'[+-]?\d+(?!e)'
        t.value = int(t.value)
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore = ' \t'

    def t_error(self, t):
        raise RuntimeError('invalid syntax: {}'.format(t))

    def __init__(self, filename='ifspec.ifs'):
        lex_dir = op.join(op.dirname(__file__), 'tables')
        lex_module = 'gomjabbar.ifs.tables.lextab'

        self.lexer = lex.lex(
            module=self, reflags=re.VERBOSE | re.IGNORECASE,
            lextab=lex_module, outputdir=lex_dir, optimize=1,
        )
        self.filename = filename
        self.lexer.filename = filename
