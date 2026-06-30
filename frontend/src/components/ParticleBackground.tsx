import { useEffect, useRef } from 'react'

/**
 * Hack-style multi-layered background:
 *   - hex grid traced from moving node swarm
 *   - horizontal scanline sweep
 *   - radial cyan / violet glows via CSS orbs
 *
 * Performance: capped at ~30fps, paused when document is hidden.
 */
export function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let nodes: { x: number; y: number; vx: number; vy: number; r: number }[] = []
    let animationId = 0
    let lastFrame = 0
    const frameInterval = 1000 / 30
    let width = 0
    let height = 0
    const hexSize = 28
    let connectDistance = 130
    let visible = !document.hidden

    function resize() {
      width = canvas!.width = window.innerWidth
      height = canvas!.height = window.innerHeight
      connectDistance = Math.min(160, width / 6)

      const area = width * height
      const count = Math.min(70, Math.max(28, Math.floor(area / 22000)))

      nodes = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        r: 1 + Math.random() * 1.5,
      }))
    }

    function drawHex(x: number, y: number, size: number, alpha: number) {
      ctx!.beginPath()
      for (let i = 0; i < 6; i++) {
        const a = (Math.PI / 3) * i + Math.PI / 6
        const hx = x + Math.cos(a) * size
        const hy = y + Math.sin(a) * size
        if (i === 0) ctx!.moveTo(hx, hy)
        else ctx!.lineTo(hx, hy)
      }
      ctx!.closePath()
      ctx!.strokeStyle = `rgba(0, 240, 255, ${alpha})`
      ctx!.lineWidth = 0.6
      ctx!.stroke()
    }

    function animate(timestamp: number) {
      animationId = requestAnimationFrame(animate)
      if (!visible) return
      if (timestamp - lastFrame < frameInterval) return
      lastFrame = timestamp

      ctx!.clearRect(0, 0, width, height)

      // Move nodes
      for (const n of nodes) {
        n.x += n.vx
        n.y += n.vy
        if (n.x < 0 || n.x > width) n.vx *= -1
        if (n.y < 0 || n.y > height) n.vy *= -1
      }

      // Draw lattice hex centers behind connections
      const spacing = hexSize * Math.sqrt(3)
      const rows = Math.ceil(height / (hexSize * 1.5)) + 1
      const cols = Math.ceil(width / spacing) + 2
      for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
          const x = c * spacing + (r % 2) * (spacing / 2)
          const y = r * hexSize * 1.5
          // only draw hexes near active nodes
          let nearest = Infinity
          for (const n of nodes) {
            const dx = n.x - x
            const dy = n.y - y
            const d = Math.sqrt(dx * dx + dy * dy)
            if (d < nearest) nearest = d
          }
          if (nearest < 220) {
            const a = 0.18 * (1 - nearest / 220)
            drawHex(x, y, hexSize / 2.4, a)
          }
        }
      }

      // Connections between nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x
          const dy = nodes[i].y - nodes[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < connectDistance) {
            const t = dist / connectDistance
            const stroke = `rgba(0, 240, 255, ${(1 - t) * 0.18})`
            ctx!.strokeStyle = stroke
            ctx!.lineWidth = 0.6
            ctx!.beginPath()
            ctx!.moveTo(nodes[i].x, nodes[i].y)
            ctx!.lineTo(nodes[j].x, nodes[j].y)
            ctx!.stroke()
          }
        }
      }

      // Nodes
      for (const n of nodes) {
        ctx!.beginPath()
        ctx!.arc(n.x, n.y, n.r, 0, Math.PI * 2)
        ctx!.fillStyle = 'rgba(0, 240, 255, 0.7)'
        ctx!.fill()
        // Glow
        ctx!.beginPath()
        ctx!.arc(n.x, n.y, n.r * 3, 0, Math.PI * 2)
        const grad = ctx!.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 3)
        grad.addColorStop(0, 'rgba(180, 0, 255, 0.32)')
        grad.addColorStop(1, 'rgba(180, 0, 255, 0)')
        ctx!.fillStyle = grad
        ctx!.fill()
      }
    }

    function onVisibility() {
      visible = !document.hidden
    }

    let resizeTimer: number
    function debouncedResize() {
      clearTimeout(resizeTimer)
      resizeTimer = window.setTimeout(resize, 200)
    }

    resize()
    animationId = requestAnimationFrame(animate)
    window.addEventListener('resize', debouncedResize)
    document.addEventListener('visibilitychange', onVisibility)

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', debouncedResize)
      document.removeEventListener('visibilitychange', onVisibility)
      clearTimeout(resizeTimer)
    }
  }, [])

  return (
    <>
      <canvas
        ref={canvasRef}
        className="fixed inset-0 -z-10 pointer-events-none"
        aria-hidden="true"
      />
      {/* Glow orbs (CSS animated) + scanline overlays on top */}
      <div className="bg-orbs" aria-hidden="true">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <div className="orb orb-3" />
      </div>
    </>
  )
}
