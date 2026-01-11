<script lang="ts">
	import { Building2, Info, Hash, CheckCircle2, Copy, Shuffle, MapPin } from 'lucide-svelte';
	import { loadCatalogRows } from 'catalogmx/utils';
	import { base } from '$app/paths';
	import { calculateClabeCheckDigit, generateClabe, validateClabe } from '$lib/catalogmx';

	type Bank = {
		code: string;
		name: string;
		full_name: string;
		rfc: string | null;
		spei: number;
	};

	type Plaza = {
		codigo: string;
		plaza: string;
		estado: string;
		cve_entidad: string;
	};

	// State
	let banks = $state<Bank[]>([]);
	let plazas = $state<Plaza[]>([]);
	let selectedBankCode = $state('');
	let selectedPlazaKey = $state('');
	let branchCode = $state('');
	let accountNumber = $state('');
	let generatedClabe = $state('');
	let isValid = $state(false);
	let breakdown = $state<{
		bankCode: string;
		bankName: string;
		branchCode: string;
		plazaName: string | null;
		plazaEstado: string | null;
		accountNumber: string;
		checkDigit: string;
	} | null>(null);
	let copySuccess = $state(false);

	const allBanks = loadCatalogRows<Bank>('banxico/banks.json');
	const allPlazas = loadCatalogRows<Plaza>('banxico/codigos_plaza.json');
	banks = allBanks.filter((bank) => bank.spei === 1).sort((a, b) => a.code.localeCompare(b.code));
	plazas = allPlazas;

	const plazaOptions = $derived(
		plazas.map((plaza) => ({
			key: `${plaza.codigo}-${plaza.cve_entidad}`,
			code: plaza.codigo,
			label: `${plaza.codigo} - ${plaza.plaza} (${plaza.estado})`,
			plaza: plaza.plaza,
			estado: plaza.estado,
		}))
	);

	function generateRandomAccountNumber() {
		// Generate random 11-digit account number
		const random = Math.floor(Math.random() * 100000000000).toString().padStart(11, '0');
		accountNumber = random;
	}

	function generateClabeValue() {
		// Reset state
		generatedClabe = '';
		breakdown = null;
		isValid = false;

		// Validate inputs
		if (!selectedBankCode || !branchCode || !accountNumber) {
			return;
		}

		// Pad codes properly
		const bankCodePadded = selectedBankCode.padStart(3, '0');
		const branchCodePadded = branchCode.padStart(3, '0');
		const accountNumberPadded = accountNumber.padStart(11, '0');

		// Validate lengths
		if (bankCodePadded.length !== 3 || branchCodePadded.length !== 3 || accountNumberPadded.length !== 11) {
			return;
		}

		// Generate CLABE
		const clabe = generateClabe(bankCodePadded, branchCodePadded, accountNumberPadded);
		const checkDigit = calculateClabeCheckDigit(clabe.substring(0, 17));
		isValid = validateClabe(clabe);

		if (isValid) {
			generatedClabe = clabe;

			// Find bank name
		const bank = banks.find((b) => b.code === bankCodePadded);
		const plazaMatches = plazas.filter((plaza) => plaza.codigo === branchCodePadded);
		const plazaInfo = plazaMatches[0];

		breakdown = {
			bankCode: bankCodePadded,
			bankName: bank ? bank.name : 'Desconocido',
			branchCode: branchCodePadded,
			plazaName: plazaInfo?.plaza ?? null,
			plazaEstado: plazaInfo?.estado ?? null,
			accountNumber: accountNumberPadded,
			checkDigit
		};
		}
	}

	function copyToClipboard() {
		if (generatedClabe) {
			navigator.clipboard.writeText(generatedClabe);
			copySuccess = true;
			setTimeout(() => {
				copySuccess = false;
			}, 2000);
		}
	}

	// Auto-generate when inputs change
	$effect(() => {
		if (selectedBankCode && branchCode && accountNumber) {
			generateClabeValue();
		}
	});

	$effect(() => {
		if (!selectedPlazaKey) {
			return;
		}
		const selected = plazaOptions.find((option) => option.key === selectedPlazaKey);
		if (selected) {
			branchCode = selected.code;
		}
	});
