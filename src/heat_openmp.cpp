#include "heat_openmp.hpp"
#include <omp.h>
#include <stdexcept>
#include <utility>

namespace heat {
OpenmpResult solve_openmp(const Parameters& p, int requested_threads) {
    const auto d = validate(p);
    if (requested_threads < 1 || omp_in_parallel())
        throw std::invalid_argument("require positive Q and a non-nested solve");
    auto old = initial_field(p.N);
    std::vector<double> next(d.nodes, 0.0);
    const auto N = p.N, M = p.M, w = N + 1;
    const double r = d.r;
    int actual_threads = 0;
    omp_set_dynamic(0);
    const double start = omp_get_wtime();
    // Both physical boundaries start at zero and are never written again.
    // Shared vectors change roles only in single, between two implicit barriers.
#pragma omp parallel default(none) shared(old, next, actual_threads) firstprivate(N, M, w, r) num_threads(requested_threads)
    {
#pragma omp single
        actual_threads = omp_get_num_threads();
        // n, i, j and k are private by their block/loop declarations.
        for (std::size_t n = 0; n < M; ++n) {
            // Chunk size 1: row i belongs to thread (i-1) % actual_threads.
#pragma omp for schedule(static, 1)
            for (std::size_t i = 1; i < N; ++i)
                for (std::size_t j = 1; j < N; ++j) {
                    const auto k = i * w + j;
                    next[k] = (1.0 - 4.0 * r) * old[k] +
                        r * (old[k-w] + old[k+w] + old[k-1] + old[k+1]);
                }
            // for's barrier completes every write before swapping; single's
            // barrier publishes the swap before ANY thread starts the next step.
#pragma omp single
            old.swap(next);
        }
    }
    const double elapsed = omp_get_wtime() - start;
    return {std::move(old), actual_threads, elapsed};
}
} // namespace heat
