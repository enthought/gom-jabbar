import contextlib
import os
import os.path as op
from subprocess import check_call
import sys

import jinja2

from gomjabbar.ifs.build import (
    build_connections_list, build_parameters_list, count_static_vars,
    parse_file
)

DATA_DIR = op.join(op.dirname(__file__), 'data')
TEMPLATE_LOADER = jinja2.FileSystemLoader(DATA_DIR)
TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER, trim_blocks=True,
                                  keep_trailing_newline=True)
TEMPLATE_ENV.filters['array_size'] = lambda v: max(1, len(v))


def build_test(dir_path, name, code, parameters_dict):
    """ Build a C source file which can be used to test part of a code model.
    """
    conns, params, num_vars = _get_template_context(dir_path, parameters_dict)
    output = op.join(dir_path, name + '.mod')
    with open(output, 'w') as fp:
        _render_templates(fp, conns, params, num_vars)
        fp.write(code)

    return _compile_test(output)


def _compile_test(path):
    """ Build an executable for a code model test.

    Returns the path of the resulting executable.
    """
    code_dir, path = op.split(path)
    root = op.abspath(sys.prefix)
    code_dir = op.abspath(code_dir)
    with _in_dir(code_dir):
        # Preprocess the .mod file with cmpp
        cmd = [op.join(root, 'bin', 'cmpp'), '-mod', path]
        check_call(cmd)

        # Compile the resulting .c file
        module_path = op.splitext(path)[0]
        c_file = module_path + '.c'
        obj_file = module_path + '.o'
        cmd = ['cc', '-c', '-o', obj_file, c_file,
               '-I' + op.join(root, 'include')]
        check_call(cmd)

        # Link the resulting .o file with cfunc.o into an executable
        cfunc_obj_file = op.join(op.dirname(path), 'cfunc.o')
        cmd = ['cc', '-o', module_path, cfunc_obj_file, obj_file]
        check_call(cmd)

    return op.join(code_dir, module_path)


def _get_template_context(dir_path, parameters_dict):
    ast = parse_file(op.join(dir_path, 'ifspec.ifs'))
    connections, parameters = [], []
    num_static_vars = 0
    if ast.port_table:
        connections = build_connections_list(ast.port_table)
    if ast.parameter_table:
        parameters = build_parameters_list(ast.parameter_table,
                                           parameters_dict)
    if ast.static_var_table:
        num_static_vars = count_static_vars(ast.static_var_table)
    return connections, parameters, num_static_vars


@contextlib.contextmanager
def _in_dir(path):
    restore = op.curdir
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(restore)


def _render_templates(fp, connections, parameters, num_static_vars):
    template = TEMPLATE_ENV.get_template('alloc.c.jinja')
    context = {
        'num_conns': len(connections),
        'num_params': len(parameters),
        'num_static_vars': num_static_vars,
    }
    fp.write(template.render(context))

    template = TEMPLATE_ENV.get_template('connections.c.jinja')
    context = {'connections': connections}
    fp.write(template.render(context))

    template = TEMPLATE_ENV.get_template('params.c.jinja')
    context = {'parameters': parameters}
    fp.write(template.render(context))
