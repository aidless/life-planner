/**
 * ErrorBoundary — 全局错误边界
 *
 * 捕获子组件渲染时的 JS 错误，显示友好提示，不让整个 App 崩溃。
 */

import { Component, type ReactNode } from "react";
import { Result, Button, Typography } from "antd";

const { Paragraph, Text } = Typography;

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: { componentStack?: string }) {
    console.error("[ErrorBoundary] Caught error:", error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: 48, maxWidth: 720, margin: "0 auto" }}>
          <Result
            status="error"
            title="页面出错了"
            subTitle="应用遇到了一个意外错误，请尝试刷新页面或联系管理员。"
            extra={[
              <Button key="reset" type="primary" onClick={this.handleReset}>
                重试
              </Button>,
              <Button key="reload" onClick={this.handleReload}>
                刷新页面
              </Button>,
            ]}
          >
            <div style={{
              background: "#fff2f0",
              padding: 16,
              borderRadius: 8,
              border: "1px solid #ffccc7",
              textAlign: "left",
            }}>
              <Text strong style={{ color: "#cf1322" }}>错误详情：</Text>
              <Paragraph
                copyable={{ text: this.state.error?.stack || "" }}
                style={{ marginTop: 8, marginBottom: 0 }}
              >
                <pre style={{ margin: 0, fontSize: 12, whiteSpace: "pre-wrap", wordBreak: "break-word" }}>
                  {this.state.error?.message || "未知错误"}
                </pre>
              </Paragraph>
            </div>
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}