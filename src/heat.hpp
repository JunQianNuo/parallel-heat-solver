#pragma once
#include <cstddef>
#include <vector>

namespace heat {
struct Parameters {
    std::size_t N = 20;
    std::size_t M = 400;
    double T = 0.1;
    double alpha = 1.0;
};
struct Discretization {
    std::size_t nodes;
    double h, dt, r;
};
Discretization validate(const Parameters& p);
std::vector<double> initial_field(std::size_t N);
// Distinct, equally sized fields of (N+1)^2 nodes are required.
// Every new boundary value is explicitly set to zero.
void step(const std::vector<double>& old, std::vector<double>& next,
          std::size_t N, double r);
std::vector<double> solve(const Parameters& p, double* loop_seconds = nullptr);
double exact(std::size_t i, std::size_t j, const Parameters& p);
double max_error(const std::vector<double>& field, const Parameters& p);
} // namespace heat
