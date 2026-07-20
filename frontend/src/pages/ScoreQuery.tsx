import React, { useState } from 'react';
import { Card, Form, Input, Select, Button, Table, Tag, Spin } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { queryScores, CollegeScoreRecord } from '../services/api';

const PROVINCES = ['山东', '广东'];

export default function ScoreQueryPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CollegeScoreRecord[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    const values = form.getFieldsValue();
    setLoading(true);
    setSearched(true);
    try {
      const result = await queryScores({
        year: values.year ? Number(values.year) : undefined,
        province: values.province || undefined,
        college: values.college || undefined,
        major: values.major || undefined,
      });
      setData(result);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: '年份', dataIndex: 'year', width: 80 },
    { title: '省份', dataIndex: 'province', width: 80 },
    { title: '院校', dataIndex: 'college_name', width: 200,
      render: (text: string, record: CollegeScoreRecord) => (
        <a href={`/colleges/${record.id}`}>{text}</a>
      ),
    },
    { title: '专业', dataIndex: 'major_name', width: 200 },
    { title: '批次', dataIndex: 'batch', width: 100 },
    { title: '最低分', dataIndex: 'min_score', width: 90,
      render: (v: number | null) => v ?? '-',
    },
    { title: '最低位次', dataIndex: 'min_rank', width: 100,
      render: (v: number | null) => v ? v.toLocaleString() : '-',
    },
    { title: '来源', dataIndex: 'source', width: 150, render: (v: string) => <Tag>{v}</Tag> },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Form form={form} layout="inline" style={{ flexWrap: 'wrap', gap: 8 }}>
          <Form.Item name="college" label="院校">
            <Input placeholder="如：北京大学" allowClear style={{ width: 160 }} />
          </Form.Item>
          <Form.Item name="major" label="专业">
            <Input placeholder="如：计算机" allowClear style={{ width: 140 }} />
          </Form.Item>
          <Form.Item name="province" label="省份">
            <Select placeholder="全部" allowClear style={{ width: 120 }} options={PROVINCES.map(p => ({ label: p, value: p }))} />
          </Form.Item>
          <Form.Item name="year" label="年份">
            <Select placeholder="全部" allowClear style={{ width: 100 }} options={[
              { label: '2025', value: '2025' },
              { label: '2024', value: '2024' },
              { label: '2023', value: '2023' },
            ]} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch} loading={loading}>
              查询
            </Button>
          </Form.Item>
        </Form>
      </Card>

      {searched && (
        <Card title={`查询结果（${data.length} 条）`}>
          <Table
            rowKey="id"
            columns={columns}
            dataSource={data}
            loading={loading}
            pagination={{ pageSize: 50, showSizeChanger: true, showTotal: t => `共 ${t} 条` }}
            scroll={{ x: 1000 }}
            size="middle"
          />
        </Card>
      )}
    </div>
  );
}
