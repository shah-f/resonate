import { useEffect, useRef } from "react";

/**
 * Animated "cosmic instrument" backdrop for the landing page.
 * Glowing ember orb + tilted orbital rings with traveling satellite nodes,
 * constellation hairlines and a twinkling starfield — all in the warm palette.
 * Pure 2D canvas; respects prefers-reduced-motion.
 */
export function CosmicBackdrop() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvasEl = canvasRef.current;
    if (!canvasEl) return;
    const canvas = canvasEl;
    const rawCtx = canvas.getContext("2d");
    if (!rawCtx) return;
    const ctx = rawCtx;

    const reduceMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    let width = 0;
    let height = 0;
    let cx = 0;
    let cy = 0;

    const STAR_COUNT = 150;
    const stars = Array.from({ length: STAR_COUNT }, () => ({
      x: Math.random(),
      y: Math.random(),
      r: Math.random() * 1.2 + 0.2,
      phase: Math.random() * Math.PI * 2,
      speed: Math.random() * 1.4 + 0.4,
    }));

    const TILT = 0.34;
    const rings = [
      { rx: 0.2, op: 0.5 },
      { rx: 0.31, op: 0.32 },
      { rx: 0.44, op: 0.2 },
    ];

    const nodes = [
      { ring: 0, a: 0.0, s: 0.34, sz: 2.6 },
      { ring: 1, a: 2.1, s: -0.22, sz: 2.1 },
      { ring: 2, a: 4.0, s: 0.16, sz: 1.9 },
      { ring: 1, a: 5.4, s: 0.27, sz: 1.7 },
    ];

    function resize() {
      width = canvas.clientWidth;
      height = canvas.clientHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      cx = width / 2;
      cy = height * 0.4;
    }

    let raf = 0;
    let t = 0;

    function frame() {
      if (!reduceMotion) t += 0.016;
      ctx.clearRect(0, 0, width, height);
      const baseR = Math.min(width, height);

      // Starfield
      for (const st of stars) {
        const tw = reduceMotion
          ? 0.6
          : Math.sin(t * st.speed + st.phase) * 0.5 + 0.5;
        ctx.globalAlpha = 0.12 + tw * 0.5;
        ctx.fillStyle = "#ffd9a8";
        ctx.beginPath();
        ctx.arc(st.x * width, st.y * height, st.r, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;

      // Glowing ember orb
      const pulse = reduceMotion ? 0.5 : Math.sin(t * 0.8) * 0.5 + 0.5;
      const orbR = baseR * 0.16;
      const haloR = orbR * (1.55 + pulse * 0.28);
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, haloR);
      grad.addColorStop(0, "rgba(255, 178, 96, 0.95)");
      grad.addColorStop(0.35, "rgba(249, 115, 22, 0.5)");
      grad.addColorStop(0.7, "rgba(234, 88, 12, 0.16)");
      grad.addColorStop(1, "rgba(234, 88, 12, 0)");
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(cx, cy, haloR, 0, Math.PI * 2);
      ctx.fill();

      // Dark planet core + ember rim
      ctx.fillStyle = "rgba(18, 11, 6, 0.92)";
      ctx.beginPath();
      ctx.arc(cx, cy, orbR * 0.58, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "rgba(251, 146, 60, 0.55)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.arc(cx, cy, orbR * 0.58, 0, Math.PI * 2);
      ctx.stroke();

      // Orbital rings (tilted)
      for (const ring of rings) {
        const rx = baseR * ring.rx;
        ctx.strokeStyle = `rgba(251, 146, 60, ${ring.op})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.ellipse(cx, cy, rx, rx * TILT, 0, 0, Math.PI * 2);
        ctx.stroke();
      }

      // Satellite node positions
      const pts = nodes.map((n) => {
        const rx = baseR * rings[n.ring].rx;
        const a = n.a + (reduceMotion ? 0 : t * n.s);
        return {
          x: cx + Math.cos(a) * rx,
          y: cy + Math.sin(a) * rx * TILT,
          sz: n.sz,
        };
      });

      // Constellation hairlines
      ctx.strokeStyle = "rgba(251, 146, 60, 0.13)";
      ctx.lineWidth = 1;
      for (let i = 0; i < pts.length; i++) {
        for (let j = i + 1; j < pts.length; j++) {
          const dist = Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y);
          if (dist < baseR * 0.52) {
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.stroke();
          }
        }
      }

      // Satellite nodes with soft glow
      for (const p of pts) {
        ctx.globalAlpha = 0.22;
        ctx.fillStyle = "#fb923c";
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.sz * 2.6, 0, Math.PI * 2);
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.fillStyle = "#ffd9a8";
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.sz, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.globalAlpha = 1;

      raf = requestAnimationFrame(frame);
    }

    resize();
    frame();
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none absolute inset-0 h-full w-full"
      data-testid="canvas-cosmic-backdrop"
      aria-hidden="true"
    />
  );
}
