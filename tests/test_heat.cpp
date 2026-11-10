#include "heat.hpp"
#include <cmath>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>

namespace {
void require(bool ok, const std::string& message) {
    if (!ok) throw std::runtime_error(message);
}
void near(double a, double b, double tolerance = 1e-13) {
    require(std::isfinite(a) && std::abs(a - b) <= tolerance, "value mismatch");
}
void rejects(const std::function<void()>& f) {
    bool rejected = false;
    try { f(); } catch (const std::invalid_argument&) { rejected = true; }
    require(rejected, "invalid input accepted");
}
void boundaries(const std::vector<double>& field, std::size_t n) {
    for (std::size_t k = 0; k <= n; ++k) {
        require(field[k] == 0 && field[n * (n + 1) + k] == 0 &&
                field[k * (n + 1)] == 0 && field[k * (n + 1) + n] == 0,
                "boundary not exactly zero");
    }
}
void initial() {
    const auto f = heat::initial_field(4);
    require(f.size() == 25, "node count");
    boundaries(f, 4);
    near(f[6], .5); near(f[7], std::sqrt(.5)); near(f[12], 1);
    const auto odd = heat::initial_field(3);
    for (const auto k : {5,6,9,10}) near(odd[k], .75);
}
void hand() {
    std::vector<double> old(16, 0), next(16, -99);
    old[5] = 1; old[6] = 2; old[9] = 3; old[10] = 4;
    const auto saved = old;
    heat::step(old, next, 3, .125);
    near(next[5], 1.125); near(next[6], 1.625);
    near(next[9], 2.125); near(next[10], 2.625);
    require(old == saved, "old layer overwritten");
    boundaries(next, 3);
    auto f = heat::solve({2,1,.0625,1}); // r=1/4, sole center vanishes.
    for (double v : f) near(v, 0);
}
void parity() {
    for (std::size_t m : {1,2,3,4,9,10}) {
        const auto f = heat::solve({2,m,static_cast<double>(m)/32,1});
        near(f[4], std::pow(.5, static_cast<double>(m)));
        boundaries(f, 2);
    }
    // Discrete eigenmode checks every node without repeating stencil code.
    const double pi = std::acos(-1.0);
    for (std::size_t m : {7,8}) {
        heat::Parameters p{7,m,.01,.3};
        const auto d = heat::validate(p);
        auto expected = heat::initial_field(p.N);
        const double gain = std::pow(1 - 8*d.r*std::pow(std::sin(pi/(2*p.N)),2),m);
        const auto f = heat::solve(p);
        for (std::size_t k=0; k<f.size(); ++k) near(f[k], expected[k]*gain);
        boundaries(f,p.N);
    }
}
void validation() {
    const double nan = std::numeric_limits<double>::quiet_NaN();
    const double inf = std::numeric_limits<double>::infinity();
    for (auto p : {heat::Parameters{1,1,.01,1}, {2,0,.01,1}, {2,1,0,1},
                   {2,1,-1,1}, {2,1,.01,0}, {2,1,.01,-1}, {2,1,nan,1},
                   {2,1,inf,1}, {2,1,.01,nan}, {2,1,.01,inf},
                   {2,1,std::nextafter(.0625,1.),1},
                   {2,1,1e308,1e308}, {2,10,1e-320,1e-320},
                   {2,std::numeric_limits<std::size_t>::max(),1e-320,1},
                   {std::numeric_limits<std::size_t>::max(),1,.01,1},
                   {std::numeric_limits<std::size_t>::max()/2,1,.01,1}})
        rejects([&]{heat::validate(p);});
    near(heat::validate({2,1,.0625,1}).r,.25,0);
    heat::validate({2,1,std::nextafter(.0625,0.),1});
    std::vector<double> a(9), b(8), c(9);
    rejects([&]{heat::step(a,a,2,.1);});
    rejects([&]{heat::step(a,b,2,.1);});
    rejects([&]{heat::step(a,c,2,nan);});
    rejects([&]{heat::step(a,c,2,.3);});
    rejects([&]{heat::initial_field(0);});
    rejects([&]{heat::max_error(b,{2,1,.01,1});});
}
void analytic() {
    double previous = 0;
    for (std::size_t n : {20,40,80}) {
        heat::Parameters p{n,n*n,.1,1};
        const auto f = heat::solve(p);
        const auto error = heat::max_error(f,p);
        require(error > 0 && error < 2e-4 * 400 / (n*n), "analytic error bound");
        if (previous > 0) require(previous/error > 3.8 && previous/error < 4.2,
                                  "basic refinement ratio");
        previous = error;
        boundaries(f,n);
        for (std::size_t i=0;i<=n;++i)
            for (std::size_t j=0;j<=n;++j) {
                const auto v = f[i*(n+1)+j];
                require(std::isfinite(v) && v >= 0 && v <= 1, "maximum principle");
                near(v,f[j*(n+1)+i]);
                near(v,f[(n-i)*(n+1)+j]);
            }
        std::cout << std::setprecision(17) << "N=" << n << " M=" << p.M
                  << " T=" << p.T << " alpha=" << p.alpha << " r="
                  << heat::validate(p).r << " E_inf=" << error << '\n';
    }
}
}
int main(int argc, char** argv) {
    try {
        require(argc == 2,"test name required");
        const std::string name = argv[1];
        if (name == "initial") initial();
        else if (name == "hand") hand();
        else if (name == "parity") parity();
        else if (name == "validation") validation();
        else if (name == "analytic") analytic();
        else throw std::runtime_error("unknown test");
        std::cout << name << " PASS\n";
    } catch (const std::exception& e) {
        std::cerr << e.what() << '\n'; return 1;
    }
}
