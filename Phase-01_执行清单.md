# Phase -1 执行清单：数据获取与验证（第1-12周）

> 本文档是 `DESIGN_v0.2.0.md` 第9章路线图的**可执行版本**。
> 每天具体做什么、敲什么命令、产出什么，一目了然。
> 适合"用AI写代码的小白"按步骤执行。

---

## 前置准备（第0.5天）

### 0.1 创建项目目录结构

```bash
# 在项目根目录 F:\life-planner\ 下创建目录
mkdir F:\life-planner\backend
mkdir F:\life-planner\backend\app
mkdir F:\life-planner\backend\app\models
mkdir F:\life-planner\backend\app\api
mkdir F:\life-planner\backend\app\services
mkdir F:\life-planner\backend\app\db
mkdir F:\life-planner\backend\scripts
mkdir F:\life-planner\data
mkdir F:\life-planner\data\raw
mkdir F:\life-planner\data\processed
mkdir F:\life-planner\data\exports
mkdir F:\life-planner\docs
```

### 0.2 安装Python环境（如果用AI辅助编码，可跳过，让AI帮你装）

```bash
# 检查Python版本（需要3.10+）
python --version

# 如果版本低于3.10，去 https://www.python.org/downloads/ 下载安装
# 安装后重新打开终端，再检查
```

### 0.3 创建Python虚拟环境

```bash
# 进入后端目录
cd F:\life-planner\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 激活后命令行前面会出现 (venv) 标记
```

### 0.4 安装基础Python包

```bash
# 升级pip
python -m pip install --upgrade pip

# 安装基础包（按需求安装，不用一次全装）
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary python-dotenv pydantic requests beautifulsoup4 lxml pandas
```

### 0.5 创建 requirements.txt

```bash
# 在 F:\life-planner\backend\ 下创建 requirements.txt
# 内容如下（让AI帮你写，或复制粘贴）：
```

**`F:\life-planner\backend\requirements.txt` 内容：**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
pandas==2.1.3
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

### 0.6 初始化Git仓库（可选，但推荐）

```bash
cd F:\life-planner
git init
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
git add .
git commit -m "Initial commit: project structure"
```

---

## Phase A：3省试点（第1-2周）

### Week 1：爬虫框架 + 山东/河南/广东分数线爬取

#### Day 1-2：搭建爬虫框架

**目标**：写出一个可复用的爬虫基类，能爬取任意一个省考试院的分数线页面。

**让AI帮你写的提示词（直接复制给AI）**：

```
请在 F:\life-planner\backend\scripts\ 下创建 crawler_base.py，实现一个爬虫基类：

class CrawlerBase:
    def __init__(self, province_name, base_url):
        self.province_name = province_name
        self.base_url = base_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def fetch_page(self, url, params=None):
        """获取页面内容，带重试和延时"""
        import time
        import requests
        for attempt in range(3):
            try:
                resp = requests.get(url, headers=self.headers, params=params, timeout=10)
                resp.raise_for_status()
                time.sleep(1)  # 礼貌性延时
                return resp.text
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                time.sleep(2)
        return None
    
    def parse_score_line(self, html):
        """解析分数线表格，返回列表[{'year', 'college', 'major', 'score', 'batch'}]"""
        raise NotImplementedError("子类必须实现")
    
    def save_to_csv(self, data, filename):
        """保存到 CSV"""
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)

请同时创建 shandong_crawler.py（继承CrawlerBase），实现山东分数线爬取。
山东数据来源：https://www.sdzk.cn/ 的历年分数线页面。
先只写框架，不急着爬取，让我确认方向对不对。
```

**AI写完后，你要做的**：
1. 检查代码是否有明显错误（让AI解释每段代码的意思）
2. 运行测试：`python F:\life-planner\backend\scripts\shandong_crawler.py`
3. 如果报错，把错误信息发给AI，让它修复

#### Day 3-4：爬取山东省分数线（2018-2025）

