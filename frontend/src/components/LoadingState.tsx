/**
 * LoadingState — 统一的加载中/空状态/错误状态组件
 *
 * 用于所有页面替换各自实现的 loading 占位。
 */

import { Spin, Empty, Alert, Typography } from "antd";
import type { ReactNode } from "react";

const { Text } = Typography;

interface Props {
  loading?: boolean;
  error?: string | null;
  empty?: boolean;
  emptyText?: string;
  loadingText?: string;
  children?: ReactNode;
  /** fullScreen: 占满父容器（minHeight 240px） */
  fullScreen?: boolean;
}

export default function LoadingState({
  loading,
  error,
  empty,
  emptyText = "暂无数据",
  loadingText = "加载中...",
  children,
  fullScreen = true,
}: Props) {
  const containerStyle = fullScreen
    ? { padding: 48, textAlign: "center" as const, minHeight: 240 }
    : { padding: 24, textAlign: "center" as const };

  if (error) {
    return (
      <div style={containerStyle}>
        <Alert
          type="error"
          showIcon
          message="加载失败"
          description={
            <div>
              <Text>{error}</Text>
              <br />
              <Text type="secondary" style={{ fontSize: 12 }}>
                请检查网络或稍后重试
              </Text>
            </div>
          }
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div style={containerStyle}>
        <Spin tip={loadingText} size="large">
          <div style={{ minHeight: 100 }} />
        </Spin>
      </div>
    );
  }

  if (empty) {
    return (
      <div style={containerStyle}>
        <Empty description={emptyText} />
      </div>
    );
  }

  return <>{children}</>;
}