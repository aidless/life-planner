import { Alert } from "antd";

type AdviceNoteProps = {
  detail?: string;
};

export default function AdviceNote({ detail }: AdviceNoteProps) {
  return (
    <Alert
      type="warning"
      showIcon
      style={{ marginBottom: 16 }}
      message="未经验证，不能当建议用"
      description={
        detail ??
        "这是个人全栈演示。模型输出、固定模板和分数线快照都没有做过效果验证，不是医疗、财务、心理咨询或招生录取指导。"
      }
    />
  );
}
