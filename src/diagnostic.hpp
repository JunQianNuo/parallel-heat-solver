#pragma once
#include "cli.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#ifdef __linux__
#include <sched.h>
#endif

namespace heat::diag {
struct Options {
    Parameters p;
    std::string variant = "baseline";
    bool profile = false, summary = false;
    int threads = 1;
};
struct Worker {
    double boundary=0, communication=0, update=0, sync=0, exchange=0, total=0;
    std::size_t rows=0;
    int cpu=-1;
};
inline double now() {
    return std::chrono::duration<double>(std::chrono::steady_clock::now().time_since_epoch()).count();
}
inline int cpu() {
#ifdef __linux__
    return sched_getcpu();
#else
    return -1;
#endif
}
inline Options parse(int argc, char** argv, const std::vector<std::string>& variants,
                     bool openmp=false) {
    Options o;
    bool seen_variant=false;
    std::vector<char*> args{argv[0]};
    for (int k=1;k<argc;++k) {
        const std::string key=argv[k];
        if (key=="--variant") {
            if (seen_variant || k+1==argc) throw std::invalid_argument("duplicate/missing variant");
            seen_variant=true; o.variant=argv[++k];
        } else if (key=="--profile") {
            if (o.profile) throw std::invalid_argument("duplicate profile");
            o.profile=true;
        } else args.push_back(argv[k]);
    }
    if (std::find(variants.begin(),variants.end(),o.variant)==variants.end())
        throw std::invalid_argument("unsupported diagnostic variant");
    if (o.profile && o.variant=="baseline")
        throw std::invalid_argument("baseline calls original solver; profile requires replica/variant");
    o.p=parse_arguments(static_cast<int>(args.size()),args.data(),openmp?&o.threads:nullptr,&o.summary);
    return o;
}
inline int help(const char* name, const char* variants) {
    print_help(name, std::string(name).find("openmp")!=std::string::npos);
    std::cout << "Diagnostic only: --variant " << variants
              << "; --profile (not baseline). Default baseline.\n";
    std::cout.flush();return std::cout?0:1;
}
inline void print_worker(int id, const Worker& s) {
    std::cerr << std::setprecision(17) << "WORKER {\"id\":"<<id<<",\"cpu\":"<<s.cpu
       <<",\"rows\":"<<s.rows<<",\"boundary\":"<<s.boundary
       <<",\"communication\":"<<s.communication<<",\"update\":"<<s.update
       <<",\"sync\":"<<s.sync<<",\"exchange\":"<<s.exchange
       <<",\"total\":"<<s.total<<"}\n";
}
inline void finish(const Options& o, const std::vector<double>& field, double elapsed) {
    std::cerr << std::setprecision(17) << "loop_seconds="<<elapsed<<'\n'
              << "variant="<<o.variant<<" profile="<<(o.profile?1:0)<<'\n';
    print_field(o.p,field,o.summary);
}
// Diagnostics only: aligned allocation and padded row stride are an explicit factor.
struct AlignedGrid {
    std::unique_ptr<double, decltype(&std::free)> storage{nullptr,&std::free};
    std::size_t stride;
    AlignedGrid(std::size_t N, bool padded):stride(padded?((N+1+7)/8)*8:N+1) {
        if (stride > static_cast<std::size_t>(-1)/(N+1)/sizeof(double))
            throw std::invalid_argument("diagnostic grid overflow");
        auto bytes=stride*(N+1)*sizeof(double);
        if (bytes>static_cast<std::size_t>(-1)-63) throw std::invalid_argument("alignment overflow");
        storage.reset(static_cast<double*>(std::aligned_alloc(64,((bytes+63)/64)*64)));
        if (!storage) throw std::bad_alloc();
        std::fill_n(storage.get(),stride*(N+1),0.0);
    }
    double* data() {return storage.get();}
};
// One separately compiled function, shared by SERIAL/MPI diagnostics only.
void rows(const double* old, double* next, std::size_t first, std::size_t last,
          std::size_t N, std::size_t stride, double r);
}
