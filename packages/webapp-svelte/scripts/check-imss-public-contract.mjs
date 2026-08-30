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
	'action',
	'aria-label',
	'alt',
	'content',
	'formaction',
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
	if (node.type === 'Literal' && ['string', 'number', 'boolean'].includes(typeof node.value)) {
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
	if (node.type === 'ConditionalExpression' && typeof node.test?.value === 'boolean') {
		return staticString(node.test.value ? node.consequent : node.alternate);
	}
	return null;
}

function combineStaticValues(left, right) {
	return left.flatMap((prefix) => right.map((suffix) => prefix + suffix));
}

function staticStringValues(node, bindings = new Map(), seen = new Set()) {
	if (!node) return [];
	if (node.type === 'Identifier' && bindings.has(node.name)) {
		if (seen.has(node.name)) return [];
		const nextSeen = new Set(seen);
		nextSeen.add(node.name);
		return staticStringValues(bindings.get(node.name), bindings, nextSeen);
	}
	if (node.type === 'ConditionalExpression') {
		if (typeof node.test?.value === 'boolean') {
			return staticStringValues(node.test.value ? node.consequent : node.alternate, bindings, seen);
		}
		return [
			...staticStringValues(node.consequent, bindings, seen),
			...staticStringValues(node.alternate, bindings, seen)
		];
	}
	if (node.type === 'TemplateLiteral') {
		let values = [node.quasis[0].value.cooked ?? ''];
		for (let index = 0; index < node.expressions.length; index += 1) {
			const expressionValues = staticStringValues(node.expressions[index], bindings, seen);
			if (expressionValues.length === 0) return [];
			const suffix = node.quasis[index + 1].value.cooked ?? '';
			values = combineStaticValues(values, expressionValues).map((value) => value + suffix);
		}
		return values;
	}
	if (node.type === 'BinaryExpression' && node.operator === '+') {
		return combineStaticValues(
			staticStringValues(node.left, bindings, seen),
			staticStringValues(node.right, bindings, seen)
		);
	}
	if (node.type === 'LogicalExpression') {
		const leftValues = staticStringValues(node.left, bindings, seen);
		const rightValues = staticStringValues(node.right, bindings, seen);
		if (typeof node.left?.value === 'boolean') {
			if (node.operator === '&&') return node.left.value ? rightValues : leftValues;
			if (node.operator === '||') return node.left.value ? leftValues : rightValues;
		}
		return [...leftValues, ...rightValues];
	}
	if (node.type === 'SequenceExpression') {
		return staticStringValues(node.expressions.at(-1), bindings, seen);
	}
	const value = staticString(node);
	return value === null ? [] : [value];
}

function createStaticEvaluator(ast) {
	const bindings = new Map();
	for (const script of [ast.instance, ast.module]) {
		for (const statement of script?.content?.body ?? []) {
			if (statement.type !== 'VariableDeclaration' || statement.kind !== 'const') continue;
			for (const declaration of statement.declarations) {
				if (declaration.id?.type === 'Identifier' && declaration.init) {
					bindings.set(declaration.id.name, declaration.init);
				}
			}
		}
	}
	walk(ast.html, (node) => {
		if (
			node.type === 'ConstTag' &&
			node.expression?.type === 'AssignmentExpression' &&
			node.expression.left?.type === 'Identifier'
		) {
			bindings.set(node.expression.left.name, node.expression.right);
		}
	});
	return (node) => staticStringValues(node, bindings);
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
	return (
		node.type === 'Element' &&
		node.name === 'a' &&
		node.attributes?.length === 2 &&
		node.attributes.some(
			(attribute) =>
				attribute.type === 'Attribute' &&
				attribute.name === 'class' &&
				attribute.value?.length === 1 &&
				attribute.value[0].type === 'Text' &&
				attribute.value[0].data === 'font-medium underline'
		) &&
		hasIssueHref(node) &&
		hasExactPendingAuditLinkText(node)
	);
}

function staticPartValues(parts, evaluateStatic) {
	if (!Array.isArray(parts)) return [];
	let values = [''];
	for (const part of parts) {
		let partValues;
		if (part.type === 'Text') {
			partValues = [part.data];
		} else if (isInlineExpression(part)) {
			partValues = evaluateStatic(part.expression);
		} else {
			return [];
		}
		if (partValues.length === 0) return [];
		values = combineStaticValues(values, partValues);
	}
	return values;
}

