import { ApplicantInput, ScoringResponse, StoredApplicant } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'https://sreejithm-leaseth-mvp.hf.space'
const LOCAL_STORAGE_KEY = 'leaseth_submissions'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

// Local storage helpers for offline/demo mode
function getLocalAssessments(): StoredApplicant[] {
  try {
    const data = localStorage.getItem(LOCAL_STORAGE_KEY)
    return data ? JSON.parse(data) : []
  } catch {
    return []
  }
}

function saveLocalAssessment(input: ApplicantInput, result: ScoringResponse): void {
  try {
    const assessments = getLocalAssessments()
    const stored: StoredApplicant = {
      id: result.applicant_id || `local-${Date.now()}`,
      input,
      result,
      scored_at: new Date().toISOString(),
    }
    assessments.unshift(stored) // Add to beginning
    localStorage.setItem(LOCAL_STORAGE_KEY, JSON.stringify(assessments.slice(0, 100))) // Keep last 100
  } catch (e) {
    console.error('Failed to save to local storage:', e)
  }
}

export async function scoreApplicant(data: ApplicantInput): Promise<ScoringResponse> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 15000) // 15s timeout

  // Ensure applicant_id exists
  const requestData = {
    ...data,
    applicant_id: data.applicant_id || `app-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  }

  try {
    const response = await fetch(`${API_URL}/api/score`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new ApiError(
        response.status,
        errorData.detail || `API error: ${response.status}`
      )
    }

    const result = await response.json()

    // Save to local storage for offline access
    saveLocalAssessment(data, result)

    return result
  } catch (error) {
    clearTimeout(timeoutId)

    if (error instanceof ApiError) {
      throw error
    }

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new ApiError(408, 'Request timed out. The server might be starting up - please try again.')
      }
      throw new ApiError(0, `Could not reach the server. ${error.message}`)
    }

    throw new ApiError(0, 'An unexpected error occurred')
  }
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/health`, {
      method: 'GET',
    })
    return response.ok
  } catch {
    return false
  }
}

export async function fetchApplicants(skip = 0, limit = 50): Promise<StoredApplicant[]> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000) // 10s timeout

  try {
    const response = await fetch(
      `${API_URL}/api/applicants?skip=${skip}&limit=${limit}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal,
      }
    )

    clearTimeout(timeoutId)

    if (!response.ok) {
      // If API fails, fall back to local storage
      console.warn('API unavailable, using local storage')
      return getLocalAssessments()
    }

    const apiData = await response.json()

    // Merge with local data (API data takes precedence)
    const localData = getLocalAssessments()
    const apiIds = new Set(apiData.map((a: StoredApplicant) => a.id))
    const mergedData = [
      ...apiData,
      ...localData.filter(a => !apiIds.has(a.id))
    ]

    return mergedData
  } catch (error) {
    clearTimeout(timeoutId)

    // On any error, fall back to local storage
    console.warn('Failed to fetch from API, using local storage:', error)
    return getLocalAssessments()
  }
}

// Clear local assessments (for testing)
export function clearLocalAssessments(): void {
  localStorage.removeItem(LOCAL_STORAGE_KEY)
}
