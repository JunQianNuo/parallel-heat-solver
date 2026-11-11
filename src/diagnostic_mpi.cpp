#include "diagnostic.hpp"
#include "heat_mpi.hpp"
#include <cstdint>

namespace {
template<bool Profile>
std::vector<double> replica(const heat::diag::Options& o,MPI_Comm comm,double& seconds,
                            std::vector<heat::diag::Worker>& workers) {
    int rank=0,size=0;
    heat::mpi_check(MPI_Comm_rank(comm,&rank),"rank",comm);
    heat::mpi_check(MPI_Comm_size(comm,&size),"size",comm);
    const auto& p=o.p;const auto d=heat::validate(p);const auto b=heat::mpi_block(p,size,rank);
    const auto w=p.N+1;
    std::vector<double> old,next,global,stats;
    std::vector<int> counts,displs;
    int ready=1,all=0;
    try {
        old.assign((b.rows+2)*w,0.0);next.assign(old.size(),0.0);
        if(rank==0) {
            global.assign(d.nodes,0.0);counts.resize(size);displs.resize(size);
            workers.resize(size);stats.resize(size*8);
            for(int k=0;k<size;++k) {
                const auto block=heat::mpi_block(p,size,k);
                counts[k]=static_cast<int>(block.rows*w);displs[k]=static_cast<int>(block.offset*w);
            }
        }
    } catch(const std::exception&) {ready=0;}
    heat::mpi_check(MPI_Allreduce(&ready,&all,1,MPI_INT,MPI_MIN,comm),"allocation status",comm);
    if(!all) throw std::runtime_error("collective diagnostic allocation failed");
    const double pi=std::acos(-1.0);
    for(std::size_t i=1;i<=b.rows;++i)
        for(std::size_t j=1;j<p.N;++j)
            old[i*w+j]=std::sin(pi*static_cast<double>(b.offset+i)/p.N)*std::sin(pi*static_cast<double>(j)/p.N);
    const int up=rank==0?MPI_PROC_NULL:rank-1,down=rank==size-1?MPI_PROC_NULL:rank+1;
    const bool skip=o.variant=="no-null",common=o.variant=="common";
    heat::diag::Worker s;s.rows=b.rows;s.cpu=heat::diag::cpu();
    heat::mpi_check(MPI_Barrier(comm),"before timing",comm);
    const double start=MPI_Wtime();
    for(std::size_t n=0;n<p.M;++n) {
        double t=0;if constexpr(Profile)t=MPI_Wtime();
        if(up==MPI_PROC_NULL)std::fill_n(old.data(),w,0.0);
        if(down==MPI_PROC_NULL)std::fill_n(old.data()+(b.rows+1)*w,w,0.0);
        if constexpr(Profile){const double z=MPI_Wtime();s.boundary+=z-t;t=z;}
        if(!skip) {
            heat::mpi_check(MPI_Sendrecv(old.data()+w,static_cast<int>(w),MPI_DOUBLE,up,71,
                old.data()+(b.rows+1)*w,static_cast<int>(w),MPI_DOUBLE,down,71,comm,MPI_STATUS_IGNORE),"top",comm);
            heat::mpi_check(MPI_Sendrecv(old.data()+b.rows*w,static_cast<int>(w),MPI_DOUBLE,down,72,
                old.data(),static_cast<int>(w),MPI_DOUBLE,up,72,comm,MPI_STATUS_IGNORE),"bottom",comm);
        }
        if constexpr(Profile){const double z=MPI_Wtime();s.communication+=z-t;t=z;}
        if(common) {
            for(std::size_t k=1;k<=b.rows;++k)next[k*w]=next[k*w+p.N]=0.0;
            heat::diag::rows(old.data(),next.data(),1,b.rows+1,p.N,w,d.r);
        } else {
            for(std::size_t k=1;k<=b.rows;++k) {
                next[k*w]=next[k*w+p.N]=0.0;
                for(std::size_t j=1;j<p.N;++j) {
                    const auto a=k*w+j;
                    next[a]=(1.0-4.0*d.r)*old[a]+d.r*(old[a-w]+old[a+w]+old[a-1]+old[a+1]);
                }
            }
        }
        if constexpr(Profile){const double z=MPI_Wtime();s.update+=z-t;t=z;}
        old.swap(next);
        if constexpr(Profile)s.exchange+=MPI_Wtime()-t;
    }
    s.total=MPI_Wtime()-start;
    heat::mpi_check(MPI_Reduce(&s.total,&seconds,1,MPI_DOUBLE,MPI_MAX,0,comm),"max time",comm);
    const double local[8]={s.boundary,s.communication,s.update,s.sync,s.exchange,s.total,
                          static_cast<double>(s.rows),static_cast<double>(s.cpu)};
    heat::mpi_check(MPI_Gather(local,8,MPI_DOUBLE,stats.data(),8,MPI_DOUBLE,0,comm),"worker stats",comm);
    if(rank==0)for(int k=0;k<size;++k) {
        const double* a=stats.data()+8*k;
        workers[k]={a[0],a[1],a[2],a[3],a[4],a[5],static_cast<std::size_t>(a[6]),static_cast<int>(a[7])};
    }
    double error=0,maximum=0;
    for(std::size_t k=1;k<=b.rows;++k)for(std::size_t j=1;j<p.N;++j)
        error=std::max(error,std::abs(old[k*w+j]-heat::exact(b.offset+k,j,p)));
    heat::mpi_check(MPI_Reduce(&error,&maximum,1,MPI_DOUBLE,MPI_MAX,0,comm),"error",comm);
    heat::mpi_check(MPI_Gatherv(old.data()+w,static_cast<int>(b.rows*w),MPI_DOUBLE,
        rank==0?global.data()+w:nullptr,counts.data(),displs.data(),MPI_DOUBLE,0,comm),"field",comm);
    if(rank==0 && heat::max_error(global,p)!=maximum)throw std::runtime_error("gather/error mismatch");
    return global;
}
}
int main(int argc,char** argv) {
    if(MPI_Init(&argc,&argv)!=MPI_SUCCESS)return 1;
    const auto comm=MPI_COMM_WORLD;
    heat::mpi_check(MPI_Comm_set_errhandler(comm,MPI_ERRORS_RETURN),"errors",comm);
    int rank=0,size=0;heat::mpi_check(MPI_Comm_rank(comm,&rank),"rank",comm);heat::mpi_check(MPI_Comm_size(comm,&size),"size",comm);
    heat::diag::Options o;int status=0,help=0;
    const std::vector<std::string> variants={"baseline","replica","no-null","common"};
    if(rank==0)try {
        help=heat::help_requested(argc,argv);
        if(help)status=heat::diag::help("heat_mpi_diag","baseline|replica|no-null|common");
        else {
            o=heat::diag::parse(argc,argv,variants);heat::mpi_block(o.p,size,0);
            if(o.variant=="no-null" && size!=1)throw std::invalid_argument("no-null requires P=1");
        }
    } catch(const std::exception& e){std::cerr<<"input error: "<<e.what()<<'\n';status=2;}
    heat::mpi_check(MPI_Bcast(&status,1,MPI_INT,0,comm),"input status",comm);
    heat::mpi_check(MPI_Bcast(&help,1,MPI_INT,0,comm),"help",comm);
    if(status==0 && !help) {
        std::uint64_t ints[2]={o.p.N,o.p.M};double reals[2]={o.p.T,o.p.alpha};
        int variant=static_cast<int>(std::find(variants.begin(),variants.end(),o.variant)-variants.begin());
        int flags[2]={variant,o.profile?1:0};
        heat::mpi_check(MPI_Bcast(ints,2,MPI_UINT64_T,0,comm),"parameters",comm);
        heat::mpi_check(MPI_Bcast(reals,2,MPI_DOUBLE,0,comm),"parameters",comm);
        heat::mpi_check(MPI_Bcast(flags,2,MPI_INT,0,comm),"diagnostic flags",comm);
        o.p={static_cast<std::size_t>(ints[0]),static_cast<std::size_t>(ints[1]),reals[0],reals[1]};
        o.variant=variants[flags[0]];o.profile=flags[1]!=0;
        try {
            double seconds=0;std::vector<double> field;std::vector<heat::diag::Worker> workers;
            if(o.variant=="baseline")field=heat::solve_mpi(o.p,comm,&seconds);
            else field=o.profile?replica<true>(o,comm,seconds,workers):replica<false>(o,comm,seconds,workers);
            if(rank==0) {
                std::cerr<<"P_actual="<<size<<'\n';
                for(std::size_t k=0;k<workers.size();++k)heat::diag::print_worker(static_cast<int>(k),workers[k]);
                heat::diag::finish(o,field,seconds);
            }
        } catch(const std::exception& e){if(rank==0)std::cerr<<"runtime error: "<<e.what()<<'\n';status=1;}
        heat::mpi_check(MPI_Bcast(&status,1,MPI_INT,0,comm),"result status",comm);
    }
    return MPI_Finalize()==MPI_SUCCESS?status:1;
}
