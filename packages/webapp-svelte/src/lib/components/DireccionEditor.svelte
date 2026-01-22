<script lang="ts">
	import { MapPin, Copy, ChevronDown } from 'lucide-svelte';
	import { query } from '$lib/db';

	interface Direccion {
		cp: string;
		colonia: string;
		municipio: string;
		estado: string;
		calle: string;
		numero: string;
	}

	interface ColoniaOption {
		asentamiento: string;
		municipio: string;
		estado: string;
	}

	interface Props {
		direccion: Direccion;
		title?: string;
		copied?: boolean;
		onchange: (direccion: Direccion) => void;
		onCopy?: (text: string) => void;
	}

	let { direccion, title = 'Dirección', copied = false, onchange, onCopy }: Props = $props();

	// Available colonias for the current CP
	let colonias = $state<ColoniaOption[]>([]);
	let loadingColonias = $state(false);

	function formatAddress(): string {
		const parts = [];
		if (direccion.calle) {
			parts.push(`${direccion.calle}${direccion.numero ? ' ' + direccion.numero : ''}`);
		}
		if (direccion.colonia) parts.push(direccion.colonia);
		if (direccion.municipio) parts.push(direccion.municipio);
		if (direccion.estado) parts.push(direccion.estado);
		if (direccion.cp) parts.push(`C.P. ${direccion.cp}`);
		return parts.join(', ');
	}

	async function lookupPostalCode(cp: string): Promise<void> {
		if (cp.length !== 5) {
			colonias = [];
			return;
		}

		loadingColonias = true;
		try {
			const results = await query<ColoniaOption>(
				`SELECT asentamiento, municipio, estado FROM codigos_postales WHERE cp = '${cp}' ORDER BY asentamiento`
			);

			colonias = results;

			if (results.length > 0) {
				// Use first colonia by default
				const { asentamiento, municipio, estado } = results[0];
				onchange({
					...direccion,
					cp,
					colonia: asentamiento,
					municipio,
					estado
				});
			}
		} catch (error) {
			console.error('Error looking up postal code:', error);
			colonias = [];
		} finally {
			loadingColonias = false;
		}
	}

	function selectColonia(asentamiento: string): void {
		const selected = colonias.find(c => c.asentamiento === asentamiento);
		if (selected) {
			onchange({
				...direccion,
				colonia: selected.asentamiento,
				municipio: selected.municipio,
				estado: selected.estado
			});
		}
	}

	function updateField(field: keyof Direccion, value: string): void {
		onchange({ ...direccion, [field]: value });
	}

	// Load colonias when CP changes externally (e.g., initial load)
	$effect(() => {
		if (direccion.cp?.length === 5 && colonias.length === 0) {
			loadColoniasOnly(direccion.cp);
		}
	});

	async function loadColoniasOnly(cp: string): Promise<void> {
		try {
			const results = await query<ColoniaOption>(
				`SELECT asentamiento, municipio, estado FROM codigos_postales WHERE cp = '${cp}' ORDER BY asentamiento`
			);
			colonias = results;

			// If current colonia is not in the list, select the first one
			if (results.length > 0) {
				const currentColoniaExists = results.some(c => c.asentamiento === direccion.colonia);
				if (!currentColoniaExists) {
					const { asentamiento, municipio, estado } = results[0];
					onchange({
						...direccion,
						colonia: asentamiento,
						municipio,
						estado
					});
				}
			}
		} catch (error) {
			console.error('Error loading colonias:', error);
		}
	}
</script>

<div class="card p-6">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
			<MapPin class="h-5 w-5 text-red-500" />
			{title}
			<span class="text-xs font-normal text-slate-400">(editable)</span>
		</h3>
		{#if onCopy}
			<button
				class="text-brand-500 hover:text-brand-600 flex items-center gap-1 text-sm"
				onclick={() => onCopy?.(formatAddress())}
			>
				<Copy class="h-4 w-4" />
				{copied ? '✓' : 'copiar'}
			</button>
		{/if}
	</div>
	<div class="space-y-3">
		<div class="grid grid-cols-3 gap-2">
			<div class="col-span-2">
				<label class="text-sm text-slate-600 dark:text-slate-400">Calle</label>
				<input
					type="text"
					class="input mt-1"
					value={direccion.calle}
					oninput={(e) => updateField('calle', e.currentTarget.value)}
				/>
			</div>
			<div>
				<label class="text-sm text-slate-600 dark:text-slate-400">Número</label>
				<input
					type="text"
					class="input mt-1"
					value={direccion.numero}
					oninput={(e) => updateField('numero', e.currentTarget.value)}
				/>
			</div>
		</div>
		<div>
			<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
				Colonia
				{#if colonias.length > 1}
					<span class="text-xs text-slate-400">({colonias.length} disponibles)</span>
				{/if}
			</label>
			{#if colonias.length > 1}
				<div class="relative mt-1">
					<select
						class="input w-full appearance-none pr-8"
						onchange={(e) => selectColonia(e.currentTarget.value)}
					>
						{#each colonias as colonia}
							<option value={colonia.asentamiento} selected={colonia.asentamiento === direccion.colonia}>{colonia.asentamiento}</option>
						{/each}
					</select>
					<ChevronDown class="absolute right-2 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
				</div>
			{:else}
				<input
					type="text"
					class="input mt-1"
					value={direccion.colonia}
					oninput={(e) => updateField('colonia', e.currentTarget.value)}
				/>
			{/if}
		</div>
		<div class="grid grid-cols-2 gap-2">
			<div>
				<label class="text-sm text-slate-600 dark:text-slate-400">Municipio</label>
				<input
					type="text"
					class="input mt-1"
					value={direccion.municipio}
					oninput={(e) => updateField('municipio', e.currentTarget.value)}
				/>
			</div>
			<div>
				<label class="text-sm text-slate-600 dark:text-slate-400">Estado</label>
				<input
					type="text"
					class="input mt-1"
					value={direccion.estado}
					oninput={(e) => updateField('estado', e.currentTarget.value)}
				/>
			</div>
		</div>
		<div>
			<label class="text-sm text-slate-600 dark:text-slate-400">
				C.P. <span class="text-xs text-slate-400">(autocompleta dirección)</span>
			</label>
			<input
				type="text"
				class="input mt-1 font-mono w-32"
				value={direccion.cp}
				maxlength="5"
				placeholder="00000"
				oninput={(e) => {
					const cp = e.currentTarget.value.replace(/\D/g, '').slice(0, 5);
					updateField('cp', cp);
					if (cp.length === 5) {
						lookupPostalCode(cp);
					} else {
						colonias = [];
					}
				}}
			/>
		</div>
	</div>
</div>
