        #pragma once
        #include <string>
        #include "p006_c.h"
#include "p007_b.h"
#include "p010_c.h"

        inline int p041_c_value() {
            (void)p006_c_value();
    (void)p007_b_value();
    (void)p010_c_value();
    return 42;
        }

        std::string p041_c_info();