function staticAttributeValues(attribute, evaluateStatic) {
	return attribute.type === 'Attribute' ? staticPartValues(attribute.value, evaluateStatic) : [];
}

function staticPublicAttributeValues(attribute, evaluateStatic) {
	return publicAttributeNames.has(attribute.name) ? staticAttributeValues(attribute, evaluateStatic) : [];
}

function hasExactClass(node, name, className) {
	return (
		node?.type === 'Element' &&
		node.name === name &&
		node.attributes?.length === 1 &&
		node.attributes[0].type === 'Attribute' &&
		node.attributes[0].name === 'class' &&
		node.attributes[0].value?.length === 1 &&
		node.attributes[0].value[0].type === 'Text' &&
		node.attributes[0].value[0].data === className
	);
}

function isCanonicalPendingAuditNotice(node, parents) {
	if (!isVerifiedIssueAnchor(node)) return false;
	const paragraph = parents.get(node);
	const alert = parents.get(paragraph);
	const container = parents.get(alert);
	const section = parents.get(container);
	const root = parents.get(section);
	return (
		hasExactClass(paragraph, 'p', 'text-sm text-amber-900 dark:text-amber-300') &&
		hasExactClass(
			alert,
			'div',
			'mt-4 flex items-start gap-2 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800'
		) &&
		hasExactClass(container, 'div', 'max-w-5xl mx-auto px-4 sm:px-6 lg:px-8') &&
		hasExactClass(section, 'section', 'py-8 md:py-12 border-b border-slate-200 dark:border-slate-800') &&
		root?.type === 'Fragment'
	);
}

function staticRenderedTextOutsideVerifiedIssueAnchors(node, evaluateStatic) {
	if (!node || typeof node !== 'object') return '';
	if (Array.isArray(node)) return node.map((child) => staticRenderedTextOutsideVerifiedIssueAnchors(child, evaluateStatic)).join('');
	if (node.type === 'Element' && isVerifiedIssueAnchor(node)) return '';
	if (node.type === 'Text') return node.data;
	if (isInlineExpression(node)) return evaluateStatic(node.expression).join(' ');
	return ['children', 'else', 'fallback', 'pending', 'then', 'catch']
		.map((key) => staticRenderedTextOutsideVerifiedIssueAnchors(node[key], evaluateStatic))
		.join('');
}

function eventHandlerHasPublicReference(attribute, evaluateStatic) {
	const expression =
		attribute.type === 'EventHandler'
			? attribute.expression
			: attribute.type === 'Attribute' && attribute.name.startsWith('on')
				? attribute.value
				: null;
	if (!expression) return false;
	let found = false;
	walk(expression, (node) => {
		if (evaluateStatic(node).some((value) => publicReference.test(value))) found = true;
	});
	return found;
}

function spreadPublicAttributeValues(attribute, evaluateStatic) {
	if (attribute.type !== 'Spread' || attribute.expression?.type !== 'ObjectExpression') return [];
	return attribute.expression.properties.flatMap((property) => {
		if (property.type !== 'Property') return [];
		const names = property.computed
			? evaluateStatic(property.key)
			: [property.key.type === 'Identifier' ? property.key.name : property.key.value];
		return names.some((name) => publicAttributeNames.has(name)) ? evaluateStatic(property.value) : [];
	});
}

function spreadEventHandlerHasPublicReference(attribute, evaluateStatic) {
	if (attribute.type !== 'Spread' || attribute.expression?.type !== 'ObjectExpression') return false;
	return attribute.expression.properties.some((property) => {
		if (property.type !== 'Property') return false;
		const names = property.computed
			? evaluateStatic(property.key)
			: [property.key.type === 'Identifier' ? property.key.name : property.key.value];
		if (!names.some((name) => typeof name === 'string' && name.startsWith('on'))) return false;
		let found = false;
		walk(property.value, (node) => {
			if (evaluateStatic(node).some((value) => publicReference.test(value))) found = true;
		});
		return found;
	});
}

