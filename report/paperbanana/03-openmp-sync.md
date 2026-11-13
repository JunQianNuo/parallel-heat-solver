# Figure brief: OpenMP cyclic row ownership and two synchronization points

## Scientific facts to preserve

This implementation uses one persistent OpenMP team around the time loop. Both old and next buffers are shared; loop indices and temporary cell-index variables are private. The worksharing loop distributes whole internal rows with schedule(static,1), cyclically, not as contiguous per-thread blocks.

Use the concrete example N=7, so internal rows are 1..6, and actual Q=4 threads: thread 0 owns rows 1 and 5; thread 1 owns 2 and 6; thread 2 owns 3; thread 3 owns 4. Each internal cell has exactly one writer in next, and all stencil reads use old. The physical boundaries remain zero.

At each step: parallel row updates -> implicit barrier at the end of omp for -> one thread performs the buffer swap under omp single -> implicit barrier at the end of single -> next time step. Both barriers involve the whole team, including any threads with no assigned rows. No nowait, no concurrent per-thread swaps, and no team recreation on every time step.

Requested Q and actual team size Q are distinct recorded quantities. Q greater than the internal row count is legal; unused threads still synchronize. Do not impose the MPI implementation's P<=N-1 constraint on OpenMP. This diagram is conceptual, not a timing or speedup result.

## Visual intent and composition

Use a large ownership panel with rows 1..6 visibly mapped to four thread lanes. Below it, show four parallel timelines spanning one time step. A vertical barrier line closes the update phase; one highlighted swap action sits in a single lane; a second full-team barrier closes the swap phase before all lanes continue. Do not imply that all threads independently swap the shared buffers.

Use white, #115EA2, #092F51, #C9D7E3 and black. Prefer line styles and lane position over four competing bright thread colors. Large high-contrast marks, flat academic visual style, minimal English labels: T0..T3, old, next, update, barrier, single swap. No small Chinese paragraphs, long equation, photographic CPUs, fake elapsed times, or performance claims. The final PPT overlays editable Chinese captions and labels.

## Audit after generation

Correct cyclic ownership; exactly one writer per cell; old and next shared; one swap; both barriers cross all lanes; no next step before the second barrier; actual Q is a thread count, not MPI P.
