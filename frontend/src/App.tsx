import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { ConfigProvider, Layout, Menu, Typography, Drawer, Button, theme as antdTheme } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MenuOutlined, BulbOutlined, BulbFilled } from '@ant-design/icons';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import NotifBell from '@/components/NotifBell';
import SuspenseLoading from '@/components/SuspenseLoading';
import NotFound from '@/components/NotFound';
import { useTheme } from '@/hooks/useTheme';
import { useModules } from '@/hooks/useModules';

// Pages (lazy loaded)
const DashboardPage = React.lazy(() => import('./pages/Dashboard'));
const LoginPage = React.lazy(() => import('./pages/Login'));
const RegisterPage = React.lazy(() => import('./pages/Register'));
const CollegeListPage = React.lazy(() => import('./pages/CollegeList'));
const CollegeDetailPage = React.lazy(() => import('./pages/CollegeDetail'));
const ScoreQueryPage = React.lazy(() => import('./pages/ScoreQuery'));
const PredictPage = React.lazy(() => import('./pages/PredictPage'));

// 12 维度子页面
const PsychologyPage = React.lazy(() => import('./pages/Psychology'));
const FamilyPage = React.lazy(() => import('./pages/Family'));
const InterestPage = React.lazy(() => import('./pages/Interest'));
const SocialPage = React.lazy(() => import('./pages/Social'));
const LearningPage = React.lazy(() => import('./pages/Learning'));
const TravelPage = React.lazy(() => import('./pages/Travel'));
const IntimacyPage = React.lazy(() => import('./pages/Intimacy'));
const MeaningPage = React.lazy(() => import('./pages/Meaning'));

// 8 个核心学业子页面（W36 修复：之前未路由）
const DailyTrackerPage = React.lazy(() => import('./pages/DailyTracker'));
const ExamAnalyzerPage = React.lazy(() => import('./pages/ExamAnalyzer'));
const LifePlannerPage = React.lazy(() => import('./pages/LifePlanner'));
const CollegeAdvisorPage = React.lazy(() => import('./pages/CollegeAdvisor'));
const SubjectSelectionPage = React.lazy(() => import('./pages/SubjectSelection'));
const CareerAdvisorPage = React.lazy(() => import('./pages/CareerAdvisor'));
const StudyPlannerPage = React.lazy(() => import('./pages/StudyPlanner'));
const GradAdvisorPage = React.lazy(() => import('./pages/GradAdvisor'));
const AICoachPage = React.lazy(() => import('./pages/AICoach'));
const RecommendPage = React.lazy(() => import('./pages/Recommend'));
const FinancePage = React.lazy(() => import('./pages/Finance'));
const HabitsPage = React.lazy(() => import('./pages/Habits'));
const HealthPage = React.lazy(() => import('./pages/Health'));

const { Header, Content, Footer } = Layout;

