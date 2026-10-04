        #pragma once
        #include <string>
        #include "p015_c.h"
#include "p014_b.h"

        inline int p033_c_value() {
            (void)p015_c_value();
    (void)p014_b_value();
    return 42;
        }

        std::string p033_c_info();