**让AI帮你扩展 shandong_crawler.py**，加入：
- `parse_score_line()` 方法：解析山东考试院页面的表格
- `crawl_years()` 方法：循环爬取2018-2025年
- 保存到 `F:\life-planner\data\raw\shandong_scores_2018_2025.csv`

**运行爬取**：
```bash
cd F:\life-planner\backend
venv\Scripts\activate
python scripts/shandong_crawler.py
```

**检查产出**：
- `F:\life-planner\data\raw\shandong_scores_2018_2025.csv` 应该有以下列：
  `year, college_name, major_name, batch, min_score, province, source_url`

#### Day 5-6：爬取河南/广东分数线

**复制 shandong_crawler.py 改成 henan_crawler.py / guangdong_crawler.py**

让AI帮你写提示词：
```
参考 shandong_crawler.py，创建 henan_crawler.py 和 guangdong_crawler.py。
河南数据来源：https://www.haeea.cn/
广东数据来源：https://eea.gd.gov.cn/
保持相同的 CSV 输出格式（year, college_name, major_name, batch, min_score, province, source_url）
```

**运行爬取**：
```bash
python scripts/henan_crawler.py
python scripts/guangdong_crawler.py
```

**检查产出**：
- `F:\life-planner\data\raw\henan_scores_2018_2025.csv`
- `F:\life-planner\data\raw\guangdong_scores_2018_2025.csv`

#### Day 7：数据质量校验（人工核对）

**让AI帮你写校验脚本**：

提示词：
```
在 F:\life-planner\backend\scripts\ 下创建 validate_data.py，功能：
1. 读取3个CSV文件（山东/河南/广东）
2. 统计：总条数、每年条数、每省条数
3. 检查异常：分数为空、分数<0或>750、年份不在2018-2025
4. 输出校验报告到 F:\life-planner\data\raw\validation_report.txt
```

**运行校验**：
```bash
python scripts/validate_data.py
```

**人工核对**：
- 打开 `validation_report.txt`，看是否有异常
- 随机抽10条数据，去对应省考试院官网核对是否一致

---

### Week 2：一分一段表 + 数据导入数据库

#### Day 8-9：爬取一分一段表（山东/河南/广东）

**让AI帮你写 yikuan_crawler.py**：

提示词：
```
创建 F:\life-planner\backend\scripts\yikuan_crawler.py，爬取一分一段表。
一分一段表格式：分数、人数、累计人数
数据源：
- 山东：https://www.sdzk.cn/ 的一分一段表页面
- 河南：https://www.haeea.cn/ 的一分一段表页面  
- 广东：https://eea.gd.gov.cn/ 的一分一段表页面
输出CSV：year, score, count, cumulative_count, province, source_url
```

**运行爬取**：
```bash
python scripts/yikuan_crawler.py
```

**检查产出**：
- `F:\life-planner\data\raw\shandong_yikuan_2018_2025.csv`
- `F:\life-planner\data\raw\henan_yikuan_2018_2025.csv`
- `F:\life-planner\data\raw\guangdong_yikuan_2018_2025.csv`

#### Day 10-11：创建数据库表 + 导入数据

**让AI帮你写数据库模型**：

提示词：
```
在 F:\life-planner\backend\app\db\ 下创建 models.py，定义以下表（用SQLAlchemy ORM）：

1. college_scores（院校录取分数线）
   - id: Integer, 主键
   - year: Integer
   - college_name: String(200)
   - major_name: String(200), 可为空
   - batch: String(50)  # 本科一批/本科二批/专科批
   - min_score: Integer
   - province: String(50)
   - source_url: String(500)
   - created_at: DateTime

2. province_rank（一分一段表）
   - id: Integer, 主键
   - year: Integer
   - score: Integer
   - count: Integer  # 该分数人数
   - cumulative_count: Integer  # 累计人数
   - province: String(50)
   - source_url: String(500)
   - created_at: DateTime

3. college_info（院校信息）
   - id: Integer, 主键
   - college_name: String(200)
   - province: String(50)
   - city: String(50)
   - type: String(50)  # 985/211/普通本科/专科
   - created_at: DateTime

同时创建 database.py（数据库连接和SessionLocal）。
```

