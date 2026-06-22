import clsx from 'clsx'

interface ShieldProps {
  tier: number
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

const sizeClasses = {
  sm: 'w-6 h-8 text-[10px]',
  md: 'w-10 h-14 text-xs',
  lg: 'w-16 h-22 text-sm',
  xl: 'w-24 h-32 text-base',
}

export function Shield({ tier, size = 'md', className }: ShieldProps) {
  const marks = Array.from({ length: 5 }, (_, i) => i < tier)

  return (
    <div
      className={clsx(
        'relative flex flex-col items-center justify-center rounded-t-lg border-2 border-current',
        sizeClasses[size],
        className,
      )}
      aria-label={`Shield tier ${tier}`}
    >
      <span className="font-mono font-bold">{tier}</span>
      <div className="mt-1 flex gap-0.5">
        {marks.map((filled, idx) => (
          <div
            key={idx}
            className={clsx(
              'h-1 w-1 rounded-full',
              filled ? 'bg-current' : 'bg-current/20',
            )}
          />
        ))}
      </div>
    </div>
  )
}

export function shieldColor(tier: number): string {
  switch (tier) {
    case 1:
      return 'text-shield-1'
    case 2:
      return 'text-shield-2'
    case 3:
      return 'text-shield-3'
    case 4:
      return 'text-shield-4'
    case 5:
      return 'text-shield-5'
    default:
      return 'text-[var(--text-muted)]'
  }
}
