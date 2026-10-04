        #pragma once
        #include <string>
        #include "p023_b.h"
#include "p001_b.h"

        inline int p027_a_value() {
            (void)p023_b_value();
    (void)p001_b_value();
    return 42;
        }

        std::string p027_a_info();
