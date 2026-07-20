import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Typography, Progress, Card, Button, Radio, Result, Table, Tag, Space, message } from "antd";
import { ArrowLeftOutlined, CheckCircleOutlined } from "@ant-design/icons";

const { Title, Paragraph, Text } = Typography;

type Step = "intro" | "question" | "result";

// 霍兰德 6 维度代码：R(现实) I(研究) A(艺术) S(社会) E(企业) C(常规)
const HOLLAND = ["R", "I", "A", "S", "E", "C"] as const;
type Holland = typeof HOLLAND[number];

// 60 题霍兰德职业兴趣测评（每题对应一个维度）
const QUESTIONS: { id: number; text: string; dim: Holland }[] = [
  { id: 1, text: "我喜欢动手操作工具或机器", dim: "R" },
  { id: 2, text: "我喜欢探索自然规律与现象", dim: "I" },
  { id: 3, text: "我喜欢绘画、音乐或写作", dim: "A" },
  { id: 4, text: "我喜欢帮助他人解决困难", dim: "S" },
  { id: 5, text: "我喜欢说服或领导团队", dim: "E" },
  { id: 6, text: "我喜欢整理数据和文件", dim: "C" },
  { id: 7, text: "我喜欢户外运动与体能活动", dim: "R" },
  { id: 8, text: "我喜欢做科学实验", dim: "I" },
  { id: 9, text: "我喜欢设计创意作品", dim: "A" },
  { id: 10, text: "我喜欢与人合作完成任务", dim: "S" },
  { id: 11, text: "我喜欢挑战与竞争", dim: "E" },
  { id: 12, text: "我喜欢按流程规范做事", dim: "C" },
  { id: 13, text: "我喜欢修理电器或机械", dim: "R" },
  { id: 14, text: "我喜欢思考抽象问题", dim: "I" },
  { id: 15, text: "我喜欢表演或戏剧", dim: "A" },
  { id: 16, text: "我喜欢倾听他人倾诉", dim: "S" },
  { id: 17, text: "我喜欢组织活动并担任负责人", dim: "E" },
  { id: 18, text: "我喜欢做表格和归档工作", dim: "C" },
  { id: 19, text: "我喜欢木工或手工制作", dim: "R" },
  { id: 20, text: "我喜欢阅读科普书籍", dim: "I" },
  { id: 21, text: "我喜欢摄影或视频创作", dim: "A" },
  { id: 22, text: "我喜欢做志愿者服务", dim: "S" },
  { id: 23, text: "我喜欢销售或推广产品", dim: "E" },
  { id: 24, text: "我喜欢记账或预算管理", dim: "C" },
  { id: 25, text: "我喜欢野外探险", dim: "R" },
  { id: 26, text: "我喜欢数学解题", dim: "I" },
  { id: 27, text: "我喜欢写小说或诗歌", dim: "A" },
  { id: 28, text: "我喜欢教导他人知识", dim: "S" },
  { id: 29, text: "我喜欢创业或开拓新市场", dim: "E" },
  { id: 30, text: "我喜欢遵守规则和制度", dim: "C" },
  { id: 31, text: "我喜欢体育竞技", dim: "R" },
  { id: 32, text: "我喜欢研究历史或哲学", dim: "I" },
  { id: 33, text: "我喜欢时尚与造型设计", dim: "A" },
  { id: 34, text: "我喜欢调解纠纷", dim: "S" },
  { id: 35, text: "我喜欢公开演讲", dim: "E" },
  { id: 36, text: "我喜欢处理日常行政事务", dim: "C" },
  { id: 37, text: "我喜欢驾驶或操作设备", dim: "R" },
  { id: 38, text: "我喜欢分析复杂数据", dim: "I" },
  { id: 39, text: "我喜欢烹饪或美食创作", dim: "A" },
  { id: 40, text: "我喜欢陪伴老人或小孩", dim: "S" },
  { id: 41, text: "我喜欢谈判或说服他人", dim: "E" },
  { id: 42, text: "我喜欢校对文件", dim: "C" },
  { id: 43, text: "我喜欢种植花草或照顾宠物", dim: "R" },
  { id: 44, text: "我喜欢编程或算法题", dim: "I" },
  { id: 45, text: "我喜欢逛艺术展览", dim: "A" },
  { id: 46, text: "我喜欢参加社交聚会", dim: "S" },
  { id: 47, text: "我喜欢制定目标和计划并执行", dim: "E" },
  { id: 48, text: "我喜欢整理物品分类摆放", dim: "C" },
  { id: 49, text: "我喜欢动手组装家具", dim: "R" },
  { id: 50, text: "我喜欢天文学或地理学", dim: "I" },
  { id: 51, text: "我喜欢做手工艺或 DIY", dim: "A" },
  { id: 52, text: "我喜欢安慰受伤的朋友", dim: "S" },
  { id: 53, text: "我喜欢带领团队完成挑战", dim: "E" },
  { id: 54, text: "我喜欢填写报表", dim: "C" },
  { id: 55, text: "我喜欢钓鱼或露营", dim: "R" },
  { id: 56, text: "我喜欢做化学实验", dim: "I" },
  { id: 57, text: "我喜欢弹奏乐器", dim: "A" },
  { id: 58, text: "我喜欢为他人提供建议", dim: "S" },
  { id: 59, text: "我喜欢影响他人决策", dim: "E" },
  { id: 60, text: "我喜欢在图书馆整理书籍", dim: "C" },
];

