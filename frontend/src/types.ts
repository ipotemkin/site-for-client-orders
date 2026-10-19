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

export type BehaviorPayload = {
  id: string;
  time_on_page_seconds: number;
  buttons_clicked: { id: string; at: number }[];
  cursor_hotspots: { x: number; y: number; at: number }[];
  return_count: number;
  raw_metrics: Record<string, unknown>;
};
