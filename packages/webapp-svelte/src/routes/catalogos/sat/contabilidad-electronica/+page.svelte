<script lang="ts">
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { ChevronRight, Search, Loader2, AlertCircle, Layers } from 'lucide-svelte';
	import TreeView from '$lib/components/TreeView.svelte';
	import { query } from '$lib/db';

	type VersionKey = '2024-01-22' | '2026-01-13';

	interface CodigoAgrupadorRow {
		codigo: string;
		nombre: string;
		nivel: number | null;
	}

	interface TreeNode {
		id: string;
		label: string;
		nivel: number | null;
		children?: TreeNode[];
		hasChildren?: boolean;
	}

	const versions: { value: VersionKey; label: string }[] = [
		{ value: '2026-01-13', label: 'RMF 2026 (13-ene-2026)' },
		{ value: '2024-01-22', label: 'RMF 2024 (22-ene-2024)' },
	];

	let version = $state<VersionKey>('2026-01-13');
	let data = $state<CodigoAgrupadorRow[]>([]);
	let tree = $state<TreeNode[]>([]);
	let filteredTree = $state<TreeNode[]>([]);
	let selectedId = $state<string | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let searchQuery = $state('');
	let nivelFilter = $state<'all' | 'grupo' | '1' | '2'>('all');
	let expandedIds = $state(new Set<string>());
	let byCodigo = $state(new Map<string, CodigoAgrupadorRow>());
	let matchCount = $state(0);

	function tableForVersion(ver: VersionKey): string {
		return ver === '2024-01-22'
			? 'sat_contabilidad_electronica_codigo_agrupador_2024'
			: 'sat_contabilidad_electronica_codigo_agrupador_2026';
	}

	function buildTree(rows: CodigoAgrupadorRow[]): TreeNode[] {
		const roots: TreeNode[] = [];
		let currentRoot: TreeNode | null = null;
		let currentLevel1: TreeNode | null = null;

		for (const row of rows) {
			const node: TreeNode = {
				id: row.codigo,
				label: row.nombre,
				nivel: row.nivel ?? null,
			};

			if (row.nivel == null) {
				roots.push(node);
				currentRoot = node;
				currentLevel1 = null;
				continue;
			}

			if (row.nivel === 1) {
				if (currentRoot) {
					(currentRoot.children ??= []).push(node);
					currentRoot.hasChildren = true;
				} else {
					roots.push(node);
				}
				currentLevel1 = node;
				continue;
			}

			if (row.nivel === 2) {
				if (currentLevel1) {
					(currentLevel1.children ??= []).push(node);
					currentLevel1.hasChildren = true;
				} else if (currentRoot) {
					(currentRoot.children ??= []).push(node);
					currentRoot.hasChildren = true;
				} else {
					roots.push(node);
				}
				continue;
			}

			if (currentLevel1) {
				(currentLevel1.children ??= []).push(node);
				currentLevel1.hasChildren = true;
			} else if (currentRoot) {
				(currentRoot.children ??= []).push(node);
				currentRoot.hasChildren = true;
			} else {
				roots.push(node);
			}
		}

		return roots;
	}

	function removeAccents(value: string): string {
		return value.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
	}

	function isNivelMatch(node: TreeNode): boolean {
		if (nivelFilter === 'all') return true;
		if (nivelFilter === 'grupo') return node.nivel == null;
		return node.nivel?.toString() === nivelFilter;
	}

	function filterTree(nodes: TreeNode[], queryText: string) {
		const normalized = removeAccents(queryText.toLowerCase());
		const expanded = new Set<string>();
		let matches = 0;

		const walk = (items: TreeNode[]): TreeNode[] => {
			const result: TreeNode[] = [];
			for (const item of items) {
				const idNormalized = removeAccents(item.id.toLowerCase());
				const labelNormalized = removeAccents(item.label.toLowerCase());
				const itemMatch =
					isNivelMatch(item) &&
					(idNormalized.includes(normalized) || labelNormalized.includes(normalized));
				const children = item.children ? walk(item.children) : [];
				if (itemMatch || children.length > 0) {
					if (children.length > 0) {
						expanded.add(item.id);
					}
					if (itemMatch) matches += 1;
					result.push({
						...item,
						children,
						hasChildren: children.length > 0 || item.hasChildren,
					});
				}
			}
			return result;
		};

		return { nodes: walk(nodes), expanded, matches };
	}

	function expandAll(nodes: TreeNode[]) {
		const expanded = new Set<string>();
		const walk = (items: TreeNode[]) => {
			for (const item of items) {
				if (item.children && item.children.length > 0) {
					expanded.add(item.id);
					walk(item.children);
				}
			}
		};
		walk(nodes);
		expandedIds = expanded;
	}

	function collapseAll() {
		expandedIds = new Set<string>();
	}

	async function loadData() {
		try {
			loading = true;
			error = null;
			selectedId = null;
			searchQuery = '';
			expandedIds = new Set<string>();

			const table = tableForVersion(version);
			const result = await query<CodigoAgrupadorRow>(
				`SELECT codigo, nombre, nivel FROM ${table} ORDER BY rowid`
			);
			data = result;
			byCodigo = new Map(result.map((row) => [row.codigo, row]));
			tree = buildTree(result);
			filteredTree = tree;
			matchCount = 0;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading codigo agrupador data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});

	$: if (searchQuery.trim() || nivelFilter !== 'all') {
		const { nodes, expanded, matches } = filterTree(tree, searchQuery.trim());
		filteredTree = nodes;
		expandedIds = expanded;
		matchCount = matches;
	} else {
		filteredTree = tree;
		matchCount = 0;
	}

	$: selectedItem = selectedId ? byCodigo.get(selectedId) : null;
