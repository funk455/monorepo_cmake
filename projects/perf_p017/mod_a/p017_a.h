        #pragma once
        #include <string>
        #include "p012_c.h"
#include "p005_c.h"
#include "p013_b.h"
#include "p001_a.h"

        inline int p017_a_value() {
            (void)p012_c_value();
    (void)p005_c_value();
    (void)p013_b_value();
    (void)p001_a_value();
    return 42;
        }

        std::string p017_a_info();
