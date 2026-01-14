import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { get, post, del } from './client'
import type { BrandName } from '@/types'

interface GenerateViralRequest {
  topic: string
  brands?: BrandName[]
}

interface GenerateViralResponse {
  title: string
  content_lines: string[]
}

interface GenerateCaptionsRequest {
  title: string
  content_lines: string[]
  brands: BrandName[]
}

interface ScheduleReelRequest {
  brand: BrandName
  job_id: string
  reel_id: string
  scheduled_time?: string
}

interface AutoScheduleRequest {
  brand: BrandName
  reel_id: string
  variant: string
  caption?: string
  user_id?: string
  video_path?: string
  thumbnail_path?: string
}

interface NextSlotResponse {
  brand: BrandName
  next_slot: string
  formatted: string
}

// API functions
export const reelsApi = {
  generateViral: (data: GenerateViralRequest) => 
    post<GenerateViralResponse>('/reels/generate-viral', data),
  
  generateCaptions: (data: GenerateCaptionsRequest) =>
    post<Record<BrandName, string>>('/reels/generate-captions', data),
  
  schedule: (data: ScheduleReelRequest) =>
    post<{ success: boolean; scheduled_time: string }>('/reels/schedule', data),
  
  autoSchedule: (data: AutoScheduleRequest) =>
    post<{ success: boolean; scheduled_for: string }>('/reels/schedule-auto', data),
  
  getScheduled: async () => {
    const response = await get<{ total: number; schedules: Array<{
      schedule_id: string
      reel_id: string
      scheduled_time: string
      status: string
      platforms: string[]
      brand: string
      variant: string
      caption?: string
      created_at?: string
      published_at?: string
      error?: string
    }> }>('/reels/scheduled')
    // Transform to expected format
    return response.schedules.map(s => ({
      id: s.schedule_id,
      brand: s.brand as BrandName,
      job_id: s.reel_id, // Use reel_id as identifier
      reel_id: s.reel_id,
      title: s.caption || 'Scheduled Post',
      scheduled_time: s.scheduled_time,
      caption: s.caption,
      status: s.status,
    }))
  },
  
  deleteScheduled: (id: string) =>
    del<{ success: boolean }>(`/reels/scheduled/${id}`),
  
  getNextSlots: () =>
    get<Record<BrandName, NextSlotResponse>>('/reels/next-slots'),
  
  getNextSlotForBrand: (brand: BrandName) =>
    get<NextSlotResponse>(`/reels/next-slot/${brand}`),
}

// React Query hooks
export function useGenerateViral() {
  return useMutation({
    mutationFn: reelsApi.generateViral,
  })
}

export function useGenerateCaptions() {
  return useMutation({
    mutationFn: reelsApi.generateCaptions,
  })
}

export function useScheduleReel() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: reelsApi.schedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduled'] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useAutoScheduleReel() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: reelsApi.autoSchedule,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduled'] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useScheduledPosts() {
  return useQuery({
    queryKey: ['scheduled'],
    queryFn: reelsApi.getScheduled,
    refetchInterval: 30000,
  })
}

export function useDeleteScheduled() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: reelsApi.deleteScheduled,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scheduled'] })
    },
  })
}

export function useNextSlots() {
  return useQuery({
    queryKey: ['next-slots'],
    queryFn: reelsApi.getNextSlots,
    staleTime: 60000,
  })
}
