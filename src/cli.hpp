#pragma once
#include "heat.hpp"
namespace heat {
// A non-null threads enables the OpenMP-only --threads option, default 1.
Parameters parse_arguments(int argc, char** argv, int* threads = nullptr,
                           bool* summary_only = nullptr);
bool help_requested(int argc, char** argv);
int print_help(const char* program, bool openmp = false);
void print_field(const Parameters& p, const std::vector<double>& field,
                 bool summary_only = false);
} // namespace heat
