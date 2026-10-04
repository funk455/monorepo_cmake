        #pragma once
        #include <string>
        #include "p018_a.h"
#include "p019_b.h"
#include "p019_a.h"

        inline int p021_b_value() {
            (void)p018_a_value();
    (void)p019_b_value();
    (void)p019_a_value();
    return 42;
        }

        std::string p021_b_info();
