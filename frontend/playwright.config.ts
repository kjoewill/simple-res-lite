// frontend/playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 30_000,
  webServer: [
    {
      command: './run_uvicorn.sh',
      cwd: '../backend',
      port: 8000,
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev -- --port 5173 --strictPort',
      cwd: '.',
      port: 5173,
      reuseExistingServer: !process.env.CI,
    },
  ],
  use: {
    baseURL: 'http://localhost:5173',
  },
});
