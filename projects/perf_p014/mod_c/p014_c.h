        #pragma once
        #include <string>
        #include "p013_c.h"
#include "p005_a.h"

        inline int p014_c_value() {
            (void)p013_c_value();
    (void)p005_a_value();
    return 42;
        }

        std::string p014_c_info();