// Auth gate: redirect to /login if not authenticated
function RequireAuth({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  const location = useLocation();
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
}

function ThemeToggleButton() {
  const { theme, toggle } = useTheme();
  return (
    <Button
      type="text"
      icon={theme === 'dark'
        ? <BulbFilled style={{ color: 'white', fontSize: 18 }} />
        : <BulbOutlined style={{ color: 'white', fontSize: 18 }} />}
      onClick={toggle}
      title={theme === 'dark' ? '切换到浅色模式' : '切换到深色模式'}
      style={{ marginLeft: 8 }}
    />
  );
}

function AppLayout() {
  const location = useLocation();
  const path = location.pathname;

  // 移动端检测
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [drawerOpen, setDrawerOpen] = useState(false);
  useEffect(() => {
    const handler = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', handler);
    return () => window.removeEventListener('resize', handler);
  }, []);
  useEffect(() => {
    setDrawerOpen(false); // 路由变化时关闭 drawer
  }, [path]);

  // 计算当前 selectedKey（带嵌套路径处理）
  const computeSelected = (p: string): string => {
    if (p === '/') return '/dashboard';
    if (p.startsWith('/college') || p === '/colleges' || p === '/predict' || p === '/scores') return p;
    return p;
  };
  const selectedKey = computeSelected(path);

  // 菜单项（P7-B3：数据源为后端 /api/modules 自声明聚合，
  // 首屏与降级用 config/modules.ts 静态镜像——与旧硬编码逐项一致。
  // 静态 <Route> 保留：未知/被删域的 path 不进菜单但深链仍可达。）
  const { menuItems } = useModules();

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', background: '#1677ff' }}>
        {isMobile && (
          <Button
            type="text"
            icon={<MenuOutlined style={{ color: 'white', fontSize: 20 }} />}
            onClick={() => setDrawerOpen(true)}
            style={{ marginRight: 8 }}
          />
        )}
        <Typography.Title level={4} style={{ color: 'white', margin: 0, marginRight: 32, whiteSpace: 'nowrap' }}>
          人生规划系统
        </Typography.Title>
        <ThemeToggleButton />
        <NotifBell />
        {!isMobile && (
          <Menu
            theme="dark"
            mode="horizontal"
            selectedKeys={[selectedKey]}
            style={{ background: 'transparent', flex: 1, borderBottom: 'none', minWidth: 0, flexWrap: 'wrap' }}
            items={menuItems.map((m) => ({
              key: m.key,
              label: <Link to={m.key}><span style={{ color: 'white' }}>{m.label}</span></Link>,
            }))}
          />
        )}
      </Header>

      {/* 移动端 Drawer 菜单 */}
      <Drawer
        title="菜单"
        placement="left"
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        width={280}
      >
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems.map((m) => ({
            key: m.key,
            label: <Link to={m.key}>{m.label}</Link>,
          }))}
        />
      </Drawer>
      <Content style={{ padding: '24px 16px', background: '#f5f5f5' }}>
        <React.Suspense fallback={<SuspenseLoading />}>
          <ErrorBoundary>
          <Routes>
            {/* 公开路由 */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* 核心学业子页面（W36 修复：之前未路由） */}
            <Route path="/dashboard" element={<RequireAuth><DashboardPage /></RequireAuth>} />
            <Route path="/daily" element={<RequireAuth><DailyTrackerPage /></RequireAuth>} />
            <Route path="/exams" element={<RequireAuth><ExamAnalyzerPage /></RequireAuth>} />
            <Route path="/goals" element={<RequireAuth><LifePlannerPage /></RequireAuth>} />
            <Route path="/study" element={<RequireAuth><StudyPlannerPage /></RequireAuth>} />
            <Route path="/subject-selection" element={<RequireAuth><SubjectSelectionPage /></RequireAuth>} />
            <Route path="/college" element={<RequireAuth><CollegeAdvisorPage /></RequireAuth>} />
            <Route path="/career" element={<RequireAuth><CareerAdvisorPage /></RequireAuth>} />
            <Route path="/grad" element={<RequireAuth><GradAdvisorPage /></RequireAuth>} />
            <Route path="/ai" element={<RequireAuth><AICoachPage /></RequireAuth>} />
            <Route path="/recommend" element={<RequireAuth><RecommendPage /></RequireAuth>} />
            <Route path="/finance" element={<RequireAuth><FinancePage /></RequireAuth>} />
            <Route path="/habits" element={<RequireAuth><HabitsPage /></RequireAuth>} />
            <Route path="/health" element={<RequireAuth><HealthPage /></RequireAuth>} />

            {/* 高考志愿 — 4 个路由 */}
            <Route path="/scores" element={<RequireAuth><ScoreQueryPage /></RequireAuth>} />
            <Route path="/predict" element={<RequireAuth><PredictPage /></RequireAuth>} />
            <Route path="/colleges" element={<RequireAuth><CollegeListPage /></RequireAuth>} />
            <Route path="/colleges/:id" element={<RequireAuth><CollegeDetailPage /></RequireAuth>} />

            {/* 12 维度子页面 */}
            <Route path="/psychology" element={<RequireAuth><PsychologyPage /></RequireAuth>} />
            <Route path="/family" element={<RequireAuth><FamilyPage /></RequireAuth>} />
            <Route path="/interest" element={<RequireAuth><InterestPage /></RequireAuth>} />
            <Route path="/social" element={<RequireAuth><SocialPage /></RequireAuth>} />
            <Route path="/learning" element={<RequireAuth><LearningPage /></RequireAuth>} />
            <Route path="/travel" element={<RequireAuth><TravelPage /></RequireAuth>} />
            <Route path="/intimacy" element={<RequireAuth><IntimacyPage /></RequireAuth>} />
            <Route path="/meaning" element={<RequireAuth><MeaningPage /></RequireAuth>} />

            {/* 兜底 */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          </ErrorBoundary>
        </React.Suspense>
      </Content>
      <Footer style={{ textAlign: 'center', color: '#999' }}>
        人生规划系统 MVP · 数据来源：各省教育考试院
      </Footer>
    </Layout>
  );
}

function App() {
  const { theme } = useTheme();
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme === 'dark' ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
      }}
    >
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ConfigProvider>
  );
}

export default App;
