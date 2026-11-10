#pragma once
#include "heat.hpp"
namespace heat {
Parameters parse_arguments(int argc, char** argv);
bool help_requested(int argc, char** argv);
int print_help(const char* program);
void print_field(const Parameters& p, const std::vector<double>& field);
} // namespace heat
