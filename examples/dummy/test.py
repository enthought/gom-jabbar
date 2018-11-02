from __future__ import print_function

import os.path as op
from subprocess import check_output

from gomjabbar.generate import build_test

mod_code = """
extern void cm_dummy(ARGS);

int main(int argc, char **argv) {
    Mif_Private_t* mif_private = allocate_mif_private();
    init_connections(mif_private);
    init_params(mif_private);

    INIT = MIF_TRUE;
    cm_dummy(mif_private);

    INIT = MIF_FALSE;
    cm_dummy(mif_private);

    free_mif_private(mif_private);
    return 0;
}
"""


def run(path):
    output = check_output([path])
    return output.decode('utf8').strip()


def main():
    parameters = {
        'd': 42.0,
    }
    with build_test(op.dirname(__file__), 'test', mod_code, parameters) as pth:
        run(pth)


if __name__ == '__main__':
    main()
