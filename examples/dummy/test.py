from __future__ import print_function

import os.path as op
from subprocess import check_output

from gomjabbar.generate import build_test

mod_code = """
#include <stdio.h>

int main(int argc, char **argv) {
    GJ_SETUP(mif_private);

    INIT = MIF_TRUE;
    cm_dummy(mif_private);

    printf("%4.1f\\n", PARAM(d));

    INIT = MIF_FALSE;
    cm_dummy(mif_private);

    GJ_TEARDOWN(mif_private);
    return 0;
}
"""


def run(path):
    output = check_output([path])
    return output.decode('utf8').strip()


def main():
    code_model_dir = op.dirname(__file__)
    parameters = {
        'd': 42.0,
    }
    with build_test(code_model_dir, mod_code, parameters) as pth:
        output = run(pth)
        assert output == '42.0'


if __name__ == '__main__':
    main()
