#include "projectlib.h"
#include <iostream>
#include <string>

int main(int argc, char** argv) {
  std::string url = (argc > 1) ? argv[1] : "https://example.com";
  std::string msg = (argc > 2) ? argv[2] : "hello monorepo sample";
  std::cout << make_banner(url, msg) << std::endl;
  return 0;
}