**让AI帮你写数据导入脚本**：

提示词：
```
创建 F:\life-planner\backend\scripts\import_data.py，功能：
1. 读取CSV文件（山东/河南/广东的分数线和一分一段表）
2. 批量插入到数据库（用SQLAlchemy bulk_insert_mappings）
3. 支持增量导入（如果数据已存在则跳过）
4. 输出导入统计：成功条数、跳过条数、失败条数

使用方法：
python scripts/import_data.py --type scores --file data/raw/shandong_scores_2018_2025.csv
python scripts/import_data.py --type rank --file data/raw/shandong_yikuan_2018_2025.csv
```

**运行导入**：
```bash
# 先创建数据库（SQLite，方便开发）
# 在 F:\life-planner\backend\ 下创建 data.db（SQLite文件）

# 运行导入
python scripts/import_data.py --type scores --file data/raw/shandong_scores_2018_2025.csv
python scripts/import_data.py --type scores --file data/raw/henan_scores_2018_2025.csv
python scripts/import_data.py --type scores --file data/raw/guangdong_scores_2018_2025.csv

python scripts/import_data.py --type rank --file data/raw/shandong_yikuan_2018_2025.csv
python scripts/import_data.py --type rank --file data/raw/henan_yikuan_2018_2025.csv
python scripts/import_data.py --type rank --file data/raw/guangdong_yikuan_2018_2025.csv
```

**检查产出**：
- `F:\life-planner\backend\data.db` SQLite数据库文件
- 用DB Browser for SQLite打开，查看 `college_scores` 和 `province_rank` 表是否有数据

#### Day 12-14：后端API框架 + 数据查询接口

**让AI帮你写FastAPI应用**：

提示词：
```
在 F:\life-planner\backend\app\ 下创建 main.py，启动FastAPI应用。
创建以下API接口（先写框架，返回Mock数据即可）：

GET /api/college-data/scores
  参数: year, province, college_name(可选), batch(可选)
  返回: [{year, college_name, major_name, batch, min_score, province}]

GET /api/college-data/rank
  参数: year, province, score(可选)
  返回: [{year, score, count, cumulative_count, province}]

GET /api/college-data/college-info
  参数: province(可选), type(可选)
  返回: [{college_name, province, city, type}]

运行：uvicorn app.main:app --reload
测试：浏览器访问 http://localhost:8000/docs
```

**运行测试**：
```bash
cd F:\life-planner\backend
uvicorn app.main:app --reload

# 打开浏览器访问 http://localhost:8000/docs
# 测试 /api/college-data/scores 接口
```

**检查产出**：
- `http://localhost:8000/docs` 可以看到Swagger文档
- 调用接口能返回数据（可能是Mock数据，后面再接数据库）

---

## Phase B：扩展至20省（第3-6周）

### Week 3-4：爬取其余7个Easy省

**Easy省列表**（见DESIGN_v0.2.0.md第2.2.1章）：
四川(seea.cn)、河北(hebeea.edu.cn)、湖南(hneeb.cn)、安徽(ahzsks.cn)、江西(jxeea.cn)、辽宁(lnzsks.com)、陕西(sneea.cn)

**让AI帮你批量写爬虫**：

提示词：
```
参考 shandong_crawler.py，批量创建以下省份的爬虫脚本（每个省一个文件）：
- sichuan_crawler.py (四川 seea.cn)
- hebei_crawler.py (河北 hebeea.edu.cn)
- hunan_crawler.py (湖南 hneeb.cn)
- anhui_crawler.py (安徽 ahzsks.cn)
- jiangxi_crawler.py (江西 jxeea.cn)
- liaoning_crawler.py (辽宁 lnzsks.com)
- shaanxi_crawler.py (陕西 sneea.cn)

每个爬虫保存到 F:\life-planner\backend\scripts\crawlers\
先写一个省（四川），让我确认方向对不对，再写其余6个。
```

**运行爬取**（每天跑2-3个省）：
```bash
python scripts/crawlers/sichuan_crawler.py
python scripts/crawlers/hebei_crawler.py
# ... 依次运行
```

