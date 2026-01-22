<script lang="ts">
	import { FileText, Plus, X } from 'lucide-svelte';
	import SearchableSelect from './SearchableSelect.svelte';

	interface Regimen {
		code: string;
		description: string;
	}

	interface Props {
		regimenes: Regimen[];
		availableRegimenes: Regimen[];
		embedded?: boolean;
		onchange: (regimenes: Regimen[]) => void;
	}

	let { regimenes, availableRegimenes, embedded = false, onchange }: Props = $props();

	let showAddRegimen = $state(false);

	const unusedRegimenes = $derived(
		availableRegimenes.filter((ar) => !regimenes.some((r) => r.code === ar.code))
	);

	const selectOptions = $derived(
		unusedRegimenes.map((r) => ({ value: r.code, label: `${r.code} - ${r.description}` }))
	);

	function addRegimen(code: string): void {
		const regimen = availableRegimenes.find((r) => r.code === code);
		if (regimen && !regimenes.some((r) => r.code === code)) {
			onchange([...regimenes, { code: regimen.code, description: regimen.description }]);
			showAddRegimen = false;
		}
	}

	function removeRegimen(code: string): void {
		onchange(regimenes.filter((r) => r.code !== code));
	}
</script>

{#snippet content()}
	<div class="space-y-2">
		{#if regimenes.length === 0}
			<p class="text-sm text-slate-500 dark:text-slate-400 italic">Sin régimen fiscal asignado</p>
		{:else}
			{#each regimenes as regimen}
				<div class="flex items-center justify-between gap-2 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg">
					<div class="flex-1 min-w-0">
						<span class="text-xs font-mono text-slate-500 dark:text-slate-400">{regimen.code}</span>
						<p class="text-sm text-slate-700 dark:text-slate-300 truncate">{regimen.description}</p>
					</div>
					<button
						type="button"
						class="p-1 text-slate-400 hover:text-red-500 flex-shrink-0"
						onclick={() => removeRegimen(regimen.code)}
						title="Quitar régimen"
					>
						<X class="h-4 w-4" />
					</button>
				</div>
			{/each}
		{/if}

		{#if showAddRegimen && unusedRegimenes.length > 0}
			<div class="pt-2">
				<SearchableSelect
					options={selectOptions}
					value=""
					placeholder="Buscar régimen..."
					onchange={(code) => {
						if (code) addRegimen(code);
					}}
				/>
			</div>
		{/if}

		{#if unusedRegimenes.length > 0}
			<button
				type="button"
				class="flex items-center gap-1 text-sm text-brand-500 hover:text-brand-600 mt-2"
				onclick={() => {
					showAddRegimen = !showAddRegimen;
				}}
			>
				<Plus class="h-4 w-4" />
				{showAddRegimen ? 'Cancelar' : 'Agregar régimen'}
			</button>
		{/if}
	</div>
{/snippet}

{#if embedded}
	<div class="pt-3 border-t border-slate-200 dark:border-slate-700 mt-3">
		<div class="flex items-center gap-2 mb-2">
			<FileText class="h-4 w-4 text-orange-500" />
			<span class="text-sm font-medium text-slate-700 dark:text-slate-300">Régimen Fiscal</span>
			<span class="text-xs text-slate-400">({regimenes.length})</span>
		</div>
		{@render content()}
	</div>
{:else}
	<div class="card p-6">
		<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
			<FileText class="h-5 w-5 text-orange-500" />
			Régimen Fiscal
			<span class="text-xs font-normal text-slate-400">({regimenes.length})</span>
		</h3>
		{@render content()}
	</div>
{/if}
