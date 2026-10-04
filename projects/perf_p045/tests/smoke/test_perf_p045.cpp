#include "p045_c.h"
#include <cassert>
#include <iostream>

int main() {
    assert(p045_c_value() == 42);
    std::cout << p045_c_info() << " OK\n";
    return 0;
}
