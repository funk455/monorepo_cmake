        #pragma once
        #include <string>
        #include "p040_c.h"
#include "p038_a.h"

        inline int p049_c_value() {
            (void)p040_c_value();
    (void)p038_a_value();
    return 42;
        }

        std::string p049_c_info();
