# FAILURE_MODES

这些是这个演示会怎样误导人，以及代码现在实际怎么做。不是一份已修复清单。

## 分数线过期或对不上考试院

高考短名单读的是 SQLite 里的 `college_scores` / `province_ranks`，不是仓库里的 JSON。新鲜克隆和 Compose 启动后这两张表是空的。

已提交的快照自带年份：山东 JSON 的 `source` 写成 `sdzk.cn_2024` 或 `sdzk.cn_2025`；广东 JSON 有 2024/2025 的 `year`，没有 `source`；江苏脚本 JSON 的 `source` 形如 `jsjyksy_2025_*`。本次没有重新下载，也没有对照考试院网页或 PDF 复核。清单 `backend/data/raw/DATA_DOWNLOAD_CHECKLIST.md` 和树上的文件不一致。

`province_easy.py` 可以生成 `source: "mock"` 的河南/广东行。已提交 JSON 里这次没找到这种行，不代表以后的导入不会混进去。

没有位次行时，接口返回空档，并带 `rank_status: no_data`。它不再代入一个固定位次。有数据时，冲/稳/保是位次区间里各取最多 5 条。`confidence` 是写死的档位常数，不是录取概率。

## 模型幻觉

Claude 只在设置了 `ANTHROPIC_API_KEY` 时被调用。没有 key 时 `AIClient.analyze` 返回固定字符串「AI 分析服务未配置（缺少 ANTHROPIC_API_KEY）」。

有 key 时，回复仍然是未经验证的演示。系统提示要求模型自己声明这一点，这不能阻止幻觉。仪表盘上以前标成「今日建议」的句子来自 `_suggest_action` 的固定模板，按最低分的维度挑，不是模型生成的。

## 示例数据被当成真实生活

注册会调用 `scripts/init_user_data.py`，写入约 30 天随机记录，包括健康、财务和习惯。这些数字每次注册都不同，没有固定随机种子。仪表盘有示例横幅。5 年时间轴是前端写死的示例，不是该用户的计划。

健康、财务、习惯没有前端路由，但示例行仍然会写进数据库。已开放维度的平均分不把这三个维度算进去；数据库里的行还在。

## SECRET_KEY 与鉴权

`backend/app/config.py` 在 `SECRET_KEY` 和 `JWT_SECRET_KEY` 都为空时，用 `secrets.token_urlsafe` 生成进程内密钥。开发 compose 允许这个空值。重启后旧 token 失效。生产 compose 用 `${SECRET_KEY:?...}` 拒绝空密钥。

`backend/app/middleware/trust_bd.py` 在可选的 `trust_cap` 能被导入时才会挂上。那个文件把 JWT 解码设成 `verify_signature: False`，并且在 `LIFE_PLANNER_SECRET` 缺省时使用字符串 `dev-secret-key-change-in-prod`。它用的不是应用的 `SECRET_KEY`。普通克隆导入失败，`main.py` 只打一条 warning，中间件不启用。这不是一道开着的安全边界。不要把「中间件文件存在」说成请求已被能力系统拦住。

作者机器上的 `F:/life-planner` 路径如果被某条脚本拿去打开数据库，在这台机器上会失败。它们不是部署路径。带这个路径的源文件在开头有 AUTHOR_PATH 标记。
