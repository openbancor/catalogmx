<script lang="ts">
	import { CreditCard, Info, Building2, MapPin, Hash, CheckCircle2, XCircle } from 'lucide-svelte';
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import { CLABEValidator } from '$lib/catalogmx';
	import { query } from '$lib/db';

	const SITE_URL = 'https://catalogmx.openbancor.com';
	const canonicalUrl = `${SITE_URL}/calculadoras/informacion-clabe`;
	const clabeInfoJsonLd = {
		'@context': 'https://schema.org',
		'@graph': [
			{
				'@type': 'WebPage',
				name: 'Información de una CLABE',
				url: canonicalUrl,
				description:
					'Pega una CLABE de 18 dígitos y obtén banco, plaza, cuenta y validación de dígito de control.'
			},
			{
				'@type': 'FAQPage',
				mainEntity: [
					{
						'@type': 'Question',
						name: '¿Qué información se puede obtener de una CLABE?',
						acceptedAnswer: {
							'@type': 'Answer',
							text: 'Se puede identificar banco, plaza, número de cuenta y validar el dígito de control.'
						}
					},
					{
						'@type': 'Question',
						name: '¿Cómo sé si una CLABE es válida?',
						acceptedAnswer: {
							'@type': 'Answer',
							text: 'Una CLABE válida debe tener 18 dígitos, estructura correcta y dígito de control correcto.'
						}
					}
				]
			}
		]
	};

	type Bank = { code: string; name: string };
	type Plaza = { codigo: string; plaza: string; estado: string; cve_entidad: string };

	let clabe = $state('');
	let banksData: Bank[] = [];
	let plazasData: Plaza[] = [];
	let catalogsReady = $state(false);
	let catalogsError = $state<string | null>(null);

	let decodeResult = $state<{
		isValid: boolean;
		bankCode: string | null;
		bankName: string | null;
		branchCode: string | null;
		plazaName: string | null;
		plazaEstado: string | null;
		plazaMatches: number;
		accountNumber: string | null;
		checkDigit: string | null;
		checkDigitValid: boolean;
		errors: string[];
	} | null>(null);

	onMount(async () => {
		try {
			const [banks, plazas] = await Promise.all([
				query<Bank>('SELECT code, name FROM banxico_banks ORDER BY code'),
				query<Plaza>('SELECT codigo, plaza, estado, cve_entidad FROM banxico_codigos_plaza ORDER BY codigo')
			]);
			banksData = banks;
			plazasData = plazas;
		} catch (error) {
			catalogsError = error instanceof Error ? error.message : 'Error loading catalogs';
		} finally {
			catalogsReady = true;
		}
	});

	function decodeClabe(value: string): void {
		const errors: string[] = [];
		let bankCode: string | null = null;
		let bankName: string | null = null;
		let branchCode: string | null = null;
		let plazaName: string | null = null;
		let plazaEstado: string | null = null;
		let plazaMatches = 0;
		let accountNumber: string | null = null;
		let checkDigit: string | null = null;
		let checkDigitValid = false;

		if (value.length !== 18) {
			errors.push('La CLABE debe tener exactamente 18 dígitos');
		}

		const validator = new CLABEValidator(value);
		const isValid = validator.isValid();

		const components = validator.getComponents();
		if (components) {
			bankCode = components.bankCode;
			branchCode = components.branchCode;
			accountNumber = components.accountNumber;
			checkDigit = components.checkDigit;

			const bank = banksData.find((item) => item.code === bankCode);
			if (bank) {
				bankName = bank.name;
			} else {
				errors.push('Código de banco no reconocido');
			}

			const plazas = plazasData.filter((item) => item.codigo === branchCode);
			plazaMatches = plazas.length;
			if (plazas.length > 0) {
				plazaName = plazas[0].plaza;
				plazaEstado = plazas[0].estado;
			} else {
				errors.push('Código de plaza no reconocido');
			}
		}

		checkDigitValid = isValid;
		if (!checkDigitValid) {
			errors.push('Dígito de control incorrecto');
		}

		decodeResult = {
			isValid,
			bankCode,
			bankName,
			branchCode,
			plazaName,
			plazaEstado,
			plazaMatches,
			accountNumber,
			checkDigit,
			checkDigitValid,
			errors
		};
	}

	$effect(() => {
		const normalized = clabe.replace(/\D/g, '').slice(0, 18);
		if (normalized !== clabe) {
			clabe = normalized;
			return;
		}
		if (normalized && catalogsReady) {
			decodeClabe(normalized);
		} else {
			decodeResult = null;
		}
	});
