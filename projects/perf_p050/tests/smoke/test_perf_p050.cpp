#include "p050_c.h"
#include <cassert>
#include <iostream>

int main() {
    assert(p050_c_value() == 42);
    std::cout << p050_c_info() << " OK\n";
    return 0;
}
