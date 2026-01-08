<script lang="ts">
	import {
		createSvelteTable,
		getCoreRowModel,
		getSortedRowModel,
		getFilteredRowModel,
		getPaginationRowModel,
		FlexRender,
		type ColumnDef,
		type SortingState,
		type PaginationState,
	} from '$lib/table';
	import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-svelte';
	import { cn } from '$lib/utils';

	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	type TData = Record<string, any>;

	interface Props {
		data: TData[];
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		columns: ColumnDef<any, any>[];
		pageSize?: number;
		searchable?: boolean;
		searchPlaceholder?: string;
	}

	let { data, columns, pageSize = 25, searchable = true, searchPlaceholder = 'Buscar...' }: Props = $props();

	let sorting = $state<SortingState>([]);
	let globalFilter = $state('');
	let paginationPageSize = $state(pageSize);
	let paginationPageIndex = $state(0);

	const pagination = $derived<PaginationState>({
		pageIndex: paginationPageIndex,
		pageSize: paginationPageSize,
	});

	const table = createSvelteTable({
		get data() { return data; },
		get columns() { return columns; },
		state: {
			get sorting() { return sorting; },
			get globalFilter() { return globalFilter; },
			get pagination() { return pagination; },
		},
		onSortingChange: (updater) => {
			sorting = typeof updater === 'function' ? updater(sorting) : updater;
		},
		onGlobalFilterChange: (updater) => {
			globalFilter = typeof updater === 'function' ? updater(globalFilter) : updater;
		},
		onPaginationChange: (updater) => {
			const newPagination = typeof updater === 'function' ? updater(pagination) : updater;
			paginationPageIndex = newPagination.pageIndex;
			paginationPageSize = newPagination.pageSize;
		},
		getCoreRowModel: getCoreRowModel(),
		getSortedRowModel: getSortedRowModel(),
		getFilteredRowModel: getFilteredRowModel(),
		getPaginationRowModel: getPaginationRowModel(),
	});

	const pageCount = $derived(table.getPageCount());
	const currentPage = $derived(pagination.pageIndex + 1);
	const totalRows = $derived(table.getFilteredRowModel().rows.length);
</script>

<div class="space-y-4">
	<!-- Search and info -->
	<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
		{#if searchable}
			<input
				type="search"
				placeholder={searchPlaceholder}
				bind:value={globalFilter}
				class="input max-w-sm"
			/>
		{/if}
		<p class="text-sm text-slate-500 dark:text-slate-400">
			{totalRows.toLocaleString('es-MX')} registro{totalRows !== 1 ? 's' : ''}
		</p>
	</div>

	<!-- Table -->
	<div class="overflow-x-auto border border-slate-200 dark:border-slate-700 rounded-lg">
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
							No se encontraron resultados
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
					value={paginationPageSize}
					onchange={(e) => {
						paginationPageSize = Number(e.currentTarget.value);
						paginationPageIndex = 0;
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
					onclick={() => table.setPageIndex(0)}
					disabled={!table.getCanPreviousPage()}
				>
					<ChevronsLeft class="h-4 w-4" />
				</button>
				<button
					class="btn btn-ghost p-2"
					onclick={() => table.previousPage()}
					disabled={!table.getCanPreviousPage()}
				>
					<ChevronLeft class="h-4 w-4" />
				</button>

				<span class="px-4 text-sm text-slate-600 dark:text-slate-400">
					Página {currentPage} de {pageCount}
				</span>

				<button
					class="btn btn-ghost p-2"
					onclick={() => table.nextPage()}
					disabled={!table.getCanNextPage()}
				>
					<ChevronRight class="h-4 w-4" />
				</button>
				<button
					class="btn btn-ghost p-2"
					onclick={() => table.setPageIndex(pageCount - 1)}
					disabled={!table.getCanNextPage()}
				>
					<ChevronsRight class="h-4 w-4" />
				</button>
			</div>
		</div>
	{/if}
</div>
