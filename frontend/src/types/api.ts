/**
 * API Type Definitions
 * 
 * TypeScript type definitions for API requests and responses.
 * Follows the standard API response format: { code, data, message }
 */

/**
 * Standard API Response Format
 */
export interface ApiResponse<T = unknown> {
  code: number;
  data: T;
  message: string;
}

/**
 * Authentication Types
 */
export interface LoginRequest {
  phone: string;
  password: string;
}

export interface RegisterRequest {
  phone: string;
  password: string;
  confirm_password: string;
  nickname?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export interface UserProfile {
  id: number;
  phone: string;
  nickname?: string;
  avatar?: string;
  created_at: string;
  updated_at?: string;
}

/**
 * Subject Selection Types
 */
export interface Question {
  id: number;
  question: string;
  options: { value: number; label: string }[];
  type: "holland" | "ability";
}

export interface AssessmentResult {
  holland_result: string;
  description: string;
  ability_scores?: Record<string, number>;
}

export interface RecommendationResult {
  top3: Array<{
    combination_name: string;
    match_score: number;
    coverage_rate: number;
    reasons?: string[];
  }>;
}

export interface SubjectCombination {
  id: number;
  name: string;
  coverage_rate: number;
  description: string;
}

/**
 * Mistake Analysis Types
 */
export interface MistakeRecord {
  id: number;
  user_id: number;
  subject: string;
  image_url: string;
  ocr_text: string;
  analysis: MistakeAnalysis;
  created_at: string;
}

export interface MistakeAnalysis {
  knowledge_points: string[];
  error_type: string;
  severity: 'low' | 'medium' | 'high';
  suggestions: string[];
  mastery_score: number; // 0-100
}

/**
 * College Recommendation Types
 */
export interface CollegeRecommendationRequest {
  score: number;
  province: string;
  subjects: string[];
  preferences?: {
    location?: string[];
    type?: string[]; // 985, 211, 普通
    major?: string[];
  };
}

export interface CollegeRecommendation {
  id: number;
  college_name: string;
  major_name: string;
  probability: 'safe' | 'match' | 'reach';
  score_line: number;
  ranking: number;
  location: string;
  type: string;
  reasons: string[];
}

/**
 * College Advisor Result (from POST /api/college/predict)
 */
export interface CollegeAdvisorResult {
  reach: CollegeRecommendation[];
  match: CollegeRecommendation[];
  safe: CollegeRecommendation[];
  summary: string;
}

export interface ExamRecord {
  exam_id: number;
  subject: string;
  exam_name: string;
  date: string;
  status: 'pending' | 'processing' | 'done';
  score?: number;
  total_score?: number;
}