</script>

<svelte:head>
	<title>Información de una CLABE | Banco y plaza - catalogmx</title>
	<meta
		name="description"
		content="Pega una CLABE de 18 dígitos y obtén información: banco, plaza, cuenta y validación del dígito de control."
	/>
	<meta
		name="keywords"
		content="información de CLABE, decodificar CLABE, banco de una CLABE, plaza de una CLABE, validar CLABE"
	/>
	<meta name="robots" content="index, follow, max-image-preview:large" />
	<link rel="canonical" href={canonicalUrl} />
	<meta property="og:type" content="website" />
	<meta property="og:title" content="Información de una CLABE | Banco y plaza - catalogmx" />
	<meta property="og:description" content="Descubre banco, plaza y cuenta de una CLABE y valida su dígito de control." />
	<meta property="og:url" content={canonicalUrl} />
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Información de una CLABE - catalogmx" />
	<meta name="twitter:description" content="Decodifica una CLABE de 18 dígitos con catálogos Banxico." />
	{@html `<script type="application/ld+json">${JSON.stringify(clabeInfoJsonLd)}</script>`}
</svelte:head>

<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/calculadoras" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Calculadoras
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">Información CLABE</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-emerald-100 dark:bg-emerald-900/30">
				<CreditCard class="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Información de una CLABE
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Pasa una CLABE y obtén banco, plaza, cuenta y validación
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg border border-emerald-200 dark:border-emerald-800">
			<Info class="h-5 w-5 text-emerald-600 dark:text-emerald-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-emerald-900 dark:text-emerald-300">
				<p class="font-medium mb-1">CLABE (18 dígitos)</p>
				<p>La CLABE identifica banco, plaza y cuenta para transferencias SPEI en México. Aquí puedes decodificarla en segundos.</p>
			</div>
		</div>
	</div>
</section>

