export type SearchDirection = 'most_similar' | 'best_quality' | 'lowest_price' | 'best_value'
export type RunStatus = 'pending' | 'running' | 'partial' | 'completed' | 'failed'

export interface Candidate {
  product_id: string
  brand: string
  model: string
  exact_variant?: string | null
  estimated_price: number
  estimated_used_price_pln?: number
  key_features: string[]
  similarity_reasons: string[]
  differences: string[]
  why_it_fits: string
  tradeoff: string
  image_url?: string | null
  confidence: number
  data_gaps: string[]
}

export interface SessionResponse {
  session_id: string
  stage: 'discovery'
}

export interface MessageResponse {
  session_id: string
  stage: 'discovery' | 'product_selection' | 'searching'
  question?: string | null
  candidates: Candidate[]
  run_id?: string
  status?: RunStatus
  is_final_ranking: boolean
}

export interface Listing {
  source: string
  title: string
  url: string
  price: string | number
  currency: string
  condition: string
  exact_variant?: string | null
  warranty?: string | null
  returns?: string | null
  location?: string | null
  image_urls?: string[]
  retrieved_at?: string | null
  data_gaps?: string[]
  confidence?: number
}

export interface Recommendation {
  rank: number
  recommended: boolean
  score: number
  score_breakdown: {
    product_match?: number
    offer_quality?: number
    seller_trust?: number
    confidence?: number
    data_gaps?: string[]
    [key: string]: unknown
  }
  explanation?: string | null
  listings?: Listing
  listing?: Listing
  source_url?: string | null
  retrieved_at?: string | null
  confidence: number
  data_gaps: string[]
  is_stale: boolean
  field_availability: Record<string, string | number | boolean | null>
}

export interface RunResponse {
  id: string
  status: RunStatus
  recommendations: Recommendation[]
  sources_succeeded?: string[]
  error_summary?: Record<string, string>
  new_price_benchmark?: {
    product_name: string
    price: string | number
    currency: string
    url: string
    source: string
    retrieved_at: string
  } | null
}
