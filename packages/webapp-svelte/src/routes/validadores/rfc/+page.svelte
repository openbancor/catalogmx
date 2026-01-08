<script lang="ts">
	import { Building2, CheckCircle2, XCircle, Info, Calendar, User } from 'lucide-svelte';

	// State
	let rfc = $state('');
	let validationResult = $state<{
		isValid: boolean;
		tipo: string;
		fecha: string | null;
		errors: string[];
		checksumValid: boolean;
	} | null>(null);

	// RFC Validation Logic
	const RFC_REGEX = /^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$/;
	const GENERIC_RFCS = ['XAXX010101000', 'XEXX010101000'];

	const CHECKSUM_TABLE: { [key: string]: string } = {
		'0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05', '6': '06', '7': '07', '8': '08', '9': '09',
		'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15', 'G': '16', 'H': '17', 'I': '18', 'J': '19',
		'K': '20', 'L': '21', 'M': '22', 'N': '23', '&': '24', 'O': '25', 'P': '26', 'Q': '27', 'R': '28', 'S': '29',
		'T': '30', 'U': '31', 'V': '32', 'W': '33', 'X': '34', 'Y': '35', 'Z': '36', ' ': '37', 'Ñ': '38'
	};

	function calculateCheckDigit(rfcWithoutChecksum: string): string {
		let str = rfcWithoutChecksum;
		if (str.length === 11) {
			str = ' ' + str;
		}

		let sum = 0;
		let position = 13;

		for (const char of str) {
			const value = parseInt(CHECKSUM_TABLE[char] || '00');
			sum += value * position;
			position--;
		}

		const residual = sum % 11;

		if (residual === 0) {
			return '0';
		} else {
			const result = 11 - residual;
			if (result === 10) {
				return 'A';
			} else {
				return result.toString();
			}
		}
	}

	function validateDate(dateStr: string): boolean {
		try {
			const year = parseInt(dateStr.substring(0, 2));
			const month = parseInt(dateStr.substring(2, 4));
			const day = parseInt(dateStr.substring(4, 6));

			if (month < 1 || month > 12) return false;
			if (day < 1 || day > 31) return false;

			// Full year estimation
			const fullYear = year >= 0 && year <= 30 ? 2000 + year : 1900 + year;

			// Basic date validation
			const date = new Date(fullYear, month - 1, day);
			return date.getMonth() === month - 1 && date.getDate() === day;
		} catch {
			return false;
		}
	}

	function validateRFC(value: string): void {
		const errors: string[] = [];
		let isValid = false;
		let tipo = '';
		let fecha: string | null = null;
		let checksumValid = false;

		const rfcUpper = value.toUpperCase().trim();

		// Length validation
		if (rfcUpper.length !== 12 && rfcUpper.length !== 13) {
			errors.push('El RFC debe tener 12 caracteres (persona moral) o 13 caracteres (persona física)');
			validationResult = { isValid: false, tipo: 'RFC Inválido', fecha: null, errors, checksumValid: false };
			return;
		}

		// Regex validation
		if (!RFC_REGEX.test(rfcUpper)) {
			errors.push('El formato del RFC no es válido');
			validationResult = { isValid: false, tipo: 'RFC Inválido', fecha: null, errors, checksumValid: false };
			return;
		}

		// Check if generic
		if (GENERIC_RFCS.includes(rfcUpper)) {
			validationResult = {
				isValid: true,
				tipo: 'Genérico',
				fecha: '2000-01-01',
				errors: [],
				checksumValid: true
			};
			return;
		}

		// Determine tipo
		const fourthChar = rfcUpper[3];
		if (rfcUpper.length === 13 && /[A-ZÑ]/.test(fourthChar)) {
			tipo = 'Persona Física';
		} else if (rfcUpper.length === 12 && /[0-9]/.test(fourthChar)) {
			tipo = 'Persona Moral';
		} else {
			errors.push('El cuarto carácter no corresponde al tipo de RFC');
		}

		// Extract and validate date
		const dateStr = rfcUpper.substring(rfcUpper.length === 13 ? 4 : 3, rfcUpper.length === 13 ? 10 : 9);
		if (validateDate(dateStr)) {
			const year = parseInt(dateStr.substring(0, 2));
			const month = dateStr.substring(2, 4);
			const day = dateStr.substring(4, 6);
			const fullYear = year >= 0 && year <= 30 ? 2000 + year : 1900 + year;
			fecha = `${fullYear}-${month}-${day}`;
		} else {
			errors.push('La fecha en el RFC no es válida');
		}

		// Validate checksum
		const rfcWithoutChecksum = rfcUpper.substring(0, rfcUpper.length - 1);
		const expectedChecksum = calculateCheckDigit(rfcWithoutChecksum);
		const actualChecksum = rfcUpper[rfcUpper.length - 1];

		checksumValid = expectedChecksum === actualChecksum;
		if (!checksumValid) {
			errors.push(`Dígito verificador incorrecto (esperado: ${expectedChecksum}, actual: ${actualChecksum})`);
		}

		isValid = errors.length === 0;

		validationResult = {
			isValid,
			tipo: tipo || 'RFC Inválido',
			fecha,
			errors,
			checksumValid
		};
	}

	// Auto-validate when RFC changes
	$effect(() => {
		if (rfc.trim()) {
			validateRFC(rfc);
		} else {
			validationResult = null;
		}
	});
