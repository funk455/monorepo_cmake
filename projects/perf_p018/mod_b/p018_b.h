        #pragma once
        #include <string>
        #include "p006_a.h"
#include "p017_c.h"

        inline int p018_b_value() {
            (void)p006_a_value();
    (void)p017_c_value();
    return 42;
        }

        std::string p018_b_info();
