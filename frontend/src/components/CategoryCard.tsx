import type { CategoryScore } from '@/types'

interface CategoryCardProps {
  category: CategoryScore
}

export function CategoryCard({ category }: CategoryCardProps) {
  const lostRatio = category.points_lost / category.points_total
  const statusColor =
    lostRatio === 0
      ? 'bg-emerald-500'
      : lostRatio < 0.3
        ? 'bg-amber-500'
        : 'bg-red-500'

  return (
    <div className="card p-5">
      <div className="mb-2 flex items-start justify-between">
        <div>
          <div className="text-sm font-medium text-[var(--text-secondary)]">
            {category.parent_group}
          </div>
          <h3 className="text-base font-semibold">{category.category_name}</h3>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold">
            {category.points_remaining}/{category.points_total}
          </div>
          <div className="text-xs text-[var(--text-muted)]">
            {category.points_lost > 0 ? `-${category.points_lost} lost` : 'No deductions'}
          </div>
        </div>
      </div>

      <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--bg-secondary)]">
        <div
          className={`h-full rounded-full ${statusColor}`}
          style={{
            width: `${(category.points_remaining / category.points_total) * 100}%`,
          }}
        />
      </div>
    </div>
  )
}
