/**
 * SuspenseLoading — React.lazy 加载占位
 */

import { Spin } from "antd";

export default function SuspenseLoading() {
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "100vh",
      flexDirection: "column",
      gap: 16,
    }}>
      <Spin size="large" />
      <div style={{ color: "#999", fontSize: 14 }}>页面加载中...</div>
    </div>
  );
}