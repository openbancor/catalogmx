import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { parse } from 'svelte/compiler';

const issueUrl = 'https://github.com/openbancor/catalogmx/issues/97';
const prohibitedReference = /modalidad\s*10|modalidad10|calcularModalidad10|m10|\bpti\b/i;
const pendingAuditText = 'pendiente de auditoría';

const routes = [
	{
		name: 'Landing de calculadoras',
		url: new URL('../src/routes/calculadoras/+page.svelte', import.meta.url),
		requiresPendingAuditNotice: false
	},
	{
		name: 'Calculadora IMSS',
		url: new URL('../src/routes/calculadoras/imss/+page.svelte', import.meta.url),
		requiresPendingAuditNotice: true
	}
];

function walk(node, visit) {
	if (!node || typeof node !== 'object') return;
	if (Array.isArray(node)) {
		for (const child of node) walk(child, visit);
		return;
	}

	if (typeof node.type === 'string') visit(node);
	for (const [key, value] of Object.entries(node)) {
		if (key !== 'loc' && key !== 'metadata') walk(value, visit);
	}
}

function hasIssueHref(node) {
	const href = node.attributes?.find((attribute) => attribute.type === 'Attribute' && attribute.name === 'href');
	return (
		href?.value?.length === 1 &&
		href.value[0].type === 'Text' &&
		href.value[0].data === issueUrl
	);
}

function staticString(node) {
	if (node.type === 'Literal' && typeof node.value === 'string') return node.value;
	if (node.type === 'TemplateLiteral' && node.expressions.length === 0) {
		return node.quasis.map((quasi) => quasi.value.cooked).join('');
	}
	if (node.type === 'BinaryExpression' && node.operator === '+') {
		const left = staticString(node.left);
		const right = staticString(node.right);
		return left !== null && right !== null ? left + right : null;
	}
	return null;
}

function isProhibitedIdentifier(name) {
	return /modalidad\s*10|modalidad10|calcularModalidad10|m10/i.test(name) || name.includes('PTI');
}

function hasExactPendingAuditText(node) {
	return (
		node.children?.length === 1 &&
		node.children[0].type === 'Text' &&
		node.children[0].data === pendingAuditText
	);
}

function assertPublicRouteContract(source, route) {
	const ast = parse(source);
	const violations = [];
	let hasPendingAuditIssueLink = false;

	walk(ast, (node) => {
		if (node.type === 'Identifier' && isProhibitedIdentifier(node.name)) {
			violations.push(`identificador prohibido: ${node.name}`);
		}

		if (
			(node.type === 'Literal' && typeof node.value === 'string' && prohibitedReference.test(node.value)) ||
			(node.type === 'TemplateElement' && prohibitedReference.test(node.value.raw))
		) {
			violations.push('literal de script prohibido');
		}

		const value = staticString(node);
		if (value !== null && prohibitedReference.test(value)) {
			violations.push('expresión de script prohibida');
		}

		if (node.type === 'Text' && prohibitedReference.test(node.data)) {
			violations.push('contenido visible que ofrece o calcula Modalidad 10/PTI');
		}

		if (
			node.type === 'Element' &&
			node.name === 'a' &&
			hasIssueHref(node) &&
			hasExactPendingAuditText(node)
		) {
			hasPendingAuditIssueLink = true;
		}
	});

	assert.equal(
		violations.length,
		0,
		`${route.name} incumple el contrato público: ${violations.join('; ')}`
	);
	if (route.requiresPendingAuditNotice) {
		assert.ok(
			hasPendingAuditIssueLink,
			`${route.name} debe enlazar el issue #97 con texto visible "pendiente de auditoría"`
		);
	}
}

function runSelfTests() {
	const route = { name: 'fixture', requiresPendingAuditNotice: true };
	const clean = `<p>Esta modalidad administrativa no está disponible. <a href="${issueUrl}">pendiente de auditoría</a>.</p>`;

	assert.doesNotThrow(() => assertPublicRouteContract(clean, route));
	assert.throws(() => assertPublicRouteContract(`<script>const value = 'modalidad10';</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const value = "modalidad10";</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const calcularM10 = true;</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const PTICalculator = true;</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<p>M10 disponible</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const label = 'M' + '10';</script><p>{label}</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<a href="${issueUrl}">Modalidad 10/PTI pendiente de auditoría</a>`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<script>let suffix = ' adicional';</script><a href="${issueUrl}">pendiente de auditoría{suffix}</a>`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<!-- <a href="${issueUrl}">pendiente de auditoría</a> -->`,
			route
		)
	);
}

runSelfTests();

for (const route of routes) {
	const source = await readFile(fileURLToPath(route.url), 'utf8');
	assertPublicRouteContract(source, route);
}
