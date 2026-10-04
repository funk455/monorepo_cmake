        #pragma once
        #include <string>
        #include "p024_c.h"
#include "p024_b.h"

        inline int p050_c_value() {
            (void)p024_c_value();
    (void)p024_b_value();
    return 42;
        }

        std::string p050_c_info();
