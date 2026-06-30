import type { CategoryScore } from '@/types'

interface CategoryCardProps {
  category: CategoryScore
}

export function CategoryCard({ category }: CategoryCardProps) {
  const lostRatio = category.points_lost / category.points_total
  const statusColor =
    lostRatio === 0
      ? '#00ff9c'
      : lostRatio < 0.3
        ? '#ffb020'
        : '#ff3060'

  const remainingPct = (category.points_remaining / category.points_total) * 100

  return (
    <div className="panel glass-card-hover p-4">
      <div className="mb-3 flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="num text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
            ▸ {category.parent_group}
          </div>
          <h3 className="mt-0.5 truncate display-title text-[13px] tracking-[0.04em] text-white">
            {category.category_name}
          </h3>
        </div>
        <div className="text-right">
          <div
            className="num text-xl font-bold leading-none glitch"
            data-text={`${category.points_remaining}/${category.points_total}`}
            style={{ color: statusColor, textShadow: `0 0 10px ${statusColor}80` }}
          >
            {category.points_remaining}/{category.points_total}
          </div>
          <div className="num mt-1 text-[10px] uppercase tracking-[0.12em]" style={{ color: statusColor }}>
            {category.points_lost > 0 ? `-${category.points_lost} lost` : 'no.deductions'}
          </div>
        </div>
      </div>

      <div className="relative h-2 w-full overflow-hidden rounded-sm bg-[rgba(0,240,255,0.06)]">
        <div
          className="absolute left-0 top-0 h-full"
          style={{
            width: `${remainingPct}%`,
            background: statusColor,
            boxShadow: `0 0 12px ${statusColor}80`,
          }}
        />
        {/* tick marks */}
        {Array.from({ length: 10 }).map((_, i) => (
          <div
            key={i}
            className="absolute top-0 h-full w-px bg-[rgba(0,0,0,0.5)]"
            style={{ left: `${(i + 1) * 10}%` }}
          />
        ))}
      </div>
    </div>
  )
}