</script>

<svelte:head>
	<title>Catálogo de Cuentas (Código Agrupador SAT) - catalogmx</title>
	<meta
		name="description"
		content="Catálogo del código agrupador de cuentas del SAT para Contabilidad Electrónica (Anexo 24)."
	/>
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catálogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Contabilidad Electrónica</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<Layers class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Código Agrupador de Cuentas (Anexo 24)
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Catálogo oficial del SAT para la Contabilidad Electrónica, presentado como árbol jerárquico.
				</p>
			</div>
		</div>
	</div>

	<!-- Controls -->
	<div class="grid gap-4 lg:grid-cols-[1fr_auto_auto] items-center mb-6">
		<div class="relative">
			<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
			<input
				type="search"
				class="w-full pl-10 pr-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
				placeholder="Buscar por código o descripción..."
				bind:value={searchQuery}
			/>
		</div>
		<div class="flex items-center gap-3">
			<label class="text-sm text-slate-500 dark:text-slate-400">Nivel</label>
			<select
				class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
				bind:value={nivelFilter}
			>
				<option value="all">Todos</option>
				<option value="grupo">Grupos</option>
				<option value="1">Nivel 1</option>
				<option value="2">Nivel 2</option>
			</select>
		</div>
		<div class="flex items-center gap-3">
			<label class="text-sm text-slate-500 dark:text-slate-400">Versión</label>
			<select
				class="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm"
				bind:value={version}
				onchange={loadData}
			>
				{#each versions as v}
					<option value={v.value}>{v.label}</option>
				{/each}
			</select>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-4 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total de cuentas</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Coincidencias</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{searchQuery.trim() ? matchCount.toLocaleString('es-MX') : '—'}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Navegación</p>
			<div class="flex gap-2">
				<button class="btn btn-secondary text-xs" onclick={() => expandAll(filteredTree)}>
					Expandir
				</button>
				<button class="btn btn-secondary text-xs" onclick={collapseAll}>
					Colapsar
				</button>
			</div>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Fuente</p>
			<p class="text-sm font-semibold text-slate-900 dark:text-white">
				Anexo 24 RMF
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catálogo desde SQLite...</span>
		</div>
	{:else if error}
		<div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
			<div class="flex items-start gap-3">
				<AlertCircle class="h-5 w-5 text-red-500 mt-0.5" />
				<div>
					<p class="font-medium text-red-800 dark:text-red-200">Error al cargar datos</p>
					<p class="text-sm text-red-600 dark:text-red-300 mt-1">{error}</p>
					<button onclick={loadData} class="btn btn-secondary mt-3 text-sm">
						Reintentar
					</button>
				</div>
			</div>
		</div>
	{:else}
		<div class="grid gap-6 lg:grid-cols-[minmax(0,2fr)_minmax(0,1fr)]">
			<div class="card p-4">
				<TreeView
					items={filteredTree}
					bind:expandedIds
					{selectedId}
					onSelect={(item: TreeNode) => (selectedId = item.id)}
					renderLabel={(item: TreeNode) => item.label}
					renderMeta={(item: TreeNode) => (item.nivel ? `Nivel ${item.nivel}` : 'Grupo')}
				/>
			</div>
			<div class="space-y-4">
				<div class="card p-4">
					<h2 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">
						Detalle de cuenta
					</h2>
					{#if selectedItem}
						<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
							<div>
								<span class="text-xs uppercase text-slate-400">Código</span>
								<div class="font-mono text-slate-900 dark:text-white">{selectedItem.codigo}</div>
							</div>
							<div>
								<span class="text-xs uppercase text-slate-400">Nombre</span>
								<div class="text-slate-900 dark:text-white">{selectedItem.nombre}</div>
							</div>
							<div>
								<span class="text-xs uppercase text-slate-400">Nivel</span>
								<div class="text-slate-900 dark:text-white">
									{selectedItem.nivel ?? 'Grupo'}
								</div>
							</div>
						</div>
					{:else}
						<p class="text-sm text-slate-500 dark:text-slate-400">
							Selecciona una cuenta en el árbol para ver sus detalles.
						</p>
					{/if}
				</div>
				<div class="card p-4">
					<h2 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">
						Acerca del catálogo
					</h2>
					<p class="text-sm text-slate-600 dark:text-slate-300">
						El código agrupador es la correspondencia oficial entre el catálogo de cuentas del contribuyente
						y el catálogo SAT para la Contabilidad Electrónica (Anexo 24). Esta vista muestra la estructura
						jerárquica por niveles.
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
