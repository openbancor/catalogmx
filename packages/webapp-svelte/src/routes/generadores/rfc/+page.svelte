<script lang="ts">
	import { CreditCard, Info, User, Building2, Calendar, AlertCircle, CheckCircle2 } from 'lucide-svelte';
	import { base } from '$app/paths';

	// Helper function to remove accents
	function removeAccents(str: string): string {
		const accents: Record<string, string> = {
			'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
			'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
			'ü': 'u', 'Ü': 'U', 'ñ': 'n', 'Ñ': 'N'
		};
		return str.split('').map(char => accents[char] || char).join('');
	}

	// Constants
	const EXCLUDED_WORDS_FISICA = ['DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI'];
	const EXCLUDED_WORDS_MORAL = [
		'EL', 'LA', 'DE', 'LOS', 'LAS', 'Y', 'DEL', 'MI',
		'COMPAÑIA', 'COMPAÑÍA', 'CIA', 'CIA.', 'SOCIEDAD', 'SOC', 'SOC.',
		'COOPERATIVA', 'COOP', 'COOP.', 'S.A.', 'SA', 'S.A', 'S. A.', 'S. A',
		'S.A.B.', 'SAB', 'S.A.B', 'S. A. B.', 'S. A. B', 'S. DE R.L.',
		'S DE RL', 'SRL', 'S.R.L.', 'S. R. L.', 'S. EN C.', 'S EN C',
		'S.C.', 'SC', 'S. EN C. POR A.', 'S EN C POR A', 'S. EN N.C.',
		'S EN NC', 'A.C.', 'AC', 'A. C.', 'A. EN P.', 'A EN P', 'S.C.L.',
		'SCL', 'S.N.C.', 'SNC', 'C.V.', 'CV', 'C. V.', 'SA DE CV',
		'S.A. DE C.V.', 'SA DE CV MI', 'S.A. DE C.V. MI', 'S.A.B. DE C.V.',
		'SAB DE CV', 'S.A.B DE C.V', 'SRL DE CV', 'S.R.L. DE C.V.',
		'SRL DE CV MI', 'SRL MI', 'THE', 'OF', 'COMPANY', 'AND', 'CO', 'CO.',
		'MC', 'VON', 'MAC', 'VAN', 'PARA', 'POR', 'AL', 'E', 'EN', 'CON', 'SUS', 'A'
	];
	const CACOPHONIC_WORDS = [
		'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'COGE', 'COJA',
		'COJE', 'COJI', 'COJO', 'CULO', 'FETO', 'GUEY', 'JOTO', 'KACA', 'KACO',
		'KAGA', 'KAGO', 'KOGE', 'KOJO', 'KAKA', 'KULO', 'MAME', 'MAMO', 'MEAR',
		'MEON', 'MION', 'MOCO', 'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO',
		'QULO', 'RATA', 'RUIN'
	];
	const VOCALES = 'AEIOU';
	const ALLOWED_CHARS = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ&';

	const CHECKSUM_TABLE: Record<string, string> = {
		'0': '00', '1': '01', '2': '02', '3': '03', '4': '04', '5': '05',
		'6': '06', '7': '07', '8': '08', '9': '09', 'A': '10', 'B': '11',
		'C': '12', 'D': '13', 'E': '14', 'F': '15', 'G': '16', 'H': '17',
		'I': '18', 'J': '19', 'K': '20', 'L': '21', 'M': '22', 'N': '23',
		'&': '24', 'O': '25', 'P': '26', 'Q': '27', 'R': '28', 'S': '29',
		'T': '30', 'U': '31', 'V': '32', 'W': '33', 'X': '34', 'Y': '35',
		'Z': '36', ' ': '37', 'Ñ': '38'
	};

	const QUOTIENT_TABLE: Record<string, string> = {
		' ': '00', '0': '00', '1': '01', '2': '02', '3': '03', '4': '04',
		'5': '05', '6': '06', '7': '07', '8': '08', '9': '09', '&': '10',
		'A': '11', 'B': '12', 'C': '13', 'D': '14', 'E': '15', 'F': '16',
		'G': '17', 'H': '18', 'I': '19', 'J': '21', 'K': '22', 'L': '23',
		'M': '24', 'N': '25', 'O': '26', 'P': '27', 'Q': '28', 'R': '29',
		'S': '32', 'T': '33', 'U': '34', 'V': '35', 'W': '36', 'X': '37',
		'Y': '38', 'Z': '39', 'Ñ': '40'
	};

	const HOMOCLAVE_TABLE = [
		'1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E',
		'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T',
		'U', 'V', 'W', 'X', 'Y', 'Z'
	];

	type PersonType = 'fisica' | 'moral';

	// State
	let personType = $state<PersonType>('fisica');

	// Persona Física
	let nombre = $state('');
	let apellidoPaterno = $state('');
	let apellidoMaterno = $state('');
	let fechaNacimiento = $state('');

	// Persona Moral
	let razonSocial = $state('');
	let fechaConstitucion = $state('');

	let rfcGenerado = $state('');
	let pasos = $state<string[]>([]);

	// Helper functions
	function cleanName(name: string, excludedWords: string[]): string {
		if (!name) return '';

		const upper = name.toUpperCase().trim();
		const words = upper.split(/\s+/).filter(w => !excludedWords.includes(w));
		const joined = words.join(' ');

		let result = '';
		for (const char of joined) {
			if (ALLOWED_CHARS.includes(char) || char === ' ') {
				result += char;
			} else {
				const cleaned = removeAccents(char);
				if (ALLOWED_CHARS.includes(cleaned)) {
					result += cleaned;
				}
			}
		}

		return result.trim();
	}

	function calculateChecksum(rfc12: string): string {
		let rfcPadded = rfc12;
		if (rfcPadded.length === 11) {
			rfcPadded = ' ' + rfcPadded;
		}

		let suma = 0;
		let index = 13;

		for (const char of rfcPadded) {
			const value = parseInt(CHECKSUM_TABLE[char] || '00');
			suma += value * index;
			index--;
		}

		const residual = suma % 11;

		if (residual === 0) return '0';
		const checkDigit = 11 - residual;
		return checkDigit === 10 ? 'A' : checkDigit.toString();
	}

	function calculateHomoclave(nombreCompleto: string): string {
		let cadena = '0';

		for (const char of nombreCompleto) {
			if (QUOTIENT_TABLE[char]) {
				cadena += QUOTIENT_TABLE[char];
			}
		}

		let suma = 0;
		for (let i = 0; i < cadena.length - 1; i++) {
			const pair = parseInt(cadena.substring(i, i + 2));
			const nextDigit = parseInt(cadena[i + 1]);
			suma += pair * nextDigit;
		}

		suma = suma % 1000;
		const first = Math.floor(suma / 34);
		const second = suma % 34;

		return HOMOCLAVE_TABLE[first] + HOMOCLAVE_TABLE[second];
	}

	function generateLettersFisica(): string {
		const paterno = cleanName(apellidoPaterno, EXCLUDED_WORDS_FISICA);
		const materno = cleanName(apellidoMaterno, EXCLUDED_WORDS_FISICA);
		const nombreClean = cleanName(nombre, EXCLUDED_WORDS_FISICA);

		if (!paterno || !nombreClean) {
			throw new Error('Apellido paterno y nombre son requeridos');
		}

		const parts: string[] = [];

		// First letter of paterno
		parts.push(paterno[0]);

		// First vowel of paterno (after first letter)
		let vowelFound = false;
		for (let i = 1; i < paterno.length; i++) {
			if (VOCALES.includes(paterno[i])) {
				parts.push(paterno[i]);
				vowelFound = true;
				break;
			}
		}
		if (!vowelFound) parts.push('X');

		// First letter of materno or X
		if (materno) {
			parts.push(materno[0]);
		} else {
			parts.push('X');
		}

		// First letter of nombre (skip JOSE/MARIA if compound)
		const nombreWords = nombreClean.split(' ');
		let nombreToUse = nombreClean;
		if (nombreWords.length > 1 && (nombreWords[0] === 'MARIA' || nombreWords[0] === 'JOSE')) {
			nombreToUse = nombreWords.slice(1).join(' ');
		}
		parts.push(nombreToUse[0]);

		let clave = parts.join('');

		// Check for cacophonic words
		if (CACOPHONIC_WORDS.includes(clave)) {
			clave = clave.substring(0, 3) + 'X';
		}

		return clave;
	}

	function generateLettersMoral(): string {
		let razon = razonSocial.toUpperCase().trim();

		// Remove excluded words
		for (const excluded of EXCLUDED_WORDS_MORAL.sort((a, b) => b.length - a.length)) {
			razon = razon.replace(new RegExp(`\\b${excluded}\\b`, 'g'), ' ');
		}

		// Clean special characters
		const allowedForProcessing = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .ÑÁÉÍÓÚÜñáéíóúü';
		let razonLimpia = '';
		for (const char of razon) {
			if (allowedForProcessing.includes(char)) {
				razonLimpia += char;
			} else {
				razonLimpia += ' ';
			}
		}

		// Replace Ñ with X
		razonLimpia = razonLimpia.replace(/Ñ/g, 'X').replace(/ñ/g, 'X');

		// Clean and get words
		const words = razonLimpia.split(/\s+/).filter(w => w.length > 0);

		// Clean accents
		const finalWords = words.map(w => removeAccents(w).toUpperCase()).filter(w => w.length > 0);

		if (finalWords.length === 0) {
			throw new Error('Razón social inválida');
		}

		const clave: string[] = [];

		if (finalWords.length === 1) {
			// Single word: first 3 letters
			const word = finalWords[0];
			clave.push(word[0] || 'X');
			clave.push(word[1] || 'X');
			clave.push(word[2] || 'X');
		} else if (finalWords.length === 2) {
			// Two words: first letter of first, first two letters of second
			clave.push(finalWords[0][0]);
			clave.push(finalWords[1][0]);
			clave.push(finalWords[1][1] || 'X');
		} else {
			// Three or more: first letter of each of first 3
			clave.push(finalWords[0][0]);
			clave.push(finalWords[1][0]);
			clave.push(finalWords[2][0]);
		}

		let result = clave.join('');

		// Check for cacophonic words
		if (CACOPHONIC_WORDS.includes(result)) {
			result = result.substring(0, 2) + 'X';
		}

		return result;
	}

	function generateDate(fecha: string): string {
		const date = new Date(fecha);
		const yy = date.getFullYear().toString().substring(2);
		const mm = (date.getMonth() + 1).toString().padStart(2, '0');
		const dd = date.getDate().toString().padStart(2, '0');
		return yy + mm + dd;
	}

	function generateRFC() {
		pasos = [];
		rfcGenerado = '';

		try {
			let letters = '';
			let dateStr = '';
			let nombreCompleto = '';

			if (personType === 'fisica') {
				if (!nombre || !apellidoPaterno || !fechaNacimiento) {
					pasos.push('❌ Por favor completa todos los campos requeridos');
					return;
				}

				letters = generateLettersFisica();
				pasos.push(`1. Letras del nombre: ${letters}`);

				dateStr = generateDate(fechaNacimiento);
				pasos.push(`2. Fecha de nacimiento: ${dateStr}`);

				const paterno = cleanName(apellidoPaterno, EXCLUDED_WORDS_FISICA);
				const materno = cleanName(apellidoMaterno, EXCLUDED_WORDS_FISICA);
				const nombreClean = cleanName(nombre, EXCLUDED_WORDS_FISICA);
				nombreCompleto = [paterno, materno, nombreClean].filter(Boolean).join(' ');
			} else {
				if (!razonSocial || !fechaConstitucion) {
					pasos.push('❌ Por favor completa todos los campos requeridos');
					return;
				}

				letters = generateLettersMoral();
				pasos.push(`1. Letras de la razón social: ${letters}`);

				dateStr = generateDate(fechaConstitucion);
				pasos.push(`2. Fecha de constitución: ${dateStr}`);

				nombreCompleto = razonSocial.toUpperCase().trim();
			}

			const homoclave = calculateHomoclave(nombreCompleto);
			pasos.push(`3. Homoclave: ${homoclave}`);

			const rfc12 = letters + dateStr + homoclave;
			const checksum = calculateChecksum(rfc12);
			pasos.push(`4. Dígito verificador: ${checksum}`);

			rfcGenerado = rfc12 + checksum;
			pasos.push(`✅ RFC generado: ${rfcGenerado}`);
		} catch (error) {
			if (error instanceof Error) {
				pasos.push(`❌ Error: ${error.message}`);
			}
		}
	}

	// Auto-generate when inputs change
	$effect(() => {
		if (personType === 'fisica') {
			if (nombre && apellidoPaterno && fechaNacimiento) {
				generateRFC();
			}
		} else {
			if (razonSocial && fechaConstitucion) {
				generateRFC();
			}
		}
	});
