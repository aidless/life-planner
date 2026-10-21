/**
 * Dashboard v2.1 — professional visual pass (logic unchanged)
 *
 * What changed vs v2:
 * - removed nested Layout/Header/Footer (AppLayout already provides chrome;
 *   double header + double footer was the biggest "toy" signal)
 * - removed all emoji; section headers use antd icons + typographic hierarchy
 * - hero / stat / recommendation / milestone / entry all share one spacing
 *   language (16px radius, theme.css vars, icon tiles)
 * - 12-dimension entry grid fixed: dimensionConfig only declares 1 path, so the
 *   old filter (coming_soon && path) rendered an empty card. Now uses an
 *   explicit route map covering the real routes in App.tsx.
 *
 * Data source unchanged: GET /api/dashboard.
 */

import { useEffect, useState } from "react";
import {
  Avatar, Button, Card, Col, Dropdown, Progress, Row, Tag, Typography,
  message, Alert, List,
} from "antd";
import {
  ArrowRightOutlined,
  CalendarOutlined,
  CompassOutlined,
  DashboardOutlined,
  FireOutlined,
  LineChartOutlined,
  LogoutOutlined,
  BulbOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import apiClient from "@/api/client";
import DimensionsGrid from "@/components/dimensions/DimensionsGrid";
import FiveYearOverview from "@/components/dimensions/FiveYearOverview";
import LoadingState from "@/components/LoadingState";
import { getHealthLevel } from "@/config/dimensionConfig";
import type { MenuProps } from "antd";
import "./dashboard.css";

const { Text, Paragraph, Title } = Typography;

interface DashboardData {
  user_id: number;
  average_score: number;
  average_level: string;
  dimensions: Array<{
    key: string;
    name: string;
    score: number;
    level: string;
    components?: Record<string, unknown>;
    updated_at?: string | null;
  }>;
  next_milestones: Array<{
    title: string;
    days_until: number;
    category: string;
    due_date?: string | null;
  }>;
  ai_recommendations: Array<{
    priority: string;
    dimension: string;
    action: string;
    reason: string;
  }>;
  active_modules_count: number;
  total_modules: number;
}

/** dimension key -> real route in App.tsx (dimensionConfig only declares 1 path) */
const DIMENSION_ROUTES: Record<string, string> = {
  career: "/college",
  health: "/health",
  finance: "/finance",
  habits: "/habits",
  psychology: "/psychology",
  family: "/family",
  interest: "/interest",
  social: "/social",
  learning: "/learning",
  travel: "/travel",
  intimacy: "/intimacy",
  meaning: "/meaning",
};

const CATEGORY_LABEL: Record<string, string> = {
  family: "家庭",
  intimacy: "亲密",
};

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, token, logout } = useAuthStore();
  const [msgApi, contextHolder] = message.useMessage();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = async () => {
    if (!token) {
      msgApi.warning("请先登录");
      navigate("/login");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const r = await apiClient.get("/dashboard");
      if (r.data.success) {
        setDashboard(r.data.data);
      } else {
        setError(r.data.error || "加载失败");
      }
    } catch (err: unknown) {
      const e = err as { userMessage?: string; message?: string };
      setError(e.userMessage || e.message || "Dashboard 加载失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleLogout = () => {
    logout();
    msgApi.info("已退出登录");
    navigate("/login");
  };

  const userMenu: MenuProps["items"] = [
    { key: "logout", icon: <LogoutOutlined />, label: "退出登录", onClick: handleLogout },
  ];

  const scoresFromApi = dashboard
    ? Object.fromEntries(dashboard.dimensions.map((d) => [d.key, d.score]))
    : {};

  const avgScore = dashboard?.average_score ?? 0;
  const overallLevel = getHealthLevel(avgScore);
  const lowDims = dashboard ? [...dashboard.dimensions].sort((a, b) => a.score - b.score).slice(0, 1) : [];
  const today = new Date().toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric", weekday: "long" });

  return (
    <div className="lp-dash">
      {contextHolder}

      {error ? (
        <Alert
          type="error"
          showIcon
          message="仪表盘加载失败"
          description={error}
          action={<a onClick={() => fetchDashboard()}>重试</a>}
        />
      ) : null}

      <LoadingState loading={loading} error={null} empty={!dashboard} emptyText="暂无仪表盘数据，先去记录一条日常吧">
        {/* Hero — single page header (AppLayout already owns the blue top bar) */}
        <section className="lp-hero">
          <div>
            <div className="lp-eyebrow">总览 · 12 维度人生仪表盘</div>
            {/* e2e 契约：仪表盘首屏必须有 h3（25-pages.spec selector=h3），故用 Title level=3 */}
            <Title level={3} style={{ margin: 0 }}>欢迎回来，{user?.username || "同学"}</Title>
            <div className="lp-hero-sub">{today} · 先看最弱的一块，再决定今天做什么</div>
          </div>
          <div className="lp-hero-actions">
            <Dropdown menu={{ items: userMenu }} placement="bottomRight">
              <div className="lp-userchip">
                <Avatar size="small" icon={<UserOutlined />} />
                <Text style={{ fontSize: 13 }}>{user?.username || "用户"}</Text>
              </div>
            </Dropdown>
            <Button onClick={() => navigate("/daily")}>去记录</Button>
            <Button type="primary" onClick={() => navigate("/recommend")}>
              查看推荐 <ArrowRightOutlined />
            </Button>
          </div>
        </section>

        {/* Summary stats */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Card className="lp-stat-card" styles={{ body: { padding: 20 } }}>
              <div className="lp-stat-top">
                <div className="lp-icon-tile" style={{ background: overallLevel.bgColor, color: overallLevel.color }}>
                  <DashboardOutlined />
                </div>
                <span className="lp-stat-label">12 维度综合健康度</span>
              </div>
              <div className="lp-stat-value" style={{ color: overallLevel.color }}>
                {avgScore}
              </div>
              <div className="lp-stat-sub">
                {dashboard?.average_level || overallLevel.label} · 12 维度平均
              </div>
              <Progress
                percent={Math.max(0, Math.min(100, avgScore))}
                strokeColor={overallLevel.color}
                showInfo={false}
                size="small"
                style={{ marginTop: 12 }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card className="lp-stat-card" styles={{ body: { padding: 20 } }}>
              <div className="lp-stat-top">
                <div className="lp-icon-tile" style={{ background: "#e6f4ff", color: "#1677ff" }}>
                  <LineChartOutlined />
                </div>
                <span className="lp-stat-label">已激活维度</span>
              </div>
              <div className="lp-stat-value" style={{ color: "#1677ff" }}>
                {dashboard ? `${dashboard.active_modules_count}/12` : "0/12"}
              </div>
              <div className="lp-stat-sub">有数据即激活 · 覆盖学业 / 健康 / 生活全域</div>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card className="lp-stat-card" styles={{ body: { padding: 20 } }}>
              <div className="lp-stat-top">
                <div className="lp-icon-tile" style={{ background: "#fff1f0", color: "#f5222d" }}>
                  <FireOutlined />
                </div>
                <span className="lp-stat-label">最需要关注</span>
              </div>
              {lowDims.length > 0 ? (
                <>
                  <div style={{ fontSize: 20, fontWeight: 650, color: "#cf1322", margin: "2px 0 6px" }}>
                    {lowDims[0].name} · {lowDims[0].score}分
                  </div>
                  <div className="lp-stat-sub">
                    {lowDims[0].level} ·
                    <a
                      onClick={() => navigate(DIMENSION_ROUTES[lowDims[0].key] ?? "/recommend")}
                      style={{ marginLeft: 4 }}
                    >
                      去改善 <ArrowRightOutlined style={{ fontSize: 11 }} />
                    </a>
                  </div>
                </>
              ) : (
                <Text type="secondary">暂无数据</Text>
              )}
            </Card>
          </Col>
        </Row>

        {/* Coach recommendations */}
        {dashboard && dashboard.ai_recommendations.length > 0 && (
          <Card
            className="lp-section-card"
            title={<span><BulbOutlined style={{ marginRight: 8 }} />教练建议</span>}
            extra={<a onClick={() => navigate("/recommend")}>查看全部推荐 <ArrowRightOutlined style={{ fontSize: 11 }} /></a>}
            styles={{ body: { padding: 16 } }}
          >
            <List
              dataSource={dashboard.ai_recommendations.slice(0, 4)}
              renderItem={(rec, idx) => (
                <List.Item key={idx} className="lp-rec-item" style={{ border: "1px solid var(--border-light)" }}>
                  <div style={{ width: "100%" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4, flexWrap: "wrap" }}>
                      <Tag color={rec.priority === "high" ? "red" : "orange"}>
                        {rec.dimension} · {rec.priority === "high" ? "高优先级" : "建议"}
                      </Tag>
                      <Text strong>{rec.action}</Text>
                    </div>
                    <Text type="secondary" style={{ fontSize: 12 }}>{rec.reason}</Text>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        )}

        {/* Milestones */}
        {dashboard && dashboard.next_milestones.length > 0 && (
          <Card
            className="lp-section-card"
            title={<span><CalendarOutlined style={{ marginRight: 8 }} />即将到来的里程碑</span>}
            extra={<Text type="secondary" style={{ fontSize: 12 }}>{dashboard.next_milestones.length} 个在路上</Text>}
            styles={{ body: { padding: 16 } }}
          >
            <Row gutter={[12, 12]}>
              {dashboard.next_milestones.slice(0, 6).map((m, idx) => (
                <Col xs={24} sm={12} md={8} key={idx}>
                  <div className="lp-mile-tile">
                    <Tag>{CATEGORY_LABEL[m.category] ?? m.category}</Tag>
                    <Paragraph ellipsis={{ rows: 1 }} style={{ fontSize: 14, margin: "8px 0 0" }}>
                      {m.title}
                    </Paragraph>
                    <div className="lp-mile-count">
                      还有 {m.days_until} 天
                    </div>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        )}

        {/* 12-dimension grid */}
        <DimensionsGrid scores={scoresFromApi} />

        {/* 5-year overview */}
        <FiveYearOverview />

        {/* Module entries — all 12 with real routes */}
        <Card
          className="lp-section-card"
          title={<span><CompassOutlined style={{ marginRight: 8 }} />进入 12 维度模块</span>}
          styles={{ body: { padding: 16 } }}
        >
          <Row gutter={[12, 12]}>
            {dashboard?.dimensions.map((d) => {
              const route = DIMENSION_ROUTES[d.key];
              if (!route) return null;
              const level = getHealthLevel(d.score);
              return (
                <Col xs={12} sm={8} md={6} key={d.key}>
                  <Card
                    hoverable
                    size="small"
                    className="lp-entry-card"
                    onClick={() => navigate(route)}
                  >
                    <div className="lp-entry-row">
                      <div className="lp-entry-icon" style={{ color: level.color, background: level.bgColor }}>
                        <CompassOutlined />
                      </div>
                      <Text strong>{d.name}</Text>
                    </div>
                    <div className="lp-entry-foot">
                      <span>健康度 {d.score} · {d.level}</span>
                      <ArrowRightOutlined />
                    </div>
                  </Card>
                </Col>
              );
            })}
          </Row>
        </Card>

        <Paragraph type="secondary" style={{ fontSize: 12, textAlign: "center", margin: "4px 0 0" }}>
          数据来自各维度真实记录 · 每天 08:00 与 21:00 自动生成教练建议
        </Paragraph>
      </LoadingState>
    </div>
  );
}
