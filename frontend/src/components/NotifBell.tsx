/** Header 通知铃铛：未读 high 推送数，点击跳 /recommend */
import { useEffect, useState } from "react";
import { Badge, Button } from "antd";
import { BellOutlined } from "@ant-design/icons";
import { Link } from "react-router-dom";
import apiClient from "@/api/client";

export default function NotifBell() {
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!localStorage.getItem("token")) return;
    apiClient
      .get("/recommend/notifications", { params: { unread_only: true } })
      .then((res) => setUnread((res.data.data || []).length))
      .catch(() => undefined);
  }, []);

  return (
    <Link to="/recommend" title="智能推荐">
      <Badge count={unread} size="small" offset={[-2, 4]}>
        <Button
          type="text"
          icon={<BellOutlined style={{ color: "white", fontSize: 18 }} />}
        />
      </Badge>
    </Link>
  );
}
