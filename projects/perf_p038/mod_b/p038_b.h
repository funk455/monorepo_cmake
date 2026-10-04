        #pragma once
        #include <string>
        #include "p030_c.h"
#include "p017_b.h"

        inline int p038_b_value() {
            (void)p030_c_value();
    (void)p017_b_value();
    return 42;
        }

        std::string p038_b_info();
