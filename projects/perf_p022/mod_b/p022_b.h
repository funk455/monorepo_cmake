        #pragma once
        #include <string>
        #include "p021_b.h"
#include "p010_a.h"

        inline int p022_b_value() {
            (void)p021_b_value();
    (void)p010_a_value();
    return 42;
        }

        std::string p022_b_info();
