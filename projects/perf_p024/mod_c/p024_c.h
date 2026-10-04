        #pragma once
        #include <string>
        #include "p021_b.h"
#include "p022_b.h"
#include "p023_b.h"
#include "p007_c.h"

        inline int p024_c_value() {
            (void)p021_b_value();
    (void)p022_b_value();
    (void)p023_b_value();
    (void)p007_c_value();
    return 42;
        }

        std::string p024_c_info();
