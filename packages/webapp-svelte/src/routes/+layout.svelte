<script lang="ts">
	import '../app.css';
	import { page } from '$app/stores';
	import { Sun, Moon, Menu, X, Database, CheckCircle, Calculator, Code, Github, Search } from 'lucide-svelte';

	let { children } = $props();

	let darkMode = $state(false);
	let mobileMenuOpen = $state(false);
	let searchQuery = $state('');

	const navItems = [
		{ href: '/catalogos', label: 'Catálogos', icon: Database },
		{ href: '/validadores', label: 'Validadores', icon: CheckCircle },
		{ href: '/calculadoras', label: 'Calculadoras', icon: Calculator },
		{ href: '/api', label: 'API', icon: Code },
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

	$effect(() => {
		darkMode = document.documentElement.classList.contains('dark');
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
					<a href="/" class="flex items-center gap-2 font-semibold text-lg">
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

	<!-- Main content -->
	<main class="flex-1">
		{@render children()}
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
