<script lang="ts">
	import { ChevronDown, Search, X } from 'lucide-svelte';

	interface Option {
		value: string;
		label: string;
		searchText?: string; // Optional field for custom search text (e.g., includes full name)
	}

	interface Props {
		options: Option[];
		value: string;
		placeholder?: string;
		onchange: (value: string) => void;
	}

	let { options, value, placeholder = 'Seleccionar...', onchange }: Props = $props();

	let isOpen = $state(false);
	let searchQuery = $state('');
	let inputRef: HTMLInputElement | null = $state(null);
	let containerRef: HTMLDivElement | null = $state(null);

	const filteredOptions = $derived(
		searchQuery
			? options.filter((opt) => {
					const searchIn = opt.searchText ?? opt.label.toLowerCase();
					return searchIn.includes(searchQuery.toLowerCase());
				})
			: options
	);

	const selectedOption = $derived(options.find((opt) => opt.value === value));

	function handleSelect(optionValue: string): void {
		onchange(optionValue);
		isOpen = false;
		searchQuery = '';
	}

	function handleKeyDown(e: KeyboardEvent): void {
		if (e.key === 'Escape') {
			isOpen = false;
			searchQuery = '';
		} else if (e.key === 'Enter' && filteredOptions.length === 1) {
			handleSelect(filteredOptions[0].value);
		}
	}

	function handleClickOutside(e: MouseEvent): void {
		if (containerRef && !containerRef.contains(e.target as Node)) {
			isOpen = false;
			searchQuery = '';
		}
	}

	$effect(() => {
		if (isOpen) {
			document.addEventListener('click', handleClickOutside);
			// Focus input when opening
			setTimeout(() => inputRef?.focus(), 10);
		} else {
			document.removeEventListener('click', handleClickOutside);
		}

		return () => {
			document.removeEventListener('click', handleClickOutside);
		};
	});
</script>

<div class="relative" bind:this={containerRef}>
	<!-- Trigger button -->
	<button
		type="button"
		class="input w-full flex items-center justify-between gap-2 text-left"
		onclick={() => {
			isOpen = !isOpen;
		}}
	>
		<span class="truncate {!selectedOption ? 'text-slate-400' : ''}">
			{selectedOption?.label || placeholder}
		</span>
		<ChevronDown class="h-4 w-4 text-slate-400 flex-shrink-0 {isOpen ? 'rotate-180' : ''} transition-transform" />
	</button>

	<!-- Dropdown -->
	{#if isOpen}
		<div class="absolute z-50 mt-1 w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-64 overflow-hidden">
			<!-- Search input -->
			<div class="p-2 border-b border-slate-200 dark:border-slate-700">
				<div class="relative">
					<Search class="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
					<input
						bind:this={inputRef}
						type="text"
						class="w-full pl-8 pr-8 py-1.5 text-sm border border-slate-200 dark:border-slate-600 rounded bg-slate-50 dark:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
						placeholder="Buscar..."
						bind:value={searchQuery}
						onkeydown={handleKeyDown}
					/>
					{#if searchQuery}
						<button
							type="button"
							class="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
							onclick={() => {
								searchQuery = '';
								inputRef?.focus();
							}}
						>
							<X class="h-4 w-4" />
						</button>
					{/if}
				</div>
			</div>

			<!-- Options list -->
			<div class="overflow-y-auto max-h-48">
				{#if filteredOptions.length === 0}
					<div class="px-3 py-2 text-sm text-slate-500 dark:text-slate-400">
						No se encontraron resultados
					</div>
				{:else}
					{#each filteredOptions as option}
						<button
							type="button"
							class="w-full px-3 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-700 {option.value === value ? 'bg-brand-50 dark:bg-brand-900/20 text-brand-600 dark:text-brand-400' : 'text-slate-700 dark:text-slate-300'}"
							onclick={() => handleSelect(option.value)}
						>
							{option.label}
						</button>
					{/each}
				{/if}
			</div>
		</div>
	{/if}
</div>