</script>

<svelte:head>
	<title>Generador CLABE - catalogmx</title>
	<meta name="description" content="Genera CLABE (Clave Bancaria Estandarizada) con digito verificador calculado. Herramienta para generar numeros de cuenta interbancarios validos." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/generadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Generadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">CLABE</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
				<Building2 class="h-8 w-8 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Generador CLABE
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Genera CLABE con digito verificador calculado para transferencias interbancarias
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
			<Info class="h-5 w-5 text-purple-600 dark:text-purple-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-purple-900 dark:text-purple-300">
				<p class="font-medium mb-1">Clave Bancaria Estandarizada</p>
				<p>CLABE es el numero de cuenta de 18 digitos usado en Mexico para transferencias electronicas interbancarias (SPEI). Incluye banco, sucursal, cuenta y digito verificador.</p>
			</div>
		</div>
	</div>
</section>

<!-- Generator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Hash class="h-5 w-5 text-brand-500" />
					Datos de la cuenta
				</h2>

				<div class="space-y-5">
					<!-- Bank selector -->
					<div>
						<label for="bank" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Banco *
						</label>
						<select
							id="bank"
							bind:value={selectedBankCode}
							class="input"
						>
							<option value="">Selecciona un banco...</option>
							{#each banks as bank}
								<option value={bank.code}>
									{bank.code} - {bank.name}
								</option>
							{/each}
						</select>
						<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
							Solo bancos habilitados para SPEI
						</p>
					</div>

					<!-- Branch code -->
					<div>
						<label for="branch" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Codigo de Sucursal/Plaza *
						</label>
						<div class="mb-3">
							<label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">
								Plaza sugerida (opcional)
							</label>
							<select
								bind:value={selectedPlazaKey}
								class="input text-sm"
							>
								<option value="">Selecciona una plaza...</option>
								{#each plazaOptions as plaza}
									<option value={plaza.key}>{plaza.label}</option>
								{/each}
							</select>
						</div>
						<input
							id="branch"
							type="text"
							bind:value={branchCode}
							maxlength="3"
							pattern="[0-9]*"
							class="input font-mono"
							placeholder="001"
						/>
						<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
							3 digitos (se rellenara con ceros a la izquierda)
						</p>
					</div>

					<!-- Account number -->
					<div>
						<label for="account" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Numero de Cuenta *
						</label>
						<div class="flex gap-2">
							<input
								id="account"
								type="text"
								bind:value={accountNumber}
								maxlength="11"
								pattern="[0-9]*"
								class="input font-mono flex-1"
								placeholder="01234567890"
							/>
							<button
								type="button"
								onclick={generateRandomAccountNumber}
								class="btn btn-secondary px-3"
								title="Generar numero aleatorio"
							>
								<Shuffle class="h-4 w-4" />
							</button>
						</div>
						<p class="text-xs text-slate-500 dark:text-slate-400 mt-1">
							11 digitos (se rellenara con ceros a la izquierda)
						</p>
					</div>

					<!-- Info box -->
					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<div class="flex gap-2 text-sm text-slate-600 dark:text-slate-400">
							<Info class="h-4 w-4 flex-shrink-0 mt-0.5" />
							<p>
								El digito verificador se calcula automaticamente usando el algoritmo modulo 10 con pesos [3,7,1].
							</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					CLABE Generada
				</h2>

				{#if generatedClabe && breakdown}
					<div class="space-y-6">
						<!-- CLABE Result -->
						<div class="p-6 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 rounded-lg border border-purple-200 dark:border-purple-800">
							<div class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-2">
								CLABE Completa
							</div>
							<div class="text-3xl font-bold text-purple-900 dark:text-purple-100 tracking-wider font-mono break-all">
								{generatedClabe}
							</div>
							{#if isValid}
								<div class="flex items-center gap-1 mt-2 text-xs text-green-600 dark:text-green-400">
									<CheckCircle2 class="h-3 w-3" />
									Digito verificador valido
								</div>
							{/if}
						</div>

						<!-- Breakdown -->
						<div class="space-y-3">
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300">
								Desglose de la CLABE
							</h3>

							<div class="space-y-2">
								<!-- Bank -->
								<div class="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
									<span class="text-sm text-slate-600 dark:text-slate-400">Banco</span>
									<span class="text-sm font-mono font-semibold text-slate-900 dark:text-white">
										{breakdown.bankCode} - {breakdown.bankName}
									</span>
								</div>

								<!-- Branch -->
								<div class="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
									<span class="text-sm text-slate-600 dark:text-slate-400">Sucursal/Plaza</span>
									<div class="text-right">
										<span class="text-sm font-mono font-semibold text-slate-900 dark:text-white">
											{breakdown.branchCode}
										</span>
										{#if breakdown.plazaName}
											<div class="text-xs text-slate-500 dark:text-slate-400">
												{breakdown.plazaName}
												{#if breakdown.plazaEstado}
													<span> · {breakdown.plazaEstado}</span>
												{/if}
											</div>
										{/if}
									</div>
								</div>

								<!-- Account -->
								<div class="flex justify-between items-center p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
									<span class="text-sm text-slate-600 dark:text-slate-400">Numero de Cuenta</span>
									<span class="text-sm font-mono font-semibold text-slate-900 dark:text-white">
										{breakdown.accountNumber}
									</span>
								</div>

								<!-- Check digit -->
								<div class="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
									<span class="text-sm text-green-700 dark:text-green-300 font-medium">Digito Verificador</span>
									<span class="text-sm font-mono font-bold text-green-900 dark:text-green-100">
										{breakdown.checkDigit}
									</span>
								</div>
							</div>
						</div>

						<!-- Copy button -->
						<button
							class="btn btn-primary w-full"
							onclick={copyToClipboard}
						>
							{#if copySuccess}
								<CheckCircle2 class="h-4 w-4" />
								Copiado!
							{:else}
								<Copy class="h-4 w-4" />
								Copiar CLABE
							{/if}
						</button>
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<Building2 class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Completa los campos para generar la CLABE</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info section -->
		<div class="mt-8 grid gap-4 md:grid-cols-2">
			<!-- Algorithm info -->
			<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">
					Algoritmo de Verificacion
				</h3>
				<div class="text-xs text-slate-600 dark:text-slate-400 space-y-1">
					<p>1. Multiplicar cada digito por su peso (patron 3,7,1)</p>
					<p>2. Tomar modulo 10 de cada producto</p>
					<p>3. Sumar todos los resultados</p>
					<p>4. Calcular: (10 - (suma % 10)) % 10</p>
				</div>
			</div>

			<!-- Structure info -->
			<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
				<h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-2">
					Estructura CLABE
				</h3>
				<div class="text-xs text-slate-600 dark:text-slate-400 space-y-1">
					<p><strong>Posiciones 1-3:</strong> Codigo del banco</p>
					<p><strong>Posiciones 4-6:</strong> Codigo de sucursal/plaza</p>
					<p><strong>Posiciones 7-17:</strong> Numero de cuenta (11 digitos)</p>
					<p><strong>Posicion 18:</strong> Digito verificador</p>
				</div>
			</div>
		</div>

		<!-- Warning -->
		<div class="mt-4 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
			<p class="text-xs text-amber-900 dark:text-amber-300">
				<strong>Nota:</strong> Este generador crea CLABEs con estructura valida para propositos de prueba y desarrollo.
				Para transferencias reales, siempre usa la CLABE oficial proporcionada por tu banco.
				Las CLABEs generadas aqui no estan registradas en el sistema bancario real.
			</p>
		</div>
	</div>
</section>
