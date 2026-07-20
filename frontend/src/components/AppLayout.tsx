import { useState } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { Layout, Menu, Button, Avatar, Dropdown, theme } from "antd";
import {
  DashboardOutlined, AimOutlined, CalendarOutlined,
  FileTextOutlined, RobotOutlined, BankOutlined,
  CompassOutlined, BookOutlined, ExperimentOutlined,
  LogoutOutlined, MenuFoldOutlined, MenuUnfoldOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "@/store/authStore";
import Dashboard from "@/pages/Dashboard";
import LifePlanner from "@/pages/LifePlanner";
import DailyTracker from "@/pages/DailyTracker";
import ExamAnalyzer from "@/pages/ExamAnalyzer";
import AICoach from "@/pages/AICoach";
import CollegeAdvisor from "@/pages/CollegeAdvisor";
import CareerAdvisor from "@/pages/CareerAdvisor";
import StudyPlanner from "@/pages/StudyPlanner";
import GradAdvisor from "@/pages/GradAdvisor";

const { Header, Sider, Content } = Layout;

const menuItems = [
  { key: "/", icon: <DashboardOutlined />, label: "仪表盘" },
  { key: "/daily", icon: <CalendarOutlined />, label: "日常记录" },
  { key: "/exams", icon: <FileTextOutlined />, label: "考试分析" },
  { key: "/goals", icon: <AimOutlined />, label: "人生目标" },
  { key: "/study", icon: <BookOutlined />, label: "学习规划" },
  { key: "/college", icon: <BankOutlined />, label: "高考志愿" },
  { key: "/career", icon: <CompassOutlined />, label: "职业发展" },
  { key: "/grad", icon: <ExperimentOutlined />, label: "研究生" },
  { key: "/ai", icon: <RobotOutlined />, label: "AI 教练" },
];

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const { token: themeToken } = theme.useToken();

  const currentKey = "/" + (location.pathname.split("/")[1] || "");

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const userMenuItems = [
    { key: "logout", icon: <LogoutOutlined />, label: "退出登录", onClick: handleLogout },
  ];

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        breakpoint="lg"
        style={{ background: themeToken.colorBgContainer }}
      >
        <div style={{
          height: 64, display: "flex", alignItems: "center", justifyContent: "center",
          borderBottom: `1px solid ${themeToken.colorBorderSecondary}`,
        }}>
          <span style={{ fontSize: collapsed ? 18 : 16, fontWeight: 700 }}>
            {collapsed ? "人生" : "人生规划系统"}
          </span>
        </div>
        <Menu
          mode="inline"
          selectedKeys={[currentKey]}
          items={menuItems}
          onClick={(info) => navigate(info.key)}
          style={{ borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header style={{
          padding: "0 24px", background: themeToken.colorBgContainer,
          display: "flex", alignItems: "center", justifyContent: "space-between",
          borderBottom: `1px solid ${themeToken.colorBorderSecondary}`,
        }}>
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />
          <Dropdown menu={{ items: userMenuItems }}>
            <div style={{ cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}>
              <Avatar style={{ backgroundColor: themeToken.colorPrimary }}>
                {user?.display_name?.[0] || "U"}
              </Avatar>
              <span>{user?.display_name || user?.username}</span>
            </div>
          </Dropdown>
        </Header>
        <Content style={{ margin: 24, padding: 24, background: themeToken.colorBgContainer, borderRadius: 8 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/daily" element={<DailyTracker />} />
            <Route path="/exams" element={<ExamAnalyzer />} />
            <Route path="/goals" element={<LifePlanner />} />
            <Route path="/study" element={<StudyPlanner />} />
            <Route path="/college" element={<CollegeAdvisor />} />
            <Route path="/career" element={<CareerAdvisor />} />
            <Route path="/grad" element={<GradAdvisor />} />
            <Route path="/ai" element={<AICoach />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}
