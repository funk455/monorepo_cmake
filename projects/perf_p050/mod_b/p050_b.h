    #pragma once
    #include <string>
    #include "p028_c.h"

    inline int p050_b_value() {
        (void)p028_c_value();
return 42;
    }

    std::string p050_b_info();
