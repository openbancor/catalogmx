<script lang="ts">
	import {
		User,
		Building2,
		Info,
		RefreshCw,
		Copy,
		CheckCircle2,
		AlertCircle,
		Loader2,
		Sparkles,
		CreditCard,
		Phone,
		MapPin
	} from 'lucide-svelte';
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import {
		generateRfcPersonaFisica,
		generateRfcPersonaMoral,
		generateCurp,
		generateClabe,
		generateNss,
		validateRfc,
		validateCurp,
		validateClabe,
		validateNss,
		RFCValidator
	} from '$lib/catalogmx';
	import { query } from '$lib/db';
	import { fakerES_MX as faker } from '@faker-js/faker';
	import SearchableSelect from '$lib/components/SearchableSelect.svelte';

	type ValidationStatus = 'empty' | 'validating' | 'valid' | 'invalid' | 'warning';

	interface FieldValidation {
		status: ValidationStatus;
		message?: string;
	}

	// Data from DB
	let states = $state<{ code: string; name: string }[]>([]);
	let banks = $state<{ code: string; name: string; full_name: string }[]>([]);
	let plazas = $state<{ codigo: string; estado: string; plaza: string }[]>([]);
	let dataReady = $state(false);
	let copied = $state<string | null>(null);

	// Form data
	let nombre = $state('');
	let apellidoPaterno = $state('');
	let apellidoMaterno = $state('');
	let fechaNacimiento = $state('');
	let sexo = $state<'H' | 'M'>('H');
	let estadoNacimiento = $state('');
	let estadoNacimientoNombre = $state('');

	// Identifiers (can be entered manually OR generated)
	let rfc = $state('');
	let curp = $state('');
	let nss = $state('');
	let clabe = $state('');

	// Banking extracted from CLABE
	let bancoCode = $state('');
	let bancoNombre = $state('');
	let plazaCode = $state('');
	let plazaLocalidad = $state('');
	let cuenta = $state('');

	// Address
	let cp = $state('');
	let colonia = $state('');
	let municipio = $state('');
	let estado = $state('');
	let calle = $state('');
	let numero = $state('');

	// Contact
	let telefono = $state('');
	let email = $state('');

	// Validation states
	let rfcValidation = $state<FieldValidation>({ status: 'empty' });
	let curpValidation = $state<FieldValidation>({ status: 'empty' });
	let nssValidation = $state<FieldValidation>({ status: 'empty' });
	let clabeValidation = $state<FieldValidation>({ status: 'empty' });
	let cpValidation = $state<FieldValidation>({ status: 'empty' });
	let telefonoValidation = $state<FieldValidation>({ status: 'empty' });
	let emailValidation = $state<FieldValidation>({ status: 'empty' });

	// Colonias for CP
	let colonias = $state<{ asentamiento: string; municipio: string; estado: string }[]>([]);

	// Mode flags
	let autoGenerateRfc = $state(true);
	let autoGenerateCurp = $state(true);

	// Standalone RFC validator (works for both física and moral)
	let rfcStandalone = $state('');
	let rfcStandaloneValidation = $state<FieldValidation>({ status: 'empty' });
	let rfcStandaloneType = $state<'fisica' | 'moral' | 'generico' | 'invalido' | null>(null);
	let rfcStandaloneDate = $state<string | null>(null);
	let rfcStandaloneDetails = $state<Record<string, boolean> | null>(null);

	// Persona Moral generation
	let razonSocial = $state('');
	let fechaConstitucion = $state('');
	let rfcMoral = $state('');
	let rfcMoralValidation = $state<FieldValidation>({ status: 'empty' });

	function validateRfcStandalone(): void {
		if (!rfcStandalone) {
			rfcStandaloneValidation = { status: 'empty' };
			rfcStandaloneType = null;
			rfcStandaloneDate = null;
			rfcStandaloneDetails = null;
			return;
		}

		const upperRfc = rfcStandalone.toUpperCase().trim();

		try {
			const validator = new RFCValidator(upperRfc);
			const isValid = validator.validate(true);
			const details = validator.getValidationDetails(true);
			const type = validator.detectType();
			const date = validator.getDate();

			rfcStandaloneDetails = details;
			rfcStandaloneType = type;
			rfcStandaloneDate = date ? date.toLocaleDateString('es-MX', { year: 'numeric', month: 'long', day: 'numeric' }) : null;

			if (isValid) {
				rfcStandaloneValidation = {
					status: 'valid',
					message: `RFC válido - ${type === 'fisica' ? 'Persona Física' : type === 'moral' ? 'Persona Moral' : 'Genérico'}`
				};
			} else {
				const failedChecks = Object.entries(details).filter(([, v]) => !v).map(([k]) => k);
				rfcStandaloneValidation = {
					status: 'invalid',
					message: `RFC inválido: ${failedChecks.join(', ')}`
				};
			}
		} catch (e) {
			rfcStandaloneValidation = { status: 'invalid', message: 'Error al validar RFC' };
			rfcStandaloneType = null;
			rfcStandaloneDate = null;
			rfcStandaloneDetails = null;
		}
	}

	function generateRfcMoralFromData(): void {
		if (!razonSocial || !fechaConstitucion) return;

		try {
			const generated = generateRfcPersonaMoral({ razonSocial, fechaConstitucion });
			rfcMoral = generated;
			validateRfcMoralField();
		} catch (e) {
			rfcMoralValidation = { status: 'invalid', message: 'Error al generar RFC' };
		}
	}

	function validateRfcMoralField(): void {
		if (!rfcMoral) {
			rfcMoralValidation = { status: 'empty' };
			return;
		}

		const isValid = validateRfc(rfcMoral);
		if (isValid) {
			rfcMoralValidation = { status: 'valid', message: 'RFC válido' };
		} else {
			rfcMoralValidation = { status: 'invalid', message: 'RFC inválido' };
		}
	}

	onMount(async () => {
		try {
			const [statesData, banksData, plazasData] = await Promise.all([
				query<{ code: string; name: string }>('SELECT code, name FROM inegi_states ORDER BY name'),
				query<{ code: string; name: string; full_name: string }>('SELECT code, name, full_name FROM banxico_banks WHERE spei = 1 ORDER BY name'),
				query<{ codigo: string; estado: string; plaza: string }>('SELECT DISTINCT codigo, estado, plaza FROM banxico_codigos_plaza ORDER BY estado, plaza')
			]);
			states = statesData;
			banks = banksData;
			plazas = plazasData;
			dataReady = true;
		} catch (error) {
			console.error('Error loading data:', error);
			dataReady = true;
		}
	});

	// Derived data for selects
	const stateOptions = $derived(states.map(s => ({ value: s.code, label: s.name })));
	const bankOptions = $derived(banks.map(b => ({ value: b.code, label: b.name, searchText: `${b.name} ${b.full_name}`.toLowerCase() })));

	function getDifferentiator(dateValue: string): string {
		const year = parseInt(dateValue.substring(0, 4));
		return year < 2000 ? '0' : 'A';
	}

	// Auto-generate RFC when personal data changes
	$effect(() => {
		if (autoGenerateRfc && nombre && apellidoPaterno && fechaNacimiento) {
			try {
				const newRfc = generateRfcPersonaFisica({
					nombre,
					apellidoPaterno,
					apellidoMaterno,
					fechaNacimiento
				});
				rfc = newRfc;
				validateRfcField();
			} catch {
				// Ignore generation errors
			}
		}
	});

	// Auto-generate CURP when personal data changes
	$effect(() => {
		if (autoGenerateCurp && nombre && apellidoPaterno && fechaNacimiento && estadoNacimientoNombre) {
			try {
				const newCurp = generateCurp({
					nombre,
					apellidoPaterno,
					apellidoMaterno,
					fechaNacimiento,
					sexo,
					estado: estadoNacimientoNombre,
					differentiator: getDifferentiator(fechaNacimiento)
				});
				curp = newCurp;
				validateCurpField();
			} catch {
				// Ignore generation errors
			}
		}
	});

	// Validate RFC
	function validateRfcField(): void {
		if (!rfc) {
			rfcValidation = { status: 'empty' };
			return;
		}

		const upperRfc = rfc.toUpperCase();
		if (upperRfc.length < 12) {
			rfcValidation = { status: 'invalid', message: 'RFC muy corto' };
			return;
		}

		if (upperRfc.length > 13) {
			rfcValidation = { status: 'invalid', message: 'RFC muy largo' };
			return;
		}

		try {
			const isValid = validateRfc(upperRfc);
			if (isValid) {
				rfcValidation = { status: 'valid', message: 'RFC válido' };
			} else {
				rfcValidation = { status: 'invalid', message: 'RFC inválido' };
			}
		} catch {
			rfcValidation = { status: 'invalid', message: 'Error al validar RFC' };
		}
	}

	// Validate CURP
	function validateCurpField(): void {
		if (!curp) {
			curpValidation = { status: 'empty' };
			return;
		}

		const upperCurp = curp.toUpperCase();
		if (upperCurp.length !== 18) {
			curpValidation = { status: 'invalid', message: `CURP debe tener 18 caracteres (tiene ${upperCurp.length})` };
			return;
		}

		try {
			const isValid = validateCurp(upperCurp);
			if (isValid) {
				curpValidation = { status: 'valid', message: 'CURP válido' };
				// Check consistency with RFC if both present
				if (rfc && rfc.length >= 10) {
					const rfcBase = rfc.substring(0, 10).toUpperCase();
					const curpBase = upperCurp.substring(0, 10);
					if (rfcBase !== curpBase) {
						curpValidation = { status: 'warning', message: 'CURP válido pero no coincide con RFC' };
					}
				}
			} else {
				curpValidation = { status: 'invalid', message: 'CURP inválido (dígito verificador)' };
			}
		} catch {
			curpValidation = { status: 'invalid', message: 'Error al validar CURP' };
		}
	}

	// Validate NSS
	function validateNssField(): void {
		if (!nss) {
			nssValidation = { status: 'empty' };
			return;
		}

		const cleanNss = nss.replace(/\D/g, '');
		if (cleanNss.length !== 11) {
			nssValidation = { status: 'invalid', message: `NSS debe tener 11 dígitos (tiene ${cleanNss.length})` };
			return;
		}

		try {
			const isValid = validateNss(cleanNss);
			if (isValid) {
				// Check birth year consistency
				const nssBirthYear = cleanNss.substring(4, 6);
				if (fechaNacimiento) {
					const dateBirthYear = fechaNacimiento.substring(2, 4);
					if (nssBirthYear !== dateBirthYear) {
						nssValidation = { status: 'warning', message: `NSS válido pero año (${nssBirthYear}) no coincide con fecha de nacimiento (${dateBirthYear})` };
						return;
					}
				}
				nssValidation = { status: 'valid', message: 'NSS válido' };
			} else {
				nssValidation = { status: 'invalid', message: 'NSS inválido (dígito verificador)' };
			}
		} catch {
			nssValidation = { status: 'invalid', message: 'Error al validar NSS' };
		}
	}

	// Validate CLABE and extract bank/plaza/account
	function validateClabeField(): void {
		if (!clabe) {
			clabeValidation = { status: 'empty' };
			bancoCode = '';
			bancoNombre = '';
			plazaCode = '';
			plazaLocalidad = '';
			cuenta = '';
			return;
		}

		const cleanClabe = clabe.replace(/\D/g, '');
		if (cleanClabe.length !== 18) {
			clabeValidation = { status: 'invalid', message: `CLABE debe tener 18 dígitos (tiene ${cleanClabe.length})` };
			return;
		}

		try {
			const isValid = validateClabe(cleanClabe);
			if (isValid) {
				// Extract components
				const extractedBankCode = cleanClabe.substring(0, 3);
				const extractedPlazaCode = cleanClabe.substring(3, 6);
				const extractedAccount = cleanClabe.substring(6, 17);

				// Look up bank name
				const bank = banks.find(b => b.code === extractedBankCode);
				bancoCode = extractedBankCode;
				bancoNombre = bank?.name || `Banco ${extractedBankCode}`;

				// Look up plaza
				const plaza = plazas.find(p => p.codigo === extractedPlazaCode);
				plazaCode = extractedPlazaCode;
				plazaLocalidad = plaza?.plaza || '';

				cuenta = extractedAccount;

				if (bank) {
					clabeValidation = { status: 'valid', message: `CLABE válida - ${bank.name}` };
				} else {
					clabeValidation = { status: 'warning', message: 'CLABE válida pero banco desconocido' };
				}
			} else {
				clabeValidation = { status: 'invalid', message: 'CLABE inválida (dígito verificador)' };
			}
		} catch {
			clabeValidation = { status: 'invalid', message: 'Error al validar CLABE' };
		}
	}

	// Lookup postal code
	async function lookupPostalCode(): Promise<void> {
		if (!cp || cp.length !== 5) {
			cpValidation = { status: cp ? 'invalid' : 'empty', message: cp ? 'C.P. debe tener 5 dígitos' : undefined };
			colonias = [];
			return;
		}

		cpValidation = { status: 'validating' };

		try {
			const results = await query<{ asentamiento: string; municipio: string; estado: string }>(
				`SELECT asentamiento, municipio, estado FROM codigos_postales WHERE cp = '${cp}' ORDER BY asentamiento`
			);

			if (results.length > 0) {
				colonias = results;
				colonia = results[0].asentamiento;
				municipio = results[0].municipio;
				estado = results[0].estado;
				cpValidation = { status: 'valid', message: `${results.length} colonia(s) encontrada(s)` };
			} else {
				colonias = [];
				cpValidation = { status: 'invalid', message: 'Código postal no encontrado' };
			}
		} catch {
			cpValidation = { status: 'invalid', message: 'Error al buscar código postal' };
		}
	}

	// Validate phone
	function validatePhoneField(): void {
		if (!telefono) {
			telefonoValidation = { status: 'empty' };
			return;
		}

		const cleanPhone = telefono.replace(/\D/g, '');
		if (cleanPhone.length !== 10) {
			telefonoValidation = { status: 'invalid', message: `Teléfono debe tener 10 dígitos (tiene ${cleanPhone.length})` };
			return;
		}

		// Check for valid Mexican area codes
		const prefix = cleanPhone.substring(0, 2);
		const validPrefixes = ['55', '56', '33', '81', '44', '22', '66', '99', '61', '62', '64', '65', '67', '68', '69'];
		if (validPrefixes.includes(prefix) || (parseInt(cleanPhone.substring(0, 3)) >= 200 && parseInt(cleanPhone.substring(0, 3)) <= 999)) {
			telefonoValidation = { status: 'valid', message: 'Teléfono válido' };
		} else {
			telefonoValidation = { status: 'warning', message: 'Prefijo no reconocido' };
		}
	}

	// Validate email
	function validateEmailField(): void {
		if (!email) {
			emailValidation = { status: 'empty' };
			return;
		}

		const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
		if (emailRegex.test(email)) {
			emailValidation = { status: 'valid', message: 'Email válido' };
		} else {
			emailValidation = { status: 'invalid', message: 'Email inválido' };
		}
	}

	// Generate random personal data
	function generateRandomPersonalData(): void {
		const randomSexo: 'H' | 'M' = faker.helpers.arrayElement(['H', 'M']);
		sexo = randomSexo;
		nombre = faker.person.firstName(randomSexo === 'H' ? 'male' : 'female');
		apellidoPaterno = faker.person.lastName().split(' ')[0];
		apellidoMaterno = Math.random() < 0.15 ? '' : faker.person.lastName().split(' ')[0];
		fechaNacimiento = faker.date.birthdate({ min: 1950, max: 2005, mode: 'year' }).toISOString().split('T')[0];

		if (states.length > 0) {
			const randomState = faker.helpers.arrayElement(states);
			estadoNacimiento = randomState.code;
			estadoNacimientoNombre = randomState.name;
		}
	}

	// Generate NSS based on current birth date
	function generateRandomNss(): void {
		if (!fechaNacimiento) return;

		const birthYear = parseInt(fechaNacimiento.substring(0, 4));
		const birthYearForNss = fechaNacimiento.substring(2, 4);
		const workStartAge = faker.number.int({ min: 18, max: 35 });
		const registrationYear = String((birthYear + workStartAge) % 100).padStart(2, '0');
		const subdelegation = String(faker.number.int({ min: 1, max: 97 })).padStart(2, '0');
		const sequential = String(faker.number.int({ min: 1, max: 9999 })).padStart(4, '0');
		nss = generateNss(subdelegation, registrationYear, birthYearForNss, sequential);
		validateNssField();
	}

	// Generate CLABE based on current bank/plaza or random
	function generateRandomClabe(): void {
		const bank = bancoCode || (banks.length > 0 ? faker.helpers.arrayElement(banks).code : '002');
		const plaza = plazaCode || (plazas.length > 0 ? faker.helpers.arrayElement(plazas).codigo : '180');
		const accountNumber = faker.string.numeric(11);
		clabe = generateClabe(bank, plaza, accountNumber);
		validateClabeField();
	}

	// Generate random address
	async function generateRandomAddress(): Promise<void> {
		const majorCities = ['Ciudad de México', 'Jalisco', 'Nuevo León', 'México', 'Puebla', 'Guanajuato'];
		const randomState = faker.helpers.arrayElement(majorCities);

		try {
			const result = await query<{ cp: string; asentamiento: string; municipio: string; estado: string }>(
				`SELECT cp, asentamiento, municipio, estado FROM codigos_postales WHERE estado = '${randomState}' ORDER BY RANDOM() LIMIT 1`
			);

			if (result[0]) {
				cp = result[0].cp;
				await lookupPostalCode();
				colonia = result[0].asentamiento;
			}
		} catch {
			// Fallback
			cp = '06600';
			await lookupPostalCode();
		}

		calle = faker.location.street();
		numero = faker.string.numeric({ length: { min: 1, max: 4 } });
	}

	// Generate random contact
	function generateRandomContact(): void {
		telefono = faker.string.numeric(10);
		validatePhoneField();
		email = faker.internet.email({ firstName: nombre || 'usuario', lastName: apellidoPaterno || 'ejemplo' }).toLowerCase();
		validateEmailField();
	}

	// Copy to clipboard
	function copyToClipboard(text: string, field: string): void {
		navigator.clipboard.writeText(text);
		copied = field;
		setTimeout(() => { copied = null; }, 2000);
	}

	// Clear all fields
	function clearAll(): void {
		nombre = '';
		apellidoPaterno = '';
		apellidoMaterno = '';
		fechaNacimiento = '';
		sexo = 'H';
		estadoNacimiento = '';
		estadoNacimientoNombre = '';
		rfc = '';
		curp = '';
		nss = '';
		clabe = '';
		bancoCode = '';
		bancoNombre = '';
		plazaCode = '';
		plazaLocalidad = '';
		cuenta = '';
		cp = '';
		colonia = '';
		municipio = '';
		estado = '';
		calle = '';
		numero = '';
		telefono = '';
		email = '';
		colonias = [];

		rfcValidation = { status: 'empty' };
		curpValidation = { status: 'empty' };
		nssValidation = { status: 'empty' };
		clabeValidation = { status: 'empty' };
		cpValidation = { status: 'empty' };
		telefonoValidation = { status: 'empty' };
		emailValidation = { status: 'empty' };
	}

	// Generate all random data
	async function generateAll(): Promise<void> {
		generateRandomPersonalData();
		// Wait for effects to run
		await new Promise(resolve => setTimeout(resolve, 50));
		generateRandomNss();
		generateRandomClabe();
		await generateRandomAddress();
		generateRandomContact();
	}

	// Validation status icon component helper
	function getStatusColor(status: ValidationStatus): string {
		switch (status) {
			case 'valid': return 'text-green-500';
			case 'invalid': return 'text-red-500';
			case 'warning': return 'text-amber-500';
			case 'validating': return 'text-blue-500';
			default: return 'text-slate-400';
		}
	}

	// Mexican phone formatting
	function formatPhone(phone: string): string {
		const digits = phone.replace(/\D/g, '');
		if (digits.length !== 10) return phone;
		const prefix = digits.substring(0, 2);
		if (['55', '56', '33', '81'].includes(prefix)) {
			return `${digits.substring(0, 2)} ${digits.substring(2, 6)} ${digits.substring(6)}`;
		}
		return `${digits.substring(0, 3)} ${digits.substring(3, 6)} ${digits.substring(6)}`;
	}

	// Format CLABE with spaces
	function formatClabe(c: string): string {
		const digits = c.replace(/\D/g, '');
		if (digits.length !== 18) return c;
		return `${digits.substring(0, 3)} ${digits.substring(3, 6)} ${digits.substring(6, 10)} ${digits.substring(10, 14)} ${digits.substring(14)}`;
	}
