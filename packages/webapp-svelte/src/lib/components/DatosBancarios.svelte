<script lang="ts">
	import { Briefcase, Copy, MapPin } from 'lucide-svelte';
	import SearchableSelect from './SearchableSelect.svelte';

	interface DatosBancarios {
		banco: string;
		bancoNombre: string;
		plaza: string;
		plazaLocalidad: string;
		clabe: string;
		cuenta: string;
		tarjeta: string;
		tarjetaTipo: 'Visa' | 'Mastercard';
	}

	interface Bank {
		code: string;
		name: string;
		full_name: string;
	}

	interface Plaza {
		codigo: string;
		estado: string;
		plaza: string;
	}

	type ClabeFormat = '3-3-5-5-2' | '4-4-4-4-2' | '3-3-4-4-4';

	interface Props {
		datos: DatosBancarios;
		banks: Bank[];
		plazas?: Plaza[];
		clabeFormat?: ClabeFormat;
		copied: string | null;
		onBankChange: (bancoCode: string) => void;
		onPlazaChange?: (plazaCode: string) => void;
		onCopy: (text: string, field: string) => void;
		onFormatChange?: (format: ClabeFormat) => void;
		onCardTypeChange?: (tipo: 'Visa' | 'Mastercard') => void;
	}

	let {
		datos,
		banks,
		plazas = [],
		clabeFormat = '3-3-4-4-4',
		copied,
		onBankChange,
		onPlazaChange,
		onCopy,
		onFormatChange,
		onCardTypeChange
	}: Props = $props();

	const bankOptions = $derived(
		banks.map((b) => ({
			value: b.code,
			label: b.name,
			searchText: `${b.name} ${b.full_name}`.toLowerCase()
		}))
	);

	// Get unique plaza codes with their localities for selection
	const plazaOptions = $derived(() => {
		if (!plazas.length) return [];

		// Group plazas by code and list their localities
		const grouped = new Map<string, { estado: string; localidades: string[] }>();
		for (const p of plazas) {
			if (!grouped.has(p.codigo)) {
				grouped.set(p.codigo, { estado: p.estado, localidades: [] });
			}
			const entry = grouped.get(p.codigo)!;
			if (p.plaza && !entry.localidades.includes(p.plaza)) {
				entry.localidades.push(p.plaza);
			}
		}

		// Convert to options format
		return Array.from(grouped.entries()).map(([codigo, { estado, localidades }]) => {
			const mainLocality = localidades[0] || estado;
			const label = localidades.length > 1
				? `${codigo} - ${mainLocality} (+${localidades.length - 1})`
				: `${codigo} - ${mainLocality}`;
			return {
				value: codigo,
				label,
				searchText: `${codigo} ${estado} ${localidades.join(' ')}`.toLowerCase()
			};
		}).sort((a, b) => a.value.localeCompare(b.value));
	});

	// Get localities for the currently selected plaza
	const currentPlazaLocalidades = $derived(() => {
		if (!plazas.length || !datos.plaza) return [];
		return plazas
			.filter(p => p.codigo === datos.plaza && p.plaza)
			.map(p => p.plaza)
			.filter((v, i, a) => a.indexOf(v) === i); // unique
	});

	function formatClabe(clabe: string, format: ClabeFormat): string {
		const digits = clabe.replace(/\D/g, '');
		if (digits.length !== 18) return clabe;

		switch (format) {
			case '3-3-5-5-2':
				return `${digits.substring(0, 3)} ${digits.substring(3, 6)} ${digits.substring(6, 11)} ${digits.substring(11, 16)} ${digits.substring(16)}`;
			case '4-4-4-4-2':
				return `${digits.substring(0, 4)} ${digits.substring(4, 8)} ${digits.substring(8, 12)} ${digits.substring(12, 16)} ${digits.substring(16)}`;
			case '3-3-4-4-4':
				return `${digits.substring(0, 3)} ${digits.substring(3, 6)} ${digits.substring(6, 10)} ${digits.substring(10, 14)} ${digits.substring(14)}`;
			default:
				return clabe;
		}
	}

	function formatCard(card: string): string {
		return card.replace(/(\d{4})/g, '$1 ').trim();
	}
</script>

