#include "diagnostic.hpp"
namespace heat::diag {
void rows(const double* old, double* next, std::size_t first, std::size_t last,
          std::size_t N, std::size_t w, double r) {
    for (std::size_t i=first;i<last;++i)
        for (std::size_t j=1;j<N;++j) {
            const auto k=i*w+j;
            next[k]=(1.0-4.0*r)*old[k]+r*(old[k-w]+old[k+w]+old[k-1]+old[k+1]);
        }
}
}
