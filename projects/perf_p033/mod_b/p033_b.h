        #pragma once
        #include <string>
        #include "p015_a.h"
#include "p005_c.h"
#include "p012_a.h"

        inline int p033_b_value() {
            (void)p015_a_value();
    (void)p005_c_value();
    (void)p012_a_value();
    return 42;
        }

        std::string p033_b_info();
