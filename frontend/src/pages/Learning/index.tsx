/**
 * Learning 学习页面
 *
 * 书籍 + 课程双轨 + 进度追踪
 */

import { useEffect, useState } from "react";
import {
  Card, Form, Input, Select, InputNumber, Button, Table, Tag, Tabs, Typography,
  Row, Col, Progress, message, Rate,
} from "antd";
import { ReadOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";

const { Title, Text } = Typography;

interface Book {
  id: number;
  title: string;
  author: string | null;
  category: string | null;
  status: string;
  total_pages: number | null;
  current_page: number | null;
  rating: number | null;
}

interface Course {
  id: number;
  title: string;
  platform: string | null;
  category: string | null;
  status: string;
  progress_percent: number;
}

export default function Learning() {
  const [books, setBooks] = useState<Book[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [bookForm] = Form.useForm();
  const [courseForm] = Form.useForm();
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [editingCourse, setEditingCourse] = useState<Course | null>(null);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [br, cr] = await Promise.all([
        apiClient.get("/learning/books"),
        apiClient.get("/learning/courses"),
      ]);
      setBooks(br.data.data || []);
      setCourses(cr.data.data || []);
    } catch (err: any) {
      message.error(err?.userMessage || "加载失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAll(); }, []);

  const handleAddBook = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/learning/books", values);
      message.success("书籍已添加");
      bookForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleAddCourse = async (values: Record<string, unknown>) => {
    try {
      await apiClient.post("/learning/courses", values);
      message.success("课程已添加");
      courseForm.resetFields();
      fetchAll();
    } catch (err: any) {
      message.error("添加失败");
    }
  };

  const handleUpdateBook = async (id: number, fields: Record<string, unknown>) => {
    try {
      await apiClient.put(`/learning/books/${id}`, fields);
      message.success("已更新");
      fetchAll();
    } catch (err: any) {
      message.error("更新失败");
    }
  };

  const handleUpdateCourse = async (id: number, fields: Record<string, unknown>) => {
    try {
      await apiClient.put(`/learning/courses/${id}`, fields);
      message.success("已更新");
      fetchAll();
    } catch (err: any) {
      message.error("更新失败");
    }
  };

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: "0 auto" }}>
      <Title level={3} style={{ margin: 0 }}>
        <ReadOutlined style={{ color: "#2f54eb", marginRight: 12 }} />
        学习 · Learning
      </Title>
      <Text type="secondary">读书、课程、技能 — 终身学习是 AI 时代核心能力</Text>
      <div style={{ marginBottom: 24 }} />

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">书籍总数</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{books.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">已读</Text><div style={{ fontSize: 30, color: "#52c41a", fontWeight: 600 }}>{books.filter((b) => b.status === "finished").length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">课程总数</Text><div style={{ fontSize: 30, fontWeight: 600 }}>{courses.length}</div></Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card><Text type="secondary">已完成</Text><div style={{ fontSize: 30, color: "#52c41a", fontWeight: 600 }}>{courses.filter((c) => c.status === "finished").length}</div></Card>
        </Col>
      </Row>

      <Tabs
        defaultActiveKey="books"
        items={[
          {
            key: "books",
            label: `📚 书籍 (${books.length})`,
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col xs={24} md={12}>
                    <Card title="📚 添加书籍">
                      <Form form={bookForm} layout="vertical" onFinish={handleAddBook}>
                        <Form.Item name="title" label="书名" rules={[{ required: true }]}>
                          <Input />
                        </Form.Item>
                        <Form.Item name="author" label="作者">
                          <Input />
                        </Form.Item>
                        <Form.Item name="category" label="类别">
                          <Select
                            options={[
                              { value: "技术", label: "技术" }, { value: "小说", label: "小说" },
                              { value: "商业", label: "商业" }, { value: "心理", label: "心理" },
                              { value: "历史", label: "历史" }, { value: "其他", label: "其他" },
                            ]}
                          />
                        </Form.Item>
                        <Form.Item name="total_pages" label="总页数">
                          <InputNumber min={1} style={{ width: "100%" }} />
                        </Form.Item>
                        <Button type="primary" htmlType="submit">添加</Button>
                      </Form>
                    </Card>
                  </Col>
                  <Col xs={24} md={12}>
                    <Card title="💡 阅读建议">
                      <p>每年读完 25 本书 = 每月 2 本</p>
                      <p style={{ color: "#999" }}>每读完一本花 5 分钟记录关键收获</p>
                    </Card>
                  </Col>
                </Row>

                <Card title="📖 书架">
                  <Table
                    dataSource={books}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                    columns={[
                      { title: "书名", dataIndex: "title", key: "title" },
                      { title: "作者", dataIndex: "author", key: "author" },
                      { title: "类别", dataIndex: "category", key: "category" },
                      {
                        title: "进度",
                        key: "progress",
                        render: (b: Book) => {
                          const pct = b.total_pages && b.current_page
                            ? Math.round((b.current_page / b.total_pages) * 100)
                            : 0;
                          return <Progress percent={pct} size="small" />;
                        },
                      },
                      {
                        title: "状态",
                        dataIndex: "status",
                        key: "status",
                        render: (s: string) => <Tag color={s === "finished" ? "green" : s === "paused" ? "orange" : "blue"}>{s}</Tag>,
                      },
                      {
                        title: "操作",
                        key: "actions",
                        render: (b: Book) => (
                          <Button size="small" onClick={() => setEditingBook(b)}>更新进度</Button>
                        ),
                      },
                    ]}
                  />
                </Card>
              </>
            ),
          },
          {
            key: "courses",
            label: `🎓 课程 (${courses.length})`,
            children: (
              <>
                <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                  <Col xs={24} md={12}>
                    <Card title="🎓 添加课程">
                      <Form form={courseForm} layout="vertical" onFinish={handleAddCourse}>
                        <Form.Item name="title" label="课程名" rules={[{ required: true }]}>
                          <Input />
                        </Form.Item>
                        <Form.Item name="platform" label="平台">
                          <Select
                            showSearch
                            options={[
                              { value: "Coursera", label: "Coursera" }, { value: "edX", label: "edX" },
                              { value: "慕课网", label: "慕课网" }, { value: "B站", label: "B站" },
                              { value: "中国大学MOOC", label: "中国大学MOOC" },
                              { value: "其他", label: "其他" },
                            ]}
                          />
                        </Form.Item>
                        <Form.Item name="category" label="类别">
                          <Input />
                        </Form.Item>
                        <Button type="primary" htmlType="submit">添加</Button>
                      </Form>
                    </Card>
                  </Col>
                </Row>

                <Card title="📚 我的课程">
                  <Table
                    dataSource={courses}
                    rowKey="id"
                    loading={loading}
                    pagination={{ pageSize: 10 }}
                    columns={[
                      { title: "课程", dataIndex: "title", key: "title" },
                      { title: "平台", dataIndex: "platform", key: "platform" },
                      {
                        title: "进度",
                        dataIndex: "progress_percent",
                        key: "progress",
                        render: (p: number) => <Progress percent={p} size="small" />,
                      },
                      {
                        title: "状态",
                        dataIndex: "status",
                        key: "status",
                        render: (s: string) => <Tag color={s === "finished" ? "green" : s === "paused" ? "orange" : "blue"}>{s}</Tag>,
                      },
                      {
                        title: "操作",
                        key: "actions",
                        render: (c: Course) => (
                          <Button size="small" onClick={() => setEditingCourse(c)}>更新</Button>
                        ),
                      },
                    ]}
                  />
                </Card>
              </>
            ),
          },
        ]}
      />

      {editingBook && (
        <Card
          title={`更新《${editingBook.title}》进度`}
          style={{ marginTop: 24 }}
          extra={<Button onClick={() => setEditingBook(null)}>取消</Button>}
        >
          <Form
            layout="inline"
            onFinish={(v) => {
              handleUpdateBook(editingBook.id, v);
              setEditingBook(null);
            }}
          >
            <Form.Item name="current_page" label="当前页" rules={[{ required: true }]}>
              <InputNumber min={0} max={editingBook.total_pages || 1000} />
            </Form.Item>
            <Form.Item name="rating" label="评分">
              <Rate />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">保存</Button>
            </Form.Item>
          </Form>
        </Card>
      )}

      {editingCourse && (
        <Card
          title={`更新《${editingCourse.title}》`}
          style={{ marginTop: 24 }}
          extra={<Button onClick={() => setEditingCourse(null)}>取消</Button>}
        >
          <Form
            layout="inline"
            onFinish={(v) => {
              handleUpdateCourse(editingCourse.id, v);
              setEditingCourse(null);
            }}
          >
            <Form.Item name="progress_percent" label="进度（%）" rules={[{ required: true }]}>
              <InputNumber min={0} max={100} />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit">保存</Button>
            </Form.Item>
          </Form>
        </Card>
      )}
    </div>
  );
}