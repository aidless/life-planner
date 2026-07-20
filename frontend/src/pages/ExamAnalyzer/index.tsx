import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Typography, Card, Button, Table, Tag, Upload, Modal, Progress, Result, Spin, message } from "antd";
import { ArrowLeftOutlined, UploadOutlined, FileSearchOutlined, CheckCircleOutlined } from "@ant-design/icons";
import type { UploadFile, UploadProps } from "antd";
import apiClient from "@/api/client";

const { Paragraph, Text } = Typography;

interface ExamRecord {
  id: number;
  subject: string;
  name: string;            // 后端字段名是 name
  exam_date: string;
  score: number;           // 后端字段名是 score（不是 user_score）
  total_score: number;
}

interface DiagnosisReport {
  exam_id: number;
  subject: string;
  exam_name: string;
  total_score: number;
  score: number;
  knowledge_points: Array<{ name: string; mastery: number; status: string }>;
  error_types: string[];
  suggestions: string[];
  summary: string;
}

export default function ExamAnalyzer() {
  const navigate = useNavigate();
  const [exams, setExams] = useState<ExamRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [currentExamId, setCurrentExamId] = useState<number | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [diagnosis, setDiagnosis] = useState<DiagnosisReport | null>(null);
  const [msgApi, contextHolder] = message.useMessage();

  // Load exam history — fix: 后端实际端点是 GET /api/exams
  const loadExams = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<any>("/exams");
      const items = res.data?.data || res.data || [];
      setExams(items);
    } catch {
      msgApi.error("加载历史记录失败");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadExams(); }, []);

  // 创建考试记录 — fix: 后端是 POST /api/exams (ExamCreate schema)
  const handleUpload = async (subject: string, examName: string, totalScore: number, userScore: number) => {
    setUploading(true);
    try {
      const res = await apiClient.post<any>("/exams", {
        name: examName,           // 后端字段是 name 不是 exam_name
        subject,
        exam_date: new Date().toISOString(),  // datetime ISO
        total_score: totalScore,
        score: userScore,         // 后端字段是 score 不是 user_score
        full_score: totalScore,
      });
      const newId = res.data?.data?.id;
      if (newId) {
        setCurrentExamId(newId);
        setUploadModalOpen(false);
        msgApi.success("试卷记录已创建");
        await triggerAnalysis(newId, subject, examName, totalScore, userScore);
        await loadExams();
      }
    } catch (err: any) {
      msgApi.error(`上传失败：${err.response?.data?.detail || err.message}`);
    } finally {
      setUploading(false);
    }
  };

  // 触发 AI 分析 — fix: 后端是 POST /api/exams/{id}/analyze
  const triggerAnalysis = async (examId: number, subject: string, examName: string, totalScore: number, userScore: number) => {
    setAnalyzing(true);
    try {
      const res = await apiClient.post<any>(`/exams/${examId}/analyze`);
      const analysis = res.data?.data?.analysis;
      // 把真后端结果 + 派生 mock 字段合并到 UI 模型
      setDiagnosis({
        exam_id: examId,
        subject,
        exam_name: examName,
        total_score: totalScore,
        score: userScore,
        knowledge_points: analysis?.knowledge_points || [],
        error_types: analysis?.error_types || [],
        suggestions: analysis?.suggestions || [],
        summary: analysis?.summary || "AI 分析已完成",
      });
    } catch (err: any) {
      // AI 调用失败时显示基础报告（不阻塞流程）
      setDiagnosis({
        exam_id: examId,
        subject,
        exam_name: examName,
        total_score: totalScore,
        score: userScore,
        knowledge_points: [],
        error_types: [],
        suggestions: [
          `本次得分：${userScore}/${totalScore}（得分率 ${totalScore ? Math.round(userScore / totalScore * 100) : 0}%）`,
          "AI 详细诊断暂不可用，请稍后重试或检查 ANTHROPIC_API_KEY 配置",
        ],
        summary: `已记录 ${subject} 考试数据。AI 分析功能依赖 ANTHROPIC_API_KEY 配置。`,
      });
      msgApi.warning("AI 分析暂不可用，已显示基础报告");
    } finally {
      setAnalyzing(false);
    }
  };

  // ---- Upload Modal ---
  const [uploadSubject, setUploadSubject] = useState("数学");
  const [uploadExamName, setUploadExamName] = useState("");
  const [uploadTotalScore, setUploadTotalScore] = useState(150);
  const [uploadUserScore, setUploadUserScore] = useState(0);
  const [uploadFileList, setUploadFileList] = useState<UploadFile[]>([]);

  const uploadProps: UploadProps = {
    accept: "image/*",
    maxCount: 1,
    fileList: uploadFileList,
    beforeUpload: (file) => {
      setUploadFileList([file as unknown as UploadFile]);
      return false;
    },
    onRemove: () => { setUploadFileList([]); },
  };

  const confirmUpload = () => {
    if (!uploadExamName) {
      msgApi.warning("请填写试卷名称");
      return;
    }
    handleUpload(uploadSubject, uploadExamName, uploadTotalScore, uploadUserScore);
  };

  // ---- Render ----
  if (diagnosis) {
    const kpColumns = [
      { title: "知识点", dataIndex: "name", key: "name" },
      {
        title: "掌握度", dataIndex: "mastery", key: "mastery",
        render: (v: number) => <Progress percent={v} size="small" strokeColor={v >= 80 ? "#52c41a" : v >= 60 ? "#faad14" : "#ff4d4f"} />,
      },
      {
        title: "状态", dataIndex: "status", key: "status",
        render: (s: string) => <Tag color={s === "掌握" ? "green" : s === "薄弱" ? "orange" : "red"}>{s}</Tag>,
      },
    ];
    return (
      <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
        {contextHolder}
        <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => { setDiagnosis(null); loadExams(); }} style={{ marginBottom: 16, paddingLeft: 0 }}>
          返回列表
        </Button>
        <Result
          icon={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
          title="📊 错题诊断报告"
          subTitle={`${diagnosis.exam_name}（${diagnosis.subject}）| 得分：${diagnosis.score}/${diagnosis.total_score}`}
        />
        <Card title="📋 诊断摘要" style={{ marginBottom: 24, borderRadius: 12 }}>
          <Paragraph>{diagnosis.summary}</Paragraph>
          {diagnosis.error_types.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Text strong>主要错误类型：</Text>
              <div style={{ marginTop: 8 }}>
                {diagnosis.error_types.map((t: string, i: number) => <Tag key={i} color="red">{t}</Tag>)}
              </div>
            </div>
          )}
        </Card>
        {diagnosis.knowledge_points.length > 0 && (
          <Card title="🧠 知识点掌握度分析" style={{ marginBottom: 24, borderRadius: 12 }}>
            <Table dataSource={diagnosis.knowledge_points} columns={kpColumns} rowKey="name" pagination={false} size="small" />
          </Card>
        )}
        <Card title="💡 提分建议" style={{ marginBottom: 24, borderRadius: 12 }}>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {diagnosis.suggestions.map((s: string, i: number) => <li key={i}><Text>{s}</Text></li>)}
          </ul>
        </Card>
        <div style={{ textAlign: "center" }}>
          <Button type="primary" size="large" onClick={() => { setDiagnosis(null); }}>
            继续分析其他试卷 →
          </Button>
        </div>
      </div>
    );
  }

  const columns = [
    { title: "科目", dataIndex: "subject", key: "subject", width: 80 },
    { title: "试卷名称", dataIndex: "name", key: "name" },
    {
      title: "日期", dataIndex: "exam_date", key: "exam_date", width: 120,
      render: (d: string) => d ? new Date(d).toLocaleDateString("zh-CN") : "-",
    },
    {
      title: "得分", key: "score", width: 100,
      render: (_: unknown, r: ExamRecord) => `${r.score}/${r.total_score}`,
    },
    {
      title: "操作", key: "action", width: 120,
      render: (_: unknown, record: ExamRecord) => (
        <Button type="link" size="small" onClick={() => triggerAnalysis(record.id, record.subject, record.name, record.total_score, record.score)}>
          分析报告
        </Button>
      ),
    },
  ];

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: 24 }}>
      {contextHolder}
      <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => navigate("/dashboard")} style={{ marginBottom: 16, paddingLeft: 0 }}>
        返回首页
      </Button>
      <Card
        title={<span><FileSearchOutlined /> 错题分析记录</span>}
        extra={<Button type="primary" icon={<UploadOutlined />} onClick={() => { setUploadFileList([]); setUploadExamName(""); setUploadModalOpen(true); }}>上传试卷</Button>}
        style={{ borderRadius: 12 }}
      >
        <Table dataSource={exams} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 10 }} size="middle" />
      </Card>

      {/* Upload Modal */}
      <Modal
        title="上传试卷图片"
        open={uploadModalOpen}
        onCancel={() => setUploadModalOpen(false)}
        footer={[
          <Button key="cancel" onClick={() => setUploadModalOpen(false)}>取消</Button>,
          <Button key="upload" type="primary" loading={uploading} onClick={confirmUpload}>
            开始分析
          </Button>,
        ]}
      >
        <div style={{ display: "flex", flexDirection: "column", gap: 16, marginTop: 16 }}>
          <div>
            <Text strong>科目：</Text>
            <div style={{ marginTop: 8 }}>
              {["数学", "物理", "化学", "生物", "英语"].map((s) => (
                <Button key={s} type={uploadSubject === s ? "primary" : "default"} size="small" onClick={() => setUploadSubject(s)} style={{ marginRight: 8, marginBottom: 8 }}>{s}</Button>
              ))}
            </div>
          </div>
          <div>
            <Text strong>试卷名称：</Text>
            <input
              style={{ width: "100%", padding: 8, marginTop: 8, border: "1px solid #d9d9d9", borderRadius: 6 }}
              placeholder="如：2025年月考数学试卷"
              value={uploadExamName}
              onChange={(e) => setUploadExamName(e.target.value)}
            />
          </div>
          <div style={{ display: "flex", gap: 16 }}>
            <div style={{ flex: 1 }}>
              <Text strong>总分：</Text>
              <input
                type="number"
                style={{ width: "100%", padding: 8, marginTop: 8, border: "1px solid #d9d9d9", borderRadius: 6 }}
                value={uploadTotalScore}
                onChange={(e) => setUploadTotalScore(parseInt(e.target.value) || 150)}
              />
            </div>
            <div style={{ flex: 1 }}>
              <Text strong>我的得分：</Text>
              <input
                type="number"
                style={{ width: "100%", padding: 8, marginTop: 8, border: "1px solid #d9d9d9", borderRadius: 6 }}
                value={uploadUserScore}
                onChange={(e) => setUploadUserScore(parseInt(e.target.value) || 0)}
              />
            </div>
          </div>
          <div>
            <Text strong>试卷图片（可选，AI OCR 暂未启用）：</Text>
            <Upload {...uploadProps} style={{ marginTop: 8 }}>
              <Button icon={<UploadOutlined />}>选择图片</Button>
            </Upload>
            <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>当前版本需手动输入分数，AI 视觉分析待集成</Text>
          </div>
        </div>
      </Modal>

      {/* Analyzing indicator */}
      {analyzing && (
        <Card style={{ position: "fixed", bottom: 24, right: 24, width: 300, boxShadow: "0 4px 16px rgba(0,0,0,0.2)", borderRadius: 12, zIndex: 1000 }}>
          <Spin spinning={true} tip="AI 正在分析试卷...">
            <div style={{ padding: 8 }}>正在识别错题并生成诊断报告，请稍候...</div>
          </Spin>
        </Card>
      )}
    </div>
  );
}