**导入数据库**：
```bash
python scripts/import_data.py --type scores --file data/raw/sichuan_scores_2018_2025.csv
# ... 依次导入
```

### Week 5-6：爬取10个Medium省 + 院校基本信息

**Medium省列表**：
北京(bjeea.cn)、上海(shmeea.edu.cn)、浙江(zjzs.net)、江苏(jseea.cn)、湖北(hbea.edu.cn)、山西(sxkszx.cn)、福建(eeafj.cn)、广西(gxeea.cn)、吉林(jleea.com.cn)、黑龙江(lzk.hl.cn)、内蒙古(nm.zsks.cn)、新疆(zkxj.edu.cn)、重庆(cqksy.cn)、云南(ynzs.cn)

**让AI帮你写Medium省爬虫**（部分省份可能是PDF，需要OCR）：

提示词：
```
创建 Medium 省份的爬虫（14个省）。注意：
- 北京/上海/浙江 可能是PDF格式，需要先下载PDF再解析
- 江苏/湖北/山西 可能是HTML+PDF混合
- 先用 requests 试试能否直接获取HTML，如果不行再考虑PDF

每个省一个文件，保存到 F:\life-planner\backend\scripts\crawlers\medium\
先写北京（PDF解析），让我确认PDF解析方案是否可行。
```

**爬取院校基本信息**（3000+所）：

提示词：
```
创建 F:\life-planner\backend\scripts\college_info_crawler.py，爬取院校基本信息。
数据源：阳光高考平台 https://yxzy.cn/ 的院校库
输出CSV：college_name, province, city, type(985/211/普通本科/专科), website(可选)
```

**运行爬取+导入**（并行进行）：
```bash
# 爬取Medium省（每天2-3个省）
python scripts/crawlers/medium/beijing_crawler.py
# ...

# 爬取院校信息
python scripts/college_info_crawler.py

# 导入院校信息到数据库
python scripts/import_data.py --type college-info --file data/raw/college_info.csv
```

---

## Phase C：攻坚+后端起步（第7-10周）

### Week 7-8：完成7个Hard省爬取

**Hard省列表**：
天津(zhaokao.net)、贵州(zsksy.guizhou.gov.cn)、甘肃(ganseea.cn)、海南(ea.hainan.gov.cn)、宁夏(nxjyks.cn)、青海(qhjyks.com)、西藏(xzzsks.com.cn)

**让AI帮你写Hard省爬虫**（可能需要手动处理）：

提示词：
```
创建 Hard 省份的爬虫（7个省）。这些省份的网站可能：
- 需要验证码（先用简单OCR试试，不行就手动下载）
- 数据结构不统一（需要单独适配）
- 数据分散在多个页面（需要递归爬取）

每个省一个文件，保存到 F:\life-planner\backend\scripts\crawlers\hard\
先写天津（可能最简单），让我确认方向。
```

**运行爬取+导入**：
```bash
python scripts/crawlers/hard/tianjin_crawler.py
# ... 依次运行Hard省

# 导入数据库
python scripts/import_data.py --type scores --file data/raw/tianjin_scores_2018_2025.csv
# ...
```

### Week 9-10：数据整合 + 后端API完善

**数据整合**（多源数据对齐）：

提示词：
```
创建 F:\life-planner\backend\scripts\data_integration.py，功能：
1. 检查数据一致性（同一院校在不同省份的名称是否统一）
2. 统一院校名称（如"北京大学"和"北大"视为同一所）
3. 填补数据缺口（如果某年数据缺失，用前后年平均值填充）
4. 输出数据质量报告到 F:\life-planner\data\processed\data_quality_report.txt
```

**后端API完善**（接入真实数据库）：

提示词：
```
修改 F:\life-planner\backend\app\main.py，让API接口返回真实数据库数据（不用Mock）。
需要：
1. 在 app/api/ 下创建 college_data.py（分数线/位次/院校信息查询）
2. 用SQLAlchemy查询数据库，返回JSON
3. 添加分页（page/page_size）
4. 添加缓存（用functools.lru_cache或redis）
5. 添加错误处理（数据库连不上怎么办）
```

