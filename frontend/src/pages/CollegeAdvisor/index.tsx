import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Typography, Card, Form, Input, Select, Button, Tag, Result, Spin, message } from "antd";
import { ArrowLeftOutlined, SolutionOutlined, BankOutlined } from "@ant-design/icons";
import apiClient from "@/api/client";
import AdviceNote from "@/components/AdviceNote";

const { Paragraph, Text } = Typography;
const { Option } = Select;

const provinces = [
  "北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
  "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南",
  "湖北", "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州",
  "云南", "西藏", "陕西", "甘肃", "青海", "宁夏", "新疆",
];

const subjectOptions = ["物理", "化学", "生物", "政治", "历史", "地理"];

interface RecommendItem {
  id?: number;
  college_name?: string;
  name?: string;
  major_name?: string;
  probability?: "reach" | "match" | "safe" | "dash" | "steady";
  score_line?: number;
  min_score?: number;
  ranking?: number;
  min_rank?: number;
  location?: string;
  province?: string;
  type?: string;
  reasons?: string[];
}

interface RecommendResult {
  reach: RecommendItem[];
  match: RecommendItem[];
  safe: RecommendItem[];
  summary: string;
}

export default function CollegeAdvisor() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RecommendResult | null>(null);
  const [form] = Form.useForm();
  const [msgApi, contextHolder] = message.useMessage();

  const handleSubmit = async (values: { score: number; province: string; subjects: string[] }) => {
    setLoading(true);
    try {
      // 修：真后端端点是 POST /api/college/predict
      const res = await apiClient.post<any>("/college/predict", {
        score: values.score,
        province: values.province,
        subject_combination: values.subjects.join("+"),
        year: 2025,
      });
      const data = res.data?.data || {};
      const listed = (data.dash?.length || 0) + (data.steady?.length || 0) + (data.safe?.length || 0);
      const rankNote = data.rank_status === "no_data"
        ? "分数表没有对应位次，结果是空的，没有填占位位次。"
        : data.rank_status === "from_province_ranks"
          ? `位次来自分数表反查：${data.user_rank}。`
          : data.user_rank
            ? `使用填写的位次：${data.user_rank}。`
            : "";
      setResult({
        reach: data.dash || [],
        match: data.steady || [],
        safe: data.safe || [],
        summary: `按位次区间从数据库取出 ${listed} 条，不是模型筛选。请求里的年份是 2025。${rankNote}`,
      });
    } catch (err: any) {
      const detail = err.response?.data?.detail || "推荐失败";
      msgApi.error(`推荐失败：${detail}`);
    } finally {
      setLoading(false);
    }
  };

  // 适配两种数据格式（mock fallback + 真后端）
  const normalize = (c: RecommendItem) => ({
    id: c.id ?? 0,
    name: c.college_name || c.name || "未知",
    major: c.major_name || "",
    score_line: c.score_line || c.min_score || 0,
    ranking: c.ranking || c.min_rank || 0,
    location: c.location || c.province || "",
    type: c.type || "",
    probability: c.probability || "match",
    reasons: c.reasons || [],
  });

  const renderCollegeCard = (raw: RecommendItem, idx: number, color: string) => {
    const c = normalize(raw);
    const probLabel = c.probability === "reach" || c.probability === "dash" ? "冲"
      : c.probability === "match" || c.probability === "steady" ? "稳" : "保";
    return (
      <Card key={`${c.id}-${idx}`} size="small" style={{ marginBottom: 12, borderLeft: `4px solid ${color}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <Text strong style={{ fontSize: 15 }}>{c.name}</Text>
            <Tag color={color === "#ff4d4f" ? "red" : color === "#faad14" ? "orange" : "green"} style={{ marginLeft: 8 }}>
              {probLabel}
            </Tag>
            <div style={{ marginTop: 4 }}>
              <Text type="secondary">
                {c.major && `${c.major} · `}{c.location && `${c.location} · `}{c.type && c.type}
              </Text>
            </div>
            {c.reasons.length > 0 && c.reasons.map((r: string, i: number) => (
              <Tag key={i} style={{ marginTop: 4 }}>{r}</Tag>
            ))}
          </div>
          <div style={{ textAlign: "right", minWidth: 100 }}>
            <div style={{ fontSize: 18, fontWeight: "bold", color: "#1677ff" }}>{c.score_line || "—"}</div>
            <Text type="secondary" style={{ fontSize: 12 }}>录取分</Text>
            {c.ranking > 0 && (
              <>
                <div style={{ fontSize: 12, marginTop: 4 }}>{c.ranking.toLocaleString()}</div>
                <Text type="secondary" style={{ fontSize: 11 }}>位次</Text>
              </>
            )}
          </div>
        </div>
      </Card>
    );
  };

  if (result) {
    return (
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: 24 }}>
        {contextHolder}
        <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => setResult(null)} style={{ marginBottom: 16, paddingLeft: 0 }}>
          重新填报
        </Button>
        <AdviceNote detail="下面是数据库里的位次区间短名单，不是招生录取建议。新鲜数据库是空的。source 和年份来自行内字段，这里没有对照考试院复核。" />
        <Result
          icon={<SolutionOutlined style={{ color: "#1677ff" }} />}
          title="志愿短名单"
          subTitle={result.summary}
        />
        <Card title="🚀 冲刺档（建议 1-2 所）" style={{ marginBottom: 24, borderRadius: 12, borderColor: "#ff4d4f" }}>
          {result.reach.length === 0 ? <Text type="secondary">暂无冲刺推荐</Text>
            : result.reach.map((c, i) => renderCollegeCard(c, i, "#ff4d4f"))}
        </Card>
        <Card title="🎯 稳妥档（建议 3-4 所）" style={{ marginBottom: 24, borderRadius: 12, borderColor: "#faad14" }}>
          {result.match.length === 0 ? <Text type="secondary">暂无稳妥推荐</Text>
            : result.match.map((c, i) => renderCollegeCard(c, i, "#faad14"))}
        </Card>
        <Card title="🛡️ 保底档（建议 2-3 所）" style={{ marginBottom: 24, borderRadius: 12, borderColor: "#52c41a" }}>
          {result.safe.length === 0 ? <Text type="secondary">暂无保底推荐</Text>
            : result.safe.map((c, i) => renderCollegeCard(c, i, "#52c41a"))}
        </Card>
        <div style={{ textAlign: "center", marginTop: 32 }}>
          <Button size="large" onClick={() => setResult(null)}>重新填报</Button>
          <Button type="primary" size="large" style={{ marginLeft: 16 }} onClick={() => navigate("/dashboard")}>返回首页</Button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: 24 }}>
      {contextHolder}
      <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => navigate("/dashboard")} style={{ marginBottom: 16, paddingLeft: 0 }}>
        返回首页
      </Button>
      <Card title={<span><BankOutlined /> 志愿填报</span>} style={{ borderRadius: 12 }}>
        <AdviceNote detail="提交后请求固定带 year=2025。后端按位次区间查库，每次最多 5+5+5 条。没有分数表行时列表是空的。这不是招生录取建议。" />
        <Paragraph type="secondary" style={{ marginBottom: 24 }}>
          填写分数、省份和选科。结果来自当前数据库里的分数行，不是模型，也不是「真实大学数据」的保证。
        </Paragraph>
        <Spin spinning={loading} tip="查询中...">
          <Form form={form} layout="vertical" onFinish={handleSubmit}>
            <Form.Item name="score" label="高考分数" rules={[{ required: true, message: "请输入分数" }]}>
              <Input type="number" placeholder="如：650" style={{ width: 200 }} />
            </Form.Item>
            <Form.Item name="province" label="省份" rules={[{ required: true, message: "请选择省份" }]}>
              <Select placeholder="选择省份" showSearch style={{ width: 200 }}>
                {provinces.map((p) => <Option key={p} value={p}>{p}</Option>)}
              </Select>
            </Form.Item>
            <Form.Item name="subjects" label="选考科目（3 门）" rules={[{ required: true, message: "请选择选考科目" }]}>
              <Select mode="multiple" placeholder="选择 3 门选考科目" style={{ width: "100%" }} maxTagCount={3}>
                {subjectOptions.map((s) => <Option key={s} value={s}>{s}</Option>)}
              </Select>
            </Form.Item>
            <Button type="primary" htmlType="submit" size="large" block loading={loading}>
              生成志愿推荐 →
            </Button>
          </Form>
        </Spin>
      </Card>
    </div>
  );
}