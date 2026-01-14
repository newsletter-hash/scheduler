import { clsx } from 'clsx'
import type { BrandName } from '@/types'

interface BrandBadgeProps {
  brand: BrandName
  size?: 'sm' | 'md'
}

const brandConfig: Record<BrandName, { bg: string; text: string; label: string }> = {
  gymcollege: {
    bg: 'bg-[#00435c]',
    text: 'text-white',
    label: 'Gym College',
  },
  healthycollege: {
    bg: 'bg-[#2e7d32]',
    text: 'text-white',
    label: 'Healthy College',
  },
  vitalitycollege: {
    bg: 'bg-[#c2185b]',
    text: 'text-white',
    label: 'Vitality College',
  },
  longevitycollege: {
    bg: 'bg-[#6a1b9a]',
    text: 'text-white',
    label: 'Longevity College',
  },
}

export function getBrandLabel(brand: BrandName): string {
  return brandConfig[brand]?.label || brand
}

export function getBrandColor(brand: BrandName): string {
  const colors: Record<BrandName, string> = {
    gymcollege: '#00435c',
    healthycollege: '#2e7d32',
    vitalitycollege: '#c2185b',
    longevitycollege: '#6a1b9a',
  }
  return colors[brand] || '#666'
}

function BrandBadge({ brand, size = 'sm' }: BrandBadgeProps) {
  const config = brandConfig[brand]
  
  if (!config) {
    return <span className="badge bg-gray-100 text-gray-700">{brand}</span>
  }
  
  return (
    <span
      className={clsx(
        'badge',
        config.bg,
        config.text,
        size === 'sm' ? 'text-xs px-2 py-0.5' : 'text-sm px-3 py-1'
      )}
    >
      {config.label}
    </span>
  )
}

export default BrandBadge
