import clsx from 'clsx'

interface ShieldProps {
  tier: number
  size?: 'sm' | 'md' | 'lg' | 'xl'
  active?: boolean
  className?: string
}

const sizeStyle: Record<NonNullable<ShieldProps['size']>, { w: number; h: number }> = {
  sm: { w: 28, h: 36 },
  md: { w: 40, h: 48 },
  lg: { w: 56, h: 72 },
  xl: { w: 80, h: 104 },
}

/**
 * SVG shield glyph — designed to scale, recolor, and compose.
 * Used as a row of `tier` glyphs (active=true) followed by (5-tier)
 * dimmed glyphs, so the visual itself shows the score.
 */
export function Shield({ tier, size = 'md', active = true, className }: ShieldProps) {
  const dims = sizeStyle[size]
  const tierColor =
    tier === 1 ? '#ff3060'
    : tier === 2 ? '#ffb020'
    : tier === 3 ? '#00d4ff'
    : tier === 4 ? '#00ff9c'
    : tier === 5 ? '#b400ff'
    : '#4a5b80'

  const opacity = active ? 1 : 0.18
  const glow = active ? `drop-shadow(0 0 6px ${tierColor})` : 'none'

  return (
    <svg
      viewBox="0 0 40 52"
      width={dims.w}
      height={dims.h}
      className={clsx(className)}
      style={{ filter: glow }}
      aria-label={`Shield tier ${tier}`}
    >
      <defs>
        <linearGradient id={`shield-grad-${tier}-${active}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={tierColor} stopOpacity={opacity} />
          <stop offset="100%" stopColor={tierColor} stopOpacity={opacity * 0.4} />
        </linearGradient>
      </defs>
      <path
        d="M20 1 L37 7 V25 C37 38 29 47 20 51 C11 47 3 38 3 25 V7 Z"
        fill={`url(#shield-grad-${tier}-${active})`}
        stroke={tierColor}
        strokeWidth={active ? 1.5 : 1}
        opacity={opacity}
      />
      {/* Inner circuit */}
      <path
        d="M20 8 L30 12 V25 C30 33 25 40 20 43 C15 40 10 33 10 25 V12 Z"
        fill="none"
        stroke={tierColor}
        strokeOpacity={opacity * 0.6}
        strokeWidth={0.5}
      />
      {/* Tier mark */}
      <text
        x="20"
        y="29"
        textAnchor="middle"
        fontFamily="Share Tech Mono, monospace"
        fontWeight="bold"
        fontSize="11"
        fill={tierColor}
        opacity={opacity}
      >
        {tier}
      </text>
    </svg>
  )
}

/**
 * Tier color helper (kept for back-compat consumers).
 */
export function shieldColor(tier: number): string {
  switch (tier) {
    case 1:
      return '#ff3060'
    case 2:
      return '#ffb020'
    case 3:
      return '#00d4ff'
    case 4:
      return '#00ff9c'
    case 5:
      return '#b400ff'
    default:
      return '#4a5b80'
  }
}
