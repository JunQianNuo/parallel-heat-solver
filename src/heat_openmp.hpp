#pragma once
#include "heat.hpp"

namespace heat {
struct OpenmpResult {
    std::vector<double> field;
    int actual_threads;
};
// Standalone, non-nested solve; requests Q threads with dynamic adjustment off.
// Validation and all grid allocations happen before entering the parallel region.
OpenmpResult solve_openmp(const Parameters& p, int requested_threads);
} // namespace heat
