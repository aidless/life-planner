/**
 * Life Planner 12 维度配置
 *
 * 核心原则：
 * - 学业 + 职业 = 优先级 P0（学生主业）
 * - 6 核心 + 6 辅助 = 全人发展
 * - 每个维度都有：图标、颜色、健康度计算函数、跳转路径
 */

import {
  BookOutlined,
  HeartOutlined,
  DollarOutlined,
  CheckCircleOutlined,
  SmileOutlined,
  HomeOutlined,
  StarOutlined,
  TeamOutlined,
  ReadOutlined,
  GlobalOutlined,
  HeartFilled,
  BulbOutlined,
} from "@ant-design/icons";
import type { ReactNode } from "react";

export type DimensionCategory = "core" | "auxiliary";
export type DimensionStatus = "active" | "coming_soon";

export interface DimensionMeta {
  key: string;
  name: string;
  englishName: string;
  category: DimensionCategory;
  priority: "P0" | "P1" | "P2";
  icon: ReactNode;
  color: string;
  bgColor: string;
  description: string;
  path?: string; // 路由；undefined = 即将上线
  status: DimensionStatus;
  /** 计算健康度 0-100；输入为该维度的原始数据 */
  calculateHealth?: (data: any) => number;
}

/**
 * 12 维度元数据
 */
export const DIMENSIONS: DimensionMeta[] = [
  // ── 6 核心（P0 + P1 学生群体） ────────────────────────────────────────
  {
    key: "career",
    name: "学业/职业",
    englishName: "Career",
    category: "core",
    priority: "P0",
    icon: <BookOutlined />,
    color: "#1677ff",
    bgColor: "#e6f4ff",
    description: "高考志愿、大学规划、考研、求职、职场 — 贯穿学生到职场",
    path: "/college-advisor",
    status: "active",
    calculateHealth: (data) => {
      // 聚合：daily_tracker + exam_analyzer + life_planner + career + grad
      const logs = data?.daily_logs_count ?? 0;
      const exams = data?.exams_count ?? 0;
      const goals = data?.goals_count ?? 0;
      const score = Math.min(100, logs * 2 + exams * 8 + goals * 6);
      return Math.round(score);
    },
  },
  {
    key: "health",
    name: "健康",
    englishName: "Health",
    category: "core",
    priority: "P0",
    icon: <HeartOutlined />,
    color: "#f5222d",
    bgColor: "#fff1f0",
    description: "步数、睡眠、运动、体重 — 日常习惯的健康累积",
    status: "coming_soon",
    calculateHealth: (data) => {
      const steps = data?.avg_steps ?? 0;
      const sleep = data?.avg_sleep_hours ?? 0;
      const exercise = data?.avg_exercise_minutes ?? 0;
      const stepScore = Math.min(1, steps / 10000) * 0.4;
      const sleepScore = Math.min(1, sleep / 8.0) * 0.3;
      const exerciseScore = Math.min(1, exercise / 30.0) * 0.3;
      return Math.round((stepScore + sleepScore + exerciseScore) * 100);
    },
  },
  {
    key: "finance",
    name: "财务",
    englishName: "Finance",
    category: "core",
    priority: "P0",
    icon: <DollarOutlined />,
    color: "#faad14",
    bgColor: "#fffbe6",
    description: "记账、预算、存款目标 — 财务健康是人生自由的基础",
    status: "coming_soon",
    calculateHealth: (data) => {
      const budget = data?.budget_compliance ?? 0; // 0-1
      const savings = data?.savings_progress ?? 0; // 0-1
      return Math.round((budget * 50 + savings * 50));
    },
  },
  {
    key: "habits",
    name: "习惯",
    englishName: "Habits",
    category: "core",
    priority: "P0",
    icon: <CheckCircleOutlined />,
    color: "#fa541c",
    bgColor: "#fff2e8",
    description: "晨跑、阅读、冥想 — 持续小动作累积大改变",
    status: "coming_soon",
    calculateHealth: (data) => {
      const completion = data?.avg_completion ?? 0; // 0-1
      return Math.round(completion * 100);
    },
  },
  {
    key: "psychology",
    name: "心理",
    englishName: "Psychology",
    category: "core",
    priority: "P1",
    icon: <SmileOutlined />,
    color: "#fa8c16",
    bgColor: "#fff7e6",
    description: "心情、压力、能量 — 心理健康与学业表现直接相关",
    status: "coming_soon",
    calculateHealth: (data) => {
      const mood = data?.avg_mood ?? 5; // 1-10
      return Math.round(mood * 10);
    },
  },
  {
    key: "family",
    name: "家庭",
    englishName: "Family",
    category: "core",
    priority: "P1",
    icon: <HomeOutlined />,
    color: "#eb2f96",
    bgColor: "#fff0f6",
    description: "家人关系、重要日期、亲情 — 家庭支持是人生韧性来源",
    status: "coming_soon",
    calculateHealth: (data) => {
      const connections = data?.connections_count ?? 0;
      return Math.min(100, connections * 15);
    },
  },

  // ── 6 辅助（P1 + P2 长期发展） ────────────────────────────────────────
  {
    key: "interest",
    name: "兴趣",
    englishName: "Interest",
    category: "auxiliary",
    priority: "P1",
    icon: <StarOutlined />,
    color: "#722ed1",
    bgColor: "#f9f0ff",
    description: "爱好、特长、激情 — 多元兴趣激发人生宽度",
    status: "coming_soon",
    calculateHealth: (data) => {
      const hours = data?.weekly_hours ?? 0;
      return Math.min(100, hours * 5);
    },
  },
  {
    key: "social",
    name: "社交",
    englishName: "Social",
    category: "auxiliary",
    priority: "P1",
    icon: <TeamOutlined />,
    color: "#13c2c2",
    bgColor: "#e6fffb",
    description: "友谊、深度关系、社交网络 — 社交能力是领导力基础",
    status: "coming_soon",
    calculateHealth: (data) => {
      const close = data?.close_friends ?? 0;
      return Math.min(100, close * 20);
    },
  },
  {
    key: "learning",
    name: "学习",
    englishName: "Learning",
    category: "auxiliary",
    priority: "P1",
    icon: <ReadOutlined />,
    color: "#2f54eb",
    bgColor: "#f0f5ff",
    description: "读书、课程、技能 — 终身学习是 AI 时代核心能力",
    status: "coming_soon",
    calculateHealth: (data) => {
      const books = data?.books_per_year ?? 0;
      const courses = data?.courses_count ?? 0;
      return Math.min(100, books * 4 + courses * 12);
    },
  },
  {
    key: "travel",
    name: "旅行",
    englishName: "Travel",
    category: "auxiliary",
    priority: "P2",
    icon: <GlobalOutlined />,
    color: "#52c41a",
    bgColor: "#f6ffed",
    description: "看世界、跨文化体验 — 旅行扩展认知边界",
    status: "coming_soon",
    calculateHealth: (data) => {
      const trips = data?.trips_per_year ?? 0;
      return Math.min(100, trips * 25);
    },
  },
  {
    key: "intimacy",
    name: "亲密",
    englishName: "Intimacy",
    category: "auxiliary",
    priority: "P2",
    icon: <HeartFilled />,
    color: "#ff4d4f",
    bgColor: "#fff1f0",
    description: "爱情、深度关系 — 亲密关系是幸福感的核心来源",
    status: "coming_soon",
    calculateHealth: (data) => {
      const satisfaction = data?.relationship_satisfaction ?? 5; // 1-10
      return Math.round(satisfaction * 10);
    },
  },
  {
    key: "meaning",
    name: "意义",
    englishName: "Meaning",
    category: "auxiliary",
    priority: "P2",
    icon: <BulbOutlined />,
    color: "#fadb14",
    bgColor: "#fffbe6",
    description: "价值观、人生使命 — 意义感是长期幸福的基石",
    status: "coming_soon",
    calculateHealth: (data) => {
      const clarity = data?.purpose_clarity ?? 5; // 1-10
      return Math.round(clarity * 10);
    },
  },
];

