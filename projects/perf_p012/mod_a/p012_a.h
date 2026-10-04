        #pragma once
        #include <string>
        #include "p009_b.h"
#include "p005_c.h"

        inline int p012_a_value() {
            (void)p009_b_value();
    (void)p005_c_value();
    return 42;
        }

        std::string p012_a_info();
