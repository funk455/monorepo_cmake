        #pragma once
        #include <string>
        #include "p007_b.h"
#include "p006_a.h"

        inline int p015_a_value() {
            (void)p007_b_value();
    (void)p006_a_value();
    return 42;
        }

        std::string p015_a_info();
