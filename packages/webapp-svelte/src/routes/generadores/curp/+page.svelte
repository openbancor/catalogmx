<script lang="ts">
	import { User, Info, Calendar, MapPin, CheckCircle2, AlertCircle } from 'lucide-svelte';
	import { base } from '$app/paths';
	import statesData from '../../../../../shared-data/inegi/states.json';

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
	const EXCLUDED_WORDS = ['DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI'];
	const CACOPHONIC_WORDS = [
		'BACA', 'BAKA', 'BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA',
		'KAKO', 'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO', 'COLA', 'CULO',
		'FALO', 'FETO', 'GETA', 'GUEI', 'GUEY', 'JETA', 'JOTO', 'KACA', 'KACO',
		'KAGA', 'KAGO', 'KOGE', 'KOGI', 'KOJA', 'KOJE', 'KOJI', 'KOJO', 'KOLA',
		'KULO', 'LILO', 'LOCA', 'LOCO', 'LOKA', 'LOKO', 'MAME', 'MAMO', 'MEAR',
		'MEAS', 'MEON', 'MIAR', 'MION', 'MOCO', 'MOKO', 'MULA', 'MULO', 'NACA',
		'NACO', 'PEDA', 'PEDO', 'PENE', 'PIPI', 'PITO', 'POPO', 'PUTA', 'PUTO',
		'QULO', 'RATA', 'ROBA', 'ROBE', 'ROBO', 'RUIN', 'SENO', 'TETA', 'VACA',
		'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY', 'WUEI', 'WUEY'
	];
	const VOCALES = 'AEIOU';
	const CONSONANTES = 'BCDFGHJKLMNPQRSTVWXYZ';
	const ALLOWED_CHARS = 'ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';

	// State
	let nombre = $state('');
	let apellidoPaterno = $state('');
	let apellidoMaterno = $state('');
	let fechaNacimiento = $state('');
	let sexo = $state<'H' | 'M'>('H');
	let estadoNacimiento = $state('');

	let curpGenerado = $state('');
	let pasos = $state<string[]>([]);
	let decoded = $state<{label: string, value: string}[]>([]);

	// Prepare states for select
	const states = statesData.map(s => ({
		code: s.code,
		name: s.name
	}));

	// Helper functions
	function cleanName(name: string): string {
		if (!name) return '';

		const upper = name.toUpperCase().trim();
		const words = upper.split(/\s+/).filter(w => !EXCLUDED_WORDS.includes(w));
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

	function getFirstConsonant(word: string): string {
		if (!word || word.length <= 1) return 'X';

		for (let i = 1; i < word.length; i++) {
			if (CONSONANTES.includes(word[i])) {
				return word[i];
			}
		}
		return 'X';
	}

	function generateLetters(): string {
		const paterno = cleanName(apellidoPaterno);
		const materno = cleanName(apellidoMaterno);
		const nombreClean = cleanName(nombre);

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
		if (nombreWords.length > 1) {
			if (nombreWords[0] === 'MARIA' || nombreWords[0] === 'JOSE' ||
			    nombreWords[0] === 'MA' || nombreWords[0] === 'MA.' ||
			    nombreWords[0] === 'J' || nombreWords[0] === 'J.') {
				nombreToUse = nombreWords.slice(1).join(' ');
			}
		}
		parts.push(nombreToUse[0]);

		let clave = parts.join('');

		// Check for cacophonic words
		if (CACOPHONIC_WORDS.includes(clave)) {
			clave = clave[0] + 'X' + clave.substring(2);
		}

		return clave;
	}

	function generateDate(): string {
		const date = new Date(fechaNacimiento);
		const yy = date.getFullYear().toString().substring(2);
		const mm = (date.getMonth() + 1).toString().padStart(2, '0');
		const dd = date.getDate().toString().padStart(2, '0');
		return yy + mm + dd;
	}

	function getStateCode(): string {
		const state = states.find(s => s.code === estadoNacimiento);
		return state ? state.code : 'NE';
	}

	function generateConsonants(): string {
		const paterno = cleanName(apellidoPaterno);
		const materno = cleanName(apellidoMaterno);
		const nombreClean = cleanName(nombre);

		const nombreWords = nombreClean.split(' ');
		let nombreToUse = nombreClean;
		if (nombreWords.length > 1) {
			if (nombreWords[0] === 'MARIA' || nombreWords[0] === 'JOSE' ||
			    nombreWords[0] === 'MA' || nombreWords[0] === 'MA.' ||
			    nombreWords[0] === 'J' || nombreWords[0] === 'J.') {
				nombreToUse = nombreWords.slice(1).join(' ');
			}
		}

		const consonants: string[] = [];
		consonants.push(getFirstConsonant(paterno));
		consonants.push(materno ? getFirstConsonant(materno) : 'X');
		consonants.push(getFirstConsonant(nombreToUse));

		return consonants.join('');
	}

	function calculateCheckDigit(curp17: string): string {
		const dictionary = '0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ';

		let suma = 0;
		for (let i = 0; i < 17; i++) {
			const charValue = dictionary.indexOf(curp17[i]);
			suma += charValue * (18 - i);
		}

		let digito = 10 - (suma % 10);
		if (digito === 10) digito = 0;

		return digito.toString();
	}

	function generateHomoclave(): string {
		const date = new Date(fechaNacimiento);
		const year = date.getFullYear();

		// Differentiator: 0 for before 2000, A for after
		const differentiator = year < 2000 ? '0' : 'A';

		// Build temp CURP (17 characters)
		const tempCurp =
			generateLetters() +
			generateDate() +
			sexo +
			getStateCode() +
			generateConsonants() +
			differentiator;

		// Calculate check digit
		const checkDigit = calculateCheckDigit(tempCurp);

		return differentiator + checkDigit;
	}

	function decodeCURP(curp: string) {
		decoded = [
			{ label: 'Primeras 4 letras', value: curp.substring(0, 4) + ' (Apellidos y nombre)' },
			{ label: 'Fecha de nacimiento', value: curp.substring(4, 10) + ' (AAMMDD)' },
			{ label: 'Sexo', value: curp[10] + (curp[10] === 'H' ? ' (Hombre)' : ' (Mujer)') },
			{ label: 'Estado', value: curp.substring(11, 13) + ' (' + states.find(s => s.code === curp.substring(11, 13))?.name + ')' },
			{ label: 'Consonantes internas', value: curp.substring(13, 16) },
			{ label: 'Homoclave', value: curp.substring(16, 18) }
		];
	}

	function generateCURP() {
		pasos = [];
		curpGenerado = '';
		decoded = [];

		try {
			if (!nombre || !apellidoPaterno || !fechaNacimiento || !estadoNacimiento) {
				pasos.push('❌ Por favor completa todos los campos requeridos');
				return;
			}

			const letters = generateLetters();
			pasos.push(`1. Letras del nombre: ${letters}`);

			const dateStr = generateDate();
			pasos.push(`2. Fecha de nacimiento: ${dateStr}`);

			pasos.push(`3. Sexo: ${sexo}`);

			const stateCode = getStateCode();
			const stateName = states.find(s => s.code === stateCode)?.name || 'Desconocido';
			pasos.push(`4. Estado: ${stateCode} (${stateName})`);

			const consonants = generateConsonants();
			pasos.push(`5. Consonantes internas: ${consonants}`);

			const homoclave = generateHomoclave();
			pasos.push(`6. Homoclave: ${homoclave}`);

			curpGenerado = letters + dateStr + sexo + stateCode + consonants + homoclave;
			pasos.push(`✅ CURP generada: ${curpGenerado}`);

			decodeCURP(curpGenerado);
		} catch (error) {
			if (error instanceof Error) {
				pasos.push(`❌ Error: ${error.message}`);
			}
		}
	}

	// Auto-generate when inputs change
	$effect(() => {
		if (nombre && apellidoPaterno && fechaNacimiento && estadoNacimiento) {
			generateCURP();
		}
	});
</script>

<svelte:head>
	<title>Generador CURP - catalogmx</title>
	<meta name="description" content="Genera CURP con dígito verificador según algoritmo oficial de RENAPO." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/generadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Generadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">CURP</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
				<User class="h-8 w-8 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Generador CURP
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Genera CURP con dígito verificador según algoritmo oficial de RENAPO
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Algoritmo oficial RENAPO</p>
				<p>Generación de CURP con dígito verificador calculado. Incluye validación de palabras inconvenientes.</p>
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
					<User class="h-5 w-5 text-brand-500" />
					Datos personales
				</h2>

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

					<div>
						<label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Sexo *
						</label>
						<div class="flex gap-4">
							<label class="flex items-center gap-2 cursor-pointer">
								<input
									type="radio"
									bind:group={sexo}
									value="H"
									class="h-4 w-4 text-brand-500 focus:ring-brand-500"
								/>
								<span class="text-sm text-slate-700 dark:text-slate-300">Hombre</span>
							</label>
							<label class="flex items-center gap-2 cursor-pointer">
								<input
									type="radio"
									bind:group={sexo}
									value="M"
									class="h-4 w-4 text-brand-500 focus:ring-brand-500"
								/>
								<span class="text-sm text-slate-700 dark:text-slate-300">Mujer</span>
							</label>
						</div>
					</div>

					<div>
						<label for="estado" class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
							Estado de Nacimiento *
						</label>
						<select
							id="estado"
							bind:value={estadoNacimiento}
							class="input"
						>
							<option value="">Selecciona un estado</option>
							{#each states as state}
								<option value={state.code}>{state.name}</option>
							{/each}
						</select>
					</div>
				</div>
			</div>

			<!-- Results -->
			<div class="card p-6">
				<h2 class="text-xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					CURP Generada
				</h2>

				{#if curpGenerado}
					<div class="space-y-6">
						<!-- CURP Result -->
						<div class="p-6 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 rounded-lg border border-green-200 dark:border-green-800">
							<div class="text-sm font-medium text-green-700 dark:text-green-300 mb-2">
								CURP Generada
							</div>
							<div class="text-3xl font-bold text-green-900 dark:text-green-100 tracking-wider font-mono break-all">
								{curpGenerado}
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

						<!-- Decoded Info -->
						{#if decoded.length > 0}
							<div>
								<h3 class="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">
									Información decodificada
								</h3>
								<div class="space-y-2">
									{#each decoded as item}
										<div class="flex justify-between text-sm p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
											<span class="text-slate-600 dark:text-slate-400">{item.label}:</span>
											<span class="font-medium text-slate-900 dark:text-slate-100 font-mono">{item.value}</span>
										</div>
									{/each}
								</div>
							</div>
						{/if}

						<!-- Copy button -->
						<button
							class="btn btn-primary w-full"
							onclick={() => {
								navigator.clipboard.writeText(curpGenerado);
							}}
						>
							Copiar CURP
						</button>
					</div>
				{:else}
					<div class="flex items-center justify-center h-64 text-slate-400 dark:text-slate-500">
						<div class="text-center">
							<User class="h-12 w-12 mx-auto mb-3 opacity-50" />
							<p class="text-sm">Completa los campos para generar la CURP</p>
						</div>
					</div>
				{/if}
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Nota:</strong> Este generador utiliza el algoritmo oficial de RENAPO para calcular la CURP.
				La CURP generada incluye el dígito verificador calculado. Para obtener la CURP oficial,
				debes tramitarla ante RENAPO con documentación válida. La homoclave asignada oficialmente puede diferir
				de la calculada aquí, ya que RENAPO asigna homoclaves únicas para evitar duplicados.
			</p>
		</div>
	</div>
</section>
