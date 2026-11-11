#include "cli.hpp"
#include "heat_mpi.hpp"
#include <cstdint>
#include <cstdio>
#include <iostream>
#include <iomanip>
#include <locale>
#include <stdexcept>

int main(int argc, char** argv) {
    // Before successful initialization there is no usable communicator to abort.
    if (MPI_Init(&argc, &argv) != MPI_SUCCESS) return 1;
    const auto comm = MPI_COMM_WORLD;
    heat::mpi_check(MPI_Comm_set_errhandler(comm, MPI_ERRORS_RETURN), "set_errhandler", comm);
    int rank = 0, size = 0;
    heat::mpi_check(MPI_Comm_rank(comm, &rank), "Comm_rank", comm);
    heat::mpi_check(MPI_Comm_size(comm, &size), "Comm_size", comm);
    std::cout.imbue(std::locale::classic());
    std::cerr.imbue(std::locale::classic());
    heat::Parameters p;
    bool summary_only = false;
    int status = 0, help = 0;
    if (rank == 0) {
        try {
            help = heat::help_requested(argc, argv);
            if (help) status = heat::print_help("heat_mpi");
            else {
                p = heat::parse_arguments(argc, argv, nullptr, &summary_only);
                heat::mpi_block(p, size, 0);
            }
        } catch (const std::exception& e) {
            std::cerr << "input error: " << e.what() << '\n';
            status = 2;
        }
    }
    heat::mpi_check(MPI_Bcast(&status, 1, MPI_INT, 0, comm), "Bcast input status", comm);
    heat::mpi_check(MPI_Bcast(&help, 1, MPI_INT, 0, comm), "Bcast help", comm);
    if (status == 0 && !help) {
        static_assert(sizeof(std::size_t) <= sizeof(std::uint64_t), "size_t must fit uint64_t");
        std::uint64_t integers[2] = {p.N, p.M};
        double values[2] = {p.T, p.alpha};
        heat::mpi_check(MPI_Bcast(integers, 2, MPI_UINT64_T, 0, comm), "Bcast N M", comm);
        heat::mpi_check(MPI_Bcast(values, 2, MPI_DOUBLE, 0, comm), "Bcast T alpha", comm);
        p = {static_cast<std::size_t>(integers[0]), static_cast<std::size_t>(integers[1]),
             values[0], values[1]};
        try {
            double seconds = 0;
            const auto field = heat::solve_mpi(p, comm, &seconds);
            if (rank == 0) {
                std::cerr << "P_actual=" << size << '\n';
                std::cerr << std::setprecision(17) << "loop_seconds=" << seconds << '\n';
                heat::print_field(p, field, summary_only);
            }
        } catch (const std::exception& e) {
            if (rank == 0) std::cerr << "runtime error: " << e.what() << '\n';
            status = 1;
        }
        // Output errors on root, or collective allocation failures, reach all ranks.
        heat::mpi_check(MPI_Bcast(&status, 1, MPI_INT, 0, comm), "Bcast result status", comm);
    }
    if (MPI_Finalize() != MPI_SUCCESS) {
        std::fprintf(stderr, "MPI_Finalize failed\n");
        return 1;
    }
    return status;
}
