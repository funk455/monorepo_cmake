        #pragma once
        #include <string>
        #include "p018_a.h"
#include "p030_c.h"

        inline int p035_a_value() {
            (void)p018_a_value();
    (void)p030_c_value();
    return 42;
        }

        std::string p035_a_info();
