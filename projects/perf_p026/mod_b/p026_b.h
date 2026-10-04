        #pragma once
        #include <string>
        #include "p025_a.h"
#include "p004_a.h"

        inline int p026_b_value() {
            (void)p025_a_value();
    (void)p004_a_value();
    return 42;
        }

        std::string p026_b_info();
