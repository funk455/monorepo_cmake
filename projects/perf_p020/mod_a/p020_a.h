        #pragma once
        #include <string>
        #include "p018_a.h"
#include "p019_b.h"

        inline int p020_a_value() {
            (void)p018_a_value();
    (void)p019_b_value();
    return 42;
        }

        std::string p020_a_info();
