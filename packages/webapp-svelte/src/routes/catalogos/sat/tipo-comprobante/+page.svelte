<script lang="ts">
	import DataTable from '$lib/components/DataTable.svelte';
	import { ChevronRight, FileType, Loader2, AlertCircle } from 'lucide-svelte';
	import type { ColumnDef } from '$lib/table';
	import { onMount } from 'svelte';
	import { query } from '$lib/db';
	import { base } from '$app/paths';

	interface TipoComprobante {
		valor: string;
		descripcion?: string;
	}

	let data = $state<TipoComprobante[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);

	// Add descriptions for the known values
	const tipoComprobanteDescriptions: Record<string, string> = {
		'I': 'Ingreso',
		'E': 'Egreso',
		'T': 'Traslado',
		'N': 'Nomina',
		'P': 'Pago'
	};

	const enrichedData = $derived(
		data.map(item => ({
			...item,
			descripcion: tipoComprobanteDescriptions[item.valor] || item.valor
		}))
	);

	const columns: ColumnDef<TipoComprobante, unknown>[] = [
		{
			accessorKey: 'valor',
			header: 'Clave',
			cell: ({ getValue }) => {
				const valor = getValue() as string;
				return valor;
			},
		},
		{
			accessorKey: 'descripcion',
			header: 'Descripcion',
			cell: ({ getValue }) => getValue() as string,
		},
	];

	async function loadData() {
		try {
			loading = true;
			error = null;

			// Load tipo comprobante data from SQLite
			const result = await query<TipoComprobante>('SELECT * FROM sat_cfdi_4_0_tipo_comprobante ORDER BY valor');
			data = result;

		} catch (e) {
			error = e instanceof Error ? e.message : 'Error loading data';
			console.error('Error loading tipo comprobante data:', e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		loadData();
	});
</script>

<svelte:head>
	<title>Tipo de Comprobante (SAT CFDI 4.0) - catalogmx</title>
	<meta name="description" content="Catalogo de tipos de comprobante del SAT para CFDI 4.0." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Breadcrumb -->
	<nav class="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400 mb-6">
		<a href="{base}/catalogos" class="hover:text-brand-500">Catalogos</a>
		<ChevronRight class="h-4 w-4" />
		<a href="{base}/catalogos/sat" class="hover:text-brand-500">SAT</a>
		<ChevronRight class="h-4 w-4" />
		<span class="text-slate-900 dark:text-white">Tipo de Comprobante</span>
	</nav>

	<!-- Header -->
	<div class="mb-8">
		<div class="flex items-start gap-4">
			<div class="bg-red-100 dark:bg-red-900/30 p-3 rounded-lg">
				<FileType class="h-6 w-6 text-red-600 dark:text-red-400" />
			</div>
			<div>
				<h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">
					Catalogo de Tipo de Comprobante
				</h1>
				<p class="text-slate-600 dark:text-slate-300">
					Tipos de comprobante validos para facturas electronicas (CFDI 4.0)
				</p>
			</div>
		</div>
	</div>

	<!-- Stats -->
	<div class="grid gap-4 sm:grid-cols-2 mb-8">
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Total tipos de comprobante</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white tabular-nums">
				{#if loading}
					<span class="animate-pulse">--</span>
				{:else}
					{data.length.toLocaleString('es-MX')}
				{/if}
			</p>
		</div>
		<div class="card p-4">
			<p class="text-sm text-slate-500 dark:text-slate-400 mb-1">Version CFDI</p>
			<p class="text-2xl font-bold text-slate-900 dark:text-white">
				4.0
			</p>
		</div>
	</div>

	<!-- Loading state -->
	{#if loading}
		<div class="flex items-center justify-center py-16">
			<Loader2 class="h-8 w-8 text-brand-500 animate-spin" />
			<span class="ml-3 text-slate-600 dark:text-slate-400">Cargando catalogo desde SQLite...</span>
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
		<!-- Data table -->
		<DataTable
			data={enrichedData}
			{columns}
			searchPlaceholder="Buscar por clave o descripcion..."
		/>
	{/if}

	<!-- Info section -->
	{#if !loading && !error}
		<div class="mt-8 card p-6">
			<h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-3">
				Acerca de este catalogo
			</h2>
			<div class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
				<p>
					<strong>Tipo de Comprobante</strong> es un elemento del CFDI que especifica el tipo
					de operacion o documento que se esta emitiendo.
				</p>
				<p>
					<strong>Tipos de comprobante disponibles:</strong>
				</p>
				<ul class="list-disc list-inside ml-4 space-y-1">
					<li><strong>I - Ingreso:</strong> Factura de venta de bienes o servicios</li>
					<li><strong>E - Egreso:</strong> Nota de credito (devoluciones, descuentos, bonificaciones)</li>
					<li><strong>T - Traslado:</strong> Comprobante de traslado de mercancias (sin valor fiscal)</li>
					<li><strong>N - Nomina:</strong> Recibo de pago de nomina</li>
					<li><strong>P - Pago:</strong> Recibo electronico de pago (complemento de pago)</li>
				</ul>
				<p>
					<strong>Fuente:</strong> Servicio de Administracion Tributaria (SAT)
				</p>
				<p>
					<strong>Uso:</strong> Campo obligatorio en el CFDI 4.0 para identificar el tipo de comprobante fiscal.
					Cada tipo tiene reglas especificas de validacion y complementos permitidos.
				</p>
			</div>
		</div>
	{/if}
</div>
