#include "projectlib.h"
#include "network.h"
#include "utils.h"
#include <string>

std::string make_banner(const std::string& url, const std::string& msg) {
  return "[" + net_fetch(url) + "] " + shout(msg);
}
