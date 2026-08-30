import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { parse } from 'svelte/compiler';

const issueUrl = 'https://github.com/openbancor/catalogmx/issues/97';
const pendingAuditLinkText = 'Modalidad 10/PTI: pendiente de auditoría';
const publicReference = /modalidad\s*10|modalidad10|\bm10\b|\bpti\b/i;
const forbiddenOptionValue = 'modalidad10';
const forbiddenCalculatorName = 'calcularmodalidad10';

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

function staticString(node) {
	if (!node) return null;
	if (node.type === 'Literal' && ['string', 'number'].includes(typeof node.value)) {
		return String(node.value);
	}
	if (node.type === 'TemplateLiteral') {
		let value = node.quasis[0].value.cooked ?? '';
		for (let index = 0; index < node.expressions.length; index += 1) {
			const expression = staticString(node.expressions[index]);
			if (expression === null) return null;
			value += expression + (node.quasis[index + 1].value.cooked ?? '');
		}
		return value;
	}
	if (node.type === 'BinaryExpression' && node.operator === '+') {
		const left = staticString(node.left);
		const right = staticString(node.right);
		return left !== null && right !== null ? left + right : null;
	}
	return null;
}

function isForbiddenScriptValue(value) {
	const normalized = value.toLowerCase();
	return (
		normalized === forbiddenOptionValue ||
		normalized === forbiddenCalculatorName ||
		publicReference.test(value)
	);
}

function isForbiddenCalculatorIdentifier(name) {
	const normalized = name.toLowerCase();
	return normalized === forbiddenOptionValue || normalized === forbiddenCalculatorName;
}

function collectElements(node, parentElement, elements, parents) {
	if (!node || typeof node !== 'object') return;
	if (Array.isArray(node)) {
		for (const child of node) collectElements(child, parentElement, elements, parents);
		return;
	}

	const currentElement = node.type === 'Element' ? node : parentElement;
	if (node.type === 'Element') {
		elements.push(node);
		parents.set(node, parentElement);
	}
	for (const child of node.children ?? []) {
		collectElements(child, currentElement, elements, parents);
	}
}

function staticRenderedText(node) {
	if (!node || typeof node !== 'object') return '';
	if (node.type === 'Text') return node.data;
	if (node.type === 'ExpressionTag') return staticString(node.expression) ?? '';
	return (node.children ?? []).map(staticRenderedText).join('');
}

function hasIssueHref(node) {
	const href = node.attributes?.find((attribute) => attribute.type === 'Attribute' && attribute.name === 'href');
	return (
		href?.value?.length === 1 &&
		href.value[0].type === 'Text' &&
		href.value[0].data === issueUrl
	);
}

function hasExactPendingAuditLinkText(node) {
	return (
		node.children?.length === 1 &&
		node.children[0].type === 'Text' &&
		node.children[0].data === pendingAuditLinkText
	);
}

function isVerifiedIssueAnchor(node) {
	return node.name === 'a' && hasIssueHref(node) && hasExactPendingAuditLinkText(node);
}

function hasPublicReferenceDescendant(node) {
	const elements = [];
	collectElements(node.children, null, elements, new Map());
	return elements.some((element) => publicReference.test(staticRenderedText(element)));
}

function isWithinVerifiedIssueAnchor(node, parents) {
	for (let current = node; current; current = parents.get(current)) {
		if (isVerifiedIssueAnchor(current)) return true;
	}
	return false;
}

function assertPublicRouteContract(source, route) {
	const ast = parse(source);
	const violations = new Set();

	walk(ast.instance, (node) => {
		if (node.type === 'Identifier' && isForbiddenCalculatorIdentifier(node.name)) {
			violations.add(`identificador o llamada prohibida: ${node.name}`);
		}

		const value = staticString(node);
		if (value !== null && isForbiddenScriptValue(value)) {
			violations.add('literal o composición de script prohibida');
		}
	});

	const elements = [];
	const parents = new Map();
	collectElements(ast.html.children, null, elements, parents);

	for (const element of elements) {
		if (
			publicReference.test(staticRenderedText(element)) &&
			!hasPublicReferenceDescendant(element) &&
			!isWithinVerifiedIssueAnchor(element, parents)
		) {
			violations.add('contenido público que ofrece o calcula Modalidad 10/PTI');
		}
	}

	assert.equal(
		violations.size,
		0,
		`${route.name} incumple el contrato público: ${Array.from(violations).join('; ')}`
	);
	if (route.requiresPendingAuditNotice) {
		assert.ok(
			elements.some(isVerifiedIssueAnchor),
			`${route.name} debe enlazar el issue #97 con texto visible "${pendingAuditLinkText}"`
		);
	}
}

function runSelfTests() {
	const route = { name: 'fixture', requiresPendingAuditNotice: true };
	const honestAnchor = `<a href="${issueUrl}">${pendingAuditLinkText}</a>`;
	const clean = `<p>Esta modalidad administrativa no está disponible. ${honestAnchor}.</p>`;
	const honestNotice = `<p>${honestAnchor}</p>`;

	assert.doesNotThrow(() => assertPublicRouteContract(clean, route));
	assert.doesNotThrow(() => assertPublicRouteContract(honestNotice, route));
	assert.doesNotThrow(() => assertPublicRouteContract(`<script>const item10 = true; const form10 = true;</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const value = 'modalidad10';</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const value = "modalidad10";</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const calcularModalidad10 = true;</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const key = 'calcularModalidad' + '10';</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<p>M10 disponible</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<p>Modalidad <strong>10</strong> disponible</p>${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<section><p>Modalidad <strong>10</strong> disponible y actualizada.</p><a href="${issueUrl}">pendiente de auditoría</a></section>`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<section><p>Modalidad <strong>10</strong> disponible y actualizada.</p>${honestAnchor}</section>`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<script>const label = 'M' + '10';</script><p>{label}</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<script>const label = \`Modalidad \${10}\`;</script><p>{label}</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<a href="${issueUrl}">Modalidad 10/PTI pendiente de auditoría</a>`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<script>let suffix = ' adicional';</script><a href="${issueUrl}">${pendingAuditLinkText}{suffix}</a>`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<!-- <a href="${issueUrl}">${pendingAuditLinkText}</a> -->`,
			route
		)
	);
}

runSelfTests();

for (const route of routes) {
	const source = await readFile(fileURLToPath(route.url), 'utf8');
	assertPublicRouteContract(source, route);
}
