#include "cli.hpp"
#include <iostream>
#include <locale>
#include <stdexcept>
int main(int argc, char** argv) {
    std::cout.imbue(std::locale::classic());
    std::cerr.imbue(std::locale::classic());
    if (heat::help_requested(argc, argv)) return heat::print_help("heat_serial");
    heat::Parameters p;
    try {
        p = heat::parse_arguments(argc, argv);
    } catch (const std::exception& e) {
        std::cerr << "input error: " << e.what() << '\n';
        return 2;
    }
    try {
        heat::print_field(p, heat::solve(p));
    } catch (const std::exception& e) {
        std::cerr << "runtime error: " << e.what() << '\n';
        return 1;
    }
}
