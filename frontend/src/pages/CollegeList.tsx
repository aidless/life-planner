import React, { useEffect, useState } from 'react';
import { Card, Input, Select, Table, Tag, Button } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { listColleges, CollegeOut } from '../services/api';

const PROVINCES = ['山东', '广东'];

export default function CollegeListPage() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CollegeOut[]>([]);
  const [keyword, setKeyword] = useState('');
  const [province, setProvince] = useState<string | undefined>();
  const [features, setFeatures] = useState<string[]>([]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const result = await listColleges({ province, features, keyword: keyword || undefined, page: 1, page_size: 100 });
      setData(result.items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const columns = [
    { title: '院校名称', dataIndex: 'name', width: 240,
      render: (text: string, record: CollegeOut) => (
        <a href={`/colleges/${record.id}`}>{text}</a>
      ),
    },
    { title: '省份', dataIndex: 'province', width: 100 },
    { title: '标签', dataIndex: 'features', width: 200,
      render: (features: string[]) => features.map(f => <Tag key={f}>{f}</Tag>),
    },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
          <Input
            placeholder="搜索院校名称..."
            prefix={<SearchOutlined />}
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            onPressEnter={fetchData}
            style={{ width: 240 }}
            allowClear
          />
          <Select
            placeholder="省份"
            value={province}
            onChange={setProvince}
            allowClear
            style={{ width: 120 }}
            options={PROVINCES.map(p => ({ label: p, value: p }))}
          />
          <Select
            mode="multiple"
            placeholder="标签"
            value={features}
            onChange={setFeatures}
            style={{ width: 200 }}
            options={[
              { label: '985', value: '985' },
              { label: '211', value: '211' },
              { label: '双一流', value: '双一流' },
            ]}
          />
          <Button type="primary" onClick={fetchData}>
            搜索
          </Button>
        </div>
      </Card>

      <Card title={`院校列表（${data.length} 所）`}>
        <Table
          rowKey="id"
          columns={columns}
          dataSource={data}
          loading={loading}
          pagination={{ pageSize: 50, showSizeChanger: true, showTotal: t => `共 ${t} 所` }}
          scroll={{ x: 600 }}
          size="middle"
        />
      </Card>
    </div>
  );
}
