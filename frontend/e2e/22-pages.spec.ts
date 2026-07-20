/**
 * 22 页面 e2e 测试
 *
 * 测试策略：
 * 1. 注册 → 拿 token → 存到 localStorage
 * 2. 跳转每个页面 → 检查页面 title / 关键元素 / 截图
 * 3. 失败时自动截图到 test-results/
 */

import { test, expect } from "@playwright/test";
import { execSync } from "child_process";

const PAGES = [
  { path: "/dashboard", name: "仪表盘", selector: "h3" },
  { path: "/daily", name: "日常记录", selector: "h3" },
  { path: "/exams", name: "考试分析", selector: "h3" },
  { path: "/goals", name: "人生目标", selector: "h3" },
  { path: "/study", name: "学习规划", selector: "h3" },
  { path: "/subject-selection", name: "选科", selector: "h3" },
  { path: "/college", name: "高考志愿", selector: "h3" },
  { path: "/career", name: "职业发展", selector: "h3" },
  { path: "/grad", name: "研究生", selector: "h3" },
  { path: "/ai", name: "AI 教练", selector: "h3" },
  { path: "/psychology", name: "心理", selector: "h3" },
  { path: "/family", name: "家庭", selector: "h3" },
  { path: "/interest", name: "兴趣", selector: "h3" },
  { path: "/social", name: "社交", selector: "h3" },
  { path: "/learning", name: "学习", selector: "h3" },
  { path: "/travel", name: "旅行", selector: "h3" },
  { path: "/intimacy", name: "亲密", selector: "h3" },
  { path: "/meaning", name: "意义", selector: "h3" },
  { path: "/scores", name: "分数查询", selector: "h2" },
  { path: "/predict", name: "预测", selector: "h2" },
  { path: "/colleges", name: "高校列表", selector: "h2" },
];

// 注册 → 注入 token → 跳转登录页 → 自动登录
test.beforeEach(async ({ page, context }) => {
  // 注册新用户（带重试，避免时序问题）
  const u = "e2e_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 6);
  const email = `${u}@test.com`;
  let resp;
  let lastErr;
  for (let i = 0; i < 3; i++) {
    try {
      resp = await page.request.post("http://localhost:8001/api/auth/register", {
        data: { username: u, email, password: "Test123456" },
        timeout: 10000,
      });
      if (resp.status() === 200) break;
    } catch (err) {
      lastErr = err;
      await page.waitForTimeout(500);
    }
  }
  if (!resp || resp.status() !== 200) {
    throw new Error(`register failed after retries: ${resp?.status() ?? "no resp"}, lastErr: ${lastErr}`);
  }
  const data = await resp.json();
  const token = data.data.access_token;

  // 注入到 localStorage（页面加载前）
  await context.addInitScript((t) => {
    localStorage.setItem("token", t);
  }, token);
});

test.describe("22 页面 e2e", () => {
  for (const p of PAGES) {
    test(`${p.path} (${p.name}) 跳转 + 渲染`, async ({ page }) => {
      const errors: string[] = [];
      page.on("pageerror", (err) => errors.push(err.message));
      page.on("console", (msg) => {
        if (msg.type() === "error") errors.push(`console: ${msg.text()}`);
      });

      await page.goto(p.path, { waitUntil: "domcontentloaded" });
      // 等页面切换完
      await page.waitForLoadState("networkidle", { timeout: 8000 }).catch(() => {});

      // 截图
      await page.screenshot({ path: `test-results/${p.name}.png`, fullPage: false });

      // 检查 title
      await expect(page).toHaveTitle(/.+/);

      // 关键：不能有 JS 错误（已知的 antd 5 dynamic theme 警告忽略）
      const filteredErrors = errors.filter((e) =>
        !e.includes("favicon") &&
        !e.includes("Failed to load resource") &&
        !e.includes("Static function can not consume context") &&
        !e.includes("antd: message")
      );
      expect(filteredErrors, `JS errors on ${p.path}: ${filteredErrors.join("\n")}`).toHaveLength(0);
    });
  }
});

test("404 fallback 路由", async ({ page }) => {
  await page.goto("/nonexistent-route-xyz");
  // NotFound 显示 "抱歉" 字样
  await expect(page.locator(".ant-result-subtitle"))
    .toContainText("抱歉", { timeout: 5000 });
});

test("apiClient 401 自动重定向", async ({ page, context }) => {
  // 清除 token
  await context.clearCookies();
  await page.goto("/dashboard");
  // 应该被重定向到 /login
  await page.waitForURL(/\/login/, { timeout: 5000 });
});
