import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { parse } from 'svelte/compiler';

const issueUrl = 'https://github.com/openbancor/catalogmx/issues/97';
const pendingAuditLinkText = 'Modalidad 10/PTI: pendiente de auditoría';
const publicReference = /modalidad\s*10|modalidad10|\bm10\b|\bpti\b/i;
const forbiddenOptionValue = 'modalidad10';
const forbiddenCalculatorName = 'calcularmodalidad10';
const publicAttributeNames = new Set([
	'aria-label',
	'alt',
	'content',
	'href',
	'label',
	'placeholder',
	'title',
	'value'
]);

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

function collectPublicNodes(node, nodes, parents, parent = null) {
	if (!node || typeof node !== 'object') return;
	if (Array.isArray(node)) {
		for (const child of node) collectPublicNodes(child, nodes, parents, parent);
		return;
	}

	if (typeof node.type === 'string') {
		parents.set(node, parent);
		if (Array.isArray(node.attributes)) nodes.push(node);
	}
	for (const [key, value] of Object.entries(node)) {
		if (key !== 'loc' && key !== 'metadata') {
			collectPublicNodes(value, nodes, parents, node);
		}
	}
}

function isInlineExpression(node) {
	return (
		node.type === 'ExpressionTag' ||
		node.type === 'MustacheTag' ||
		node.type === 'RawMustacheTag'
	);
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
	return node.type === 'Element' && node.name === 'a' && hasIssueHref(node) && hasExactPendingAuditLinkText(node);
}

function staticAttributeValue(attribute) {
	if (attribute.type !== 'Attribute' || !Array.isArray(attribute.value)) {
		return null;
	}

	let value = '';
	for (const part of attribute.value) {
		if (part.type === 'Text') {
			value += part.data;
		} else if (isInlineExpression(part)) {
			const expression = staticString(part.expression);
			if (expression === null) return null;
			value += expression;
		} else {
			return null;
		}
	}
	return value;
}

function staticPublicAttributeValue(attribute) {
	return publicAttributeNames.has(attribute.name) ? staticAttributeValue(attribute) : null;
}

function hasStaticHiddenClass(node) {
	const classAttribute = node.attributes?.find(
		(attribute) => attribute.type === 'Attribute' && attribute.name === 'class'
	);
	const className = classAttribute ? staticAttributeValue(classAttribute) : null;
	return className?.split(/\s+/).includes('hidden') ?? false;
}

function hasStaticHiddenAttribute(node) {
	return node.attributes?.some(
		(attribute) => attribute.type === 'Attribute' && attribute.name === 'hidden' && attribute.value === true
	);
}

function hasStaticHiddenStyle(node) {
	const styleAttribute = node.attributes?.find(
		(attribute) => attribute.type === 'Attribute' && attribute.name === 'style'
	);
	const style = styleAttribute ? staticAttributeValue(styleAttribute) : null;
	const normalizedStyle = style?.replace(/\s+/g, '').toLowerCase();
	return normalizedStyle?.includes('display:none') || normalizedStyle?.includes('visibility:hidden');
}

function hasStaticAriaHidden(node) {
	const ariaHiddenAttribute = node.attributes?.find(
		(attribute) => attribute.type === 'Attribute' && attribute.name === 'aria-hidden'
	);
	return ariaHiddenAttribute ? staticAttributeValue(ariaHiddenAttribute)?.toLowerCase() === 'true' : false;
}

function isInElseBranch(node, ifBlock, parents) {
	let current = node;
	while (current && parents.get(current) !== ifBlock) {
		current = parents.get(current);
	}
	return current?.type === 'ElseBlock';
}

function isStaticallyVisibleIssueAnchor(node, parents) {
	if (!isVerifiedIssueAnchor(node)) return false;
	for (let current = node; current; current = parents.get(current)) {
		if (
			current.type === 'Head' ||
			(current.type === 'Element' && current.name === 'template') ||
			hasStaticHiddenClass(current) ||
			hasStaticHiddenAttribute(current) ||
			hasStaticHiddenStyle(current) ||
			hasStaticAriaHidden(current)
		) {
			return false;
		}
		if (current.type === 'IfBlock' && typeof current.expression?.value === 'boolean') {
			const inElseBranch = isInElseBranch(node, current, parents);
			if (current.expression.value === inElseBranch) return false;
		}
	}
	return true;
}

