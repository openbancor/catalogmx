<script lang="ts">
	import { User, Info, CheckCircle2, AlertCircle } from 'lucide-svelte';
	import { base } from '$app/paths';
	import { CURPValidator, generateCurp } from '$lib/catalogmx';
	import statesData from '../../../../../shared-data/inegi/states.json';

	// State
	let nombre = $state('');
	let apellidoPaterno = $state('');
	let apellidoMaterno = $state('');
	let fechaNacimiento = $state('');
	let sexo = $state<'H' | 'M'>('H');
	let estadoNacimiento = $state('');

	let curpGenerado = $state('');
	let pasos = $state<string[]>([]);
	let decoded = $state<{ label: string; value: string }[]>([]);

	// Prepare states for select
	const states = statesData.map((s) => ({
		code: s.code,
		name: s.name
	}));

	function parseIsoDate(value: string): { year: number; month: number; day: number } | null {
		const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
		if (!match) return null;
		return {
			year: Number(match[1]),
			month: Number(match[2]),
			day: Number(match[3])
		};
	}

	function formatDate(date: Date | null): string {
		if (!date) return 'Fecha no disponible';
		const dd = date.getDate().toString().padStart(2, '0');
		const mm = (date.getMonth() + 1).toString().padStart(2, '0');
		const yyyy = date.getFullYear();
		return `${dd}/${mm}/${yyyy}`;
	}

	function getDifferentiator(dateValue: string): string {
		const parts = parseIsoDate(dateValue);
		if (!parts) {
			throw new Error('Fecha inválida');
		}
		return parts.year < 2000 ? '0' : 'A';
	}

	function generateCURP(): void {
		pasos = [];
		curpGenerado = '';
		decoded = [];

		try {
			if (!nombre || !apellidoPaterno || !fechaNacimiento || !estadoNacimiento) {
				pasos.push('❌ Por favor completa todos los campos requeridos');
				return;
			}

			const stateName = states.find((s) => s.code === estadoNacimiento)?.name;
			if (!stateName) {
				pasos.push('❌ Estado inválido');
				return;
			}

			const differentiator = getDifferentiator(fechaNacimiento);
			curpGenerado = generateCurp({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento,
				sexo,
				estado: stateName,
				differentiator
			});

			const validator = new CURPValidator(curpGenerado);
			const birthDate = validator.getBirthDate();
			const gender = validator.getGender();
			const genderLabel = gender === 'H' ? 'Hombre' : gender === 'M' ? 'Mujer' : 'No disponible';
			const stateCode = validator.getStateCode();
			const stateLabel = states.find((s) => s.code === stateCode)?.name || 'Desconocido';

			pasos.push(`✅ CURP generada: ${curpGenerado}`);
			pasos.push(`Fecha en CURP: ${formatDate(birthDate)}`);
			pasos.push(`Sexo: ${genderLabel}`);
			pasos.push(`Estado: ${stateCode ?? 'NE'} (${stateLabel})`);
			pasos.push(`Dígito verificador: ${validator.validateCheckDigit() ? 'OK' : 'Error'}`);

			decoded = [
				{ label: 'Primeras 4 letras', value: `${curpGenerado.substring(0, 4)} (Apellidos y nombre)` },
				{ label: 'Fecha de nacimiento', value: `${curpGenerado.substring(4, 10)} (AAMMDD)` },
				{ label: 'Sexo', value: `${curpGenerado[10]} (${genderLabel})` },
				{ label: 'Estado', value: `${curpGenerado.substring(11, 13)} (${stateLabel})` },
				{ label: 'Consonantes internas', value: curpGenerado.substring(13, 16) },
				{ label: 'Homoclave', value: curpGenerado.substring(16, 18) }
			];
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
