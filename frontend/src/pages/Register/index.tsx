import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Form, Input, Button, Card, Typography, Alert, message } from "antd";
import { UserOutlined, LockOutlined, SmileOutlined, MailOutlined } from "@ant-design/icons";
import { useAuthStore } from "@/store/authStore";

const { Title, Text } = Typography;

export default function Register() {
  const [loading, setLoading] = useState(false);
  const { register, error, clearError } = useAuthStore();
  const navigate = useNavigate();
  const [msgApi, contextHolder] = message.useMessage();

  const onFinish = async (values: { username: string; email: string; password: string; display_name?: string }) => {
    setLoading(true);
    clearError();
    const ok = await register(values.username, values.email, values.password, values.display_name);
    setLoading(false);
    if (ok) {
      msgApi.success("注册成功，欢迎使用人生规划系统！");
      setTimeout(() => navigate("/dashboard"), 1000);
    }
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center",
      justifyContent: "center",
      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
    }}>
      {contextHolder}
      <Card style={{ width: 400, borderRadius: 12, boxShadow: "0 8px 32px rgba(0,0,0,0.2)" }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <Title level={3} style={{ marginBottom: 4 }}>注册账号</Title>
          <Text type="secondary">创建你的人生规划账号</Text>
        </div>
        {error && <Alert message={error} type="error" showIcon style={{ marginBottom: 16 }} closable onClose={clearError} />}
        <Form onFinish={onFinish} size="large" layout="vertical">
          <Form.Item name="username" rules={[{ required: true, message: "请输入用户名" }, { min: 3, max: 50, message: "用户名 3-50 位" }]}>
            <Input prefix={<UserOutlined />} placeholder="用户名（3-50 位）" />
          </Form.Item>
          <Form.Item name="email" rules={[{ required: true, message: "请输入邮箱" }, { type: "email", message: "邮箱格式不正确" }]}>
            <Input prefix={<MailOutlined />} placeholder="邮箱" />
          </Form.Item>
          <Form.Item name="display_name" rules={[{ max: 100, message: "昵称最多 100 位" }]}>
            <Input prefix={<SmileOutlined />} placeholder="昵称（可选）" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: "请输入密码" }, { min: 8, message: "密码至少 8 位" }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="密码（至少 8 位）" />
          </Form.Item>
          <Form.Item
            name="confirmPassword"
            dependencies={["password"]}
            rules={[
              { required: true, message: "请确认密码" },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue("password") === value) return Promise.resolve();
                  return Promise.reject(new Error("两次密码不一致"));
                },
              }),
            ]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="确认密码" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block style={{ height: 44, fontSize: 16 }}>
              注册
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: "center" }}>
          <Text type="secondary">已有账号？</Text> <Link to="/login" style={{ color: "#1677ff" }}>立即登录</Link>
        </div>
      </Card>
    </div>
  );
}