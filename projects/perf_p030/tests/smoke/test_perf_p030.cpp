#include "p030_c.h"
#include <cassert>
#include <iostream>

int main() {
    assert(p030_c_value() == 42);
    std::cout << p030_c_info() << " OK\n";
    return 0;
}