function assertPublicRouteContract(source, route) {
	const ast = parse(source);
	const violations = new Set();
	const evaluateStatic = createStaticEvaluator(ast);

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
	if (publicReference.test(staticRenderedTextOutsideVerifiedIssueAnchors(ast.html, evaluateStatic))) {
		violations.add('contenido público que ofrece o calcula Modalidad 10/PTI');
	}

	for (const element of elements) {
		if (publicReference.test(staticRenderedTextOutsideVerifiedIssueAnchors(element, evaluateStatic))) {
			violations.add('contenido público que ofrece o calcula Modalidad 10/PTI');
		}
		if (!isVerifiedIssueAnchor(element)) {
			for (const attribute of element.attributes ?? []) {
				if (
					staticPublicAttributeValues(attribute, evaluateStatic).some((value) => publicReference.test(value)) ||
					spreadPublicAttributeValues(attribute, evaluateStatic).some((value) => publicReference.test(value)) ||
					eventHandlerHasPublicReference(attribute, evaluateStatic) ||
					spreadEventHandlerHasPublicReference(attribute, evaluateStatic)
				) {
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
			elements.some((element) => isCanonicalPendingAuditNotice(element, parents)),
			`${route.name} debe enlazar el issue #97 con texto visible "${pendingAuditLinkText}"`
		);
	}
}

function runSelfTests() {
	const route = { name: 'fixture', requiresPendingAuditNotice: true };
	const honestAnchor = `<a class="font-medium underline" href="${issueUrl}">${pendingAuditLinkText}</a>`;
	const honestNotice = `<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800"><div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8"><div class="mt-4 flex items-start gap-2 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800"><p class="text-sm text-amber-900 dark:text-amber-300">La modalidad administrativa para personas trabajadoras independientes no está disponible en esta calculadora;${honestAnchor}.</p></div></div></section>`;
	const clean = honestNotice;

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
	assert.throws(() =>
		assertPublicRouteContract(
			`<button onclick={() => location.href = '/calculadoras/modalidad10'}>Ir</button>${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<button on:click={() => location.href = '/calculadoras/modalidad10'}>Ir</button>${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<button {...{ onclick: () => location.href = '/calculadoras/modalidad10' }}>Ir</button>${clean}`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<a {...{ ['href']: '/calculadoras/modalidad10' }}>Ir</a>${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<p>{enabled && 'Modalidad 10 disponible'}</p>${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<p>{('Seguro', 'Modalidad 10 disponible')}</p>${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<p>{@const target = '/calculadoras/modalidad10'}<button onclick={() => location.href = target}>Ir</button></p>${clean}`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<div class="opacity-0">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div style="opacity: 0">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div class="h-0 overflow-hidden">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div class="scale-0">${honestAnchor}</div>`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<button onclick={() => enabled ? location.href = '/seguro' : location.href = '/calculadoras/modalidad10'}>Ir</button>${clean}`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<a {...{ href: '/calculadoras/modalidad10' }}>Ir</a>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<button {...{ formaction: '/calculadoras/modalidad10' }}>Ir</button>${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<style>.audit-hidden { display: none; }</style><div class="audit-hidden">${honestAnchor}</div>`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<div class="sr-only">${honestAnchor}</div>`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<script>const prefix = 'Modalidad '; const suffix = '10 disponible';</script><p>{prefix + suffix}</p>${clean}`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<p>Modalidad <strong>10</strong> disponible</p>${clean}`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<p>{enabled ? 'Seguro' : 'Modalidad 10 disponible'}</p>${clean}`,
			route
		)
	);
	assert.throws(() =>
		assertPublicRouteContract(
			`<CalculatorCard title={enabled ? 'Seguro' : 'Modalidad 10 disponible'} />${clean}`,
			route
		)
	);
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
	assert.throws(() => assertPublicRouteContract(`<div class="invisible">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div class="opacity-0">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div class:hidden={true}>${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div hidden={true}>${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div hidden="hidden">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div hidden="">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<template>${honestAnchor}</template>`, route));
	assert.throws(() => assertPublicRouteContract(`<div style="display:none">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div style="visibility: hidden">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div aria-hidden="true">${honestAnchor}</div>`, route));
	assert.throws(() => assertPublicRouteContract(`<div aria-hidden={true}>${honestAnchor}</div>`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`<div aria-hidden={enabled ? 'false' : 'true'}>${honestAnchor}</div>`,
			route
		)
	);
	assert.throws(() => assertPublicRouteContract(`<div style:display="none">${honestAnchor}</div>`, route));
	assert.throws(() =>
		assertPublicRouteContract(
			`{#if enabled}Seguro{:else}Modalidad 10 disponible{/if}${clean}`,
			route
		)
	);
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
	assert.throws(() => assertPublicRouteContract(`<form action="/calculadoras/modalidad10">Enviar</form>${clean}`, route));
	assert.throws(() => assertPublicRouteContract(`<button formaction="/calculadoras/modalidad10">Enviar</button>${clean}`, route));
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
