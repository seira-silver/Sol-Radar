export interface Evidence {
  evidence: string
  signal_id: number
  content_url: string
  source_name: string
  signal_title: string
}

export interface Idea {
  id: number
  title: string
  description: string
  problem: string
  solution: string
  why_solana: string
  scale_potential: string
  market_signals?: string | null
  supporting_signals: string[]
  created_at: string
}

export interface Narrative {
  id: number
  title: string
  summary: string
  confidence: "high" | "medium" | "low" | string
  confidence_reasoning: string
  is_active: boolean
  velocity_score: number
  rank: number | null
  tags: string[]
  key_evidence: Evidence[]
  supporting_source_names: string[]
  idea_count: number
  ideas?: Idea[]
  created_at: string
  updated_at: string
  last_detected_at: string
}

export interface NarrativeListResponse {
  narratives: Narrative[]
  total: number
  limit: number
  offset: number
}

export interface Signal {
  id: number
  scraped_content_id: number
  signal_title: string
  description: string
  signal_type: string
  novelty: "high" | "medium" | "low" | string
  evidence: string
  related_projects: string[]
  tags: string[]
  created_at: string
  content_url: string
  content_title?: string | null
  scraped_at: string
  data_source_id: number
  data_source_name: string
  data_source_url: string
  data_source_type: string
  data_source_category: string
}

export interface SignalListResponse {
  signals: Signal[]
  total: number
  limit: number
  offset: number
}

export interface Stats {
  active_narratives_count: number
  total_narratives_count: number
  total_ideas_count: number
  avg_velocity_score: number
  active_builders: number
  sources_scraped_count: number
  total_signals_count: number
  last_web_scrape_time: string | null
  last_twitter_scrape_time: string | null
  next_synthesis_time: string | null
}

export interface LandingResponse {
  stats: Stats
  narratives: NarrativeListResponse & { narratives: (Narrative & { ideas: Idea[] })[] }
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export interface ChatRequest {
  messages: ChatMessage[]
  url?: string | null
}

