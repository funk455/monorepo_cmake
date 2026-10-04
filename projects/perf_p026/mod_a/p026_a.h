        #pragma once
        #include <string>
        #include "p020_b.h"
#include "p014_b.h"

        inline int p026_a_value() {
            (void)p020_b_value();
    (void)p014_b_value();
    return 42;
        }

        std::string p026_a_info();