// 6 维度名称 + 描述
const HOLLAND_META: Record<Holland, { name: string; desc: string }> = {
  R: { name: "现实型 (Realistic)", desc: "动手操作、机器工具、户外活动" },
  I: { name: "研究型 (Investigative)", desc: "科学探索、抽象思考、分析问题" },
  A: { name: "艺术型 (Artistic)", desc: "创意表达、艺术创作、自由想象" },
  S: { name: "社会型 (Social)", desc: "帮助他人、教育引导、人际沟通" },
  E: { name: "企业型 (Enterprising)", desc: "领导说服、竞争挑战、目标达成" },
  C: { name: "常规型 (Conventional)", desc: "数据处理、规范流程、组织整理" },
};

// 选科组合（3+3 或 3+1+2 模式）
const SUBJECT_COMBINATIONS = [
  { id: "phy_chem_bio", name: "物化生", subjects: ["物理", "化学", "生物"], coverage: "95%", career: "医学、生物、工程" },
  { id: "phy_chem_geo", name: "物化地", subjects: ["物理", "化学", "地理"], coverage: "90%", career: "工程、环境、地质" },
  { id: "phy_bio_geo", name: "物生地", subjects: ["物理", "生物", "地理"], coverage: "85%", career: "环境、生态" },
  { id: "hist_pol_geo", name: "史政地", subjects: ["历史", "政治", "地理"], coverage: "92%", career: "法学、新闻、教育" },
  { id: "hist_pol_bio", name: "史政生", subjects: ["历史", "政治", "生物"], coverage: "80%", career: "文理交叉" },
  { id: "chem_bio_pol", name: "化生政", subjects: ["化学", "生物", "政治"], coverage: "85%", career: "医学预科" },
  { id: "phy_chem_pol", name: "物化政", subjects: ["物理", "化学", "政治"], coverage: "88%", career: "工科 + 管理" },
  { id: "phy_hist_pol", name: "物史政", subjects: ["物理", "历史", "政治"], coverage: "82%", career: "技术 + 政策" },
];

