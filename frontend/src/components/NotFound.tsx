/**
 * NotFound — 404 页面
 */

import { useNavigate } from "react-router-dom";
import { Result, Button } from "antd";

export default function NotFound() {
  const navigate = useNavigate();
  return (
    <div style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
      <Result
        status="404"
        title="404"
        subTitle="抱歉，您访问的页面不存在。"
        extra={[
          <Button key="home" type="primary" onClick={() => navigate("/")}>
            返回首页
          </Button>,
          <Button key="back" onClick={() => window.history.back()}>
            返回上页
          </Button>,
        ]}
      />
    </div>
  );
}