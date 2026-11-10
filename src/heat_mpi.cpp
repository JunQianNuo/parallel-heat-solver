#include "heat_mpi.hpp"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <stdexcept>

namespace heat {
void mpi_check(int code, const char* operation, MPI_Comm comm) {
    if (code == MPI_SUCCESS) return;
    char message[MPI_MAX_ERROR_STRING] = {};
    int length = 0;
    MPI_Error_string(code, message, &length);
    std::fprintf(stderr, "MPI error in %s: %.*s\n", operation, length, message);
    MPI_Abort(comm, 1);
    std::abort(); // MPI_Abort is not required to return.
}
RowBlock mpi_block(const Parameters& p, int size, int rank) {
    validate(p);
    if (size < 1 || static_cast<std::size_t>(size) > p.N - 1 || rank < 0 || rank >= size)
        throw std::invalid_argument("require 1 <= P <= N-1 and a valid rank");
    const auto w = p.N + 1;
    // A conservative total span limit makes every count, displacement and end
    // representable, including the one-rank case, before any grid allocation.
    const auto limit = static_cast<std::size_t>(std::numeric_limits<int>::max());
    if (w > limit || p.N - 1 > limit / w)
        throw std::invalid_argument("MPI interior field exceeds int count/displacement range");
    const auto q = (p.N - 1) / size, rem = (p.N - 1) % size;
    const auto r = static_cast<std::size_t>(rank);
    return {q + (r < rem), r * q + std::min(r, rem)};
}
std::vector<double> solve_mpi(const Parameters& p, MPI_Comm comm) {
    int rank = 0, size = 0;
    mpi_check(MPI_Comm_rank(comm, &rank), "Comm_rank", comm);
    mpi_check(MPI_Comm_size(comm, &size), "Comm_size", comm);
    const auto b = mpi_block(p, size, rank);
    const auto w = p.N + 1;
    const auto d = validate(p);
    std::vector<double> old, next, global;
    std::vector<int> counts, displs;
    int ready = 1, all_ready = 0;
    try {
        old.assign((b.rows + 2) * w, 0.0);
        next.assign(old.size(), 0.0);
        if (rank == 0) {
            global.assign(d.nodes, 0.0);
            counts.resize(size);
            displs.resize(size);
            for (int r = 0; r < size; ++r) {
                const auto block = mpi_block(p, size, r);
                counts[r] = static_cast<int>(block.rows * w);
                displs[r] = static_cast<int>(block.offset * w);
            }
        }
    } catch (const std::exception&) {
        ready = 0;
    }
    mpi_check(MPI_Allreduce(&ready, &all_ready, 1, MPI_INT, MPI_MIN, comm),
              "Allreduce allocation status", comm);
    if (!all_ready) throw std::runtime_error("collective grid allocation failed");
    const double pi = std::acos(-1.0);
    for (std::size_t k = 1; k <= b.rows; ++k)
        for (std::size_t j = 1; j < p.N; ++j)
            old[k*w+j] = std::sin(pi * static_cast<double>(b.offset+k) / p.N) *
                         std::sin(pi * static_cast<double>(j) / p.N);
    const int up = rank == 0 ? MPI_PROC_NULL : rank - 1;
    const int down = rank == size - 1 ? MPI_PROC_NULL : rank + 1;
    const int width = static_cast<int>(w);
    for (std::size_t n = 0; n < p.M; ++n) {
        if (up == MPI_PROC_NULL) std::fill_n(old.data(), w, 0.0);
        if (down == MPI_PROC_NULL) std::fill_n(old.data()+(b.rows+1)*w, w, 0.0);
        mpi_check(MPI_Sendrecv(old.data()+w, width, MPI_DOUBLE, up, 71,
                  old.data()+(b.rows+1)*w, width, MPI_DOUBLE, down, 71,
                  comm, MPI_STATUS_IGNORE), "Sendrecv top row", comm);
        mpi_check(MPI_Sendrecv(old.data()+b.rows*w, width, MPI_DOUBLE, down, 72,
                  old.data(), width, MPI_DOUBLE, up, 72,
                  comm, MPI_STATUS_IGNORE), "Sendrecv bottom row", comm);
        for (std::size_t k = 1; k <= b.rows; ++k) {
            next[k*w] = next[k*w+p.N] = 0.0;
            for (std::size_t j = 1; j < p.N; ++j) {
                const auto a = k*w+j;
                next[a] = (1.0 - 4.0*d.r) * old[a] +
                    d.r * (old[a-w] + old[a+w] + old[a-1] + old[a+1]);
            }
        }
        old.swap(next);
    }
    double local_error = 0, reduced_error = 0;
    for (std::size_t k = 1; k <= b.rows; ++k)
        for (std::size_t j = 1; j < p.N; ++j)
            local_error = std::max(local_error,
                std::abs(old[k*w+j] - exact(b.offset+k, j, p)));
    mpi_check(MPI_Reduce(&local_error, &reduced_error, 1, MPI_DOUBLE, MPI_MAX, 0, comm),
              "Reduce analytic error", comm);
    mpi_check(MPI_Gatherv(old.data()+w, static_cast<int>(b.rows*w), MPI_DOUBLE,
              rank == 0 ? global.data()+w : nullptr,
              rank == 0 ? counts.data() : nullptr,
              rank == 0 ? displs.data() : nullptr, MPI_DOUBLE, 0, comm), "Gatherv", comm);
    // Both maxima select an existing value: no rounding reduction is involved.
    if (rank == 0 && max_error(global, p) != reduced_error)
        throw std::runtime_error("gathered and reduced analytic errors disagree");
    return global;
}
} // namespace heat
