        #pragma once
        #include <string>
        #include "p033_a.h"
#include "p034_c.h"

        inline int p048_a_value() {
            (void)p033_a_value();
    (void)p034_c_value();
    return 42;
        }

        std::string p048_a_info();
