import { useState, useRef } from 'react'
import { Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { useQueryClient } from '@tanstack/react-query'
import { useCreateJob } from '@/api/jobs'
import type { BrandName, Variant } from '@/types'

const BRANDS: { id: BrandName; label: string; color: string }[] = [
  { id: 'gymcollege', label: 'Gym College', color: '#00435c' },
  { id: 'healthycollege', label: 'Healthy College', color: '#2e7d32' },
  { id: 'vitalitycollege', label: 'Vitality College', color: '#c2185b' },
  { id: 'longevitycollege', label: 'Longevity College', color: '#6a1b9a' },
]

const CTA_TYPES = [
  { id: 'follow_tips', label: '👉 Follow for more healthy tips' },
  { id: 'sleep_lean', label: '💬 Comment LEAN - Sleep Lean product' },
  { id: 'workout_plan', label: '💬 Comment PLAN - Workout & nutrition plan' },
]

function Generator() {
  const queryClient = useQueryClient()
  const createJob = useCreateJob()
  
  // Form state
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [selectedBrands, setSelectedBrands] = useState<BrandName[]>([
    'gymcollege', 
    'healthycollege', 
    'vitalitycollege', 
    'longevitycollege'
  ])
  const [variant, setVariant] = useState<Variant>('light')
  const [aiPrompt, setAiPrompt] = useState('')
  const [ctaType, setCtaType] = useState('follow_tips')
  
  // Loading states
  const [isAutoGenerating, setIsAutoGenerating] = useState(false)
  const [isCreatingJob, setIsCreatingJob] = useState(false)
  
  // Refs for highlighting
  const titleRef = useRef<HTMLTextAreaElement>(null)
  const contentRef = useRef<HTMLTextAreaElement>(null)
  
  // Toggle brand selection
  const toggleBrand = (brand: BrandName) => {
    setSelectedBrands(prev => 
      prev.includes(brand)
        ? prev.filter(b => b !== brand)
        : [...prev, brand]
    )
  }
  
  // Auto-generate viral content using AI
  const handleAutoGenerate = async () => {
    setIsAutoGenerating(true)
    
    try {
      const response = await fetch('/reels/auto-generate-content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Failed to generate content')
      }
      
      const data = await response.json()
      
      // Fill in the form with generated content
      setTitle(data.title)
      setContent(data.content_lines.join('\n'))
      
      // If image prompt exists, fill it in and switch to dark mode
      if (data.image_prompt) {
        setAiPrompt(data.image_prompt)
        setVariant('dark')
      }
      
      // Show success toast
      const topicInfo = data.topic_category ? ` (${data.topic_category})` : ''
      const formatInfo = data.format_style ? ` - ${data.format_style} style` : ''
      toast.success(`🎉 "${data.title}"${topicInfo}${formatInfo}`, { duration: 8000 })
      
      // Animate fields
      titleRef.current?.classList.add('highlight-pulse')
      contentRef.current?.classList.add('highlight-pulse')
      setTimeout(() => {
        titleRef.current?.classList.remove('highlight-pulse')
        contentRef.current?.classList.remove('highlight-pulse')
      }, 500)
      
    } catch (error) {
      console.error('Auto-generate error:', error)
      toast.error(error instanceof Error ? error.message : 'Failed to generate content')
    } finally {
      setIsAutoGenerating(false)
    }
  }
  
  // Create job and generate reels
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!title.trim()) {
      toast.error('Enter a title')
      return
    }
    
    if (selectedBrands.length === 0) {
      toast.error('Select at least one brand')
      return
    }
    
    // Parse content lines from textarea
    const contentLines = content.split('\n').filter(line => line.trim())
    if (contentLines.length === 0) {
      toast.error('Enter at least one content line')
      return
    }
    
    setIsCreatingJob(true)
    try {
      const job = await createJob.mutateAsync({
        title,
        content_lines: contentLines,
        brands: selectedBrands,
        variant,
        ai_prompt: variant === 'dark' ? aiPrompt : undefined,
        cta_type: ctaType,
      })
      
      // Clear the form for new input (like original vanilla JS)
      setTitle('')
      setContent('')
      setAiPrompt('')
      
      // Invalidate jobs query to update notification bell
      queryClient.invalidateQueries({ queryKey: ['jobs'] })
      
      // Show success toast with job ID
      toast.success(
        `✅ Job ${job.id.slice(0, 8)}... created and processing!`,
        { duration: 6000 }
      )
      
    } catch (error) {
      console.error('Error creating job:', error)
      toast.error('Failed to start generation')
    } finally {
      setIsCreatingJob(false)
    }
  }
  
  return (
    <div className="content-wrapper">
      <div className="container">
        <h1>📱 Instagram Reels Generator</h1>
        
        <form onSubmit={handleSubmit}>
          {/* Title */}
          <div className="form-group">
            <label htmlFor="title">Title</label>
            <textarea
              ref={titleRef}
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              rows={2}
              placeholder="e.g., Ultimate Rice Guide&#10;(Use Enter for line breaks)"
              required
              className="input-textarea"
              style={{ resize: 'vertical', minHeight: '50px' }}
            />
            <div className="help-text">Press Enter to add line breaks in the title</div>
          </div>
          
          {/* Variant */}
          <div className="form-group">
            <label>Variant</label>
            <div className="variant-options">
              <label className="radio-label">
                <input 
                  type="radio" 
                  name="variant" 
                  value="light"
                  checked={variant === 'light'}
                  onChange={() => setVariant('light')}
                /> 
                Light Mode
              </label>
              <label className="radio-label">
                <input 
                  type="radio" 
                  name="variant" 
                  value="dark"
                  checked={variant === 'dark'}
                  onChange={() => setVariant('dark')}
                /> 
                Dark Mode
              </label>
            </div>
            <div className="help-text">Light slots: 12AM, 8AM, 4PM | Dark slots: 4AM, 12PM, 8PM</div>
          </div>
          
          {/* AI Prompt (Dark Mode Only) */}
          {variant === 'dark' && (
            <div className="form-group">
              <label htmlFor="aiPrompt">AI Background Prompt (Dark Mode Only)</label>
              <textarea
                id="aiPrompt"
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                rows={4}
                placeholder="Describe the background you want for dark mode."
                className="input-textarea"
              />
              <div className="help-text">Optional: Customize the AI-generated background.</div>
            </div>
          )}
          
          {/* Brands */}
          <div className="form-group">
            <label>Brands</label>
            <div className="brand-options">
              {BRANDS.map(brand => (
                <label key={brand.id} className="checkbox-label">
                  <input 
                    type="checkbox" 
                    checked={selectedBrands.includes(brand.id)}
                    onChange={() => toggleBrand(brand.id)}
                  /> 
                  {brand.label}
                </label>
              ))}
            </div>
            <div className="help-text">Each brand has its own independent schedule</div>
          </div>
          
          {/* CTA Type */}
          <div className="form-group">
            <label htmlFor="ctaType">Call-to-Action</label>
            <select
              id="ctaType"
              value={ctaType}
              onChange={(e) => setCtaType(e.target.value)}
              className="select-input"
            >
              {CTA_TYPES.map(cta => (
                <option key={cta.id} value={cta.id}>{cta.label}</option>
              ))}
            </select>
            <div className="help-text">Select the call-to-action for the caption</div>
          </div>
          
          {/* Content Lines */}
          <div className="form-group">
            <label htmlFor="content">Content Lines</label>
            <textarea
              ref={contentRef}
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={`Enter one item per line:
Rice — Always rinse before cooking
Garlic — Crush for maximum flavor
Pasta — Salt the water generously
Chicken — Let it rest after cooking`}
              required
              className="input-textarea content-textarea"
            />
            <div className="help-text">Enter one line per item. Use "—" or "-" to separate keyword from description.</div>
          </div>
          
          {/* Action Buttons */}
          <div className="button-group">
            <button 
              type="submit" 
              disabled={isCreatingJob}
              className="btn-primary"
            >
              {isCreatingJob ? (
                <>
                  <Loader2 className="spinner-icon" />
                  Creating...
                </>
              ) : (
                '🎬 Generate Reels'
              )}
            </button>
            <button 
              type="button" 
              onClick={handleAutoGenerate}
              disabled={isAutoGenerating}
              className="btn-auto-generate"
            >
              {isAutoGenerating ? (
                <>
                  <Loader2 className="spinner-icon" />
                  Generating...
                </>
              ) : (
                '🤖 Auto-Generate Viral Post'
              )}
            </button>
          </div>
          <div className="help-text" style={{ marginTop: '8px' }}>
            💡 <strong>Auto-Generate</strong> uses AI to create a complete viral post (title, content & image prompt) from scratch!
          </div>
        </form>
      </div>
    </div>
  )
}

export default Generator
