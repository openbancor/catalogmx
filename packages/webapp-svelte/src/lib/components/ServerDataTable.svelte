<script lang="ts">
	import {
		createSvelteTable,
		getCoreRowModel,
		getSortedRowModel,
		FlexRender,
		type ColumnDef,
		type SortingState,
	} from '$lib/table';
	import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, ArrowUpDown, ArrowUp, ArrowDown, Loader2 } from 'lucide-svelte';
	import { cn } from '$lib/utils';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	type TData = Record<string, any>;

	interface Props {
		data: TData[];
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		columns: ColumnDef<any, any>[];
		pageSize?: number;
		totalRows: number;
		currentPage: number;
		loading?: boolean;
		searchable?: boolean;
		searchPlaceholder?: string;
		searchValue?: string;
		onPageChange: (page: number) => void;
		onPageSizeChange?: (size: number) => void;
		onSearch?: (term: string) => void;
	}

	let {
		data,
		columns,
		pageSize = 25,
		totalRows,
		currentPage,
		loading = false,
		searchable = true,
		searchPlaceholder = 'Buscar...',
		searchValue = '',
		onPageChange,
		onPageSizeChange,
		onSearch,
	}: Props = $props();

	let sorting = $state<SortingState>([]);
	let searchInput = $state(searchValue);
	let searchTimeout: ReturnType<typeof setTimeout> | null = null;

	const table = createSvelteTable({
		get data() { return data; },
		get columns() { return columns; },
		state: {
			get sorting() { return sorting; },
		},
		onSortingChange: (updater) => {
			sorting = typeof updater === 'function' ? updater(sorting) : updater;
		},
		getCoreRowModel: getCoreRowModel(),
		getSortedRowModel: getSortedRowModel(),
		manualPagination: true,
	});

	const pageCount = $derived(Math.ceil(totalRows / pageSize));
	const canPreviousPage = $derived(currentPage > 1);
	const canNextPage = $derived(currentPage < pageCount);

	function handleSearch(value: string) {
		if (searchTimeout) clearTimeout(searchTimeout);
		searchTimeout = setTimeout(() => {
			if (onSearch) {
				onSearch(value);
			}
		}, 300);
	}

	$effect(() => {
		handleSearch(searchInput);
	});
</script>

<div class="space-y-4">
	<!-- Search and info -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		{#if searchable && onSearch}
			<input
				type="search"
				placeholder={searchPlaceholder}
				bind:value={searchInput}
				class="input max-w-sm"
			/>
		{/if}
		<p class="text-sm text-slate-500 dark:text-slate-400">
			{#if loading}
				<span class="animate-pulse">Cargando...</span>
			{:else}
				{totalRows.toLocaleString('es-MX')} registro{totalRows !== 1 ? 's' : ''}
			{/if}
		</p>
	</div>

	<!-- Table -->
	<div class="overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-lg relative">
		{#if loading}
			<div class="absolute inset-0 bg-white/50 dark:bg-slate-900/50 flex items-center justify-center z-10">
				<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			</div>
		{/if}
		<table class="data-table">
			<thead>
				{#each table.getHeaderGroups() as headerGroup}
					<tr>
						{#each headerGroup.headers as header}
							<th
								class={cn(
									header.column.getCanSort() && 'cursor-pointer select-none hover:bg-slate-100 dark:hover:bg-slate-700'
								)}
								onclick={header.column.getToggleSortingHandler()}
							>
								<div class="flex items-center gap-2">
									{#if !header.isPlaceholder}
										<FlexRender
											content={header.column.columnDef.header}
											context={header.getContext()}
										/>
									{/if}
									{#if header.column.getCanSort()}
										{#if header.column.getIsSorted() === 'asc'}
											<ArrowUp class="h-4 w-4 text-brand-500" />
										{:else if header.column.getIsSorted() === 'desc'}
											<ArrowDown class="h-4 w-4 text-brand-500" />
										{:else}
											<ArrowUpDown class="h-4 w-4 text-slate-300 dark:text-slate-600" />
										{/if}
									{/if}
								</div>
							</th>
						{/each}
					</tr>
				{/each}
			</thead>
			<tbody>
				{#each table.getRowModel().rows as row}
					<tr>
						{#each row.getVisibleCells() as cell}
							<td>
								<FlexRender
									content={cell.column.columnDef.cell}
									context={cell.getContext()}
								/>
							</td>
						{/each}
					</tr>
				{:else}
					<tr>
						<td colspan={columns.length} class="text-center py-8 text-slate-500 dark:text-slate-400">
							{#if loading}
								Cargando datos...
							{:else}
								No se encontraron resultados
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<!-- Pagination -->
	{#if pageCount > 1}
		<div class="flex flex-col sm:flex-row items-center justify-between gap-4">
			<div class="flex items-center gap-2">
				<span class="text-sm text-slate-600 dark:text-slate-400">
					Filas por página:
				</span>
				<select
					class="input w-20 py-1 text-sm"
					value={pageSize}
					onchange={(e) => {
						if (onPageSizeChange) {
							onPageSizeChange(Number(e.currentTarget.value));
						}
					}}
				>
					{#each [10, 25, 50, 100] as size}
						<option value={size}>{size}</option>
					{/each}
				</select>
			</div>

			<div class="flex items-center gap-1">
				<button
					class="btn btn-ghost p-2"
					onclick={() => onPageChange(1)}
					disabled={!canPreviousPage || loading}
				>
					<ChevronsLeft class="h-4 w-4" />
				</button>
				<button
					class="btn btn-ghost p-2"
					onclick={() => onPageChange(currentPage - 1)}
					disabled={!canPreviousPage || loading}
				>
					<ChevronLeft class="h-4 w-4" />
				</button>

				<span class="px-4 text-sm text-slate-600 dark:text-slate-400">
					Página {currentPage} de {pageCount.toLocaleString('es-MX')}
				</span>

				<button
					class="btn btn-ghost p-2"
					onclick={() => onPageChange(currentPage + 1)}
					disabled={!canNextPage || loading}
				>
					<ChevronRight class="h-4 w-4" />
				</button>
				<button
					class="btn btn-ghost p-2"
					onclick={() => onPageChange(pageCount)}
					disabled={!canNextPage || loading}
				>
					<ChevronsRight class="h-4 w-4" />
				</button>
			</div>
		</div>
	{/if}
</div>