<div class="card p-6">
	<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
		<Briefcase class="h-5 w-5 text-green-500" />
		Datos Bancarios
	</h3>
	<div class="space-y-4">
		<div>
			<label class="text-sm text-slate-600 dark:text-slate-400">Banco</label>
			<div class="mt-1">
				<SearchableSelect
					options={bankOptions}
					value={datos.banco}
					placeholder="Seleccionar banco..."
					onchange={onBankChange}
				/>
			</div>
		</div>
		{#if onPlazaChange && plazas.length > 0}
			<div>
				<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-1">
					<MapPin class="h-3 w-3" />
					Plaza
					<span class="text-xs text-slate-400">({datos.plaza})</span>
				</label>
				<div class="mt-1">
					<SearchableSelect
						options={plazaOptions()}
						value={datos.plaza}
						placeholder="Seleccionar plaza..."
						onchange={onPlazaChange}
					/>
				</div>
				{#if currentPlazaLocalidades().length > 0}
					<div class="mt-1 text-xs text-slate-500 dark:text-slate-400">
						{#if currentPlazaLocalidades().length === 1}
							<span>{currentPlazaLocalidades()[0]}</span>
						{:else}
							<span>Localidades: {currentPlazaLocalidades().join(', ')}</span>
						{/if}
					</div>
				{/if}
			</div>
		{:else if datos.plaza}
			<div class="flex justify-between items-center text-sm">
				<span class="text-slate-600 dark:text-slate-400 flex items-center gap-1">
					<MapPin class="h-3 w-3" />
					Plaza
				</span>
				<span class="text-slate-900 dark:text-white font-mono">{datos.plaza} - {datos.plazaLocalidad || 'N/A'}</span>
			</div>
		{/if}
		<div>
			<div class="flex justify-between items-center mb-2">
				<span class="text-slate-600 dark:text-slate-400">CLABE</span>
				<select
					class="text-xs border border-slate-200 dark:border-slate-600 rounded px-2 py-1 bg-white dark:bg-slate-800"
					value={clabeFormat}
					onchange={(e) => onFormatChange?.(e.currentTarget.value as ClabeFormat)}
				>
					<option value="3-3-4-4-4">3-3-4-4-4</option>
					<option value="3-3-5-5-2">3-3-5-5-2</option>
					<option value="4-4-4-4-2">4-4-4-4-2</option>
				</select>
			</div>
			<div class="flex items-center justify-between gap-2 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg group">
				<span class="font-mono font-medium text-slate-900 dark:text-white tracking-wider">
					{formatClabe(datos.clabe, clabeFormat)}
				</span>
				<button
					class="text-brand-500 hover:text-brand-600 flex items-center gap-1 text-xs"
					onclick={() => onCopy(datos.clabe, 'clabe')}
				>
					{copied === 'clabe' ? '✓' : 'copiar'}
				</button>
			</div>
		</div>
		<div class="flex justify-between items-center group">
			<span class="text-slate-600 dark:text-slate-400">Cuenta (11 dígitos)</span>
			<button
				class="font-mono font-medium text-slate-900 dark:text-white hover:text-brand-500 flex items-center gap-1"
				onclick={() => onCopy(datos.cuenta, 'cuenta')}
			>
				{datos.cuenta}
				<Copy class="h-3 w-3 opacity-0 group-hover:opacity-100" />
			</button>
		</div>
		<div>
			<div class="flex justify-between items-center mb-2">
				<span class="text-slate-600 dark:text-slate-400">Tarjeta de Débito</span>
				{#if onCardTypeChange}
					<select
						class="text-xs border border-slate-200 dark:border-slate-600 rounded px-2 py-1 bg-white dark:bg-slate-800"
						value={datos.tarjetaTipo}
						onchange={(e) => onCardTypeChange(e.currentTarget.value as 'Visa' | 'Mastercard')}
					>
						<option value="Visa">Visa</option>
						<option value="Mastercard">Mastercard</option>
					</select>
				{:else}
					<span class="text-xs px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
						{datos.tarjetaTipo}
					</span>
				{/if}
			</div>
			<div class="flex items-center justify-between gap-2 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg group">
				<span class="font-mono font-medium text-slate-900 dark:text-white tracking-wider">
					{formatCard(datos.tarjeta)}
				</span>
				<button
					class="text-brand-500 hover:text-brand-600 flex items-center gap-1 text-xs"
					onclick={() => onCopy(datos.tarjeta, 'tarjeta')}
				>
					{copied === 'tarjeta' ? '✓' : 'copiar'}
				</button>
			</div>
		</div>
	</div>
</div>
