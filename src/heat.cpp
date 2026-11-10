#include "heat.hpp"
#include <algorithm>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace heat {
namespace {
std::size_t node_count(std::size_t N) {
    const auto limit = std::numeric_limits<std::size_t>::max();
    if (N < 2 || N == limit || N + 1 > limit / (N + 1))
        throw std::invalid_argument("N must be >= 2 with representable grid size");
    const auto nodes = (N + 1) * (N + 1);
    if (nodes > std::vector<double>().max_size() || nodes > limit / (2 * sizeof(double)))
        throw std::invalid_argument("two grid buffers exceed representable size");
    return nodes;
}
const double pi = std::acos(-1.0);
}
Discretization validate(const Parameters& p) {
    const auto nodes = node_count(p.N);
    if (p.M < 1 || !std::isfinite(p.T) || p.T <= 0 ||
        !std::isfinite(p.alpha) || p.alpha <= 0)
        throw std::invalid_argument("require M >= 1 and finite T, alpha > 0");
    const double h = 1.0 / static_cast<double>(p.N);
    const double dt = p.T / static_cast<double>(p.M);
    // Wider intermediates avoid premature product overflow/underflow.
    const long double wide_r = static_cast<long double>(p.alpha) * p.T /
        static_cast<long double>(p.M) * p.N * p.N;
    const double r = static_cast<double>(wide_r);
    if (!std::isfinite(dt) || dt <= 0 || !std::isfinite(r) || r <= 0 || wide_r > 0.25L)
        throw std::invalid_argument("require representable dt, r > 0 and stable r <= 1/4");
    return {nodes, h, dt, r};
}
std::vector<double> initial_field(std::size_t N) {
    std::vector<double> field(node_count(N), 0.0);
    const auto width = N + 1;
    for (std::size_t i = 1; i < N; ++i)
        for (std::size_t j = 1; j < N; ++j)
            field[i * width + j] = std::sin(pi * static_cast<double>(i) / N) *
                                     std::sin(pi * static_cast<double>(j) / N);
    return field;
}
void step(const std::vector<double>& old, std::vector<double>& next,
          std::size_t N, double r) {
    const auto nodes = node_count(N);
    if (&old == &next || old.size() != nodes || next.size() != nodes ||
        !std::isfinite(r) || r <= 0 || r > 0.25)
        throw std::invalid_argument("invalid step buffers or r");
    const auto w = N + 1;
    for (std::size_t k = 0; k <= N; ++k) {
        next[k] = next[N * w + k] = 0.0;
        next[k * w] = next[k * w + N] = 0.0;
    }
    for (std::size_t i = 1; i < N; ++i)
        for (std::size_t j = 1; j < N; ++j) {
            const auto k = i * w + j;
            next[k] = (1.0 - 4.0 * r) * old[k] +
                r * (old[k - w] + old[k + w] + old[k - 1] + old[k + 1]);
        }
}
std::vector<double> solve(const Parameters& p) {
    const auto d = validate(p);
    auto old = initial_field(p.N);
    std::vector<double> next(d.nodes, 0.0);
    for (std::size_t n = 0; n < p.M; ++n) {
        step(old, next, p.N, d.r);
        old.swap(next);
    }
    return old;
}
double exact(std::size_t i, std::size_t j, const Parameters& p) {
    if (i == 0 || j == 0 || i == p.N || j == p.N) return 0.0;
    const long double exponent = -2.0L * p.alpha * p.T * pi * pi;
    return static_cast<double>(std::exp(exponent)) *
        std::sin(pi * static_cast<double>(i) / p.N) *
        std::sin(pi * static_cast<double>(j) / p.N);
}
double max_error(const std::vector<double>& field, const Parameters& p) {
    const auto d = validate(p);
    if (field.size() != d.nodes) throw std::invalid_argument("invalid field size");
    double error = 0;
    for (std::size_t i = 0; i <= p.N; ++i)
        for (std::size_t j = 0; j <= p.N; ++j) {
            const auto value = field[i * (p.N + 1) + j];
            if (!std::isfinite(value)) throw std::runtime_error("nonfinite field value");
            error = std::max(error, std::abs(value - exact(i, j, p)));
        }
    return error;
}
} // namespace heat
