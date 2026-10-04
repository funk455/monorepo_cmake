        #pragma once
        #include <string>
        #include "p024_c.h"
#include "p018_b.h"

        inline int p030_c_value() {
            (void)p024_c_value();
    (void)p018_b_value();
    return 42;
        }

        std::string p030_c_info();
