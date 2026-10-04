        #pragma once
        #include <string>
        #include "p010_c.h"
#include "p010_b.h"

        inline int p032_c_value() {
            (void)p010_c_value();
    (void)p010_b_value();
    return 42;
        }

        std::string p032_c_info();
