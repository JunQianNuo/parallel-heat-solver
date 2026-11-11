#include "diagnostic.hpp"
namespace {
template<bool Profile>
std::vector<double> replica(const heat::diag::Options& o, double& seconds,
                            heat::diag::Worker& s) {
    const auto& p=o.p;const auto d=heat::validate(p);
    auto old=heat::initial_field(p.N);std::vector<double> next(d.nodes,0.0);
    const auto w=p.N+1;
    const bool common=o.variant=="common";
    s.rows=p.N-1;s.cpu=heat::diag::cpu();
    const double begin=heat::diag::now();
    for (std::size_t n=0;n<p.M;++n) {
        double t=0;
        if constexpr(Profile) t=heat::diag::now();
        // Recheck buffers and boundaries in the replica context. This context is
        // not production step; copy calibration measures its aggregate impact.
        const auto check=heat::validate(p);
        if (&old==&next || old.size()!=check.nodes || next.size()!=check.nodes)
            throw std::invalid_argument("invalid buffers");
        for (std::size_t k=0;k<=p.N;++k) {
            next[k]=next[p.N*w+k]=0.0;
            next[k*w]=next[k*w+p.N]=0.0;
        }
        if constexpr(Profile) {const double z=heat::diag::now();s.boundary+=z-t;t=z;}
        if (common) heat::diag::rows(old.data(),next.data(),1,p.N,p.N,w,d.r);
        else for (std::size_t i=1;i<p.N;++i)
            for (std::size_t j=1;j<p.N;++j) {
                const auto k=i*w+j;
                next[k]=(1.0-4.0*d.r)*old[k]+d.r*(old[k-w]+old[k+w]+old[k-1]+old[k+1]);
            }
        if constexpr(Profile) {const double z=heat::diag::now();s.update+=z-t;t=z;}
        old.swap(next);
        if constexpr(Profile) s.exchange+=heat::diag::now()-t;
    }
    seconds=heat::diag::now()-begin;s.total=seconds;return old;
}
}
int main(int argc,char** argv) {
    if (heat::help_requested(argc,argv)) return heat::diag::help("heat_serial_diag","baseline|replica|common");
    heat::diag::Options o;
    try {o=heat::diag::parse(argc,argv,{"baseline","replica","common"});}
    catch (const std::exception& e) {std::cerr<<"input error: "<<e.what()<<'\n';return 2;}
    try {
        double seconds=0;heat::diag::Worker s;std::vector<double> field;
        if(o.variant=="baseline") field=heat::solve(o.p,&seconds);
        else field=o.profile?replica<true>(o,seconds,s):replica<false>(o,seconds,s);
        if(o.variant!="baseline") heat::diag::print_worker(0,s);
        heat::diag::finish(o,field,seconds);
    } catch(const std::exception& e) {std::cerr<<"runtime error: "<<e.what()<<'\n';return 1;}
}
