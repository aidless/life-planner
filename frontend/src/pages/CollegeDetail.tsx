import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Card, Descriptions, Table, Tag, Spin, Empty, Select, Space, Statistic, Row, Col } from 'antd';
import { getCollegeDetail, CollegeDetail } from '../services/api';

interface ScoreRecord {
  year: number;
  major: string;
  min_score: number | null;
  min_rank: number | null;
  province: string;
  subject_type: string;
  source: string;
}

export default function CollegeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<CollegeDetail | null>(null);
  const [provinceFilter, setProvinceFilter] = useState<string | undefined>();
  const [subjectFilter, setSubjectFilter] = useState<string | undefined>();
  const [yearFilter, setYearFilter] = useState<number | undefined>();

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getCollegeDetail(id)
      .then(d => setData(d))
      .catch(e => console.error(e))
      .finally(() => setLoading(false));
  }, [id]);

  const allScores: ScoreRecord[] = useMemo(() => {
    return (data?.recent_scores || []).map((s: any) => ({
      ...s,
      subject_type: s.subject_type || "",
      source: s.source || "",
    }));
  }, [data]);

  // Extract unique filter options
  const provinces = useMemo(() => [...new Set(allScores.map(s => s.province))].sort(), [allScores]);
  const subjectTypes = useMemo(() => [...new Set(allScores.map(s => s.subject_type))].sort(), [allScores]);
  const years = useMemo(() => [...new Set(allScores.map(s => s.year))].sort((a, b) => b - a), [allScores]);

  // Filtered scores
  const filteredScores = useMemo(() => {
    return allScores.filter(s => {
      if (provinceFilter && s.province !== provinceFilter) return false;
      if (subjectFilter && s.subject_type !== subjectFilter) return false;
      if (yearFilter && s.year !== yearFilter) return false;
      return true;
    });
  }, [allScores, provinceFilter, subjectFilter, yearFilter]);

  // Stats by province
  const provinceStats = useMemo(() => {
    const stats: Record<string, number> = {};
    allScores.forEach(s => {
      stats[s.province] = (stats[s.province] || 0) + 1;
    });
    return stats;
  }, [allScores]);

  // Stats by subject type
  const subjectStats = useMemo(() => {
    const stats: Record<string, number> = {};
    allScores.forEach(s => {
      stats[s.subject_type] = (stats[s.subject_type] || 0) + 1;
    });
    return stats;
  }, [allScores]);

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />;
  if (!data) return <Empty description="院校不存在" />;

  const scoreColumns = [
    { title: '年份', dataIndex: 'year', width: 80, sorter: (a: ScoreRecord, b: ScoreRecord) => b.year - a.year },
    { title: '省份', dataIndex: 'province', width: 80 },
    { title: '科类', dataIndex: 'subject_type', width: 80, render: (v: string) => <Tag color={v === '物理' ? 'blue' : v === '历史' ? 'green' : 'default'}>{v}</Tag> },
    { title: '专业', dataIndex: 'major', width: 240, ellipsis: true },
    { title: '最低分', dataIndex: 'min_score', width: 90, render: (v: number | null) => v ?? '-', sorter: (a: ScoreRecord, b: ScoreRecord) => (a.min_score || 0) - (b.min_score || 0) },
    { title: '最低位次', dataIndex: 'min_rank', width: 100, render: (v: number | null) => v ? v.toLocaleString() : '-', sorter: (a: ScoreRecord, b: ScoreRecord) => (a.min_rank || Infinity) - (b.min_rank || Infinity) },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Descriptions title={data.name} bordered column={2} size="small">
          <Descriptions.Item label="院校ID">{data.id}</Descriptions.Item>
          <Descriptions.Item label="标签">
            {data.features.map(f => <Tag key={f} color="blue">{f}</Tag>)}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Stats Overview */}
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={24}>
          <Col span={6}>
            <Statistic title="总记录数" value={allScores.length} suffix="条" />
          </Col>
          {Object.entries(provinceStats).map(([prov, count]) => (
            <Col span={6} key={prov}>
              <Statistic title={`${prov}数据`} value={count} suffix="条" />
            </Col>
          ))}
          {Object.entries(subjectStats).map(([subj, count]) => (
            <Col span={6} key={subj}>
              <Statistic title={`${subj}类`} value={count} suffix="条" />
            </Col>
          ))}
        </Row>
      </Card>

      {/* Filters */}
      <Card style={{ marginBottom: 24 }}>
        <Space wrap>
          <Select
            placeholder="省份"
            value={provinceFilter}
            onChange={setProvinceFilter}
            allowClear
            style={{ width: 120 }}
            options={provinces.map(p => ({ label: p, value: p }))}
          />
          <Select
            placeholder="科类"
            value={subjectFilter}
            onChange={setSubjectFilter}
            allowClear
            style={{ width: 120 }}
            options={subjectTypes.map(s => ({ label: s, value: s }))}
          />
          <Select
            placeholder="年份"
            value={yearFilter}
            onChange={setYearFilter}
            allowClear
            style={{ width: 120 }}
            options={years.map(y => ({ label: String(y), value: y }))}
          />
        </Space>
      </Card>

      <Card title={`投档分数明细（${filteredScores.length} 条 / 共 ${allScores.length} 条）`}>
        <Table
          rowKey={(record: ScoreRecord) => `${record.year}-${record.province}-${record.subject_type}-${record.major}`}
          columns={scoreColumns}
          dataSource={filteredScores}
          pagination={{ pageSize: 20, showSizeChanger: true, showTotal: t => `共 ${t} 条` }}
          size="small"
          scroll={{ x: 700 }}
        />
      </Card>
    </div>
  );
}
