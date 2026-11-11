#include "cli.hpp"
#include <iostream>
#include <iomanip>
#include <locale>
#include <stdexcept>
int main(int argc, char** argv) {
    std::cout.imbue(std::locale::classic());
    std::cerr.imbue(std::locale::classic());
    if (heat::help_requested(argc, argv)) return heat::print_help("heat_serial");
    heat::Parameters p;
    bool summary_only = false;
    try {
        p = heat::parse_arguments(argc, argv, nullptr, &summary_only);
    } catch (const std::exception& e) {
        std::cerr << "input error: " << e.what() << '\n';
        return 2;
    }
    try {
        double seconds = 0;
        const auto field = heat::solve(p, &seconds);
        std::cerr << std::setprecision(17) << "loop_seconds=" << seconds << '\n';
        heat::print_field(p, field, summary_only);
    } catch (const std::exception& e) {
        std::cerr << "runtime error: " << e.what() << '\n';
        return 1;
    }
}
