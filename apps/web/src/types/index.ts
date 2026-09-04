export interface User {
  id: string;
  email: string;
  username: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface ResearcherProfile {
  id: string;
  user_id: string;
  interests: string[];
  skills: string[];
  projects: string[];
  publications: any[];
  research_goals: string[];
  preferred_sources: string[];
  preferred_models: string[];
  preferred_languages: string[];
  privacy_preferences: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  name: string;
  description: string;
  status: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Source {
  id: string;
  user_id: string;
  title: string;
  url: string;
  source_type: string;
  author: string;
  doi: string;
  publisher: string;
  published_at: string;
  retrieved_at: string;
  quality_score: number;
  visibility: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Memory {
  id: string;
  user_id: string;
  project_id: string;
  source_id: string;
  type: string;
  content: string;
  confidence: number;
  importance: number;
  source_reference: string;
  user_verified: boolean;
  visibility: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Skill {
  id: string;
  user_id: string;
  name: string;
  description: string;
  input_schema: Record<string, any>;
  steps: any[];
  output_schema: Record<string, any>;
  permissions: Record<string, any>;
  is_builtin: boolean;
  is_active: boolean;
  created_at: string;
}

export interface SearchResult {
  title: string;
  url: string;
  source_type: string;
  author: string;
  score: number;
  metadata: Record<string, any>;
}

export interface ResearchResponse {
  question: string;
  answer: string;
  evidence: any[];
  sources: any[];
  confidence: number;
  timestamp: string;
}

export interface EnergyStatus {
  mode: string;
  llm_requests: number;
  tokens_used: number;
  embedding_operations: number;
  documents_processed: number;
  cache_hits: number;
  cache_misses: number;
  local_vs_cloud: Record<string, number>;
  estimated_footprint: string;
}
