import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  use: {
    baseURL: "http://127.0.0.1:3100",
    trace: "on-first-retry",
  },
  webServer: [
    {
      command: "sh ../frontend/scripts/start-e2e-backend.sh",
      url: "http://127.0.0.1:8100/healthz",
      reuseExistingServer: false,
      cwd: "../backend",
    },
    {
      command: "npm run dev -- --hostname 127.0.0.1 --port 3100",
      url: "http://127.0.0.1:3100",
      reuseExistingServer: false,
      env: {
        NEXT_PUBLIC_API_BASE_URL: "http://127.0.0.1:8100/api",
      },
    },
  ],
});
