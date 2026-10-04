        #pragma once
        #include <string>
        #include "p008_a.h"
#include "p037_b.h"

        inline int p044_b_value() {
            (void)p008_a_value();
    (void)p037_b_value();
    return 42;
        }

        std::string p044_b_info();
