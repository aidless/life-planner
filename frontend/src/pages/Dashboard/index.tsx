/**
 * Dashboard v2 — 12 维度人生仪表盘（接入真实数据）
 *
 * 数据来源：/api/dashboard 聚合 12 维度 + milestones + AI recommendations
 */

import { useEffect, useState } from "react";
import {
  Avatar, Card, Col, Dropdown, Layout, Row, Tag, Typography,
  message, Alert,
} from "antd";
import {
  BulbOutlined, LogoutOutlined, UserOutlined, ArrowRightOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/store/authStore";
import apiClient from "@/api/client";
import DimensionsGrid from "@/components/dimensions/DimensionsGrid";
import FiveYearOverview from "@/components/dimensions/FiveYearOverview";
import LoadingState from "@/components/LoadingState";
import { DIMENSIONS, getHealthLevel } from "@/config/dimensionConfig";
import type { MenuProps } from "antd";

const { Title, Text, Paragraph } = Typography;
const { Header, Content, Footer } = Layout;


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
    } catch (err: any) {
      const msg = err.userMessage || err.message || "Dashboard 加载失败，请稍后重试";
      setError(msg);
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

  const overallLevel = getHealthLevel(dashboard?.average_score || 0);
  const lowDims = dashboard ? [...dashboard.dimensions].sort((a, b) => a.score - b.score).slice(0, 1) : [];

  return (
    <Layout style={{ minHeight: "100vh", background: "#f5f5f5" }}>
      {contextHolder}
      <Header
        style={{
          background: "#fff",
          padding: "0 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Title level={4} style={{ margin: 0, color: "#1677ff" }}>🧭 Life Planner</Title>
          <Text type="secondary" style={{ fontSize: 12 }}>12 维度人生仪表盘</Text>
        </div>
        <Dropdown menu={{ items: userMenu }} placement="bottomRight">
          <div style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
            <Avatar icon={<UserOutlined />} style={{ backgroundColor: "#1677ff" }} />
            <Text>{user?.username || "用户"}</Text>
          </div>
        </Dropdown>
      </Header>

      <Content style={{ padding: "24px 32px", maxWidth: 1400, margin: "0 auto", width: "100%" }}>
        {error ? (
          <Alert
            type="error"
            showIcon
            message="Dashboard 加载失败"
            description={error}
            action={<a onClick={() => fetchDashboard()}>重试</a>}
            style={{ marginBottom: 24 }}
          />
        ) : null}
        <LoadingState loading={loading} error={null} empty={!dashboard}>
          {/* Welcome */}
          <div style={{ marginBottom: 24 }}>
            <Title level={3} style={{ marginBottom: 4 }}>
              👋 欢迎回来，{user?.username || "同学"}！
            </Title>
            <Paragraph type="secondary" style={{ marginBottom: 0 }}>
              {new Date().toLocaleDateString("zh-CN", { year: "numeric", month: "long", day: "numeric", weekday: "long" })}
              ，今天也是规划人生的好日子。
            </Paragraph>
          </div>

          {/* 上方 3 个 summary 卡 */}
          <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
            <Col xs={24} sm={8}>
              <Card style={{ borderRadius: 12, background: overallLevel.bgColor }}>
                <Text type="secondary" style={{ fontSize: 12 }}>12 维度综合健康度</Text>
                <div style={{ fontSize: 36, fontWeight: 700, color: overallLevel.color, lineHeight: 1, margin: "8px 0" }}>
                  {dashboard?.average_score || 0}
                </div>
                <Text style={{ color: overallLevel.color }}>
                  {dashboard?.average_level || overallLevel.label} · 12 维度平均
                </Text>
              </Card>
            </Col>
            <Col xs={24} sm={8}>
              <Card style={{ borderRadius: 12 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>已激活维度</Text>
                <div style={{ fontSize: 36, fontWeight: 700, color: "#1677ff", lineHeight: 1, margin: "8px 0" }}>
                  {dashboard ? `${dashboard.active_modules_count}/12` : `0/12`}
                </div>
                <Text type="secondary">有数据即激活；11 子域已上线</Text>
              </Card>
            </Col>
            <Col xs={24} sm={8}>
              <Card style={{ borderRadius: 12 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>最需要关注</Text>
                {lowDims.length > 0 ? (
                  <>
                    <div style={{ fontSize: 18, fontWeight: 600, color: "#f5222d", margin: "8px 0" }}>
                      {lowDims[0].name} · {lowDims[0].score}
                    </div>
                    <Text type="secondary">{lowDims[0].level} · 点击下方卡片开始记录</Text>
                  </>
                ) : (
                  <Text type="secondary">—</Text>
                )}
              </Card>
            </Col>
          </Row>

          {/* AI 推荐 */}
          {dashboard && dashboard.ai_recommendations.length > 0 && (
            <Alert
              type="info"
              icon={<BulbOutlined />}
              showIcon
              style={{ marginBottom: 24 }}
              message="AI 教练建议"
              description={
                <div style={{ marginTop: 8 }}>
                  {dashboard.ai_recommendations.map((rec, idx) => (
                    <div
                      key={idx}
                      style={{
                        marginBottom: 8,
                        padding: "8px 12px",
                        background: rec.priority === "high" ? "#fff1f0" : "#f6ffed",
                        borderRadius: 6,
                      }}
                    >
                      <Tag color={rec.priority === "high" ? "red" : "orange"} style={{ marginRight: 8 }}>
                        {rec.dimension} · {rec.priority === "high" ? "高优先级" : "中优先级"}
                      </Tag>
                      <Text strong style={{ marginRight: 8 }}>{rec.action}</Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>{rec.reason}</Text>
                    </div>
                  ))}
                </div>
              }
            />
          )}

          {/* 即将到来的里程碑 */}
          {dashboard && dashboard.next_milestones.length > 0 && (
            <Card title="🎯 即将到来的里程碑" style={{ marginBottom: 24, borderRadius: 12 }}>
              <Row gutter={[12, 12]}>
                {dashboard.next_milestones.slice(0, 6).map((m, idx) => {
                  const color = m.category === "family" ? "#1677ff" : "#ff4d4f";
                  return (
                    <Col xs={24} sm={12} md={8} key={idx}>
                      <Card type="inner" size="small" style={{ background: "#fafafa" }}>
                        <Text type="secondary" style={{ fontSize: 11 }}>
                          {m.category === "family" ? "🎂 家庭" : "💝 亲密"}
                        </Text>
                        <div style={{ fontSize: 14, marginTop: 4 }}>
                          {m.title}
                        </div>
                        <div style={{ fontSize: 22, color, fontWeight: 600, marginTop: 4 }}>
                          还有 {m.days_until} 天
                        </div>
                      </Card>
                    </Col>
                  );
                })}
              </Row>
            </Card>
          )}

          {/* 12 维度网格 */}
          <div style={{ marginBottom: 24 }}>
            <DimensionsGrid scores={scoresFromApi} />
          </div>

          {/* 5 年人生总览 */}
          <div style={{ marginBottom: 24 }}>
            <FiveYearOverview />
          </div>

          {/* 12 维度模块入口（active 11 个） */}
          <Card title="🌟 进入 12 维度模块" style={{ borderRadius: 12 }}>
            <Row gutter={[16, 16]}>
              {DIMENSIONS.filter((d) => d.status === "coming_soon" && d.path).map((d) => (
                <Col xs={12} sm={8} md={6} key={d.key}>
                  <Card hoverable size="small" onClick={() => navigate(d.path!)} style={{ borderColor: d.color }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ fontSize: 22, color: d.color }}>{d.icon}</div>
                      <Text strong>{d.name}</Text>
                    </div>
                    <div style={{ marginTop: 8, fontSize: 12, color: "#999" }}>
                      健康度：{scoresFromApi[d.key] ?? 0}
                      <ArrowRightOutlined style={{ marginLeft: 6 }} />
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </LoadingState>
      </Content>

      <Footer style={{ textAlign: "center", color: "#999" }}>
        Life Planner v1.0 · 12 维度 · 12/11 子域已上线 · 陪你走过人生的每一步
      </Footer>
    </Layout>
  );
}