<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CreditCard class="h-5 w-5 text-brand-500" />
					CLABE a decodificar
				</h2>

				<div class="space-y-5">
					<div>
						<label for="clabe" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							CLABE (18 dígitos)
						</label>
						<input
							id="clabe"
							type="text"
							bind:value={clabe}
							maxlength="18"
							class="input font-mono tabular-nums"
							placeholder="002010077777777771"
						/>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							Solo números. No guardamos ni enviamos tu CLABE a servidores.
						</p>
					</div>

					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
							<span class="font-medium">Estructura CLABE:</span>
						</p>
						<ul class="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
							<li>• 3 dígitos: banco</li>
							<li>• 3 dígitos: plaza/sucursal</li>
							<li>• 11 dígitos: número de cuenta</li>
							<li>• 1 dígito: control</li>
						</ul>
					</div>
				</div>
			</div>

			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					Detalle de la CLABE
				</h2>

				{#if catalogsError}
					<div class="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 dark:border-amber-800 dark:bg-amber-900/20 dark:text-amber-200">
						No se pudieron cargar catálogos Banxico: {catalogsError}
					</div>
				{/if}

				{#if decodeResult}
					<div class="space-y-4">
						<div class="p-4 rounded-lg border {decodeResult.isValid ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'}">
							<div class="flex items-center gap-2">
								{#if decodeResult.isValid}
									<CheckCircle2 class="h-5 w-5 text-green-600 dark:text-green-400" />
									<span class="font-semibold text-green-900 dark:text-green-100">CLABE válida</span>
								{:else}
									<XCircle class="h-5 w-5 text-red-600 dark:text-red-400" />
									<span class="font-semibold text-red-900 dark:text-red-100">CLABE inválida</span>
								{/if}
							</div>
						</div>

						{#if decodeResult.bankCode || decodeResult.branchCode || decodeResult.accountNumber}
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Información decodificada
								</h3>

								<div class="space-y-2 text-sm">
									{#if decodeResult.bankCode}
										<div class="flex items-start gap-2 py-2">
											<Building2 class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Banco</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">
													{decodeResult.bankName || 'Desconocido'}
												</div>
												<div class="text-xs text-slate-500 dark:text-slate-400 font-mono">
													Código: {decodeResult.bankCode}
												</div>
											</div>
										</div>
									{/if}

									{#if decodeResult.branchCode}
										<div class="flex items-start gap-2 py-2">
											<MapPin class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Plaza / Sucursal</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{decodeResult.branchCode}
												</div>
												{#if decodeResult.plazaName}
													<div class="text-xs text-slate-500 dark:text-slate-400">
														{decodeResult.plazaName}
														{#if decodeResult.plazaEstado}
															<span> · {decodeResult.plazaEstado}</span>
														{/if}
														{#if decodeResult.plazaMatches > 1}
															<span> · {decodeResult.plazaMatches} plazas</span>
														{/if}
													</div>
												{/if}
											</div>
										</div>
									{/if}

									{#if decodeResult.accountNumber}
										<div class="flex items-start gap-2 py-2">
											<Hash class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Número de cuenta</div>
												<div class="font-medium text-slate-900 dark:text-slate-100 font-mono">
													{decodeResult.accountNumber}
												</div>
											</div>
										</div>
									{/if}

									{#if decodeResult.checkDigit}
										<div class="flex items-start gap-2 py-2">
											<CheckCircle2 class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Dígito de control</div>
												<div class="font-medium {decodeResult.checkDigitValid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'} font-mono">
													{decodeResult.checkDigit} {decodeResult.checkDigitValid ? '✓' : '✗'}
												</div>
											</div>
										</div>
									{/if}
								</div>
							</div>
						{/if}

						{#if decodeResult.errors.length > 0}
							<div class="space-y-2">
								<h3 class="text-sm font-semibold text-red-700 dark:text-red-300">
									Observaciones:
								</h3>
								<ul class="space-y-1">
									{#each decodeResult.errors as error}
										<li class="text-sm text-red-600 dark:text-red-400 flex items-start gap-2">
											<span class="text-red-500 mt-0.5">•</span>
											<span>{error}</span>
										</li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<CreditCard class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa una CLABE para ver sus detalles</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Esta herramienta identifica la estructura y catálogos de una CLABE.
				No confirma la existencia, titularidad o estado real de la cuenta bancaria.
			</p>
		</div>

		<div class="mt-6 p-4 bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
			<h2 class="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
				Herramientas relacionadas
			</h2>
			<p class="text-xs text-slate-600 dark:text-slate-400">
				Revisa también el
				<a href="{base}/validadores/clabe" class="text-brand-600 dark:text-brand-400 hover:underline">
					validador de CLABE
				</a>,
				el
				<a href="{base}/generadores/clabe" class="text-brand-600 dark:text-brand-400 hover:underline">
					generador de CLABE
				</a>
				y los catálogos de
				<a href="{base}/catalogos/banxico/bancos" class="text-brand-600 dark:text-brand-400 hover:underline">
					bancos
				</a>
				y
				<a href="{base}/catalogos/banxico/plazas" class="text-brand-600 dark:text-brand-400 hover:underline">
					plazas Banxico
				</a>.
			</p>
		</div>
	</div>
</section>