</script>

<svelte:head>
	<title>Validador RFC - catalogmx</title>
	<meta name="description" content="Valida RFC de personas físicas y morales. Verifica formato, dígito verificador y decodifica información." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="/validadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Validadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">RFC</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
				<Building2 class="h-8 w-8 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Validador de RFC
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Registro Federal de Contribuyentes
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">RFC - Registro Federal de Contribuyentes</p>
				<p>El RFC es la clave única de identificación fiscal en México. Persona física: 13 caracteres. Persona moral: 12 caracteres.</p>
			</div>
		</div>
	</div>
</section>

<!-- Validator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<Building2 class="h-5 w-5 text-brand-500" />
					RFC a validar
				</h2>

				<div class="space-y-5">
					<div>
						<label for="rfc" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							RFC (12 o 13 caracteres)
						</label>
						<input
							id="rfc"
							type="text"
							bind:value={rfc}
							maxlength="13"
							class="input uppercase font-mono"
							placeholder="VECJ880326XXX"
						/>
						<p class="mt-1 text-xs text-slate-500 dark:text-slate-400">
							12 caracteres = Persona Moral | 13 caracteres = Persona Física
						</p>
					</div>

					<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
						<p class="text-sm text-slate-600 dark:text-slate-400 mb-2">
							<span class="font-medium">Ejemplos válidos:</span>
						</p>
						<ul class="text-xs text-slate-500 dark:text-slate-400 space-y-1 font-mono">
							<li>• VECJ880326XXX (Persona Física)</li>
							<li>• ABC123456XXX (Persona Moral)</li>
							<li>• XAXX010101000 (Genérico Nacional)</li>
						</ul>
					</div>
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					Resultado de validación
				</h2>

				{#if validationResult}
					<div class="space-y-4">
						<!-- Validation Status Badge -->
						<div class="p-4 rounded-lg border {validationResult.isValid ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'}">
							<div class="flex items-center gap-2 mb-2">
								{#if validationResult.isValid}
									<CheckCircle2 class="h-5 w-5 text-green-600 dark:text-green-400" />
									<span class="font-semibold text-green-900 dark:text-green-100">RFC Válido</span>
								{:else}
									<XCircle class="h-5 w-5 text-red-600 dark:text-red-400" />
									<span class="font-semibold text-red-900 dark:text-red-100">RFC Inválido</span>
								{/if}
							</div>
						</div>

						<!-- Decoded Information -->
						{#if validationResult.isValid || validationResult.tipo !== 'RFC Inválido'}
							<div class="space-y-3">
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 border-b border-slate-200 dark:border-slate-700 pb-2">
									Información decodificada
								</h3>

								<div class="space-y-2 text-sm">
									<div class="flex items-start gap-2 py-2">
										<User class="h-4 w-4 text-slate-400 mt-0.5" />
										<div class="flex-1">
											<div class="text-slate-600 dark:text-slate-400">Tipo</div>
											<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.tipo}</div>
										</div>
									</div>

									{#if validationResult.fecha}
										<div class="flex items-start gap-2 py-2">
											<Calendar class="h-4 w-4 text-slate-400 mt-0.5" />
											<div class="flex-1">
												<div class="text-slate-600 dark:text-slate-400">Fecha</div>
												<div class="font-medium text-slate-900 dark:text-slate-100">{validationResult.fecha}</div>
												<div class="text-xs text-slate-500 dark:text-slate-400">
													{validationResult.tipo === 'Persona Física' ? 'Fecha de nacimiento' : 'Fecha de constitución'}
												</div>
											</div>
										</div>
									{/if}

									<div class="flex items-start gap-2 py-2">
										<CheckCircle2 class="h-4 w-4 text-slate-400 mt-0.5" />
										<div class="flex-1">
											<div class="text-slate-600 dark:text-slate-400">Dígito verificador</div>
											<div class="font-medium {validationResult.checksumValid ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}">
												{validationResult.checksumValid ? 'Válido ✓' : 'Inválido ✗'}
											</div>
										</div>
									</div>
								</div>
							</div>
						{/if}

						<!-- Errors -->
						{#if validationResult.errors.length > 0}
							<div class="space-y-2">
								<h3 class="text-sm font-semibold text-red-700 dark:text-red-300">
									Errores encontrados:
								</h3>
								<ul class="space-y-1">
									{#each validationResult.errors as error}
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
							<Building2 class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Ingresa un RFC para validar</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este validador verifica el formato, estructura y dígito verificador del RFC.
				La existencia real del RFC en el SAT solo puede verificarse en el sistema oficial del SAT.
			</p>
		</div>
	</div>
</section>
