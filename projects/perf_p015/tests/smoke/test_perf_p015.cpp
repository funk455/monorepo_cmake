#include "p015_c.h"
#include <cassert>
#include <iostream>

int main() {
    assert(p015_c_value() == 42);
    std::cout << p015_c_info() << " OK\n";
    return 0;
}
