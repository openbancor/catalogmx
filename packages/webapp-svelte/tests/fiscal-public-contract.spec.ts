import { expect, test } from '@playwright/test';

const issueUrl = 'https://github.com/openbancor/catalogmx/issues/97';
const pendingAuditText = 'Modalidad 10/PTI: pendiente de auditoría';

test('IMSS renders a visible audit notice and exposes no Modalidad 10 controls', async ({ page }) => {
	await page.goto('/calculadoras/imss');

	const notice = page.getByRole('link', { name: pendingAuditText, exact: true });
	await expect(notice).toBeVisible();
	await expect(notice).toHaveAttribute('href', issueUrl);
	const box = await notice.boundingBox();
	expect(box?.width).toBeGreaterThan(0);
	expect(box?.height).toBeGreaterThan(0);

	await expect(page.locator('[href*="modalidad10"], [value="modalidad10"]')).toHaveCount(0);
	const publicText = (await page.locator('body').innerText()).replace(pendingAuditText, '');
	expect(publicText).not.toMatch(/modalidad\s*10|modalidad10|\bm10\b|\bpti\b/i);
});

test('IMSS reports a salary below the applicable minimum without crashing', async ({ page }) => {
	await page.goto('/calculadoras/imss');
	await page.getByLabel('Salario diario integrado (SDI)').fill('1');

	await expect(page.getByTestId('cuotas-error')).toBeVisible();
	await expect(page.getByTestId('cuotas-error')).toContainText(/salario mínimo/i);
	await expect(page.getByRole('heading', { name: 'Calculadora IMSS' })).toBeVisible();
});

test('ISR exposes only its fail-closed audit state', async ({ page }) => {
	await page.goto('/calculadoras/isr');

	const state = page.getByTestId('isr-audit-state');
	await expect(state).toBeVisible();
	await expect(state).toContainText('Temporalmente no disponible');
	await expect(state).toContainText('pendientes de verificación documental');
	await expect(page.locator('main').locator('input, select, button, form')).toHaveCount(0);
});

test('calculator landing labels ISR as under audit instead of available', async ({ page }) => {
	await page.goto('/calculadoras');
	const card = page.locator('.card').filter({ has: page.getByRole('heading', { name: 'ISR' }) });

	await expect(card.getByText('En auditoría', { exact: true })).toBeVisible();
	await expect(card.getByRole('link', { name: 'Ver estado de auditoría' })).toBeVisible();
	await expect(card.getByRole('link', { name: 'Abrir calculadora' })).toHaveCount(0);
});
