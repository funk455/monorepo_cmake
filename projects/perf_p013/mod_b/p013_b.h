        #pragma once
        #include <string>
        #include "p010_c.h"
#include "p012_a.h"

        inline int p013_b_value() {
            (void)p010_c_value();
    (void)p012_a_value();
    return 42;
        }

        std::string p013_b_info();
