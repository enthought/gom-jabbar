
void cm_dummy(ARGS) {
    double multiplier;

    if (INIT == 1) {
        multiplier = STATIC_VAR(multiplier) = 0.0;
    }
    else {
        multiplier = STATIC_VAR(multiplier);
    }

    OUTPUT(port) = PARAM(d) * multiplier;
    PARTIAL(port, port) = 0.0;
}
