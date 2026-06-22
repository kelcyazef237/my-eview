import { useEffect, useRef } from 'react'

interface Node {
  x: number
  y: number
  vx: number
  vy: number
}

export function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let nodes: Node[] = []
    let animationId: number
    let lastFrame = 0
    const frameInterval = 1000 / 40 // cap at ~40fps
    let width = 0
    let height = 0
    let connectDistance = 120

    function getColors() {
      const isDark = document.documentElement.classList.contains('dark')
      const accent = isDark ? '96, 165, 250' : '15, 76, 129'
      return {
        nodeAlpha: isDark ? 0.5 : 0.3,
        lineAlpha: isDark ? 0.12 : 0.08,
        accent,
      }
    }

    function resize() {
      width = canvas!.width = window.innerWidth
      height = canvas!.height = window.innerHeight
      connectDistance = Math.min(140, width / 8)

      // Scale node count with viewport area, cap at 60
      const area = width * height
      const count = Math.min(60, Math.max(20, Math.floor(area / 25000)))

      nodes = Array.from({ length: count }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
      }))
    }

    function animate(timestamp: number) {
      animationId = requestAnimationFrame(animate)
      if (timestamp - lastFrame < frameInterval) return
      lastFrame = timestamp

      const { nodeAlpha, lineAlpha, accent } = getColors()

      ctx!.clearRect(0, 0, width, height)

      // Update positions
      for (const node of nodes) {
        node.x += node.vx
        node.y += node.vy
        if (node.x < 0 || node.x > width) node.vx *= -1
        if (node.y < 0 || node.y > height) node.vy *= -1
      }

      // Draw connections
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x
          const dy = nodes[i].y - nodes[j].y
          const dist = Math.sqrt(dx * dx + dy * dy)
          if (dist < connectDistance) {
            const opacity = lineAlpha * (1 - dist / connectDistance)
            ctx!.strokeStyle = `rgba(${accent}, ${opacity})`
            ctx!.lineWidth = 0.5
            ctx!.beginPath()
            ctx!.moveTo(nodes[i].x, nodes[i].y)
            ctx!.lineTo(nodes[j].x, nodes[j].y)
            ctx!.stroke()
          }
        }
      }

      // Draw nodes
      for (const node of nodes) {
        ctx!.fillStyle = `rgba(${accent}, ${nodeAlpha})`
        ctx!.beginPath()
        ctx!.arc(node.x, node.y, 1.8, 0, Math.PI * 2)
        ctx!.fill()
      }
    }

    let resizeTimer: number
    function debouncedResize() {
      clearTimeout(resizeTimer)
      resizeTimer = window.setTimeout(resize, 200)
    }

    resize()
    animationId = requestAnimationFrame(animate)
    window.addEventListener('resize', debouncedResize)

    return () => {
      cancelAnimationFrame(animationId)
      window.removeEventListener('resize', debouncedResize)
      clearTimeout(resizeTimer)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 pointer-events-none"
      aria-hidden="true"
    />
  )
}