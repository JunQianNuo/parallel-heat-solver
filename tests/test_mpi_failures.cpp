// Test-only allocation and MPI-call fault injection. No production flags/hooks.
#include "heat_mpi.hpp"
#include <cstdlib>
#include <iostream>
#include <new>
#include <stdexcept>
#include <string>

namespace {
bool fail_allocation = false;
bool fail_communication = false;
}
void* operator new(std::size_t size) {
    if (fail_allocation) {
        fail_allocation = false;
        throw std::bad_alloc();
    }
    if (auto* p = std::malloc(size ? size : 1)) return p;
    throw std::bad_alloc();
}
void operator delete(void* p) noexcept { std::free(p); }
void operator delete(void* p, std::size_t) noexcept { std::free(p); }

extern "C" int __real_MPI_Sendrecv(const void*, int, MPI_Datatype, int, int,
                                  void*, int, MPI_Datatype, int, int, MPI_Comm, MPI_Status*);
extern "C" int __wrap_MPI_Sendrecv(const void* send, int sc, MPI_Datatype st, int dest, int stag,
                                  void* recv, int rc, MPI_Datatype rt, int source, int rtag,
                                  MPI_Comm comm, MPI_Status* status) {
    if (fail_communication) return MPI_ERR_OTHER;
    return __real_MPI_Sendrecv(send, sc, st, dest, stag, recv, rc, rt, source, rtag, comm, status);
}
int main(int argc, char** argv) {
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS) return 1;
    const auto comm = MPI_COMM_WORLD;
    heat::mpi_check(MPI_Comm_set_errhandler(comm, MPI_ERRORS_RETURN), "errhandler", comm);
    int rank = 0, size = 0;
    heat::mpi_check(MPI_Comm_rank(comm, &rank), "rank", comm);
    heat::mpi_check(MPI_Comm_size(comm, &size), "size", comm);
    const std::string mode = argc == 2 ? argv[1] : "";
    int ok = 0, all_ok = 0;
    if (mode == "allocation-root" || mode == "allocation-worker") {
        fail_allocation = rank == (mode == "allocation-root" ? 0 : size-1);
        try { heat::solve_mpi({20,2,.001,1}, comm); }
        catch (const std::runtime_error& e) {
            ok = std::string(e.what()) == "collective grid allocation failed";
        }
        fail_allocation = false;
    } else if (mode == "communication") {
        fail_communication = rank == size-1;
        heat::solve_mpi({20,2,.001,1}, comm);
        // This marker distinguishes an accidental normal return from MPI_Abort.
        if (rank == 0) std::cerr << "unexpected solver return\n";
    } else if (mode == "partition") {
        ok = 1;
        for (std::size_t n = 2; n <= 25; ++n)
            for (int count = 1; count < static_cast<int>(n); ++count) {
                std::size_t offset = 0;
                for (int r = 0; r < count; ++r) {
                    const auto b = heat::mpi_block({n,10000,.001,1}, count, r);
                    ok &= b.offset == offset && b.rows >= 1;
                    offset += b.rows;
                }
                ok &= offset == n-1;
            }
        // Check both sides of the classic INT_MAX span without allocating grids.
        heat::mpi_block({46340,10000000000ULL,.1,1}, 1, 0);
        try { heat::mpi_block({46341,10000000000ULL,.1,1}, 1, 0); ok = 0; }
        catch (const std::invalid_argument&) {}
    }
    heat::mpi_check(MPI_Allreduce(&ok, &all_ok, 1, MPI_INT, MPI_MIN, comm), "test status", comm);
    if (rank == 0) std::cout << mode << " collective_check=" << all_ok << '\n';
    if (MPI_Finalize() != MPI_SUCCESS) return 1;
    return all_ok ? 0 : 1;
}
