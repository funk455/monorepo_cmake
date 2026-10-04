        #pragma once
        #include <string>
        #include "p002_c.h"
#include "p011_b.h"
#include "p012_b.h"

        inline int p015_b_value() {
            (void)p002_c_value();
    (void)p011_b_value();
    (void)p012_b_value();
    return 42;
        }

        std::string p015_b_info();
