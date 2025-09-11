#include "utils.h"
#include <algorithm>
#include <string>
std::string shout(const std::string& s) {
  std::string t = s;
  std::transform(t.begin(), t.end(), t.begin(), ::toupper);
  return t + "!";
}
