#include "network.h"
#include <string>
std::string net_fetch(const std::string& url) {
  return std::string("GET ") + url + " -> OK";
}
// perf touch
// perf touch
