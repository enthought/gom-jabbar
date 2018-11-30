# gomjabbar
`gomjabbar` is a package which assists in the creation of unit tests for
ngspice code models.

The test programs which it creates are run independently of the ngspice
program. The interface file (`ifspec.ifs`) for the code model is used to
generate code which initializes the `Mif_Private_t` data structure which
is used by ngspice to interact with code models. By doing this, it is
possible for test code to call any function in the code model which
takes the `ARGS` argument. At a minimum, this includes the entry point
function for the code model (`C_Function_Name` in `ifspec.ifs`).
