import { Link } from "react-router-dom";
import "./index.css";

export default function Landing() {
  const loggedIn = Boolean(localStorage.getItem("token"));

  return (
    <div className="landing">
      <header className="landing-header">
        <Link className="landing-brand" to="/">
          <span className="landing-mark" aria-hidden="true">✓</span>
          <span>
            <strong>Life Planner</strong>
            <small>人生规划系统</small>
          </span>
        </Link>
        <nav className="landing-nav" aria-label="主导航">
          <a href="#features">能做什么</a>
          <a href="#privacy">数据在哪</a>
          <a href="https://github.com/aidless/life-planner" target="_blank" rel="noreferrer">GitHub</a>
        </nav>
        <div className="landing-header-actions">
          {loggedIn ? (
            <Link className="landing-btn" to="/dashboard">进入仪表盘</Link>
          ) : (
            <>
              <Link className="landing-login" to="/login">登录</Link>
              <Link className="landing-btn" to="/register">免费开始</Link>
            </>
          )}
        </div>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <p className="landing-kicker">12 维人生仪表盘 · 计划 · 记录 · 复盘</p>
            <h1>人生很长，<br /><span>先把今天过明白。</span></h1>
            <p className="landing-lede">
              不只看成绩，也看健康、关系、意义和长期目标。
              把散落的计划收成一张仪表盘，让每天的行动和一年后的方向对得上。
            </p>
            <div className="landing-actions">
              <Link className="landing-btn landing-btn-lg" to={loggedIn ? "/dashboard" : "/register"}>
                {loggedIn ? "进入仪表盘" : "免费开始"}
              </Link>
              <Link className="landing-btn landing-btn-ghost landing-btn-lg" to="/login">
                已有账号，登录
              </Link>
            </div>
            <p className="landing-note">
              核心功能不需要 AI key · 注册后自动生成 30 天示例数据 · 示例会在仪表盘明确标注
            </p>
          </div>
          <figure className="landing-shot">
            <img src="/landing-dashboard-crop.png" alt="Life Planner 十二维人生仪表盘示例" />
            <figcaption>示例账号 · 十二维仪表盘</figcaption>
          </figure>
        </section>

        <section className="landing-features" id="features">
          <h2>不是又一个待办清单。</h2>
          <div className="landing-feature-grid">
            <article>
              <span className="landing-feature-index">01</span>
              <h3>看见全景</h3>
              <p>12 个维度：学业、职业、健康、财务、习惯、心理、家庭、兴趣、社交、学习、旅行、亲密与意义。分数只是入口，不是结论。</p>
            </article>
            <article>
              <span className="landing-feature-index">02</span>
              <h3>落到今天</h3>
              <p>目标拆成可执行计划，日常记录、考试分析、番茄专注接在同一条时间线上。今天做了什么，一年后看得见。</p>
            </article>
            <article>
              <span className="landing-feature-index">03</span>
              <h3>AI 是可选件</h3>
              <p>没有 Claude key 也能用计划、记录、目标和仪表盘。配置 key 后，AI 教练才会参与分析和建议。</p>
            </article>
          </div>
        </section>

        <section className="landing-privacy" id="privacy">
          <div className="landing-privacy-inner">
            <h2>你的生活数据，不需要经过第三方。</h2>
            <ul>
              <li><strong>账号数据库</strong>：默认 SQLite，数据在你的部署实例内；Docker 用独立卷持久化。</li>
              <li><strong>AI 可选</strong>：不配置 key 时不会调用任何模型；配置后只把当前对话发给模型提供方。</li>
              <li><strong>示例数据</strong>：注册时注入的 30 天记录是虚构的，用来展示结构；仪表盘会明确标注，不会假装成真实历史。</li>
              <li><strong>没有埋点</strong>：仓库不包含第三方统计脚本；各省分数线数据来自公开教育考试院资料。</li>
            </ul>
            <p className="landing-boundary">
              边界：Life Planner 是规划工具，不是心理治疗、医疗或财务建议。请用自己的判断做最终决定。
            </p>
          </div>
        </section>

        <section className="landing-cta">
          <h2>先看清方向，再开始行动。</h2>
          <p>注册即用。核心功能免费，AI 教练按需配置。</p>
          <Link className="landing-btn landing-btn-lg" to={loggedIn ? "/dashboard" : "/register"}>
            {loggedIn ? "回到仪表盘" : "免费开始"}
          </Link>
        </section>
      </main>

      <footer className="landing-footer">
        <div><strong>Life Planner</strong> · 人生规划系统</div>
        <div>
          <a href="https://github.com/aidless/life-planner" target="_blank" rel="noreferrer">GitHub</a>
          <span>MIT</span>
          <span>示例数据为虚构</span>
        </div>
      </footer>
    </div>
  );
}
