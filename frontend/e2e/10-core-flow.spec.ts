/**
 * 主流程 e2e（P2-2 落盘）：注册 → 登录页表单登录 → 建目标 → 删目标
 *
 * 隔离要求：必须经 E2E_API 指向独立测试后端跑，禁止默认 8001 正式库。
 *   E2E_API=http://localhost:4801 E2E_BASE_URL=http://localhost:5173 npx playwright test e2e/10-core-flow.spec.ts
 */

import { test, expect } from "@playwright/test";

const API = process.env.E2E_API ?? "http://localhost:8001";

function newUser() {
  const u = "p22_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 6);
  return { username: u, email: `${u}@test.com`, password: "Test123456" };
}

async function register(page: any, user: { username: string; email: string; password: string }) {
  const resp = await page.request.post(`${API}/api/auth/register`, {
    data: user,
    timeout: 10000,
  });
  expect(resp.status(), "register status").toBe(200);
  const data = await resp.json();
  return data.data.access_token as string;
}

function collectErrors(page: any): string[] {
  const errors: string[] = [];
  page.on("pageerror", (err: Error) => errors.push(err.message));
  page.on("console", (msg: any) => {
    if (msg.type() === "error") errors.push(`console: ${msg.text()}`);
  });
  return errors;
}

function expectNoJsErrors(errors: string[]) {
  const filtered = errors.filter(
    (e) =>
      !e.includes("favicon") &&
      !e.includes("Failed to load resource") &&
      !e.includes("Static function can not consume context") &&
      !e.includes("antd: message"),
  );
  expect(filtered, `JS errors: ${filtered.join("\n")}`).toHaveLength(0);
}

test("登录页表单登录 → 跳转 dashboard", async ({ page }) => {
  const errors = collectErrors(page);
  const user = newUser();
  await register(page, user);

  await page.goto("/login", { waitUntil: "domcontentloaded" });
  await page.getByPlaceholder("用户名").fill(user.username);
  await page.getByPlaceholder("密码").fill(user.password);
  await page.getByRole("button", { name: /登\s*录/ }).click();

  await page.waitForURL(/\/dashboard/, { timeout: 8000 });
  await expect(page.locator("h3").first()).toBeVisible({ timeout: 5000 });
  expectNoJsErrors(errors);
});

test("建目标 → 列表可见 → 删除 → 列表消失", async ({ page }) => {
  const errors = collectErrors(page);
  const user = newUser();
  const token = await register(page, user);
  await page.addInitScript((t: string) => {
    localStorage.setItem("token", t);
  }, token);

  const goalTitle = `P22目标_${Date.now().toString(36)}`;

  await page.goto("/goals", { waitUntil: "domcontentloaded" });
  await page.waitForLoadState("networkidle", { timeout: 8000 }).catch(() => {});

  // 建目标
  await page.getByRole("button", { name: "添加目标" }).click();
  await page.getByPlaceholder("如: 每天跑步5公里").fill(goalTitle);
  await page.locator(".ant-modal-footer .ant-btn-primary").click();
  await expect(page.getByText("目标已创建")).toBeVisible({ timeout: 5000 });
  await expect(page.locator(".ant-list-item", { hasText: goalTitle })).toBeVisible({ timeout: 5000 });

  // 删目标（该行最后一个按钮为删除图标按钮）
  await page.locator(".ant-list-item", { hasText: goalTitle }).locator("button").last().click();
  await expect(page.getByText("已删除")).toBeVisible({ timeout: 5000 });
  await expect(page.locator(".ant-list-item", { hasText: goalTitle })).toHaveCount(0, { timeout: 5000 });

  expectNoJsErrors(errors);
});
