        #pragma once
        #include <string>
        #include "p008_a.h"
#include "p007_c.h"

        inline int p009_a_value() {
            (void)p008_a_value();
    (void)p007_c_value();
    return 42;
        }

        std::string p009_a_info();
