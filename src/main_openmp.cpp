#include "cli.hpp"
#include "heat_openmp.hpp"
#include <iostream>
#include <iomanip>
#include <locale>
#include <new>
#include <stdexcept>

int main(int argc, char** argv) {
    std::cout.imbue(std::locale::classic());
    std::cerr.imbue(std::locale::classic());
    if (heat::help_requested(argc, argv)) return heat::print_help("heat_openmp", true);
    heat::Parameters p;
    bool summary_only = false;
    int requested_threads = 1;
    try {
        p = heat::parse_arguments(argc, argv, &requested_threads, &summary_only);
    } catch (const std::bad_alloc& e) {
        std::cerr << "runtime error: " << e.what() << '\n';
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "input error: " << e.what() << '\n';
        return 2;
    }
    try {
        const auto result = heat::solve_openmp(p, requested_threads);
        std::cerr << "Q_requested=" << requested_threads
                  << " Q_actual=" << result.actual_threads << '\n';
        std::cerr << std::setprecision(17) << "loop_seconds=" << result.loop_seconds << '\n';
        heat::print_field(p, result.field, summary_only);
    } catch (const std::exception& e) {
        std::cerr << "runtime error: " << e.what() << '\n';
        return 1;
    }
}
