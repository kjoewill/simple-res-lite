// frontend/playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 30_000,
  use: {
    baseURL: 'http://localhost:5173',
  },
});
