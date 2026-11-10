#pragma once
#include "heat.hpp"
#include <mpi.h>

namespace heat {
struct RowBlock { std::size_t rows, offset; };
// Pure validation, including the classic MPI int count/displacement limits.
RowBlock mpi_block(const Parameters& p, int size, int rank);
// Fatal MPI failures cannot safely be followed by another collective.
void mpi_check(int code, const char* operation, MPI_Comm comm);
// Collective: identical validated p on all ranks; full field only on rank 0.
// A caught allocation failure becomes a runtime_error on every rank.
std::vector<double> solve_mpi(const Parameters& p, MPI_Comm comm);
} // namespace heat
