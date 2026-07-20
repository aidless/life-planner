/**
 * Playwright E2E 配置
 *
 * 使用系统已装的 Chrome（避免 playwright download chromium 阻塞）
 */

import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 2,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    // 使用系统 Chrome（避免 chromium 下载失败）
    channel: "chrome",
    headless: true,
  },
  projects: [
    {
      name: "chromium",
      use: {
        browserName: "chromium",
        channel: "chrome",
      },
    },
  ],
});