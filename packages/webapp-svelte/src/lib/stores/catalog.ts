/**
 * Catalog store for reactive data access
 */
import { writable, derived, get } from 'svelte/store';
import { search, paginate, count, getTables } from '$lib/db';

export interface CatalogState {
	loading: boolean;
	error: string | null;
	data: Record<string, unknown>[];
	total: number;
	page: number;
	pageSize: number;
	totalPages: number;
	searchTerm: string;
}

const initialState: CatalogState = {
	loading: false,
	error: null,
	data: [],
	total: 0,
	page: 1,
	pageSize: 25,
	totalPages: 0,
	searchTerm: '',
};

/**
 * Create a catalog store for a specific table
 */
export function createCatalogStore(tableName: string, searchColumns: string[] = []) {
	const store = writable<CatalogState>({ ...initialState });

	async function load(options: { page?: number; pageSize?: number; searchTerm?: string } = {}) {
		store.update((s) => ({ ...s, loading: true, error: null }));

		try {
			const state = get(store);
			const page = options.page ?? state.page;
			const pageSize = options.pageSize ?? state.pageSize;
			const searchTerm = options.searchTerm ?? state.searchTerm;

			let result;

			if (searchTerm && searchColumns.length > 0) {
				result = await search(tableName, searchTerm, searchColumns, {
					page,
					pageSize,
				});
			} else {
				result = await paginate(tableName, {
					page,
					pageSize,
				});
			}

			store.set({
				loading: false,
				error: null,
				data: result.data,
				total: result.total,
				page: result.page,
				pageSize: result.pageSize,
				totalPages: result.totalPages,
				searchTerm,
			});
		} catch (e) {
			store.update((s) => ({
				...s,
				loading: false,
				error: e instanceof Error ? e.message : 'Error loading data',
			}));
		}
	}

	function setPage(page: number) {
		load({ page });
	}

	function setPageSize(pageSize: number) {
		load({ pageSize, page: 1 });
	}

	function setSearch(searchTerm: string) {
		load({ searchTerm, page: 1 });
	}

	function reset() {
		store.set({ ...initialState });
	}

	return {
		subscribe: store.subscribe,
		load,
		setPage,
		setPageSize,
		setSearch,
		reset,
	};
}

/**
 * Database initialization state
 */
export const dbState = writable<{
	initialized: boolean;
	loading: boolean;
	error: string | null;
	tables: string[];
}>({
	initialized: false,
	loading: false,
	error: null,
	tables: [],
});

/**
 * Initialize database and get list of tables
 */
export async function initDb() {
	dbState.update((s) => ({ ...s, loading: true, error: null }));

	try {
		const tables = await getTables();
		dbState.set({
			initialized: true,
			loading: false,
			error: null,
			tables,
		});
		return tables;
	} catch (e) {
		dbState.update((s) => ({
			...s,
			loading: false,
			error: e instanceof Error ? e.message : 'Error initializing database',
		}));
		throw e;
	}
}
