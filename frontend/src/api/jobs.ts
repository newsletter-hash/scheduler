import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { get, post, put, del } from './client'
import type { Job, BrandName } from '@/types'

// Response types from the backend
interface BackendJob {
  job_id: string
  user_id?: string
  title: string
  content_lines: string[]
  brands: BrandName[]
  variant: 'light' | 'dark'
  ai_prompt?: string
  cta_type: string
  status: string
  brand_outputs: Record<string, unknown>
  current_step?: string
  progress_percent?: number
  ai_background_path?: string
  created_at: string
  started_at?: string
  completed_at?: string
  error_message?: string
}

interface JobsListResponse {
  jobs: BackendJob[]
  total: number
}

interface JobCreateResponse {
  status: string
  job_id: string
  message: string
  job: BackendJob
}

// Transform backend job to frontend format (map job_id to id)
function transformJob(backendJob: BackendJob): Job {
  return {
    ...backendJob,
    id: backendJob.job_id,  // Map job_id to id for frontend consistency
  } as Job
}

// API functions
export const jobsApi = {
  list: async () => {
    const response = await get<JobsListResponse>('/jobs/')
    return response.jobs.map(transformJob) // Transform each job
  },
  
  get: async (id: number | string) => {
    const job = await get<BackendJob>(`/jobs/${id}`)
    return transformJob(job)
  },
  
  create: async (data: {
    title: string
    content_lines: string[]
    brands: BrandName[]
    variant: 'light' | 'dark'
    ai_prompt?: string
    cta_type: string
  }) => {
    const response = await post<JobCreateResponse>('/jobs/create', data)
    return transformJob(response.job) // Transform job from response
  },
  
  update: async (id: number | string, data: Partial<Job>) => {
    const job = await put<BackendJob>(`/jobs/${id}`, data)
    return transformJob(job)
  },
  
  delete: (id: number | string) => del<{ success: boolean }>(`/jobs/${id}`),
  
  cancel: async (id: number | string) => {
    const job = await post<BackendJob>(`/jobs/${id}/cancel`)
    return transformJob(job)
  },
  
  regenerate: async (id: number | string) => {
    const job = await post<BackendJob>(`/jobs/${id}/regenerate`)
    return transformJob(job)
  },
  
  regenerateBrand: async (id: number | string, brand: BrandName) => {
    const job = await post<BackendJob>(`/jobs/${id}/regenerate/${brand}`)
    return transformJob(job)
  },
  
  getNextSlots: (id: number | string) => 
    get<Record<BrandName, { next_slot: string; formatted: string }>>(`/jobs/${id}/next-slots`),
  
  updateBrandStatus: async (id: number | string, brand: BrandName, status: string, scheduledTime?: string) => {
    const job = await post<BackendJob>(`/jobs/${id}/brand/${brand}/status`, { status, scheduled_time: scheduledTime })
    return transformJob(job)
  },
}

// React Query hooks
export function useJobs() {
  return useQuery({
    queryKey: ['jobs'],
    queryFn: jobsApi.list,
    refetchInterval: 10000, // Poll every 10 seconds for updates
  })
}

export function useJob(id: number | string) {
  return useQuery({
    queryKey: ['jobs', id],
    queryFn: () => jobsApi.get(id),
    refetchInterval: (query) => {
      // Poll more frequently if job is generating
      const job = query.state.data
      if (job?.status === 'generating' || job?.status === 'pending') {
        return 3000
      }
      return 30000
    },
  })
}

export function useCreateJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: jobsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useUpdateJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, data }: { id: number | string; data: Partial<Job> }) => 
      jobsApi.update(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['jobs', id] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useDeleteJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: jobsApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useCancelJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: jobsApi.cancel,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['jobs', id] })
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
    },
  })
}

export function useRegenerateJob() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: jobsApi.regenerate,
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['jobs', id] })
    },
  })
}

export function useRegenerateBrand() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, brand }: { id: number | string; brand: BrandName }) => 
      jobsApi.regenerateBrand(id, brand),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['jobs', id] })
    },
  })
}

export function useJobNextSlots(id: number | string) {
  return useQuery({
    queryKey: ['jobs', id, 'next-slots'],
    queryFn: () => jobsApi.getNextSlots(id),
    enabled: !!id,
  })
}

export function useUpdateBrandStatus() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: ({ id, brand, status, scheduledTime }: { 
      id: number | string; 
      brand: BrandName; 
      status: string;
      scheduledTime?: string;
    }) => jobsApi.updateBrandStatus(id, brand, status, scheduledTime),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['jobs', id] })
      queryClient.invalidateQueries({ queryKey: ['scheduled'] })
    },
  })
}
