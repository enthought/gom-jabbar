
#define GJ_SETUP(name) \
Mif_Private_t* name = allocate_mif_private();\
init_connections(name);\
init_params(name);

#define GJ_TEARDOWN(name) \
free_mif_private(name);
