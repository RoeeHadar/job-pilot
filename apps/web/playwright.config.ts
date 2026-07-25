import os from 'node:os'
import path from 'node:path'
import { defineConfig, devices } from '@playwright/test'

const state = path.join(os.tmpdir(), `job-pilot-e2e-${Date.now()}`)
const database = path.join(state, 'test.sqlite').replaceAll('\\', '/')
const python = process.platform === 'win32' ? '.\\.venv\\Scripts\\python' : 'python'

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:5191',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    ...devices['Desktop Edge'],
    channel: process.env.CI ? undefined : 'msedge',
  },
  webServer: [
    {
      command: `${python} -m uvicorn app.main:app --host 127.0.0.1 --port 8001`,
      cwd: '../api',
      url: 'http://127.0.0.1:8001/health',
      reuseExistingServer: false,
      env: {
        DATABASE_URL: `sqlite:///${database}`,
        MEMORY_PATH: path.join(state, 'memory'),
      },
    },
    {
      command: 'npm run dev -- --host 127.0.0.1 --port 5191',
      cwd: '.',
      url: 'http://127.0.0.1:5191',
      reuseExistingServer: false,
      env: {
        VITE_API_TARGET: 'http://127.0.0.1:8001',
      },
    },
  ],
})
