<script lang="ts">
	import { base } from '$app/paths';
	import '../app.css';
	import { page } from '$app/stores';
	import { Sun, Moon, Menu, X, Database, CheckCircle, Calculator, Code, Github, Search, Sparkles, Book } from 'lucide-svelte';
	import { onMount } from 'svelte';
	import { initCatalogmxSqlite } from '$lib/catalogmx';

	let { children } = $props();

	let darkMode = $state(false);
	let mobileMenuOpen = $state(false);
	let searchQuery = $state('');
	let sqliteReady = $state(false);

	const navItems = [
		{ href: `${base}/catalogos`, label: 'Catálogos', icon: Database },
		{ href: `${base}/validadores`, label: 'Validadores', icon: CheckCircle },
		{ href: `${base}/generadores`, label: 'Generadores', icon: Sparkles },
		{ href: `${base}/calculadoras`, label: 'Calculadoras', icon: Calculator },
		{ href: `${base}/docs`, label: 'Docs', icon: Book },
	];

	const sectionNav = [
		{
			root: `${base}/catalogos`,
			items: [
				{ label: 'Todos', href: `${base}/catalogos` },
				{ label: 'SAT', href: `${base}/catalogos#sat` },
				{ label: 'SAT Nómina', href: `${base}/catalogos#sat-nomina` },
				{ label: 'INEGI', href: `${base}/catalogos#inegi` },
				{ label: 'Banxico', href: `${base}/catalogos#banxico` },
				{ label: 'SEPOMEX', href: `${base}/catalogos#sepomex` },
				{ label: 'IMSS', href: `${base}/catalogos#imss` },
				{ label: 'México', href: `${base}/catalogos#mexico` },
				{ label: 'IFT', href: `${base}/catalogos#ift` },
				{ label: 'CNBV', href: `${base}/catalogos#cnbv` },
			],
		},
		{
			root: `${base}/validadores`,
			items: [
				{ label: 'Todos', href: `${base}/validadores` },
				{ label: 'RFC', href: `${base}/validadores/rfc` },
				{ label: 'CURP', href: `${base}/validadores/curp` },
				{ label: 'CLABE', href: `${base}/validadores/clabe` },
				{ label: 'NSS', href: `${base}/validadores/nss` },
			],
		},
		{
			root: `${base}/generadores`,
			items: [
				{ label: 'Todos', href: `${base}/generadores` },
				{ label: 'RFC', href: `${base}/generadores/rfc` },
				{ label: 'CURP', href: `${base}/generadores/curp` },
				{ label: 'CLABE', href: `${base}/generadores/clabe` },
			],
		},
		{
			root: `${base}/calculadoras`,
			items: [
				{ label: 'Todas', href: `${base}/calculadoras` },
				{ label: 'ISR', href: `${base}/calculadoras/isr` },
				{ label: 'RESICO', href: `${base}/calculadoras/resico` },
				{ label: 'IVA', href: `${base}/calculadoras/iva` },
				{ label: 'IEPS', href: `${base}/calculadoras/ieps` },
				{ label: 'IMSS', href: `${base}/calculadoras/imss` },
				{ label: 'Costo', href: `${base}/calculadoras/costo-trabajador` },
				{ label: 'Tipo cambio', href: `${base}/calculadoras/tipo-cambio` },
				{ label: 'UDI', href: `${base}/calculadoras/udi` },
				{ label: 'Tasas', href: `${base}/calculadoras/tasas-interes` },
			],
		},
		{
			root: `${base}/docs`,
			items: [
				{ label: 'Inicio', href: `${base}/docs` },
				{ label: 'Instalación', href: `${base}/docs#instalacion` },
				{ label: 'Python', href: `${base}/docs#python` },
				{ label: 'TypeScript', href: `${base}/docs#typescript` },
				{ label: 'Dart', href: `${base}/docs#dart` },
				{ label: 'Recursos', href: `${base}/docs#recursos` },
			],
		},
	];

	function toggleDarkMode() {
		darkMode = !darkMode;
		if (darkMode) {
			document.documentElement.classList.add('dark');
			localStorage.setItem('theme', 'dark');
		} else {
			document.documentElement.classList.remove('dark');
			localStorage.setItem('theme', 'light');
		}
	}

	function isActive(href: string): boolean {
		return $page.url.pathname.startsWith(href);
	}

	function isSubActive(href: string): boolean {
		const [path, hash] = href.split('#');
		if (!($page.url.pathname === path || $page.url.pathname.startsWith(`${path}/`))) {
			return false;
		}
		if (hash) {
			return $page.url.pathname === path && $page.url.hash === `#${hash}`;
		}
		return $page.url.pathname === path || $page.url.pathname.startsWith(`${path}/`);
	}

	const activeSection = $derived(() => sectionNav.find(section => $page.url.pathname.startsWith(section.root)));

	$effect(() => {
		darkMode = document.documentElement.classList.contains('dark');
	});

	onMount(async () => {
		try {
			await initCatalogmxSqlite();
		} finally {
			sqliteReady = true;
		}
	});
