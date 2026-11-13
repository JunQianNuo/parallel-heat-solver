# Figure brief: MPI contiguous row blocks and old-layer halo exchange

## Scientific facts to preserve

This is an implementation schematic, not benchmark evidence. For N=8, the grid has global rows 0..8. Internal rows 1..7 are split among P=3 MPI processes as 3/2/2: rank 0 owns rows 1..3, rank 1 owns 4..5, rank 2 owns 6..7. Global physical rows 0 and 8 are zero. Every local row contains columns 0..8; only columns 1..7 are updated. Left/right columns are also zero physical boundaries.

Each rank owns two local buffers, each with one extra top halo row and one extra bottom halo row. Ghost rows duplicate neighbor boundary data, not ownership. Before local updates of each step, complete TWO blocking MPI_Sendrecv calls on old: send the first owned row upward and receive from the lower neighbor into the bottom halo; then send the last owned row downward and receive from the upper neighbor into the top halo. After communication, update all locally owned interior cells into next, then swap buffers.

The upper neighbor of rank 0 and lower neighbor of rank 2 are MPI_PROC_NULL. Receiving from MPI_PROC_NULL does not zero the buffer: physical halo rows must be cleared explicitly. No periodic connection, diagonal communication, communication-computation overlap, or per-step global barrier is implemented. The implementation requires P <= N-1 so every rank owns at least one internal row; this is not a universal MPI restriction.

## Visual intent and composition

Show an overview of the global row partition alongside three enlarged rank-local blocks. Distinguish owned rows (solid blue outline) from halos (light blue dashed outline). Use exactly two visual exchange phases, with arrows between the correct owned edge and the neighbor's ghost copy. A lower process strip shows old halo exchange -> owned-cell update into next -> swap. Keep arrows outside row labels and make ownership boundaries clear.

Use white, #115EA2, #092F51, #C9D7E3 and black, consistent with the current presentation. Flat academic engineering diagram; no 3D hardware, fake clocks, speedup numbers, or decorative icons. Short English labels and row numbers only. Native editable Chinese annotations can be added in the final PPT. Keep enough clear space for a large caption, while using most of the content area for the actual blocks and arrows.

## Audit after generation

Owned rows remain 1..3 / 4..5 / 6..7; halo copies do not become extra owned rows; physical boundaries have no wraparound arrows; communication precedes computation; no invented global step barrier; P is a process count.
