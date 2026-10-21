export type ServiceParams = {
  price_from?: string;
  price_to?: string;
  duration?: string;
  [key: string]: string | undefined;
};

export type Service = {
  id: number;
  name: string;
  description: string | null;
  params: ServiceParams;
  is_active: boolean;
  sort_order: number;
  created_at?: string;
  updated_at?: string;
};

export type ServiceInput = {
  name: string;
  description?: string | null;
  params?: ServiceParams;
  is_active?: boolean;
  sort_order?: number;
};

export type AdminSettings = {
  id?: number;
  services: string[];
  budget_min: string | null;
  budget_max: string | null;
};

export type LeadPayload = {
  first_name: string;
  last_name: string;
  middle_name?: string | null;
  email?: string | null;
  phone?: string | null;
  business_info?: string | null;
  niche?: string | null;
  company_size?: string | null;
  task_volume?: string | null;
  need_volume?: string | null;
  role?: string | null;
  budget?: string | null;
  contact_method?: string | null;
  convenient_time?: string | null;
  comments?: string | null;
  deadline?: string | null;
  task_type?: string | null;
  interested_product?: string | null;
};

export type Lead = LeadPayload & {
  id: string;
  created_at?: string;
};

export type LeadAnalysis = {
  temperature: "hot" | "warm" | "cold";
  temperature_label: string;
  score: number;
  is_urgent: boolean;
  worth_time: boolean;
  worth_time_label: string;
  needs_personal_manager: boolean;
  department: string;
  department_label: string;
  reasons: string[];
};

export type ScoredLead = Lead & {
  analysis: LeadAnalysis;
};

export type LeadQueueStats = {
  total: number;
  hot: number;
  warm: number;
  cold: number;
  urgent: number;
  with_manager: number;
  avg_score: number;
  by_department: Record<string, number>;
};

export type LeadQueueResponse = {
  stats: LeadQueueStats;
  items: ScoredLead[];
};

export type BehaviorPayload = {
  id: string;
  time_on_page_seconds: number;
  buttons_clicked: { id: string; at: number }[];
  cursor_hotspots: { x: number; y: number; at: number }[];
  return_count: number;
  raw_metrics: Record<string, unknown>;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type BehaviorMetricPayload = {
  application_id: number;
  time_on_page: number;
  buttons_clicked: string;
  cursor_positions: string;
  return_frequency: number;
};

export type PeriodTimeStats = {
  avg_seconds: number;
  max_seconds: number;
};

export type HeatPoint = {
  x: number;
  y: number;
  weight: number;
};

export type BehaviorStats = {
  day: PeriodTimeStats;
  week: PeriodTimeStats;
  month: PeriodTimeStats;
  heatmap: HeatPoint[];
};