</script>

<svelte:head>
	<title>Validador de Identidad - catalogmx</title>
	<meta name="description" content="Valida y completa datos de identidad mexicana: RFC, CURP, NSS, CLABE. Ingresa datos parciales y el sistema los valida y autocompleta." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/validadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Validadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">Identidad</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-green-100 dark:bg-green-900/30">
				<CheckCircle2 class="h-8 w-8 text-green-600 dark:text-green-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Validador de Identidad
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Ingresa datos parciales para validarlos y autocompletar campos derivados
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
			<Info class="h-5 w-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-blue-900 dark:text-blue-300">
				<p class="font-medium mb-1">Modo de uso</p>
				<p>Puedes ingresar datos manualmente para validarlos, o usar los botones de generación aleatoria para crear datos de prueba. Los identificadores (RFC, CURP) se generan automáticamente al ingresar datos personales.</p>
			</div>
		</div>
	</div>
</section>

<!-- RFC Validator (standalone - works for física and moral) -->
<section class="py-6 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Validador RFC (cualquier tipo) -->
			<div class="card p-6">
				<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
					<CheckCircle2 class="h-5 w-5 text-green-500" />
					Validar RFC
					<span class="text-xs font-normal text-slate-400">(física o moral)</span>
				</h3>
				<div class="space-y-4">
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
							RFC a validar
							{#if rfcStandaloneValidation.status === 'valid'}
								<CheckCircle2 class="h-4 w-4 text-green-500" />
							{:else if rfcStandaloneValidation.status === 'invalid'}
								<AlertCircle class="h-4 w-4 text-red-500" />
							{/if}
						</label>
						<div class="flex gap-2 mt-1">
							<input
								type="text"
								class="input font-mono flex-1 uppercase"
								bind:value={rfcStandalone}
								oninput={validateRfcStandalone}
								placeholder="XXXX000000XXX o XXX000000XXX"
								maxlength="13"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(rfcStandalone, 'rfc-standalone')}
								disabled={!rfcStandalone}
							>
								{copied === 'rfc-standalone' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if rfcStandaloneValidation.message}
							<p class="text-xs mt-1 {getStatusColor(rfcStandaloneValidation.status)}">{rfcStandaloneValidation.message}</p>
						{/if}
					</div>

					{#if rfcStandaloneDetails}
						<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-2 text-sm">
							<div class="grid grid-cols-2 gap-2">
								<div class="flex items-center gap-2">
									{#if rfcStandaloneDetails.generalRegex}
										<CheckCircle2 class="h-4 w-4 text-green-500" />
									{:else}
										<AlertCircle class="h-4 w-4 text-red-500" />
									{/if}
									<span class="text-slate-600 dark:text-slate-400">Formato</span>
								</div>
								<div class="flex items-center gap-2">
									{#if rfcStandaloneDetails.dateFormat}
										<CheckCircle2 class="h-4 w-4 text-green-500" />
									{:else}
										<AlertCircle class="h-4 w-4 text-red-500" />
									{/if}
									<span class="text-slate-600 dark:text-slate-400">Fecha</span>
								</div>
								<div class="flex items-center gap-2">
									{#if rfcStandaloneDetails.homoclave}
										<CheckCircle2 class="h-4 w-4 text-green-500" />
									{:else}
										<AlertCircle class="h-4 w-4 text-red-500" />
									{/if}
									<span class="text-slate-600 dark:text-slate-400">Homoclave</span>
								</div>
								<div class="flex items-center gap-2">
									{#if rfcStandaloneDetails.checksum}
										<CheckCircle2 class="h-4 w-4 text-green-500" />
									{:else}
										<AlertCircle class="h-4 w-4 text-red-500" />
									{/if}
									<span class="text-slate-600 dark:text-slate-400">Dígito verificador</span>
								</div>
							</div>
							{#if rfcStandaloneType}
								<div class="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-between">
									<span class="text-slate-500">Tipo:</span>
									<span class="font-medium text-slate-700 dark:text-slate-300">
										{rfcStandaloneType === 'fisica' ? 'Persona Física (13 caracteres)' :
										 rfcStandaloneType === 'moral' ? 'Persona Moral (12 caracteres)' :
										 rfcStandaloneType === 'generico' ? 'Genérico' : 'Inválido'}
									</span>
								</div>
							{/if}
							{#if rfcStandaloneDate}
								<div class="flex justify-between">
									<span class="text-slate-500">{rfcStandaloneType === 'moral' ? 'Fecha constitución:' : 'Fecha nacimiento:'}</span>
									<span class="font-medium text-slate-700 dark:text-slate-300">{rfcStandaloneDate}</span>
								</div>
							{/if}
						</div>
					{/if}
				</div>
			</div>

			<!-- Generador RFC Persona Moral -->
			<div class="card p-6">
				<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
					<Building2 class="h-5 w-5 text-purple-500" />
					Generar RFC Moral
					<span class="text-xs font-normal text-slate-400">(persona moral)</span>
				</h3>
				<div class="space-y-4">
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400">Razón Social</label>
						<input
							type="text"
							class="input mt-1"
							bind:value={razonSocial}
							oninput={generateRfcMoralFromData}
							placeholder="Nuevas Industrias Rodamex S.A. de C.V."
						/>
					</div>
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400">Fecha de Constitución</label>
						<input
							type="date"
							class="input mt-1"
							bind:value={fechaConstitucion}
							oninput={generateRfcMoralFromData}
						/>
					</div>
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
							RFC Generado
							{#if rfcMoralValidation.status === 'valid'}
								<CheckCircle2 class="h-4 w-4 text-green-500" />
							{:else if rfcMoralValidation.status === 'invalid'}
								<AlertCircle class="h-4 w-4 text-red-500" />
							{/if}
						</label>
						<div class="flex gap-2 mt-1">
							<input
								type="text"
								class="input font-mono flex-1 uppercase bg-slate-50 dark:bg-slate-800"
								bind:value={rfcMoral}
								oninput={validateRfcMoralField}
								placeholder="XXX000000XXX"
								maxlength="12"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(rfcMoral, 'rfc-moral')}
								disabled={!rfcMoral}
							>
								{copied === 'rfc-moral' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if rfcMoralValidation.message}
							<p class="text-xs mt-1 {getStatusColor(rfcMoralValidation.status)}">{rfcMoralValidation.message}</p>
						{/if}
					</div>
					{#if rfcMoral && razonSocial}
						<div class="p-3 bg-amber-50 dark:bg-amber-900/20 rounded-lg text-xs text-amber-700 dark:text-amber-300">
							<p><strong>Nota:</strong> La homoclave generada es calculada algorítmicamente. El SAT puede asignar una diferente para evitar duplicados.</p>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Main Form -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Action buttons -->
		<div class="mb-6 flex flex-wrap items-center gap-3">
			<button
				class="btn btn-primary flex items-center gap-2"
				onclick={generateAll}
				disabled={!dataReady}
			>
				<Sparkles class="h-4 w-4" />
				Generar Todo
			</button>
			<button
				class="btn btn-secondary flex items-center gap-2"
				onclick={clearAll}
			>
				Limpiar
			</button>
		</div>

		<div class="grid gap-6 lg:grid-cols-2">
			<!-- Datos Personales -->
			<div class="card p-6">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
						<User class="h-5 w-5 text-purple-500" />
						Datos Personales
					</h3>
					<button
						class="text-xs text-brand-500 hover:text-brand-600 flex items-center gap-1"
						onclick={generateRandomPersonalData}
					>
						<RefreshCw class="h-3 w-3" />
						Aleatorio
					</button>
				</div>
				<div class="space-y-4">
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400">Nombre(s)</label>
						<input
							type="text"
							class="input mt-1"
							bind:value={nombre}
							placeholder="Juan Carlos"
						/>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Apellido Paterno</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={apellidoPaterno}
								placeholder="García"
							/>
						</div>
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Apellido Materno</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={apellidoMaterno}
								placeholder="López (opcional)"
							/>
						</div>
					</div>
					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Fecha de nacimiento</label>
							<input
								type="date"
								class="input mt-1"
								bind:value={fechaNacimiento}
							/>
						</div>
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Sexo</label>
							<select class="input mt-1" bind:value={sexo}>
								<option value="H">Masculino</option>
								<option value="M">Femenino</option>
							</select>
						</div>
					</div>
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400">Estado de nacimiento</label>
						<select
							class="input mt-1"
							value={estadoNacimiento}
							onchange={(e) => {
								const selected = states.find(s => s.code === e.currentTarget.value);
								if (selected) {
									estadoNacimiento = selected.code;
									estadoNacimientoNombre = selected.name;
								}
							}}
						>
							<option value="">Seleccionar...</option>
							{#each states as state}
								<option value={state.code}>{state.name}</option>
							{/each}
						</select>
					</div>
				</div>
			</div>

			<!-- Identificadores -->
			<div class="card p-6">
				<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
					<CreditCard class="h-5 w-5 text-blue-500" />
					Identificadores
				</h3>
				<div class="space-y-4">
					<!-- RFC -->
					<div>
						<div class="flex items-center justify-between">
							<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
								RFC
								{#if rfcValidation.status === 'valid'}
									<CheckCircle2 class="h-4 w-4 text-green-500" />
								{:else if rfcValidation.status === 'invalid'}
									<AlertCircle class="h-4 w-4 text-red-500" />
								{/if}
							</label>
							<label class="flex items-center gap-1 text-xs text-slate-500">
								<input type="checkbox" bind:checked={autoGenerateRfc} class="rounded" />
								Auto-generar
							</label>
						</div>
						<div class="flex gap-2 mt-1">
							<input
								type="text"
								class="input font-mono flex-1 uppercase"
								bind:value={rfc}
								oninput={() => { autoGenerateRfc = false; validateRfcField(); }}
								placeholder="XXXX000000XXX"
								maxlength="13"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(rfc, 'rfc')}
								disabled={!rfc}
							>
								{copied === 'rfc' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if rfcValidation.message}
							<p class="text-xs mt-1 {getStatusColor(rfcValidation.status)}">{rfcValidation.message}</p>
						{/if}
					</div>

					<!-- CURP -->
					<div>
						<div class="flex items-center justify-between">
							<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
								CURP
								{#if curpValidation.status === 'valid'}
									<CheckCircle2 class="h-4 w-4 text-green-500" />
								{:else if curpValidation.status === 'invalid'}
									<AlertCircle class="h-4 w-4 text-red-500" />
								{:else if curpValidation.status === 'warning'}
									<AlertCircle class="h-4 w-4 text-amber-500" />
								{/if}
							</label>
							<label class="flex items-center gap-1 text-xs text-slate-500">
								<input type="checkbox" bind:checked={autoGenerateCurp} class="rounded" />
								Auto-generar
							</label>
						</div>
						<div class="flex gap-2 mt-1">
							<input
								type="text"
								class="input font-mono flex-1 uppercase text-sm"
								bind:value={curp}
								oninput={() => { autoGenerateCurp = false; validateCurpField(); }}
								placeholder="XXXX000000XXXXXX00"
								maxlength="18"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(curp, 'curp')}
								disabled={!curp}
							>
								{copied === 'curp' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if curpValidation.message}
							<p class="text-xs mt-1 {getStatusColor(curpValidation.status)}">{curpValidation.message}</p>
						{/if}
					</div>

					<!-- NSS -->
					<div>
						<div class="flex items-center justify-between">
							<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
								NSS
								{#if nssValidation.status === 'valid'}
									<CheckCircle2 class="h-4 w-4 text-green-500" />
								{:else if nssValidation.status === 'invalid'}
									<AlertCircle class="h-4 w-4 text-red-500" />
								{:else if nssValidation.status === 'warning'}
									<AlertCircle class="h-4 w-4 text-amber-500" />
								{/if}
							</label>
							<button
								class="text-xs text-brand-500 hover:text-brand-600 flex items-center gap-1"
								onclick={generateRandomNss}
								disabled={!fechaNacimiento}
							>
								<RefreshCw class="h-3 w-3" />
								Generar
							</button>
						</div>
						<div class="flex gap-2 mt-1">
							<input
								type="text"
								class="input font-mono flex-1"
								bind:value={nss}
								oninput={validateNssField}
								placeholder="00000000000"
								maxlength="11"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(nss, 'nss')}
								disabled={!nss}
							>
								{copied === 'nss' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if nssValidation.message}
							<p class="text-xs mt-1 {getStatusColor(nssValidation.status)}">{nssValidation.message}</p>
						{/if}
					</div>
				</div>
			</div>

			<!-- Datos Bancarios / CLABE -->
			<div class="card p-6">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
						<Building2 class="h-5 w-5 text-green-500" />
						Datos Bancarios
					</h3>
					<button
						class="text-xs text-brand-500 hover:text-brand-600 flex items-center gap-1"
						onclick={generateRandomClabe}
					>
						<RefreshCw class="h-3 w-3" />
						Generar CLABE
					</button>
				</div>
				<div class="space-y-4">
					<!-- CLABE Input -->
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
							CLABE (18 dígitos)
							{#if clabeValidation.status === 'valid'}
								<CheckCircle2 class="h-4 w-4 text-green-500" />
							{:else if clabeValidation.status === 'invalid'}
								<AlertCircle class="h-4 w-4 text-red-500" />
							{:else if clabeValidation.status === 'warning'}
								<AlertCircle class="h-4 w-4 text-amber-500" />
							{/if}
						</label>
						<div class="flex gap-2 mt-1">
							<input
								type="text"
								class="input font-mono flex-1"
								bind:value={clabe}
								oninput={validateClabeField}
								placeholder="000000000000000000"
								maxlength="18"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(clabe, 'clabe')}
								disabled={!clabe}
							>
								{copied === 'clabe' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if clabeValidation.message}
							<p class="text-xs mt-1 {getStatusColor(clabeValidation.status)}">{clabeValidation.message}</p>
						{/if}
					</div>

					<!-- Extracted CLABE data -->
					{#if clabeValidation.status === 'valid' || clabeValidation.status === 'warning'}
						<div class="p-3 bg-slate-50 dark:bg-slate-800 rounded-lg space-y-2">
							<p class="text-xs text-slate-500 font-medium mb-2">Datos extraídos de CLABE:</p>
							<div class="grid grid-cols-2 gap-2 text-sm">
								<div>
									<span class="text-slate-500">Banco:</span>
									<span class="font-medium text-slate-700 dark:text-slate-300 ml-1">{bancoNombre} ({bancoCode})</span>
								</div>
								<div>
									<span class="text-slate-500">Plaza:</span>
									<span class="font-medium text-slate-700 dark:text-slate-300 ml-1">{plazaCode} {plazaLocalidad ? `- ${plazaLocalidad}` : ''}</span>
								</div>
								<div class="col-span-2">
									<span class="text-slate-500">Cuenta:</span>
									<span class="font-mono font-medium text-slate-700 dark:text-slate-300 ml-1">{cuenta}</span>
								</div>
							</div>
							<div class="pt-2 border-t border-slate-200 dark:border-slate-700">
								<span class="text-xs text-slate-500">Formateada:</span>
								<span class="font-mono text-sm text-slate-700 dark:text-slate-300 ml-2">{formatClabe(clabe)}</span>
							</div>
						</div>
					{/if}
				</div>
			</div>

			<!-- Dirección -->
			<div class="card p-6">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
						<MapPin class="h-5 w-5 text-red-500" />
						Dirección
					</h3>
					<button
						class="text-xs text-brand-500 hover:text-brand-600 flex items-center gap-1"
						onclick={generateRandomAddress}
					>
						<RefreshCw class="h-3 w-3" />
						Aleatorio
					</button>
				</div>
				<div class="space-y-4">
					<!-- Código Postal -->
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
							Código Postal
							{#if cpValidation.status === 'valid'}
								<CheckCircle2 class="h-4 w-4 text-green-500" />
							{:else if cpValidation.status === 'invalid'}
								<AlertCircle class="h-4 w-4 text-red-500" />
							{:else if cpValidation.status === 'validating'}
								<Loader2 class="h-4 w-4 text-blue-500 animate-spin" />
							{/if}
						</label>
						<input
							type="text"
							class="input mt-1 font-mono w-32"
							bind:value={cp}
							oninput={() => {
								cp = cp.replace(/\D/g, '').slice(0, 5);
								if (cp.length === 5) lookupPostalCode();
							}}
							placeholder="00000"
							maxlength="5"
						/>
						{#if cpValidation.message}
							<p class="text-xs mt-1 {getStatusColor(cpValidation.status)}">{cpValidation.message}</p>
						{/if}
					</div>

					<!-- Colonia -->
					{#if colonias.length > 1}
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
								Colonia
								<span class="text-xs text-slate-400">({colonias.length} disponibles)</span>
							</label>
							<select
								class="input mt-1"
								bind:value={colonia}
								onchange={(e) => {
									const selected = colonias.find(c => c.asentamiento === e.currentTarget.value);
									if (selected) {
										municipio = selected.municipio;
										estado = selected.estado;
									}
								}}
							>
								{#each colonias as col}
									<option value={col.asentamiento}>{col.asentamiento}</option>
								{/each}
							</select>
						</div>
					{:else}
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Colonia</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={colonia}
								placeholder="Colonia"
							/>
						</div>
					{/if}

					<div class="grid grid-cols-2 gap-3">
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Municipio</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={municipio}
								placeholder="Municipio"
							/>
						</div>
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Estado</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={estado}
								placeholder="Estado"
							/>
						</div>
					</div>

					<div class="grid grid-cols-3 gap-3">
						<div class="col-span-2">
							<label class="text-sm text-slate-600 dark:text-slate-400">Calle</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={calle}
								placeholder="Nombre de calle"
							/>
						</div>
						<div>
							<label class="text-sm text-slate-600 dark:text-slate-400">Número</label>
							<input
								type="text"
								class="input mt-1"
								bind:value={numero}
								placeholder="123"
							/>
						</div>
					</div>
				</div>
			</div>

			<!-- Contacto -->
			<div class="card p-6 lg:col-span-2">
				<div class="flex items-center justify-between mb-4">
					<h3 class="text-lg font-semibold text-slate-900 dark:text-white flex items-center gap-2">
						<Phone class="h-5 w-5 text-teal-500" />
						Contacto
					</h3>
					<button
						class="text-xs text-brand-500 hover:text-brand-600 flex items-center gap-1"
						onclick={generateRandomContact}
					>
						<RefreshCw class="h-3 w-3" />
						Aleatorio
					</button>
				</div>
				<div class="grid gap-4 sm:grid-cols-2">
					<!-- Teléfono -->
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
							Teléfono (10 dígitos)
							{#if telefonoValidation.status === 'valid'}
								<CheckCircle2 class="h-4 w-4 text-green-500" />
							{:else if telefonoValidation.status === 'invalid'}
								<AlertCircle class="h-4 w-4 text-red-500" />
							{:else if telefonoValidation.status === 'warning'}
								<AlertCircle class="h-4 w-4 text-amber-500" />
							{/if}
						</label>
						<div class="flex gap-2 mt-1">
							<input
								type="tel"
								class="input font-mono flex-1"
								bind:value={telefono}
								oninput={() => {
									telefono = telefono.replace(/\D/g, '').slice(0, 10);
									validatePhoneField();
								}}
								placeholder="5512345678"
								maxlength="10"
							/>
							{#if telefono.length === 10}
								<button
									class="btn btn-secondary text-xs px-2"
									onclick={() => copyToClipboard(`+52${telefono}`, 'tel-e164')}
								>
									{copied === 'tel-e164' ? '✓' : 'E.164'}
								</button>
							{/if}
						</div>
						{#if telefono.length === 10}
							<p class="text-xs mt-1 text-slate-500">
								Formateado: <span class="font-mono">{formatPhone(telefono)}</span>
								<span class="mx-1">|</span>
								E.164: <span class="font-mono">+52{telefono}</span>
							</p>
						{/if}
						{#if telefonoValidation.message}
							<p class="text-xs mt-1 {getStatusColor(telefonoValidation.status)}">{telefonoValidation.message}</p>
						{/if}
					</div>

					<!-- Email -->
					<div>
						<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
							Email
							{#if emailValidation.status === 'valid'}
								<CheckCircle2 class="h-4 w-4 text-green-500" />
							{:else if emailValidation.status === 'invalid'}
								<AlertCircle class="h-4 w-4 text-red-500" />
							{/if}
						</label>
						<div class="flex gap-2 mt-1">
							<input
								type="email"
								class="input flex-1"
								bind:value={email}
								oninput={validateEmailField}
								placeholder="correo@ejemplo.com"
							/>
							<button
								class="btn btn-secondary text-xs px-2"
								onclick={() => copyToClipboard(email, 'email')}
								disabled={!email}
							>
								{copied === 'email' ? '✓' : 'Copiar'}
							</button>
						</div>
						{#if emailValidation.message}
							<p class="text-xs mt-1 {getStatusColor(emailValidation.status)}">{emailValidation.message}</p>
						{/if}
					</div>
				</div>
			</div>
		</div>

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Validaciones incluidas:</strong>
				RFC (formato y homoclave) • CURP (formato y dígito verificador) • NSS (formato, dígito verificador y consistencia con fecha de nacimiento) •
				CLABE (formato, dígito verificador y extracción de banco/plaza/cuenta) • Código Postal (catálogo SEPOMEX con colonias) •
				Teléfono (formato mexicano) • Email (formato básico).
			</p>
		</div>
	</div>
</section>
