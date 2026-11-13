# Figure brief: five-point explicit update and double buffering

## Scientific facts to preserve

This is a conceptual numerical-method diagram, not an experimental temperature field. The domain is the fixed unit square. There are N intervals per direction, h=1/N, M time steps, dt=T/M, and r=alpha*dt/h^2 <= 1/4. Row index i increases downward; column index j increases to the right.

The exact update is:
U(i,j,n+1) = (1-4r)*U(i,j,n) + r*[U(i-1,j,n)+U(i+1,j,n)+U(i,j-1,n)+U(i,j+1,n)].

All five inputs come from the SAME old time layer n. The center has weight 1-4r; each of the four axial neighbors has weight r. There are NO diagonal neighbors. The result writes only the corresponding interior cell (i,j) in a SEPARATE next buffer. Never imply in-place overwriting or a dependency on newly updated neighbors.

Initialize old with the sine-product initial condition and next with zeros. Update all interior cells, keep the four physical boundaries zero, then swap old and next once per completed layer. Repeat exactly M times. After the last swap, old is the numerical solution at T. An analytic solution does not replace time stepping. Serial code needs no inter-thread barrier; parallel synchronization is explained in separate figures.

## Visual intent and composition

Create a wide, flat academic method illustration for one slide's content region. Use three connected zones: old stencil on the left, weighted combination in the middle, separate next grid on the right. Make the five old cells unmistakable; show the output cell aligned to the old center. A bottom loop should communicate: initialize -> update ALL interior cells -> complete layer -> swap -> repeat until M steps.

Use white background, strong blue #115EA2, dark blue #092F51, pale grid lines #C9D7E3, black text. No orange, glossy 3D, decorative robots, paper-title banner, footer, or watermarks. Large geometry, thick readable arrows, low text density, balanced use of the full canvas. English/symbol labels only: old, next, n, n+1, r, 1-4r, swap, M. Avoid a long typeset equation and Chinese paragraphs: the final PPT will overlay the exact editable equation and Chinese labels. Short symbols are still subject to later human/AI verification. Do not invent numerical temperatures or performance measurements.

## Audit after generation

Exactly five old inputs; four weights r and one center weight 1-4r; four axial directions; old n -> next n+1; no write into old; boundary zero; one swap after the entire layer; repeat to M. Reject any attractive image that breaks these facts.