function staticRenderedTextOutsideVerifiedIssueAnchors(node) {
	if (!node || typeof node !== 'object') return '';
	if (node.type === 'Element' && isVerifiedIssueAnchor(node)) return '';
	if (node.type === 'Text') return node.data;
	if (isInlineExpression(node)) return staticString(node.expression) ?? '';
	return (node.children ?? []).map(staticRenderedTextOutsideVerifiedIssueAnchors).join('');
}

function assertPublicRouteContract(source, route) {
	const ast = parse(source);
	const violations = new Set();

	for (const script of [ast.instance, ast.module]) {
		walk(script, (node) => {
			if (node.type === 'Identifier' && isForbiddenCalculatorIdentifier(node.name)) {
				violations.add(`identificador o llamada prohibida: ${node.name}`);
			}

			const value = staticString(node);
			if (value !== null && isForbiddenScriptValue(value)) {
				violations.add('literal o composición de script prohibida');
			}
		});
	}

	const elements = [];
	const parents = new Map();
	collectPublicNodes(ast.html, elements, parents);
	if (publicReference.test(staticRenderedTextOutsideVerifiedIssueAnchors(ast.html))) {
		violations.add('contenido público que ofrece o calcula Modalidad 10/PTI');
	}

	for (const element of elements) {
		if (publicReference.test(staticRenderedTextOutsideVerifiedIssueAnchors(element))) {
			violations.add('contenido público que ofrece o calcula Modalidad 10/PTI');
		}
		if (!isVerifiedIssueAnchor(element)) {
			for (const attribute of element.attributes ?? []) {
				const value = staticPublicAttributeValue(attribute);
				if (value !== null && publicReference.test(value)) {
					violations.add('atributo público que ofrece o enruta Modalidad 10/PTI');
				}
			}
		}
	}

	assert.equal(
		violations.size,
		0,
		`${route.name} incumple el contrato público: ${Array.from(violations).join('; ')}`
	);
	if (route.requiresPendingAuditNotice) {
		assert.ok(
			elements.some((element) => isStaticallyVisibleIssueAnchor(element, parents)),
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
	assert.throws(() =>
		assertPublicRouteContract(`<script module>const calcularModalidad10 = true;</script>${clean}`, route)
	);
	assert.throws(() => assertPublicRouteContract(`<script>const key = 'calcularModalidad' + '10';</script>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<p>M10 disponible</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<p>Modalidad <strong>10</strong> disponible</p>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`Modalidad 10 disponible${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`{@html 'Modalidad 10 disponible'}${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<svelte:head><meta name="description" content="Modalidad 10 disponible" /></svelte:head>${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<CalculatorCard title="Modalidad 10 disponible" />${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<CalculatorCard href="/calculadoras/modalidad10" />${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`{#if true}<p>Otro cálculo</p>{:else}<p>Modalidad 10 disponible</p>{/if}${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<div class="hidden">${honestAnchor}</div>`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<div hidden>${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<template>${honestAnchor}</template>`, route));
	assert.throws(() => assertPublicRouteContract(`<div style="display:none">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div style="visibility: hidden">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div aria-hidden="true">${honestAnchor}</div>`, route));
	assert.throws(() =>
		assertPublicRouteContract(`{#if false}${honestAnchor}{/if}`, route)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<select><option value="modalidad10">Otra modalidad</option></select>${clean}`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<a href="/calculadoras/modalidad10">Otra calculadora</a>${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<a href={'/calculadoras/' + 'modalidad10'}>Otra calculadora</a>${clean}`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<button aria-label="Calcular Modalidad 10">Calcular</button>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<p>{'Modalidad ' + '10 disponible'}</p>${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<p>Modalidad 10 disponible ${honestAnchor}</p>`,
			route
		)
	);
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
