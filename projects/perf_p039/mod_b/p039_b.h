        #pragma once
        #include <string>
        #include "p008_b.h"
#include "p035_a.h"

        inline int p039_b_value() {
            (void)p008_b_value();
    (void)p035_a_value();
    return 42;
        }

        std::string p039_b_info();
