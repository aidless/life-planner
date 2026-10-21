import type { ReactNode } from "react";
import { Typography } from "antd";
import "../styles/page.css";

const { Title, Text } = Typography;

interface PageHeaderProps {
  icon: ReactNode;
  title: string;
  subtitle?: string;
  extra?: ReactNode;
}

/**
 * 全站统一页头（视觉 v2.2）：图标 + 标题 + 说明副标题 + 右侧操作区。
 * 替代各页手写的 Title + secondary Text 组合，收敛字阶与间距。
 */
export default function PageHeader({ icon, title, subtitle, extra }: PageHeaderProps) {
  return (
    <div className="lp-page-head">
      <div className="lp-page-head-main">
        <span className="lp-page-head-icon">{icon}</span>
        <div className="lp-page-head-text">
          <Title level={3} className="lp-page-title">{title}</Title>
          {subtitle && <Text type="secondary" className="lp-page-subtitle">{subtitle}</Text>}
        </div>
      </div>
      {extra && <div className="lp-page-head-extra">{extra}</div>}
    </div>
  );
}
