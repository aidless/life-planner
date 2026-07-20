import React, { useState, useEffect } from 'react';
import { Card, Form, Input, Select, Button, Table, Tag, message, Radio, Alert, Space, Progress, Tooltip } from 'antd';
import { useNavigate } from 'react-router-dom';
import { DownloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { predictColleges } from '../services/api';
import { useAuthStore } from '../store/authStore';
import apiClient from '@/api/client';

interface PredictItem {
  college_id: string;
  college_name: string;
  major: string;
  min_score: number | null;
  min_rank: number | null;
  probability: string;
  data_source?: string;
  confidence?: number;
  year?: number;
  subject_type?: string;
}

interface PredictResult {
  dash: PredictItem[];
  steady: PredictItem[];
  safe: PredictItem[];
}

const PROVINCE_OPTIONS = [
  { label: '山东', value: '山东', subjects: ['综合'] },
  { label: '广东', value: '广东', subjects: ['物理', '历史'] },
  { label: '江苏', value: '江苏', subjects: ['物理', '历史'] },
  { label: '湖北', value: '湖北', subjects: ['物理', '历史'] },
  { label: '重庆', value: '重庆', subjects: ['物理', '历史'] },
];

const YEAR_OPTIONS = [
  { label: '2025', value: 2025 },
  { label: '2024', value: 2024 },
];

export default function PredictPage() {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResult | null>(null);
  const [subjectOptions, setSubjectOptions] = useState<string[]>(['综合']);
  const navigate = useNavigate();
  const { user, token } = useAuthStore();

  const isLoggedIn = !!token && !!user;

  useEffect(() => {
    // Auto-set subject based on province
    const province = form.getFieldValue('province');
    if (province) {
      const p = PROVINCE_OPTIONS.find(p => p.value === province);
      if (p) {
        setSubjectOptions(p.subjects);
        form.setFieldValue('subject_combination', p.subjects[0]);
      }
    }
  }, [form]);

  const handleProvinceChange = (value: string) => {
    const p = PROVINCE_OPTIONS.find(p => p.value === value);
    if (p) {
      setSubjectOptions(p.subjects);
      form.setFieldValue('subject_combination', p.subjects[0]);
    }
  };

  const handlePredict = async () => {
    if (!isLoggedIn) {
      message.warning('请先登录');
      navigate('/login');
      return;
    }

    const values = form.getFieldsValue();
    if (!values.score || !values.province) {
      message.warning('请填写分数和省份');
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const res = await predictColleges({
        score: Number(values.score),
        rank: values.rank ? Number(values.rank) : undefined,
        province: values.province,
        subject_combination: values.subject_combination || subjectOptions[0],
        year: values.year ? Number(values.year) : undefined,
      });
      setResult(res);
      message.success('预测完成！');
    } catch (e: any) {
      console.error('Predict error:', e);
      const msg = e.response?.data?.message || e.response?.data?.detail || e.message || '未知错误';
      message.error('预测失败：' + msg);
      if (e.response?.status === 401 || e.response?.status === 403) {
        message.info('请重新登录');
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  const resultColumns = [
    { title: '院校', dataIndex: 'college_name', width: 200 },
    { title: '专业/专业组', dataIndex: 'major', width: 220, ellipsis: true },
    { title: '最低分', dataIndex: 'min_score', width: 90, render: (v: number | null) => v ?? '-' },
    { title: '位次', dataIndex: 'min_rank', width: 100, render: (v: number | null) => v?.toLocaleString() ?? '-' },
    { title: '概率', dataIndex: 'probability', width: 80, render: (v: string) => {
      const color = v === '冲刺' ? 'red' : v === '稳妥' ? 'orange' : 'green';
      return <Tag color={color}>{v}</Tag>;
    }},
    { title: '置信度 · 来源', dataIndex: 'confidence', width: 200, render: (_: any, row: PredictItem) => {
      const conf = row.confidence ?? 0;
      const confPct = Math.round(conf * 100);
      const color = conf >= 0.85 ? '#52c41a' : conf >= 0.75 ? '#faad14' : '#ff4d4f';
      return (
        <Space direction="vertical" size={2} style={{ width: '100%' }}>
          <Tooltip title={`置信度 ${confPct}% （按 tier 设定，非真实回归）`}>
            <Progress percent={confPct} size="small" strokeColor={color} showInfo format={(p) => `${p}%`} />
          </Tooltip>
          {row.data_source && (
            <Tooltip title="每条推荐附数据来源标签，可点击去考试院官网核对">
              <Tag style={{ fontSize: 10 }} icon={<InfoCircleOutlined />}>
                {row.data_source}
              </Tag>
            </Tooltip>
          )}
        </Space>
      );
    }},
  ];

  const [downloading, setDownloading] = useState(false);
  const handleDownloadPDF = async () => {
    const values = form.getFieldsValue();
    if (!values.score || !values.province) {
      message.warning('请先填写分数和省份');
      return;
    }
    setDownloading(true);
    try {
      const res = await apiClient.post('/college/export-pdf', {
        score: Number(values.score),
        rank: values.rank ? Number(values.rank) : undefined,
        province: values.province,
        subject_combination: values.subject_combination || subjectOptions[0],
        year: values.year ? Number(values.year) : 2025,
      }, { responseType: 'blob' });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `志愿推荐_${values.province}_${values.year || 2025}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      message.success('PDF 已下载');
    } catch (e: any) {
      console.error('Download PDF error:', e);
      message.error('下载失败：' + (e.message || '未知错误'));
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div>
      <Card title="高考志愿预测" style={{ marginBottom: 24 }}>
        {!isLoggedIn && (
          <Alert
            message="未登录"
            description="预测功能需要登录后才能使用。请先登录或注册账号。"
            type="warning"
            showIcon
            action={
              <Space>
                <Button size="small" type="primary" onClick={() => navigate('/login')}>登录</Button>
                <Button size="small" onClick={() => navigate('/register')}>注册</Button>
              </Space>
            }
            style={{ marginBottom: 16 }}
          />
        )}

        <Form form={form} layout="vertical" style={{ maxWidth: 600 }}>
          <Form.Item name="score" label="高考分数" rules={[{ required: true, message: '请输入分数' }]}>
            <Input type="number" placeholder="如：600" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item name="rank" label="位次（强烈建议填写，提高预测准确度）">
            <Input type="number" placeholder="如：20000" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item name="province" label="省份" rules={[{ required: true, message: '请选择省份' }]}>
            <Select
              placeholder="选择省份"
              style={{ width: 200 }}
              options={PROVINCE_OPTIONS}
              onChange={handleProvinceChange}
            />
          </Form.Item>
          <Form.Item name="subject_combination" label="科类">
            <Radio.Group>
              {subjectOptions.map(s => (
                <Radio key={s} value={s}>{s === '物理' ? '物理类' : s === '历史' ? '历史类' : '综合类'}</Radio>
              ))}
            </Radio.Group>
          </Form.Item>
          <Form.Item name="year" label="预测年份（基于该年份数据）">
            <Select placeholder="最新年份" allowClear style={{ width: 200 }} options={YEAR_OPTIONS} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" onClick={handlePredict} loading={loading} size="large" disabled={!isLoggedIn}>
                开始预测
              </Button>
              <Button icon={<DownloadOutlined />} onClick={handleDownloadPDF} loading={downloading} size="large" disabled={!isLoggedIn}>
                一键导出 PDF 报告
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {result && (
        <div>
          <Card title={`冲刺志愿（${result.dash.length} 所）`} style={{ marginBottom: 16 }} headStyle={{ background: '#fff1f0' }}>
            {result.dash.length === 0 ? <Alert message="未找到冲刺院校，建议扩大搜索范围或检查位次是否准确" type="info" /> :
            <Table rowKey={(r, i) => `dash-${i}`} columns={resultColumns} dataSource={result.dash} pagination={false} size="small" scroll={{ x: 700 }} />}
          </Card>
          <Card title={`稳妥志愿（${result.steady.length} 所）`} style={{ marginBottom: 16 }} headStyle={{ background: '#fff7e6' }}>
            {result.steady.length === 0 ? <Alert message="未找到稳妥院校" type="info" /> :
            <Table rowKey={(r, i) => `steady-${i}`} columns={resultColumns} dataSource={result.steady} pagination={false} size="small" scroll={{ x: 700 }} />}
          </Card>
          <Card title={`保底志愿（${result.safe.length} 所）`} headStyle={{ background: '#f6ffed' }}>
            {result.safe.length === 0 ? <Alert message="未找到保底院校" type="info" /> :
            <Table rowKey={(r, i) => `safe-${i}`} columns={resultColumns} dataSource={result.safe} pagination={false} size="small" scroll={{ x: 700 }} />}
          </Card>
        </div>
      )}
    </div>
  );
}
