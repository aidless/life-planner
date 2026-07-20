/** Shared TypeScript types for the Life Planner frontend. */

// Types from the original codebase (kept for compatibility)
export interface User {
  id: number;
  username: string;
  email: string;
  display_name: string;
  is_active: boolean;
  created_at: string;
}

export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
  meta?: Record<string, unknown>;
}

export interface LifeGoal {
  id: number;
  user_id: number;
  title: string;
  description: string;
  category: string;
  status: string;
  progress: number;
  target_date: string | null;
  priority: number;
  created_at: string;
  updated_at: string;
}

export interface DailyLog {
  id: number;
  user_id: number;
  date: string;
  activity_type: string;
  description: string;
  duration_minutes: number;
  mood_level: number | null;
  energy_level: number | null;
  notes: string;
  ai_feedback: string;
  created_at: string;
  updated_at: string;
}

export interface ExamQuestion {
  id: number;
  exam_id: number;
  question_number: number;
  topic: string;
  knowledge_point: string;
  correct: boolean;
  my_answer: string;
  correct_answer: string;
  difficulty: string;
  score_value: number;
  ai_analysis: string;
  created_at: string;
}

export interface Exam {
  id: number;
  user_id: number;
  name: string;
  subject: string;
  exam_date: string;
  total_score: number;
  score: number;
  full_score: number;
  rank: number | null;
  notes: string;
  ai_analysis: string;
  created_at: string;
  updated_at: string;
  questions: ExamQuestion[];
}

// Re-export API types from api.ts for convenience
export type {
  ApiResponse as ApiResponseApi,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  UserProfile,
  Question,
  AssessmentResult,
  RecommendationResult,
  SubjectCombination,
  MistakeRecord,
  MistakeAnalysis,
  ExamRecord,
  CollegeRecommendationRequest,
  CollegeRecommendation,
  CollegeAdvisorResult,
} from "./api";
