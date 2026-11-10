#include "cli.hpp"
#include <charconv>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <locale>
#include <stdexcept>
#include <string>
#include <system_error>

namespace {
std::size_t integer(const std::string& s) {
    std::size_t value = 0;
    const auto parsed = std::from_chars(s.data(), s.data() + s.size(), value);
    if (s.empty() || parsed.ec != std::errc{} || parsed.ptr != s.data() + s.size())
        throw std::invalid_argument("expected unsigned decimal integer: " + s);
    return value;
}
double real(const std::string& s) {
    std::size_t end = 0;
    const double value = std::stod(s, &end);
    if (end != s.size() || !std::isfinite(value) || s.find_first_of(" \t\n\r") != std::string::npos)
        throw std::invalid_argument("expected finite real: " + s);
    return value;
}
}
namespace heat {
bool help_requested(int argc, char** argv) {
    return argc == 2 && std::string(argv[1]) == "--help";
}
int print_help(const char* program) {
    std::cout << "Usage: " << program << " [--N intervals] [--M steps] [--T time] [--alpha diffusivity]\n"
              << "Defaults: N=20 M=400 T=0.1 alpha=1; require r<=1/4.\n"
              << "stdout: final field CSV; stderr: parameters and E_inf.\n";
    std::cout.flush();
    return std::cout ? 0 : 1;
}
Parameters parse_arguments(int argc, char** argv) {
    Parameters p;
    unsigned seen = 0;
    for (int k = 1; k < argc; ++k) {
        const std::string key = argv[k];
        const unsigned bit = key == "--N" ? 1 : key == "--M" ? 2 :
                             key == "--T" ? 4 : key == "--alpha" ? 8 : 0;
        if (!bit || (seen & bit) || k + 1 == argc)
            throw std::invalid_argument("unknown, duplicate or missing option: " + key);
        seen |= bit;
        const std::string value = argv[++k];
        if (bit == 1) p.N = integer(value);
        if (bit == 2) p.M = integer(value);
        if (bit == 4) p.T = real(value);
        if (bit == 8) p.alpha = real(value);
    }
    heat::validate(p);
    return p;
}
void print_field(const Parameters& p, const std::vector<double>& field) {
    const auto d = heat::validate(p);
    const double error = heat::max_error(field, p);
    std::cerr << std::setprecision(17) << "N=" << p.N << " M=" << p.M
              << " T=" << p.T << " alpha=" << p.alpha << " h=" << d.h
              << " dt=" << d.dt << " r=" << d.r << " E_inf=" << error << '\n';
    std::cout << std::setprecision(17) << "i,j,x,y,u_numeric,u_exact,abs_error\n";
    for (std::size_t i = 0; i <= p.N; ++i)
        for (std::size_t j = 0; j <= p.N; ++j) {
            const auto value = field[i * (p.N + 1) + j];
            const double reference = heat::exact(i, j, p);
            std::cout << i << ',' << j << ',' << i * d.h << ',' << j * d.h << ','
                      << value << ',' << reference << ',' << std::abs(value - reference) << '\n';
        }
    std::cout.flush();
    std::cerr.flush();
    if (!std::cout || !std::cerr) throw std::runtime_error("output failed");
}
} // namespace heat
