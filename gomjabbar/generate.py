import contextlib
import os
import os.path as op
from subprocess import check_call
import sys
import uuid

import jinja2

from gomjabbar.ifs.build import (
    build_connections_list, build_parameters_list, count_static_vars,
    parse_file
)

BIN_DIR = op.join(op.abspath(sys.prefix), 'bin')
INCLUDE_DIR = op.join(op.abspath(sys.prefix), 'include')

DATA_DIR = op.join(op.dirname(__file__), 'data')
TEMPLATE_LOADER = jinja2.FileSystemLoader(DATA_DIR)
TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER, trim_blocks=True,
                                  keep_trailing_newline=True)
TEMPLATE_ENV.filters['array_size'] = lambda v: max(1, len(v))


@contextlib.contextmanager
def build_test(code_model_dir, code, parameters):
    """ Build some code model source into a program which can be used to test
    part of a code model.

    Parameters
    ----------
    code_model_dir : str
        The path of the directory of the code model being tested.
    code : str
        Source code which will be linked with the code model into a program.
    parameters : dict
        A dictionary of values which will be assigned to the PARAMETER_TABLE
        variables defined by the code model.
    """
    conns, params, num_vars = _get_template_context(code_model_dir, parameters)
    test_name = _generate_test_name()
    output = op.join(code_model_dir, test_name + '.mod')

    try:
        with open(output, 'w') as fp:
            _render_templates(fp, conns, params, num_vars)
            fp.write(code)

        yield _compile_test(output)
    finally:
        _clean_test(op.join(code_model_dir, test_name))


def _clean_test(path):
    """ Clean up after a call to _compile_test
    """
    path = op.abspath(path)
    remove_paths = [path + ext for ext in ('', '.c', '.o', '.mod')]
    for path in remove_paths:
        if op.exists(path):
            os.remove(path)


def _compile_test(path):
    """ Build an executable for a code model test.

    Returns the path of the resulting executable.
    """
    def _compile_obj(p):
        base_name = op.splitext(p)[0]
        c_file = base_name + '.c'
        obj_file = base_name + '.o'
        cmd = ['cc', '-c', '-o', obj_file, c_file, '-I' + INCLUDE_DIR]
        check_call(cmd)
        return obj_file

    def _preprocess_mod(p):
        cmd = [op.join(BIN_DIR, 'cmpp'), '-mod', p]
        check_call(cmd)

    code_dir, path = op.split(path)
    module_path = op.splitext(path)[0]
    code_dir = op.abspath(code_dir)
    with _in_dir(code_dir):
        # Preprocess the .mod file with cmpp
        _preprocess_mod(path)
        # Compile the resulting .c file
        obj_file = _compile_obj(path)

        # Make sure cfunc.o exists
        cfunc_obj_file = 'cfunc.o'
        if not op.exists(cfunc_obj_file):
            _preprocess_mod('cfunc.mod')
            cfunc_obj_file = _compile_obj('cfunc.c')

        # Link the resulting .o file with cfunc.o into an executable
        cmd = ['cc', '-o', module_path, cfunc_obj_file, obj_file]
        check_call(cmd)

    return op.join(code_dir, module_path)


def _generate_test_name():
    return '_' + uuid.uuid4().hex[:8]


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
    restore = op.abspath(op.curdir)
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

    macros_source = TEMPLATE_LOADER.get_source(TEMPLATE_ENV, 'macros.c')[0]
    fp.write(macros_source)
