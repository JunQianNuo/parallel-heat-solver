#include "diagnostic.hpp"
#include "heat_openmp.hpp"
#include <omp.h>

namespace {
template<bool Profile,bool Block,bool Private,bool Padded>
std::vector<double> replica(const heat::diag::Options& o,double& seconds,
                            int& actual,std::vector<heat::diag::Worker>& stats) {
    const auto d=heat::validate(o.p);const auto N=o.p.N,M=o.p.M;
    auto initial=heat::initial_field(N);
    std::vector<double> old,next;
    std::unique_ptr<heat::diag::AlignedGrid> grid_a,grid_b;
    std::size_t w=N+1;
    if constexpr(Padded) {
        grid_a=std::make_unique<heat::diag::AlignedGrid>(N,true);
        grid_b=std::make_unique<heat::diag::AlignedGrid>(N,true);w=grid_a->stride;
        for(std::size_t i=0;i<=N;++i)std::copy_n(initial.data()+i*(N+1),N+1,grid_a->data()+i*w);
    } else {old=std::move(initial);next.assign(d.nodes,0.0);}
    double* shared_old=Padded?grid_a->data():old.data();
    double* shared_next=Padded?grid_b->data():next.data();
    const double r=d.r;const int requested=o.threads;
    stats.resize(requested);omp_set_dynamic(0);
    const double start=omp_get_wtime();
#pragma omp parallel default(none) shared(shared_old,shared_next,actual,stats) firstprivate(N,M,w,r,requested) num_threads(requested)
    {
        const int id=omp_get_thread_num();heat::diag::Worker local;local.cpu=heat::diag::cpu();
#pragma omp single
        actual=omp_get_num_threads();
        // Only Private uses these thread-private roles between time steps.
        double* private_old=shared_old;double* private_next=shared_next;
        const int team=omp_get_num_threads();
        if constexpr(Block) local.rows=(N-1)/team+(static_cast<std::size_t>(id)<(N-1)%team);
        else local.rows=static_cast<std::size_t>(id)<N-1?1+(N-2-id)/team:0;
        const double begin=omp_get_wtime();
        for(std::size_t n=0;n<M;++n) {
            double* src=Private?private_old:shared_old;
            double* dst=Private?private_next:shared_next;
            double t=0;if constexpr(Profile)t=omp_get_wtime();
            if constexpr(Block) {
#pragma omp for schedule(static) nowait
                for(std::size_t i=1;i<N;++i)
                    for(std::size_t j=1;j<N;++j) {
                        const auto k=i*w+j;
                        dst[k]=(1.0-4.0*r)*src[k]+r*(src[k-w]+src[k+w]+src[k-1]+src[k+1]);
                    }
            } else {
#pragma omp for schedule(static,1) nowait
                for(std::size_t i=1;i<N;++i)
                    for(std::size_t j=1;j<N;++j) {
                        const auto k=i*w+j;
                        dst[k]=(1.0-4.0*r)*src[k]+r*(src[k-w]+src[k+w]+src[k-1]+src[k+1]);
                    }
            }
            if constexpr(Profile){const double z=omp_get_wtime();local.update+=z-t;t=z;}
#pragma omp barrier
            if constexpr(Profile){const double z=omp_get_wtime();local.sync+=z-t;t=z;}
            if constexpr(Private) {
                std::swap(private_old,private_next);
            } else {
#pragma omp single
                std::swap(shared_old,shared_next);
            }
            if constexpr(Profile)local.exchange+=omp_get_wtime()-t;
        }
        local.total=omp_get_wtime()-begin;stats[id]=local;
    }
    seconds=omp_get_wtime()-start;stats.resize(actual);
    const double* final=Private?(M%2?(Padded?grid_b->data():next.data()):(Padded?grid_a->data():old.data())):shared_old;
    std::vector<double> field(d.nodes);
    for(std::size_t i=0;i<=N;++i)std::copy_n(final+i*w,N+1,field.data()+i*(N+1));
    return field;
}
template<bool Profile>
std::vector<double> select(const heat::diag::Options& o,double& t,int& q,std::vector<heat::diag::Worker>& s) {
    if(o.variant=="replica")return replica<Profile,false,false,false>(o,t,q,s);
    if(o.variant=="block")return replica<Profile,true,false,false>(o,t,q,s);
    if(o.variant=="private")return replica<Profile,false,true,false>(o,t,q,s);
    if(o.variant=="block-private")return replica<Profile,true,true,false>(o,t,q,s);
    if(o.variant=="padded")return replica<Profile,false,false,true>(o,t,q,s);
    return replica<Profile,true,false,true>(o,t,q,s);
}
}
int main(int argc,char** argv) {
    if(heat::help_requested(argc,argv))return heat::diag::help("heat_openmp_diag","baseline|replica|block|private|block-private|padded|block-padded");
    heat::diag::Options o;
    try{o=heat::diag::parse(argc,argv,{"baseline","replica","block","private","block-private","padded","block-padded"},true);}
    catch(const std::exception& e){std::cerr<<"input error: "<<e.what()<<'\n';return 2;}
    try {
        double t=0;int actual=0;std::vector<double> field;std::vector<heat::diag::Worker> stats;
        if(o.variant=="baseline") {
            auto result=heat::solve_openmp(o.p,o.threads);field=std::move(result.field);t=result.loop_seconds;actual=result.actual_threads;
        } else field=o.profile?select<true>(o,t,actual,stats):select<false>(o,t,actual,stats);
        std::cerr<<"Q_requested="<<o.threads<<" Q_actual="<<actual<<'\n';
        for(std::size_t k=0;k<stats.size();++k)heat::diag::print_worker(static_cast<int>(k),stats[k]);
        heat::diag::finish(o,field,t);
    }catch(const std::exception& e){std::cerr<<"runtime error: "<<e.what()<<'\n';return 1;}
}
