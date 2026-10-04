        #pragma once
        #include <string>
        #include "p028_a.h"
#include "p012_a.h"

        inline int p028_b_value() {
            (void)p028_a_value();
    (void)p012_a_value();
    return 42;
        }

        std::string p028_b_info();