export default function SubjectSelection() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>("intro");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});

  const total = QUESTIONS.length;

  const handleAnswer = (value: number) => {
    setAnswers({ ...answers, [QUESTIONS[currentIndex].id]: value });
  };

  const handleNext = () => {
    if (currentIndex < total - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setStep("result");
    }
  };

  const handlePrev = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  // 计算各维度得分（1-5 分制 → 总分）
  const scores = useMemo(() => {
    const init: Record<Holland, number> = { R: 0, I: 0, A: 0, S: 0, E: 0, C: 0 };
    QUESTIONS.forEach((q) => {
      const a = answers[q.id];
      if (a) init[q.dim] += a;
    });
    return init;
  }, [answers]);

  // Top 3 维度
  const top3 = useMemo(() => {
    return HOLLAND.map((d) => ({ dim: d, score: scores[d] }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
  }, [scores]);

  const currentQ = QUESTIONS[currentIndex];
  const answered = answers[currentQ.id];
  const progress = Math.round(((currentIndex + 1) / total) * 100);

  // ---- Render: Intro ----
  if (step === "intro") {
    return (
      <div style={{ maxWidth: 800, margin: "0 auto", padding: 24 }}>
        <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => navigate("/dashboard")} style={{ marginBottom: 16, paddingLeft: 0 }}>
          返回首页
        </Button>
        <Card style={{ borderRadius: 12 }}>
          <Title level={3}>🎯 霍兰德职业兴趣测评</Title>
          <Paragraph>
            通过 60 道情景选择题，从 6 个维度评估你的职业兴趣倾向，AI 推荐最适合的高考选科组合。
          </Paragraph>
          <div style={{ background: "#f5f5f5", padding: 16, borderRadius: 8, marginBottom: 24 }}>
            <Text strong>6 个维度：</Text>
            <ul style={{ marginTop: 8, marginBottom: 0 }}>
              {HOLLAND.map((d) => (
                <li key={d}><Text>{HOLLAND_META[d].name} — {HOLLAND_META[d].desc}</Text></li>
              ))}
            </ul>
          </div>
          <Paragraph type="secondary" style={{ fontSize: 12 }}>
            ⚠️ 本工具为本地离线版本，题目与推荐组合内置。所有数据仅在你的浏览器中处理，不上传服务器。
          </Paragraph>
          <Button type="primary" size="large" onClick={() => setStep("question")}>
            开始测评 →
          </Button>
        </Card>
      </div>
    );
  }

  // ---- Render: Questions ----
  if (step === "question") {
    return (
      <div style={{ maxWidth: 700, margin: "0 auto", padding: 24 }}>
        <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => navigate("/dashboard")} style={{ marginBottom: 16, paddingLeft: 0 }}>
          返回首页
        </Button>
        <Card style={{ borderRadius: 12 }}>
          <div style={{ marginBottom: 16 }}>
            <Text type="secondary">进度：{currentIndex + 1} / {total}</Text>
            <Progress percent={progress} strokeColor="#1677ff" />
          </div>
          <Title level={4} style={{ marginBottom: 24 }}>{currentQ.text}</Title>
          <Radio.Group
            value={answered}
            onChange={(e) => handleAnswer(e.target.value)}
            style={{ width: "100%" }}
          >
            <Space direction="vertical" style={{ width: "100%" }}>
              {[
                { v: 1, label: "非常不喜欢" },
                { v: 2, label: "不太喜欢" },
                { v: 3, label: "中立" },
                { v: 4, label: "比较喜欢" },
                { v: 5, label: "非常喜欢" },
              ].map((opt) => (
                <Radio key={opt.v} value={opt.v} style={{ padding: "8px 0" }}>
                  {opt.label}
                </Radio>
              ))}
            </Space>
          </Radio.Group>
          <div style={{ marginTop: 32, display: "flex", justifyContent: "space-between" }}>
            <Button disabled={currentIndex === 0} onClick={handlePrev}>
              上一题
            </Button>
            <Button type="primary" disabled={!answered} onClick={handleNext}>
              {currentIndex < total - 1 ? "下一题 →" : "提交查看结果"}
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  // ---- Render: Result ----
  const totalScore = Object.values(scores).reduce((s, v) => s + v, 0);
  const hollandCode = top3.map((t) => t.dim).join("");

  // 推荐组合：根据 top1 维度粗略映射
  const recMap: Record<Holland, string[]> = {
    R: ["phy_chem_bio", "phy_chem_geo"],
    I: ["phy_chem_bio", "chem_bio_pol"],
    A: ["hist_pol_geo", "phy_chem_pol"],
    S: ["hist_pol_bio", "chem_bio_pol"],
    E: ["hist_pol_geo", "phy_chem_pol"],
    C: ["phy_chem_bio", "hist_pol_geo"],
  };
  const recIds = recMap[top3[0].dim] || [];
  const recCombinations = SUBJECT_COMBINATIONS.filter((c) => recIds.includes(c.id));

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <Button type="link" icon={<ArrowLeftOutlined />} onClick={() => setStep("intro")} style={{ marginBottom: 16, paddingLeft: 0 }}>
        重新测评
      </Button>
      <Result
        icon={<CheckCircleOutlined style={{ color: "#52c41a" }} />}
        title="🎉 测评完成"
        subTitle={`你的霍兰德代码：${hollandCode}（共 ${totalScore} 分）`}
      />

      <Card title="📊 6 维度得分" style={{ marginBottom: 24, borderRadius: 12 }}>
        <Table
          dataSource={HOLLAND.map((d) => ({
            key: d,
            dim: d,
            name: HOLLAND_META[d].name,
            score: scores[d],
            max: 50,
            pct: Math.round((scores[d] / 50) * 100),
            rank: HOLLAND.indexOf(top3.find((t) => t.dim === d)?.dim || "R") + 1,
          }))}
          columns={[
            { title: "维度", dataIndex: "name", key: "name" },
            {
              title: "得分",
              dataIndex: "score",
              key: "score",
              render: (s: number, r: any) => `${s}/${r.max}`,
            },
            {
              title: "强度",
              dataIndex: "pct",
              key: "pct",
              render: (p: number) => (
                <Progress percent={p} size="small" strokeColor={p >= 70 ? "#52c41a" : p >= 50 ? "#1677ff" : "#bfbfbf"} />
              ),
            },
            {
              title: "排名",
              dataIndex: "rank",
              key: "rank",
              render: (rk: number) => rk <= 3 ? <Tag color="orange">Top {rk}</Tag> : rk,
            },
          ]}
          pagination={false}
          size="small"
        />
      </Card>

      <Card title="🎯 AI 推荐选科组合" style={{ marginBottom: 24, borderRadius: 12 }}>
        <Paragraph type="secondary">
          基于你的 Top 1 维度 <Tag color="orange">{HOLLAND_META[top3[0].dim].name}</Tag>，为你推荐以下组合：
        </Paragraph>
        <Table
          dataSource={recCombinations.map((c) => ({ ...c, key: c.id }))}
          columns={[
            { title: "组合", dataIndex: "name", key: "name" },
            {
              title: "科目",
              dataIndex: "subjects",
              key: "subjects",
              render: (subs: string[]) => subs.map((s) => <Tag key={s} color="blue">{s}</Tag>),
            },
            { title: "专业覆盖率", dataIndex: "coverage", key: "coverage" },
            { title: "适配职业方向", dataIndex: "career", key: "career" },
          ]}
          pagination={false}
          size="middle"
        />
        <Paragraph type="secondary" style={{ fontSize: 12, marginTop: 16 }}>
          💡 提示：选科决策需结合个人目标大学、目标专业、所在省份的选科要求综合判断。
          本结果仅供参考，最终以你的兴趣 + 实力 + 升学规划为准。
        </Paragraph>
      </Card>

      <Card title="📋 所有可选组合一览" style={{ borderRadius: 12 }}>
        <Table
          dataSource={SUBJECT_COMBINATIONS.map((c) => ({ ...c, key: c.id }))}
          columns={[
            { title: "组合", dataIndex: "name", key: "name", width: 100 },
            {
              title: "科目",
              dataIndex: "subjects",
              key: "subjects",
              render: (subs: string[]) => subs.map((s) => <Tag key={s}>{s}</Tag>),
            },
            { title: "专业覆盖率", dataIndex: "coverage", key: "coverage", width: 110 },
            { title: "适配职业方向", dataIndex: "career", key: "career" },
          ]}
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
}