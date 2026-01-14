// Type definitions for the application

export type BrandName = 'gymcollege' | 'healthycollege' | 'vitalitycollege' | 'longevitycollege'

export type JobStatus = 'pending' | 'generating' | 'completed' | 'failed' | 'cancelled'

export type BrandStatus = 'pending' | 'generating' | 'completed' | 'failed' | 'scheduled'

export type Variant = 'light' | 'dark'

export interface BrandOutput {
  status: BrandStatus
  reel_id?: string
  thumbnail_path?: string
  video_path?: string
  caption?: string
  scheduled_time?: string
  error?: string
}

export interface Job {
  id: string  // Maps to job_id from backend
  job_id: string  // Backend uses job_id as string UUID
  user_id?: string
  title: string
  content_lines: string[]
  brands: BrandName[]
  variant: Variant
  ai_prompt?: string
  cta_type: string
  status: JobStatus
  brand_outputs: Record<BrandName, BrandOutput>
  current_step?: string
  progress_percent?: number
  ai_background_path?: string
  created_at: string
  started_at?: string
  completed_at?: string
  updated_at?: string
  error_message?: string
}

export interface ScheduledPost {
  id: string
  brand: BrandName
  job_id: number
  reel_id: string
  title: string
  scheduled_time: string
  thumbnail_path?: string
  video_path?: string
  caption?: string
  status: 'scheduled' | 'published' | 'failed'
}

export interface NextSlot {
  brand: BrandName
  next_slot: string
  formatted: string
}

export interface GenerateReelRequest {
  title: string
  content_lines: string[]
  brands: BrandName[]
  variant: Variant
  ai_prompt?: string
  cta_type: string
}

export interface ScheduleRequest {
  brand: BrandName
  job_id: number
  reel_id: string
  scheduled_time?: string
  auto_schedule?: boolean
}
