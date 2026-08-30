import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './tests',
	fullyParallel: true,
	forbidOnly: Boolean(process.env.CI),
	retries: process.env.CI ? 2 : 0,
	use: {
		baseURL: 'http://127.0.0.1:4173',
		trace: 'on-first-retry'
	},
	projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
	webServer: {
		command: 'npm run preview -- --host 127.0.0.1',
		url: 'http://127.0.0.1:4173',
		reuseExistingServer: !process.env.CI
	}
});