</script>

<svelte:head>
	<title>Generador RFC - catalogmx</title>
	<meta name="description" content="Genera RFC para personas físicas y morales con homoclave calculada según algoritmo oficial del SAT." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/generadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Generadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">RFC</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-blue-100 dark:bg-blue-900/30">
				<CreditCard class="h-8 w-8 text-blue-600 dark:text-blue-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Generador RFC
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Genera RFC con homoclave según algoritmo oficial del SAT
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Algoritmo oficial SAT</p>
				<p>Generación de RFC con homoclave calculada y dígito verificador. Incluye validación de palabras inconvenientes.</p>
			</div>
		</div>
	</div>
</section>

<!-- Generator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Type selector -->
		<div class="mb-6">
			<div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 p-1 bg-slate-50 dark:bg-slate-800/50">
				<button
					class="px-4 py-2 rounded-md text-sm font-medium transition-colors {personType === 'fisica' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					onclick={() => {
						personType = 'fisica';
						rfcGenerado = '';
						pasos = [];
					}}
				>
					<User class="h-4 w-4 inline mr-2" />
					Persona Física
				</button>
				<button
					class="px-4 py-2 rounded-md text-sm font-medium transition-colors {personType === 'moral' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					onclick={() => {
						personType = 'moral';
						rfcGenerado = '';
						pasos = [];
					}}
				>
					<Building2 class="h-4 w-4 inline mr-2" />
					Persona Moral
				</button>
			</div>
		</div>

		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Input Form -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					{#if personType === 'fisica'}
						<User class="h-5 w-5 text-brand-500" />
						Datos personales
					{:else}
						<Building2 class="h-5 w-5 text-brand-500" />
						Datos de la empresa
					{/if}
				</h2>

				{#if personType === 'fisica'}
					<div class="space-y-5">
						<div>
							<label for="nombre" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Nombre(s) *
							</label>
							<input
								id="nombre"
								type="text"
								bind:value={nombre}
								class="input"
								placeholder="Juan Carlos"
							/>
						</div>

						<div>
							<label for="paterno" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Apellido Paterno *
							</label>
							<input
								id="paterno"
								type="text"
								bind:value={apellidoPaterno}
								class="input"
								placeholder="García"
							/>
						</div>

						<div>
							<label for="materno" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Apellido Materno
							</label>
							<input
								id="materno"
								type="text"
								bind:value={apellidoMaterno}
								class="input"
								placeholder="López"
							/>
						</div>

						<div>
							<label for="fecha" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Fecha de Nacimiento *
							</label>
							<input
								id="fecha"
								type="date"
								bind:value={fechaNacimiento}
								class="input"
							/>
						</div>
					</div>
				{:else}
					<div class="space-y-5">
						<div>
							<label for="razon" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Razón Social *
							</label>
							<input
								id="razon"
								type="text"
								bind:value={razonSocial}
								class="input"
								placeholder="Comercializadora de Productos del Norte S.A. de C.V."
							/>
						</div>

						<div>
							<label for="fechaConst" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
								Fecha de Constitución *
							</label>
							<input
								id="fechaConst"
								type="date"
								bind:value={fechaConstitucion}
								class="input"
							/>
						</div>

						<div class="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
							<div class="flex gap-2 text-sm text-slate-600 dark:text-slate-400">
								<AlertCircle class="h-4 w-4 flex-shrink-0 mt-0.5" />
								<p>
									Se eliminarán automáticamente las palabras reservadas como S.A., DE, C.V., etc.
								</p>
							</div>
						</div>
					</div>
				{/if}
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					RFC Generado
				</h2>

				{#if rfcGenerado}
					<div class="space-y-6">
						<!-- RFC Result -->
						<div class="p-6 bg-gradient-to-br from-brand-50 to-brand-100 dark:from-brand-900/20 dark:to-brand-800/20 rounded-lg border border-brand-200 dark:border-brand-800">
							<div class="text-sm font-medium text-brand-700 dark:text-brand-300 mb-2">
								RFC Generado
							</div>
							<div class="text-4xl font-bold text-brand-900 dark:text-brand-100 tracking-wider font-mono">
								{rfcGenerado}
							</div>
						</div>

						<!-- Steps -->
						<div>
							<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
								Pasos de generación
							</h3>
							<div class="space-y-2">
								{#each pasos as paso}
									<div class="text-sm p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg font-mono">
										{paso}
									</div>
								{/each}
							</div>
						</div>

						<!-- Copy button -->
						<button
							class="btn btn-primary w-full"
							onclick={() => {
								navigator.clipboard.writeText(rfcGenerado);
							}}
						>
							Copiar RFC
						</button>
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<CreditCard class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Completa los campos para generar el RFC</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este generador utiliza el algoritmo oficial del SAT para calcular el RFC.
				El RFC generado incluye la homoclave y dígito verificador calculados. Para obtener el RFC oficial,
				debes tramitarlo ante el SAT con documentación válida.
			</p>
		</div>
	</div>
</section>