</script>

<svelte:head>
	<title>catalogmx - Catálogos y Validadores de México</title>
</svelte:head>

<div class="min-h-screen flex flex-col">
	<!-- Header -->
	<header class="sticky top-0 z-50 border-b border-slate-200 dark:border-slate-700 bg-white/95 dark:bg-slate-900/95 backdrop-blur supports-[backdrop-filter]:bg-white/80 dark:supports-[backdrop-filter]:bg-slate-900/80">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex h-16 items-center justify-between">
				<!-- Logo -->
				<div class="flex items-center gap-8">
					<a href="{base}/" class="flex items-center gap-2 font-semibold text-lg">
						<span class="text-2xl">🇲🇽</span>
						<span class="text-brand-500">catalog</span><span class="text-slate-900 dark:text-white">mx</span>
					</a>

					<!-- Desktop nav -->
					<nav class="hidden md:flex items-center gap-1">
						{#each navItems as item}
							<a
								href={item.href}
								class="nav-link {isActive(item.href) ? 'nav-link-active' : ''}"
							>
								{item.label}
							</a>
						{/each}
					</nav>
				</div>

				<!-- Right side -->
				<div class="flex items-center gap-3">
					<!-- Search (desktop) -->
					<div class="hidden md:flex relative">
						<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
						<input
							type="search"
							placeholder="Buscar..."
							bind:value={searchQuery}
							class="pl-10 pr-4 py-1.5 text-sm rounded-md border border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent w-48 focus:w-64 transition-all"
						/>
					</div>

					<!-- GitHub -->
					<a
						href="https://github.com/openbancor/catalogmx"
						target="_blank"
						rel="noopener noreferrer"
						class="btn-ghost p-2 rounded-md"
						aria-label="GitHub"
					>
						<Github class="h-5 w-5" />
					</a>

					<!-- Dark mode toggle -->
					<button
						onclick={toggleDarkMode}
						class="btn-ghost p-2 rounded-md"
						aria-label={darkMode ? 'Activar modo claro' : 'Activar modo oscuro'}
					>
						{#if darkMode}
							<Sun class="h-5 w-5" />
						{:else}
							<Moon class="h-5 w-5" />
						{/if}
					</button>

					<!-- Mobile menu button -->
					<button
						onclick={() => mobileMenuOpen = !mobileMenuOpen}
						class="md:hidden btn-ghost p-2 rounded-md"
						aria-label="Menú"
					>
						{#if mobileMenuOpen}
							<X class="h-5 w-5" />
						{:else}
							<Menu class="h-5 w-5" />
						{/if}
					</button>
				</div>
			</div>
		</div>

		<!-- Mobile menu -->
		{#if mobileMenuOpen}
			<div class="md:hidden border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
				<div class="px-4 py-3 space-y-1">
					<!-- Mobile search -->
					<div class="relative mb-3">
						<Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
						<input
							type="search"
							placeholder="Buscar..."
							bind:value={searchQuery}
							class="input pl-10"
						/>
					</div>

					{#each navItems as item}
						{@const Icon = item.icon}
						<a
							href={item.href}
							onclick={() => mobileMenuOpen = false}
							class="flex items-center gap-3 px-3 py-2 rounded-md text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 {isActive(item.href) ? 'bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400' : ''}"
						>
							<Icon class="h-5 w-5" />
							{item.label}
						</a>
					{/each}
				</div>
			</div>
		{/if}
	</header>

	{#if activeSection}
		<div class="border-b border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/40">
			<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
				<nav class="flex items-center gap-2 py-2 overflow-x-auto" aria-label="Navegación de sección">
					{#each activeSection.items as item}
						<a
							href={item.href}
							class="subnav-link {isSubActive(item.href) ? 'subnav-link-active' : ''}"
						>
							{item.label}
						</a>
					{/each}
				</nav>
			</div>
		</div>
	{/if}

	<!-- Main content -->
	<main class="flex-1">
		{#if sqliteReady}
			{@render children()}
		{:else}
			<section class="py-16">
				<div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
					<div class="inline-flex items-center gap-3 px-4 py-2 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 text-sm">
						<span class="h-2 w-2 rounded-full bg-brand-500 animate-pulse"></span>
						Cargando base de datos...
					</div>
				</div>
			</section>
		{/if}
	</main>

	<!-- Footer -->
	<footer class="border-t border-slate-200 dark:border-slate-700 py-8 mt-12">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex flex-col md:flex-row justify-between items-center gap-4">
				<div class="text-sm text-slate-500 dark:text-slate-400">
					<span class="font-medium text-slate-700 dark:text-slate-200">catalogmx</span> — Datos oficiales de México
				</div>
				<div class="flex items-center gap-6 text-sm text-slate-500 dark:text-slate-400">
					<span>SAT • INEGI • Banxico • SEPOMEX</span>
					<a href="https://github.com/openbancor/catalogmx" target="_blank" rel="noopener noreferrer" class="hover:text-brand-500">
						GitHub
					</a>
				</div>
			</div>
		</div>
	</footer>
</div>
