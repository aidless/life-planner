import apiClient from '@/api/client';

// Types
export interface CollegeScoreRecord {
  id: number;
  year: number;
  province: string;
  college_name: string;
  major_name: string;
  batch: string;
  min_score: number | null;
  min_rank: number | null;
  source: string;
  created_at: string;
}

export interface CollegeOut {
  id: string;
  name: string;
  province: string;
  features: string[];
}

export interface CollegeDetail {
  id: string;
  name: string;
  features: string[];
  recent_scores: {
    year: number;
    major: string;
    min_score: number | null;
    min_rank: number | null;
    province: string;
  }[];
}

export interface PredictResult {
  dash: Array<{college_id: string; college_name: string; major: string; min_score: number | null; min_rank: number | null; probability: string}>;
  steady: Array<{college_id: string; college_name: string; major: string; min_score: number | null; min_rank: number | null; probability: string}>;
  safe: Array<{college_id: string; college_name: string; major: string; min_score: number | null; min_rank: number | null; probability: string}>;
}

// API functions
export async function queryScores(params: {
  year?: number;
  province?: string;
  college?: string;
  major?: string;
}): Promise<CollegeScoreRecord[]> {
  const res = await apiClient.get('/college/scores', { params });
  return res.data.data || [];
}

export async function listColleges(params: {
  province?: string;
  features?: string[];
  keyword?: string;
  page?: number;
  page_size?: number;
}): Promise<{ items: CollegeOut[]; total: number }> {
  const queryParams: Record<string, any> = { ...params };
  if (params.features && params.features.length > 0) {
    queryParams.features = params.features.join(',');
  } else {
    delete queryParams.features;
  }
  // 后端字段是 type（不接 features/keyword search），仅传支持的
  delete queryParams.keyword;
  delete queryParams.features;
  const res = await apiClient.get('/college/colleges', { params: queryParams });
  // 后端返回 {items, total, page, page_size}，适配为同样结构
  const d = res.data.data || {};
  return {
    items: d.items || [],
    total: d.total || 0,
  };
}

export async function getCollegeDetail(id: string): Promise<CollegeDetail> {
  const res = await apiClient.get(`/college/colleges/${id}`);
  return res.data.data;
}

export async function predictColleges(data: {
  score: number;
  rank?: number;
  province: string;
  subject_combination?: string;
  year?: number;
}): Promise<PredictResult> {
  const res = await apiClient.post('/college/predict', data);
  return res.data.data;
}