/**
 * 健康度等级（用于颜色显示）
 */
export function getHealthLevel(score: number): {
  label: string;
  color: string;
  bgColor: string;
} {
  if (score >= 80) return { label: "优秀", color: "#52c41a", bgColor: "#f6ffed" };
  if (score >= 60) return { label: "良好", color: "#1677ff", bgColor: "#e6f4ff" };
  if (score >= 40) return { label: "一般", color: "#faad14", bgColor: "#fffbe6" };
  return { label: "待提升", color: "#f5222d", bgColor: "#fff1f0" };
}

/**
 * 6 核心维度
 */
export const CORE_DIMENSIONS = DIMENSIONS.filter((d) => d.category === "core");

/**
 * 6 辅助维度
 */
export const AUXILIARY_DIMENSIONS = DIMENSIONS.filter(
  (d) => d.category === "auxiliary"
);

/**
 * 5 年人生总览（示例）
 */
export interface YearMilestone {
  year: number;
  label: string;
  career: string;
  health: string;
  finance: string;
  highlight: string;
}

export const FIVE_YEAR_MILESTONES: YearMilestone[] = [
  {
    year: 2026,
    label: "今年",
    career: "考研 + 毕业",
    health: "减重 5kg",
    finance: "存款 10 万",
    highlight: "🎓 研究生入学",
  },
  {
    year: 2027,
    label: "明年",
    career: "入职",
    health: "跑半马",
    finance: "存款 25 万",
    highlight: "💼 职场起步",
  },
  {
    year: 2028,
    label: "后年",
    career: "晋升",
    health: "BMI 23",
    finance: "存款 50 万",
    highlight: "📈 事业突破",
  },
  {
    year: 2029,
    label: "3 年",
    career: "行业分享 10 次",
    health: "健身习惯",
    finance: "存款 80 万",
    highlight: "🌟 个人品牌",
  },
  {
    year: 2030,
    label: "5 年",
    career: "P7 晋升",
    health: "体能巅峰",
    finance: "100 万",
    highlight: "🚀 中坚力量",
  },
];