**运行测试**：
```bash
uvicorn app.main:app --reload

# 浏览器访问 http://localhost:8000/docs
# 测试真实数据查询
```

---

## Phase D：数据运维体系（第11-12周）

### Week 11：数据更新自动化

**让AI帮你写定时更新脚本**：

提示词：
```
在 F:\life-planner\backend\app\services\ 下创建 scheduler_service.py，用APScheduler实现定时任务：

1. 每年6月1日：准备数据更新环境（创建备份、清空raw目录）
2. 每年7月15日：执行分数线更新（调用crawler脚本）
3. 每月1日：扫描高校名单更新（调用college_info_crawler.py）
4. 每周一早9点：检查数据完整性（调用validate_data.py）

同时创建监控脚本 F:\life-planner\backend\scripts\monitor.py：
- 检查数据覆盖率（已爬取省/目标省）
- 检查数据新鲜度（最新数据距今天数）
- 检查数据异常比率（分数超出合理范围）
- 如果异常，发送邮件告警（用Python的smtplib）
```

**运行测试**：
```bash
python -c "from app.services.scheduler_service import scheduler; scheduler.start(); print('Scheduler started')"
```

### Week 12：数据质量监控 + 性能优化

**让AI帮你写性能优化**：

提示词：
```
优化 F:\life-planner\backend\app\api\college_data.py 的查询性能：

1. 添加数据库索引（在models.py里加index=True）
2. 用JOIN减少查询次数
3. 用Paginate减少单次返回数据量
4. 用Cache缓存热门查询（如"2024年山东省分数线"）
5. 添加查询日志（记录慢查询>500ms）

目标：API响应时间 <100ms（P95）
```

**运行性能测试**：
```bash
# 让AI帮你写压力测试脚本
# 或者用Apach Bench: ab -n 1000 -c 10 http://localhost:8000/api/college-data/scores?year=2024&province=山东
```

**检查产出**：
- `F:\life-planner\backend\app\services\scheduler_service.py` 定时任务就绪
- `F:\life-planner\backend\scripts\monitor.py` 监控脚本就绪
- API响应时间测试通过（<100ms）

---

## 验收标准（Phase -1 结束时）

✅ **数据覆盖**：31省全部爬取完成，数据量 > 200万条  
✅ **数据质量**：准确率 > 90%（抽样100条人工核对）  
✅ **后端API**：所有 `/api/college-data/*` 接口可用，响应 < 100ms  
✅ **数据运维**：定时更新+监控告警就绪  
✅ **文档**：`F:\life-planner\data\README.md` 记录数据源、爬取脚本、更新频率  

---

## 风险提示 + 应对

| 风险 | 概率 | 影响 | 应对 |
|---|---|---|---|
| 某省爬虫失败（反爬虫/PDF解析） | 高 | 中 | 先跳过，后续手动处理；不影响整体进度 |
| 数据质量不达标（准确率<90%） | 中 | 高 | 加强数据校验；找第二个数据源交叉验证 |
| API性能不达标（>100ms） | 中 | 中 | 加索引、加缓存、优化查询 |
| 学习时间超预期（AI写的代码看不懂） | 高 | 高 | 让AI逐行解释；不懂就问；必要时回退到更简单的实现 |

---

## 下一步（Phase 0：MVP产品核心功能）

Phase -1 完成后，进入 Phase 0（第13-18周）：
- Week 13-14：后端API + 数据库（users/exams/daily_logs）
- Week 15-16：前端核心页面（登录/仪表盘/考试分析/AI教练/高考志愿）
- Week 17-18：集成测试 + Bug修复

详见 `Phase-02_MVP开发清单.md`（Phase -1完成后生成）

---

**文件版本**：v0.1.0（2026-06-10）  
**对应设计文档**：`F:\life-planner\DESIGN_v0.2.0.md` 第9章  
**适用人群**：用AI写代码的小白（需要AI辅助每一步）  
**维护者**：刘某（GitHub: aidless）
