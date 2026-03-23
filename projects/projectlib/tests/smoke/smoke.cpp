#include "projectlib.h"
#include <cassert>

int main() {
  auto out = make_banner("https://example.com", "ok");
  assert(!out.empty());
  return 0;
}
