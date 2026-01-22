<script lang="ts">
	import {
		User,
		Building2,
		Info,
		RefreshCw,
		Copy,
		CheckCircle2,
		CreditCard,
		Phone
	} from 'lucide-svelte';
	import { base } from '$app/paths';
	import { onMount } from 'svelte';
	import {
		generateRfcPersonaFisica,
		generateRfcPersonaMoral,
		generateCurp,
		generateClabe,
		generateNss
	} from '$lib/catalogmx';
	import { query } from '$lib/db';
	import type { Faker } from '@faker-js/faker';
	import DireccionEditor from '$lib/components/DireccionEditor.svelte';

	// Faker is loaded dynamically to avoid SSR issues
	let faker: Faker;
	import DatosBancarios from '$lib/components/DatosBancarios.svelte';
	import RegimenesEditor from '$lib/components/RegimenesEditor.svelte';

	type PersonType = 'fisica' | 'moral';

	let personType = $state<PersonType>('fisica');
	let loading = $state(false);
	let copied = $state<string | null>(null);

	// Data from DB
	let states = $state<{ code: string; name: string }[]>([]);
	let banks = $state<{ code: string; name: string; full_name: string }[]>([]);
	let plazas = $state<{ codigo: string; estado: string; plaza: string }[]>([]);
	let postalCodes = $state<{ cp: string; asentamiento: string; municipio: string; estado: string }[]>([]);
	let regimenesFiscales = $state<{ code: string; description: string; fisica: number; moral: number }[]>([]);
	let ladasByState = $state<Map<string, string[]>>(new Map());
	let dataReady = $state(false);

	// Derived regimes for each persona type
	const regimenesFisica = $derived(regimenesFiscales.filter((r) => r.fisica === 1));
	const regimenesMoral = $derived(regimenesFiscales.filter((r) => r.moral === 1));

	// Generated identity - Persona Física
	let personaFisica = $state<{
		nombre: string;
		apellidoPaterno: string;
		apellidoMaterno: string;
		fechaNacimiento: string;
		sexo: 'H' | 'M';
		estadoNacimiento: string;
		estadoNacimientoNombre: string;
		rfc: string;
		curp: string;
		nss: string;
		clabe: string;
		cuenta: string;
		banco: string;
		bancoNombre: string;
		plaza: string;
		plazaLocalidad: string;
		tarjeta: string;
		tarjetaTipo: 'Visa' | 'Mastercard';
		regimenes: { code: string; description: string }[];
		direccion: {
			cp: string;
			colonia: string;
			municipio: string;
			estado: string;
			calle: string;
			numero: string;
		};
		telefono: string;
		email: string;
	} | null>(null);

	// Tipos de sociedad en México (LGSM - Ley General de Sociedades Mercantiles)
	const tiposSociedad = [
		// Más comunes (con capital variable)
		{ code: 'SA_CV', name: 'S.A. de C.V.', full: 'Sociedad Anónima de Capital Variable' },
		{ code: 'SRL_CV', name: 'S. de R.L. de C.V.', full: 'Sociedad de Responsabilidad Limitada de Capital Variable' },
		{ code: 'SAS', name: 'S.A.S.', full: 'Sociedad por Acciones Simplificada' },
		{ code: 'SAPI_CV', name: 'S.A.P.I. de C.V.', full: 'Sociedad Anónima Promotora de Inversión de Capital Variable' },
		{ code: 'SAB_CV', name: 'S.A.B. de C.V.', full: 'Sociedad Anónima Bursátil de Capital Variable' },
		// Sin capital variable
		{ code: 'SA', name: 'S.A.', full: 'Sociedad Anónima' },
		{ code: 'SRL', name: 'S. de R.L.', full: 'Sociedad de Responsabilidad Limitada' },
		// En comandita
		{ code: 'SCS', name: 'S. en C.S.', full: 'Sociedad en Comandita Simple' },
		{ code: 'SCA', name: 'S. en C. por A.', full: 'Sociedad en Comandita por Acciones' },
		// Otras
		{ code: 'SNC', name: 'S.N.C.', full: 'Sociedad en Nombre Colectivo' },
		{ code: 'SC', name: 'S.C.', full: 'Sociedad Civil' },
		{ code: 'SCL', name: 'S.C.L.', full: 'Sociedad Cooperativa Limitada' },
		{ code: 'SCRL', name: 'S.C. de R.L.', full: 'Sociedad Cooperativa de Responsabilidad Limitada' },
		{ code: 'AC', name: 'A.C.', full: 'Asociación Civil' },
		{ code: 'IAP', name: 'I.A.P.', full: 'Institución de Asistencia Privada' }
	];

	// Giros comerciales comunes (actividades económicas SAT)
	const girosComerciales = [
		'Comercio al por menor',
		'Comercio al por mayor',
		'Desarrollo de software y sistemas',
		'Servicios de consultoría',
		'Servicios profesionales, científicos y técnicos',
		'Construcción de inmuebles',
		'Servicios de transporte',
		'Servicios de alimentos y bebidas',
		'Fabricación de productos',
		'Servicios financieros y de seguros',
		'Servicios inmobiliarios',
		'Servicios de salud',
		'Servicios educativos',
		'Telecomunicaciones',
		'Agricultura y ganadería'
	];

	// Generated identity - Persona Moral
	let personaMoral = $state<{
		denominacion: string;
		tipoSociedad: string;
		tipoSociedadNombre: string;
		razonSocial: string;
		fechaConstitucion: string;
		rfc: string;
		giro: string;
		sitioWeb: string;
		clabe: string;
		cuenta: string;
		banco: string;
		bancoNombre: string;
		plaza: string;
		plazaLocalidad: string;
		tarjeta: string;
		tarjetaTipo: 'Visa' | 'Mastercard';
		regimenes: { code: string; description: string }[];
		direccion: {
			cp: string;
			colonia: string;
			municipio: string;
			estado: string;
			calle: string;
			numero: string;
		};
		telefono: string;
		email: string;
		representante: {
			nombre: string;
			apellidoPaterno: string;
			apellidoMaterno: string;
			fechaNacimiento: string;
			sexo: 'H' | 'M';
			estadoNacimiento: string;
			estadoNacimientoNombre: string;
			rfc: string;
			curp: string;
		};
	} | null>(null);

	onMount(async () => {
		try {
			// Dynamically import faker to avoid SSR issues
			const fakerModule = await import('@faker-js/faker');
			faker = fakerModule.fakerES_MX;

			const [statesData, banksData, plazasData, regimenesData, ladasData] = await Promise.all([
				query<{ code: string; name: string }>('SELECT code, name FROM inegi_states ORDER BY name'),
				query<{ code: string; name: string; full_name: string }>('SELECT code, name, full_name FROM banxico_banks WHERE spei = 1 ORDER BY name'),
				query<{ codigo: string; estado: string; plaza: string }>('SELECT DISTINCT codigo, estado, plaza FROM banxico_codigos_plaza ORDER BY estado, plaza'),
				query<{ code: string; description: string; fisica: number; moral: number }>('SELECT code, description, fisica, moral FROM sat_cfdi_4_0_regimen_fiscal ORDER BY code'),
				query<{ lada: string; estado: string }>('SELECT lada, estado FROM ift_codigos_lada ORDER BY estado, lada')
			]);
			states = statesData;
			banks = banksData;
			plazas = plazasData;
			regimenesFiscales = regimenesData;

			// Build LADA codes map by state
			const ladaMap = new Map<string, string[]>();
			for (const row of ladasData) {
				const existing = ladaMap.get(row.estado) || [];
				existing.push(row.lada);
				ladaMap.set(row.estado, existing);
			}
			ladasByState = ladaMap;

			dataReady = true;
		} catch (error) {
			console.error('Error loading data:', error);
			dataReady = true;
		}
	});

	function getDifferentiator(dateValue: string): string {
		const year = parseInt(dateValue.substring(0, 4));
		return year < 2000 ? '0' : 'A';
	}

	// State name mapping between INEGI (birth state) → codigos_postales format
	const stateNameToPostalState: Record<string, string> = {
		'AGUASCALIENTES': 'Aguascalientes',
		'BAJA CALIFORNIA': 'Baja California',
		'BAJA CALIFORNIA SUR': 'Baja California Sur',
		'CAMPECHE': 'Campeche',
		'CHIAPAS': 'Chiapas',
		'CHIHUAHUA': 'Chihuahua',
		'CIUDAD DE MEXICO': 'Ciudad de México',
		'COAHUILA': 'Coahuila de Zaragoza',
		'COLIMA': 'Colima',
		'DURANGO': 'Durango',
		'ESTADO DE MEXICO': 'México',
		'GUANAJUATO': 'Guanajuato',
		'GUERRERO': 'Guerrero',
		'HIDALGO': 'Hidalgo',
		'JALISCO': 'Jalisco',
		'MICHOACAN': 'Michoacán de Ocampo',
		'MORELOS': 'Morelos',
		'NAYARIT': 'Nayarit',
		'NUEVO LEON': 'Nuevo León',
		'OAXACA': 'Oaxaca',
		'PUEBLA': 'Puebla',
		'QUERETARO': 'Querétaro',
		'QUINTANA ROO': 'Quintana Roo',
		'SAN LUIS POTOSI': 'San Luis Potosí',
		'SINALOA': 'Sinaloa',
		'SONORA': 'Sonora',
		'TABASCO': 'Tabasco',
		'TAMAULIPAS': 'Tamaulipas',
		'TLAXCALA': 'Tlaxcala',
		'VERACRUZ': 'Veracruz de Ignacio de la Llave',
		'YUCATAN': 'Yucatán',
		'ZACATECAS': 'Zacatecas'
	};

	// Postal state → Plaza state mapping
	const postalStateToPlazaState: Record<string, string> = {
		'Ciudad de México': 'CDMX',
		'México': 'Estado de México',
		'Coahuila de Zaragoza': 'Coahuila',
		'Michoacán de Ocampo': 'Michoacán',
		'Veracruz de Ignacio de la Llave': 'Veracruz'
	};

	// Get postal code state name from INEGI state name
	function getPostalStateName(inegiStateName: string): string {
		return stateNameToPostalState[inegiStateName.toUpperCase()] || inegiStateName;
	}

	// Get plaza state name from postal code state name
	function getPlazaStateName(postalStateName: string): string {
		return postalStateToPlazaState[postalStateName] || postalStateName;
	}

	// Major cities to use as fallback
	const majorCities = [
		'Ciudad de México',
		'Jalisco',
		'Nuevo León',
		'México',
		'Puebla',
		'Guanajuato',
		'Querétaro',
		'Veracruz de Ignacio de la Llave',
		'Chihuahua',
		'Baja California'
	];

	// Postal code with INEGI codes for LADA mapping
	interface PostalCodeData {
		cp: string;
		asentamiento: string;
		municipio: string;
		estado: string;
		codigo_estado: string;
		codigo_municipio: string;
	}

	// Load postal code preferring targetState (80% chance if provided)
	async function loadRandomPostalCode(targetState?: string): Promise<PostalCodeData | null> {
		try {
			// 80% chance to use target state if provided
			const useTargetState = targetState && Math.random() < 0.8;
			const stateToSearch = useTargetState ? targetState : faker.helpers.arrayElement(majorCities);

			const result = await query<PostalCodeData>(
				`SELECT cp, asentamiento, municipio, estado, codigo_estado, codigo_municipio FROM codigos_postales WHERE estado = '${stateToSearch}' ORDER BY RANDOM() LIMIT 1`
			);

			// Fallback to any postal code if not found
			if (!result[0]) {
				const fallback = await query<PostalCodeData>(
					`SELECT cp, asentamiento, municipio, estado, codigo_estado, codigo_municipio FROM codigos_postales ORDER BY RANDOM() LIMIT 1`
				);
				return fallback[0] || null;
			}
			return result[0];
		} catch {
			return null;
		}
	}

	// Postal state → LADA state mapping (same as plaza state mapping)
	const postalStateToLadaState: Record<string, string> = {
		'Ciudad de México': 'CDMX',
		'México': 'Estado de México',
		'Coahuila de Zaragoza': 'Coahuila',
		'Michoacán de Ocampo': 'Michoacán',
		'Veracruz de Ignacio de la Llave': 'Veracruz'
	};

	// Generate Mexican phone number based on address (municipality + state)
	async function generateMexicanPhone(postalData: PostalCodeData | null): Promise<string> {
		if (!postalData) {
			// Default to CDMX
			return '55' + faker.string.numeric(8);
		}

		// Try to find LADA by municipality first (most precise)
		if (postalData.codigo_estado && postalData.codigo_municipio) {
			const municipioLadas = await query<{ lada: string }>(
				`SELECT lada FROM ift_codigos_lada WHERE cve_entidad = '${postalData.codigo_estado}' AND cve_municipio = '${postalData.codigo_municipio}'`
			);
			if (municipioLadas.length > 0) {
				const lada = faker.helpers.arrayElement(municipioLadas).lada;
				const localLength = lada.length === 2 ? 8 : 7;
				return lada + faker.string.numeric(localLength);
			}
		}

		// Fallback to state-level LADA
		const ladaStateName = postalStateToLadaState[postalData.estado] || postalData.estado;
		const stateLadas = ladasByState.get(ladaStateName);
		if (stateLadas && stateLadas.length > 0) {
			const lada = faker.helpers.arrayElement(stateLadas);
			const localLength = lada.length === 2 ? 8 : 7;
			return lada + faker.string.numeric(localLength);
		}

		// Final fallback to CDMX
		return '55' + faker.string.numeric(8);
	}

	// Find a plaza matching the given state
	function findPlazaForState(postalStateName: string): { codigo: string; estado: string; plaza: string } | null {
		if (!plazas.length) return null;

		const plazaStateName = getPlazaStateName(postalStateName);
		const matchingPlazas = plazas.filter(p => p.estado === plazaStateName);

		if (matchingPlazas.length > 0) {
			return faker.helpers.arrayElement(matchingPlazas);
		}

		// Fallback to any plaza
		return faker.helpers.arrayElement(plazas);
	}

	// Helper to get clean single surname (faker es_MX sometimes returns compound surnames)
	function getCleanSurname(): string {
		const surname = faker.person.lastName();
		// If compound surname like "Nava Oquendo", take only the first part
		return surname.split(' ')[0];
	}

	async function generatePersonaFisica(): Promise<void> {
		loading = true;
		try {
			// Generate sex first to ensure name consistency
			const sexo: 'H' | 'M' = faker.helpers.arrayElement(['H', 'M']);
			const nombre = faker.person.firstName(sexo === 'H' ? 'male' : 'female');
			const apellidoPaterno = getCleanSurname();
			// 15% chance of having no maternal surname (for testing edge cases)
			const apellidoMaterno = Math.random() < 0.15 ? '' : getCleanSurname();
			const fechaNacimiento = faker.date.birthdate({ min: 1950, max: 2005, mode: 'year' }).toISOString().split('T')[0];
			// Random state - use DB data or generate random code
			const estado = states.length > 0
				? faker.helpers.arrayElement(states)
				: { code: faker.helpers.arrayElement(['AS', 'BC', 'BS', 'CC', 'CL', 'CM', 'CS', 'CH', 'DF', 'DG', 'GT', 'GR', 'HG', 'JC', 'MC', 'MN', 'MS', 'NT', 'NL', 'OC', 'PL', 'QT', 'QR', 'SP', 'SL', 'SR', 'TC', 'TS', 'TL', 'VZ', 'YN', 'ZS']), name: 'Estado' };
			// Random bank - use DB data or generate random valid bank code
			const banco = banks.length > 0
				? faker.helpers.arrayElement(banks)
				: { code: faker.helpers.arrayElement(['002', '012', '014', '021', '030', '036', '044', '058', '072', '102', '106']), name: 'Banco' };

			// Generate RFC
			const rfc = generateRfcPersonaFisica({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento
			});

			// Generate CURP
			const curp = generateCurp({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento,
				sexo,
				estado: estado.name,
				differentiator: getDifferentiator(fechaNacimiento)
			});

			// Generate NSS following IMSS rules: XXYYZZNNNNC
			// XX = subdelegación (01-97), YY = año de alta (nacimiento + 18-35), ZZ = año nacimiento, NNNN = secuencial
			const birthYear = parseInt(fechaNacimiento.substring(0, 4));
			const birthYearForNss = fechaNacimiento.substring(2, 4); // last 2 digits ZZ
			const workStartAge = faker.number.int({ min: 18, max: 35 }); // age when started working
			const registrationYear = String((birthYear + workStartAge) % 100).padStart(2, '0'); // YY
			const subdelegation = String(faker.number.int({ min: 1, max: 97 })).padStart(2, '0'); // XX (valid 01-97)
			const sequential = String(faker.number.int({ min: 1, max: 9999 })).padStart(4, '0'); // NNNN (0001-9999)
			const nss = generateNss(subdelegation, registrationYear, birthYearForNss, sequential);

			// Get random postal code for address (80% chance to match birth state)
			const targetPostalState = getPostalStateName(estado.name);
			const postalData = await loadRandomPostalCode(targetPostalState);

			// Select plaza matching the postal code's state
			const plazaData = postalData
				? (findPlazaForState(postalData.estado) || { codigo: '180', estado: 'CDMX', plaza: 'Ciudad de México' })
				: (plazas.length > 0
					? faker.helpers.arrayElement(plazas)
					: { codigo: faker.string.numeric({ length: 3, allowLeadingZeros: true }), estado: '', plaza: '' });

			// Generate 11-digit account number for CLABE (no internal Luhn - CLABE has its own check digit)
			const accountNumber = faker.string.numeric(11);
			const clabe = generateClabe(banco.code, plazaData.codigo, accountNumber);
			// Display cuenta as 11 digits (the account portion of CLABE)
			const cuenta = accountNumber;

			// Generate debit card
			const card = generateCardNumber();

			personaFisica = {
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento,
				sexo,
				estadoNacimiento: estado.code,
				estadoNacimientoNombre: estado.name,
				rfc,
				curp,
				nss,
				clabe,
				cuenta,
				banco: banco.code,
				bancoNombre: banco.name,
				plaza: plazaData.codigo,
				plazaLocalidad: plazaData.plaza,
				tarjeta: card.number,
				tarjetaTipo: card.type,
				// Default regimes: Sueldos y Salarios (605) or PFAE (612)
				regimenes: regimenesFisica.length > 0
					? [faker.helpers.arrayElement(
							regimenesFisica.filter((r) => ['605', '612'].includes(r.code))
						)].map((r) => ({ code: r.code, description: r.description }))
					: [{ code: '605', description: 'Sueldos y Salarios e Ingresos Asimilados a Salarios' }],
				direccion: {
					cp: postalData?.cp || '06600',
					colonia: postalData?.asentamiento || 'Roma Norte',
					municipio: postalData?.municipio || 'Cuauhtémoc',
					estado: postalData?.estado || 'Ciudad de México',
					calle: faker.location.street(),
					numero: faker.string.numeric({ length: { min: 1, max: 4 } })
				},
				telefono: await generateMexicanPhone(postalData),
				email: faker.internet.email({ firstName: nombre, lastName: apellidoPaterno }).toLowerCase()
			};
		} catch (error) {
			console.error('Error generating persona fisica:', error);
		} finally {
			loading = false;
		}
	}

	async function generatePersonaMoral(): Promise<void> {
		loading = true;
		try {
			// Generate company denomination and type
			const denominacion = faker.company.name();
			const tipoSociedad = faker.helpers.arrayElement(tiposSociedad);
			const razonSocial = `${denominacion} ${tipoSociedad.name}`;
			const fechaConstitucion = faker.date.between({ from: '1990-01-01', to: '2024-12-31' }).toISOString().split('T')[0];

			// Generate RFC
			const rfc = generateRfcPersonaMoral({
				razonSocial,
				fechaConstitucion
			});

			// Generate website from denomination (normalize accents: ñ→n, á→a, etc.)
			const sitioWeb = `www.${denominacion
				.toLowerCase()
				.normalize('NFD')
				.replace(/[\u0300-\u036f]/g, '')
				.replace(/[^a-z0-9]/g, '')
				.substring(0, 20)}.com.mx`;

			// Generate banking data
			const banco = banks.length > 0
				? faker.helpers.arrayElement(banks)
				: { code: faker.helpers.arrayElement(['002', '012', '014', '021', '030', '036', '044']), name: 'Banco' };

			// Get random postal code for address first (for persona moral, use major business cities)
			const postalData = await loadRandomPostalCode();

			// Select plaza matching the postal code's state
			const plazaData = postalData
				? (findPlazaForState(postalData.estado) || { codigo: '180', estado: 'CDMX', plaza: 'Ciudad de México' })
				: (plazas.length > 0
					? faker.helpers.arrayElement(plazas)
					: { codigo: faker.string.numeric({ length: 3, allowLeadingZeros: true }), estado: '', plaza: '' });

			// Generate 11-digit account number for CLABE (no internal Luhn - CLABE has its own check digit)
			const accountNumber = faker.string.numeric(11);
			const clabe = generateClabe(banco.code, plazaData.codigo, accountNumber);
			const cuenta = accountNumber;

			const card = generateCardNumber();

			// Generate representative data (sex first for name consistency)
			const repSexo: 'H' | 'M' = faker.helpers.arrayElement(['H', 'M']);
			const repNombre = faker.person.firstName(repSexo === 'H' ? 'male' : 'female');
			const repApellidoPaterno = getCleanSurname();
			const repApellidoMaterno = Math.random() < 0.15 ? '' : getCleanSurname();
			const repFechaNacimiento = faker.date.birthdate({ min: 1960, max: 1995, mode: 'year' }).toISOString().split('T')[0];
			const repEstado = states.length > 0 ? faker.helpers.arrayElement(states) : { code: 'DF', name: 'Ciudad de México' };

			const repRfc = generateRfcPersonaFisica({
				nombre: repNombre,
				apellidoPaterno: repApellidoPaterno,
				apellidoMaterno: repApellidoMaterno,
				fechaNacimiento: repFechaNacimiento
			});

			const repCurp = generateCurp({
				nombre: repNombre,
				apellidoPaterno: repApellidoPaterno,
				apellidoMaterno: repApellidoMaterno,
				fechaNacimiento: repFechaNacimiento,
				sexo: repSexo,
				estado: repEstado.name,
				differentiator: getDifferentiator(repFechaNacimiento)
			});

			personaMoral = {
				denominacion,
				tipoSociedad: tipoSociedad.code,
				tipoSociedadNombre: tipoSociedad.name,
				razonSocial,
				fechaConstitucion,
				rfc,
				giro: faker.helpers.arrayElement(girosComerciales),
				sitioWeb,
				clabe,
				cuenta,
				banco: banco.code,
				bancoNombre: banco.name,
				plaza: plazaData.codigo,
				plazaLocalidad: plazaData.plaza,
				tarjeta: card.number,
				tarjetaTipo: card.type,
				// Default regime: General de Ley Personas Morales (601)
				regimenes: regimenesMoral.length > 0
					? [regimenesMoral.find((r) => r.code === '601') || regimenesMoral[0]].map((r) => ({ code: r.code, description: r.description }))
					: [{ code: '601', description: 'General de Ley Personas Morales' }],
				direccion: {
					cp: postalData?.cp || '06600',
					colonia: postalData?.asentamiento || 'Roma Norte',
					municipio: postalData?.municipio || 'Cuauhtémoc',
					estado: postalData?.estado || 'Ciudad de México',
					calle: faker.location.street(),
					numero: faker.string.numeric({ length: { min: 1, max: 4 } })
				},
				telefono: await generateMexicanPhone(postalData),
				email: `contacto@${denominacion.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '').substring(0, 20)}.com.mx`,
				representante: {
					nombre: repNombre,
					apellidoPaterno: repApellidoPaterno,
					apellidoMaterno: repApellidoMaterno,
					fechaNacimiento: repFechaNacimiento,
					sexo: repSexo,
					estadoNacimiento: repEstado.code,
					estadoNacimientoNombre: repEstado.name,
					rfc: repRfc,
					curp: repCurp
				}
			};
		} catch (error) {
			console.error('Error generating persona moral:', error);
		} finally {
			loading = false;
		}
	}

	function generate(): void {
		if (personType === 'fisica') {
			generatePersonaFisica();
		} else {
			generatePersonaMoral();
		}
	}

	function copyToClipboard(text: string, field: string): void {
		navigator.clipboard.writeText(text);
		copied = field;
		setTimeout(() => {
			copied = null;
		}, 2000);
	}

	function copyAll(): void {
		let text = '';
		if (personType === 'fisica' && personaFisica) {
			text = `IDENTIDAD DE PRUEBA - PERSONA FÍSICA
=====================================
Nombre: ${personaFisica.nombre} ${personaFisica.apellidoPaterno} ${personaFisica.apellidoMaterno}
Fecha de Nacimiento: ${personaFisica.fechaNacimiento}
Sexo: ${personaFisica.sexo === 'H' ? 'Masculino' : 'Femenino'}
Estado de Nacimiento: ${personaFisica.estadoNacimientoNombre}

RFC: ${personaFisica.rfc}
CURP: ${personaFisica.curp}
NSS: ${personaFisica.nss}

Datos Bancarios:
Banco: ${personaFisica.bancoNombre}
CLABE: ${personaFisica.clabe}
Cuenta: ${personaFisica.cuenta}
Tarjeta (${personaFisica.tarjetaTipo}): ${personaFisica.tarjeta}

Dirección:
${personaFisica.direccion.calle} ${personaFisica.direccion.numero}
${personaFisica.direccion.colonia}
${personaFisica.direccion.municipio}, ${personaFisica.direccion.estado}
C.P. ${personaFisica.direccion.cp}

Teléfono: ${personaFisica.telefono}
Teléfono E.164: +52${personaFisica.telefono}
Email: ${personaFisica.email}

⚠️ DATOS FICTICIOS PARA PRUEBAS - NO USAR EN PRODUCCIÓN`;
		} else if (personType === 'moral' && personaMoral) {
			text = `IDENTIDAD DE PRUEBA - PERSONA MORAL
=====================================
Denominación: ${personaMoral.denominacion}
Tipo de Sociedad: ${personaMoral.tipoSociedadNombre}
Razón Social: ${personaMoral.razonSocial}
RFC: ${personaMoral.rfc}
Fecha de Constitución: ${personaMoral.fechaConstitucion}
Giro: ${personaMoral.giro}

Datos Bancarios:
Banco: ${personaMoral.bancoNombre}
CLABE: ${personaMoral.clabe}
Cuenta: ${personaMoral.cuenta}
Tarjeta (${personaMoral.tarjetaTipo}): ${personaMoral.tarjeta}

Domicilio Fiscal:
${personaMoral.direccion.calle} ${personaMoral.direccion.numero}
${personaMoral.direccion.colonia}
${personaMoral.direccion.municipio}, ${personaMoral.direccion.estado}
C.P. ${personaMoral.direccion.cp}

Contacto:
Teléfono: ${personaMoral.telefono}
Teléfono E.164: +52${personaMoral.telefono}
Email: ${personaMoral.email}
Sitio Web: ${personaMoral.sitioWeb}

Representante Legal:
Nombre: ${personaMoral.representante.nombre} ${personaMoral.representante.apellidoPaterno} ${personaMoral.representante.apellidoMaterno}
RFC: ${personaMoral.representante.rfc}
CURP: ${personaMoral.representante.curp}

⚠️ DATOS FICTICIOS PARA PRUEBAS - NO USAR EN PRODUCCIÓN`;
		}
		copyToClipboard(text, 'all');
	}

	function formatDate(dateStr: string): string {
		const [year, month, day] = dateStr.split('-');
		return `${day}/${month}/${year}`;
	}

	// Mexican phone formatting
	// Main metro areas (55, 56, 33, 81) use 2-4-4 format
	// Other areas use 3-3-4 format
	function formatPhone(phone: string): string {
		const digits = phone.replace(/\D/g, '');
		if (digits.length !== 10) return phone;

		const prefix = digits.substring(0, 2);
		// CDMX (55, 56), Guadalajara (33), Monterrey (81)
		if (['55', '56', '33', '81'].includes(prefix)) {
			return `${digits.substring(0, 2)} ${digits.substring(2, 6)} ${digits.substring(6)}`;
		}
		// Other areas: 3-3-4
		return `${digits.substring(0, 3)} ${digits.substring(3, 6)} ${digits.substring(6)}`;
	}

	// CLABE formatting options
	type ClabeFormat = '3-3-5-5-2' | '4-4-4-4-2' | '3-3-4-4-4';
	let clabeFormat = $state<ClabeFormat>('3-3-4-4-4');

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

	// Extract account number from CLABE (positions 7-17, 11 digits but we show 10 without check digit area)
	// CLABE structure: BBB PPP CCCCCCCCCCC D (bank 3, plaza 3, account 11, check 1)
	// Account is positions 6-16 (0-indexed), 11 digits
	function extractCuenta(clabe: string): string {
		if (clabe.length !== 18) return '';
		// The account number in CLABE is digits 7-17 (11 digits), but typically shown as 10
		// Some banks use 10-digit accounts padded with leading zero
		const cuenta = clabe.substring(6, 17);
		// Remove leading zeros to get effective account, then pad back to 10
		return cuenta.replace(/^0+/, '').padStart(10, '0').substring(0, 10);
	}

	// Luhn algorithm for card number validation
	function calculateLuhnCheckDigit(partialNumber: string): string {
		const digits = partialNumber.split('').map(Number);
		let sum = 0;
		for (let i = 0; i < digits.length; i++) {
			let digit = digits[digits.length - 1 - i];
			if (i % 2 === 0) {
				digit *= 2;
				if (digit > 9) digit -= 9;
			}
			sum += digit;
		}
		const checkDigit = (10 - (sum % 10)) % 10;
		return checkDigit.toString();
	}

	// Generate valid Visa or Mastercard number
	function generateCardNumber(tipo?: 'Visa' | 'Mastercard'): { number: string; type: 'Visa' | 'Mastercard' } {
		const isVisa = tipo ? tipo === 'Visa' : Math.random() < 0.5;
		let prefix: string;

		if (isVisa) {
			// Visa starts with 4
			prefix = '4';
		} else {
			// Mastercard starts with 51-55 or 2221-2720
			const mcPrefixes = ['51', '52', '53', '54', '55', '2221', '2720'];
			prefix = faker.helpers.arrayElement(mcPrefixes);
		}

		// Generate remaining digits (total 16 digits, minus prefix, minus check digit)
		const remainingLength = 15 - prefix.length;
		const middle = faker.string.numeric(remainingLength);
		const partialNumber = prefix + middle;
		const checkDigit = calculateLuhnCheckDigit(partialNumber);

		return {
			number: partialNumber + checkDigit,
			type: isVisa ? 'Visa' : 'Mastercard'
		};
	}

	// Regenerate card when type changes (for persona física)
	function regenerateCardPersonaFisica(tipo: 'Visa' | 'Mastercard'): void {
		if (!personaFisica) return;
		const card = generateCardNumber(tipo);
		personaFisica = { ...personaFisica, tarjeta: card.number, tarjetaTipo: card.type };
	}

	// Regenerate card when type changes (for persona moral)
	function regenerateCardPersonaMoral(tipo: 'Visa' | 'Mastercard'): void {
		if (!personaMoral) return;
		const card = generateCardNumber(tipo);
		personaMoral = { ...personaMoral, tarjeta: card.number, tarjetaTipo: card.type };
	}

	// Format card number in groups of 4
	function formatCard(card: string): string {
		return card.replace(/(\d{4})/g, '$1 ').trim();
	}

	// Recalculate identifiers when personal data changes
	function recalculatePersonaFisica(): void {
		if (!personaFisica) return;

		try {
			const { nombre, apellidoPaterno, apellidoMaterno, fechaNacimiento, sexo, estadoNacimientoNombre, nss } = personaFisica;

			if (!nombre || !apellidoPaterno || !fechaNacimiento) return;

			// Recalculate RFC
			const newRfc = generateRfcPersonaFisica({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento
			});

			// Recalculate CURP
			const newCurp = generateCurp({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento,
				sexo,
				estado: estadoNacimientoNombre,
				differentiator: getDifferentiator(fechaNacimiento)
			});

			// Recalculate NSS if birth year changed (NSS contains birth year in positions 5-6)
			const newBirthYearForNss = fechaNacimiento.substring(2, 4);
			const currentBirthYearInNss = nss.substring(4, 6);
			let newNss = nss;

			if (newBirthYearForNss !== currentBirthYearInNss) {
				// Regenerate NSS with new birth year
				const birthYear = parseInt(fechaNacimiento.substring(0, 4));
				const workStartAge = faker.number.int({ min: 18, max: 35 });
				const registrationYear = String((birthYear + workStartAge) % 100).padStart(2, '0');
				const subdelegation = nss.substring(0, 2); // Keep original subdelegation
				const sequential = nss.substring(6, 10); // Keep original sequential
				newNss = generateNss(subdelegation, registrationYear, newBirthYearForNss, sequential);
			}

			personaFisica = {
				...personaFisica,
				rfc: newRfc,
				curp: newCurp,
				nss: newNss
			};
		} catch (error) {
			console.error('Error recalculating identifiers:', error);
		}
	}

	// Update a field in personaFisica and recalculate
	function updatePersonaFisica<K extends keyof NonNullable<typeof personaFisica>>(
		field: K,
		value: NonNullable<typeof personaFisica>[K]
	): void {
		if (!personaFisica) return;
		personaFisica = { ...personaFisica, [field]: value };
		// Recalculate identifiers when relevant fields change
		if (['nombre', 'apellidoPaterno', 'apellidoMaterno', 'fechaNacimiento', 'sexo', 'estadoNacimientoNombre'].includes(field as string)) {
			recalculatePersonaFisica();
		}
	}

	// Recalculate RFC for persona moral when relevant fields change
	function recalculatePersonaMoral(): void {
		if (!personaMoral) return;

		try {
			const { denominacion, tipoSociedadNombre, fechaConstitucion } = personaMoral;
			if (!denominacion || !fechaConstitucion) return;

			const razonSocial = `${denominacion} ${tipoSociedadNombre}`;
			const newRfc = generateRfcPersonaMoral({ razonSocial, fechaConstitucion });

			personaMoral = {
				...personaMoral,
				razonSocial,
				rfc: newRfc
			};
		} catch (error) {
			console.error('Error recalculating persona moral RFC:', error);
		}
	}

	// Recalculate representative identifiers
	function recalculateRepresentante(): void {
		if (!personaMoral) return;

		try {
			const { nombre, apellidoPaterno, apellidoMaterno, fechaNacimiento, sexo, estadoNacimientoNombre } = personaMoral.representante;
			if (!nombre || !apellidoPaterno || !fechaNacimiento) return;

			const newRfc = generateRfcPersonaFisica({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento
			});

			const newCurp = generateCurp({
				nombre,
				apellidoPaterno,
				apellidoMaterno,
				fechaNacimiento,
				sexo,
				estado: estadoNacimientoNombre,
				differentiator: getDifferentiator(fechaNacimiento)
			});

			personaMoral = {
				...personaMoral,
				representante: {
					...personaMoral.representante,
					rfc: newRfc,
					curp: newCurp
				}
			};
		} catch (error) {
			console.error('Error recalculating representante:', error);
		}
	}

	// Regenerate CLABE when bank changes (for persona física)
	function regenerateClabePersonaFisica(bancoCode: string): void {
		if (!personaFisica) return;

		const banco = banks.find((b) => b.code === bancoCode);
		if (!banco) return;

		const plaza = plazas.length > 0
			? faker.helpers.arrayElement(plazas)
			: { codigo: personaFisica.clabe.substring(3, 6), estado: '', plaza: '' };

		// Generate 11-digit account number for CLABE
		const accountNumber = faker.string.numeric(11);
		const clabe = generateClabe(bancoCode, plaza.codigo, accountNumber);

		personaFisica = {
			...personaFisica,
			banco: bancoCode,
			bancoNombre: banco.name,
			plaza: plaza.codigo,
			plazaLocalidad: plaza.plaza,
			clabe,
			cuenta: accountNumber
		};
	}

	// Regenerate CLABE when plaza changes (for persona fisica)
	function regenerateClabeFromPlazaPersonaFisica(plazaCode: string): void {
		if (!personaFisica) return;

		const selectedPlaza = plazas.find((p) => p.codigo === plazaCode && p.plaza);
		if (!selectedPlaza) return;

		// Generate 11-digit account number for CLABE
		const accountNumber = faker.string.numeric(11);
		const clabe = generateClabe(personaFisica.banco, plazaCode, accountNumber);

		personaFisica = {
			...personaFisica,
			plaza: plazaCode,
			plazaLocalidad: selectedPlaza.plaza,
			clabe,
			cuenta: accountNumber
		};
	}

	// Regenerate CLABE when bank changes (for persona moral)
	function regenerateClabePersonaMoral(bancoCode: string): void {
		if (!personaMoral) return;

		const banco = banks.find((b) => b.code === bancoCode);
		if (!banco) return;

		const plaza = plazas.length > 0
			? faker.helpers.arrayElement(plazas)
			: { codigo: personaMoral.clabe.substring(3, 6), estado: '', plaza: '' };

		// Generate 11-digit account number for CLABE
		const accountNumber = faker.string.numeric(11);
		const clabe = generateClabe(bancoCode, plaza.codigo, accountNumber);

		personaMoral = {
			...personaMoral,
			banco: bancoCode,
			bancoNombre: banco.name,
			plaza: plaza.codigo,
			plazaLocalidad: plaza.plaza,
			clabe,
			cuenta: accountNumber
		};
	}

	// Regenerate CLABE when plaza changes (for persona moral)
	function regenerateClabeFromPlazaPersonaMoral(plazaCode: string): void {
		if (!personaMoral) return;

		const selectedPlaza = plazas.find((p) => p.codigo === plazaCode && p.plaza);
		if (!selectedPlaza) return;

		// Generate 11-digit account number for CLABE
		const accountNumber = faker.string.numeric(11);
		const clabe = generateClabe(personaMoral.banco, plazaCode, accountNumber);

		personaMoral = {
			...personaMoral,
			plaza: plazaCode,
			plazaLocalidad: selectedPlaza.plaza,
			clabe,
			cuenta: accountNumber
		};
	}

	// Update a field in personaMoral and recalculate
	function updatePersonaMoral<K extends keyof NonNullable<typeof personaMoral>>(
		field: K,
		value: NonNullable<typeof personaMoral>[K]
	): void {
		if (!personaMoral) return;
		personaMoral = { ...personaMoral, [field]: value };
		// Recalculate RFC when relevant fields change
		if (['denominacion', 'tipoSociedadNombre', 'fechaConstitucion'].includes(field as string)) {
			recalculatePersonaMoral();
		}
	}

	// Update a field in representante and recalculate
	function updateRepresentante<K extends keyof NonNullable<typeof personaMoral>['representante']>(
		field: K,
		value: NonNullable<typeof personaMoral>['representante'][K]
	): void {
		if (!personaMoral) return;
		personaMoral = {
			...personaMoral,
			representante: { ...personaMoral.representante, [field]: value }
		};
		// Recalculate identifiers when relevant fields change
		if (['nombre', 'apellidoPaterno', 'apellidoMaterno', 'fechaNacimiento', 'sexo', 'estadoNacimientoNombre'].includes(field as string)) {
			recalculateRepresentante();
		}
	}

	// Lookup postal code and auto-complete address fields
	async function lookupPostalCode(cp: string, target: 'fisica' | 'moral'): Promise<void> {
		if (cp.length !== 5) return;

		try {
			const results = await query<{ asentamiento: string; municipio: string; estado: string }>(
				`SELECT asentamiento, municipio, estado FROM codigos_postales WHERE cp = '${cp}' LIMIT 1`
			);

			if (results.length > 0) {
				const { asentamiento, municipio, estado } = results[0];

				if (target === 'fisica' && personaFisica) {
					personaFisica = {
						...personaFisica,
						direccion: {
							...personaFisica.direccion,
							cp,
							colonia: asentamiento,
							municipio,
							estado
						}
					};
				} else if (target === 'moral' && personaMoral) {
					personaMoral = {
						...personaMoral,
						direccion: {
							...personaMoral.direccion,
							cp,
							colonia: asentamiento,
							municipio,
							estado
						}
					};
				}
			}
		} catch (error) {
			console.error('Error looking up postal code:', error);
		}
	}
</script>

<svelte:head>
	<title>Generador de Identidades - catalogmx</title>
	<meta name="description" content="Genera identidades mexicanas completas de prueba con RFC, CURP, NSS, CLABE y dirección. Para desarrollo y testing." />
</svelte:head>

<!-- Hero -->
<section class="py-8 md:py-12 border-b border-slate-200 dark:border-slate-800">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex items-center gap-2 mb-4">
			<a href="{base}/generadores" class="text-sm text-slate-500 dark:text-slate-400 hover:text-brand-500">
				Generadores
			</a>
			<span class="text-slate-400">/</span>
			<span class="text-sm text-slate-700 dark:text-slate-300 font-medium">Identidad</span>
		</div>

		<div class="flex items-start gap-4 mb-4">
			<div class="p-3 rounded-lg bg-purple-100 dark:bg-purple-900/30">
				<User class="h-8 w-8 text-purple-600 dark:text-purple-400" />
			</div>
			<div>
				<h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-2">
					Generador de Identidades
				</h1>
				<p class="text-lg text-slate-600 dark:text-slate-300">
					Genera identidades mexicanas completas para pruebas y desarrollo
				</p>
			</div>
		</div>

		<div class="flex items-start gap-2 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
			<Info class="h-5 w-5 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
			<div class="text-sm text-amber-900 dark:text-amber-300">
				<p class="font-medium mb-1">Solo para pruebas</p>
				<p>Estos datos son ficticios y generados aleatoriamente. No representan personas reales. Usar solo para desarrollo y testing.</p>
			</div>
		</div>
	</div>
</section>

<!-- Generator -->
<section class="py-8">
	<div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Type selector + Generate button -->
		<div class="mb-6 flex flex-wrap items-center gap-4">
			<div class="inline-flex rounded-lg border border-slate-200 dark:border-slate-700 p-1 bg-slate-50 dark:bg-slate-800/50">
				<button
					class="px-4 py-2 rounded-md text-sm font-medium transition-colors {personType === 'fisica' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					onclick={() => {
						personType = 'fisica';
						personaFisica = null;
						personaMoral = null;
					}}
				>
					<User class="h-4 w-4 inline mr-2" />
					Persona Física
				</button>
				<button
					class="px-4 py-2 rounded-md text-sm font-medium transition-colors {personType === 'moral' ? 'bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'}"
					onclick={() => {
						personType = 'moral';
						personaFisica = null;
						personaMoral = null;
					}}
				>
					<Building2 class="h-4 w-4 inline mr-2" />
					Persona Moral
				</button>
			</div>

			<button
				class="btn btn-primary flex items-center gap-2"
				onclick={generate}
				disabled={loading || !dataReady}
			>
				<RefreshCw class="h-4 w-4 {loading ? 'animate-spin' : ''}" />
				{loading ? 'Generando...' : 'Generar Identidad'}
			</button>
		</div>

		<!-- Results -->
		{#if personType === 'fisica' && personaFisica}
			<div class="space-y-6">
				<!-- Header with copy all -->
				<div class="flex items-center justify-between">
					<h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
						<CheckCircle2 class="h-5 w-5 text-green-500" />
						Identidad Generada
					</h2>
					<button
						class="btn btn-secondary text-sm flex items-center gap-2"
						onclick={copyAll}
					>
						<Copy class="h-4 w-4" />
						{copied === 'all' ? 'Copiado!' : 'Copiar Todo'}
					</button>
				</div>

				<div class="grid gap-6 lg:grid-cols-2">
					<!-- Datos Personales (Editables) -->
					<div class="card p-6">
						<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<User class="h-5 w-5 text-purple-500" />
							Datos Personales
							<span class="text-xs font-normal text-slate-400">(editables)</span>
						</h3>
						<div class="space-y-4">
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Nombre(s)
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaFisica!.nombre, 'nombre')}>
										{copied === 'nombre' ? '✓' : 'copiar'}
									</button>
								</label>
								<input
									type="text"
									class="input mt-1"
									value={personaFisica.nombre}
									oninput={(e) => updatePersonaFisica('nombre', e.currentTarget.value)}
								/>
							</div>
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Apellido Paterno
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaFisica!.apellidoPaterno, 'paterno')}>
											{copied === 'paterno' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="text"
										class="input mt-1"
										value={personaFisica.apellidoPaterno}
										oninput={(e) => updatePersonaFisica('apellidoPaterno', e.currentTarget.value)}
									/>
								</div>
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Apellido Materno
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaFisica!.apellidoMaterno, 'materno')}>
											{copied === 'materno' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="text"
										class="input mt-1"
										value={personaFisica.apellidoMaterno}
										oninput={(e) => updatePersonaFisica('apellidoMaterno', e.currentTarget.value)}
										placeholder="(opcional)"
									/>
								</div>
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Nombre completo
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(`${personaFisica!.nombre} ${personaFisica!.apellidoPaterno} ${personaFisica!.apellidoMaterno}`.trim(), 'fullname')}>
										{copied === 'fullname' ? '✓' : 'copiar'}
									</button>
								</label>
								<div class="text-sm font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-md">
									{personaFisica.nombre} {personaFisica.apellidoPaterno} {personaFisica.apellidoMaterno}
								</div>
							</div>
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Fecha de nacimiento
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaFisica!.fechaNacimiento, 'fecha')}>
											{copied === 'fecha' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="date"
										class="input mt-1"
										value={personaFisica.fechaNacimiento}
										oninput={(e) => updatePersonaFisica('fechaNacimiento', e.currentTarget.value)}
									/>
								</div>
								<div>
									<label for="pf-sexo" class="text-sm text-slate-600 dark:text-slate-400">Sexo</label>
									<select
										id="pf-sexo"
										class="input mt-1"
										value={personaFisica.sexo}
										onchange={(e) => updatePersonaFisica('sexo', e.currentTarget.value as 'H' | 'M')}
									>
										<option value="H">Masculino</option>
										<option value="M">Femenino</option>
									</select>
								</div>
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Estado de nacimiento
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaFisica!.estadoNacimientoNombre, 'estado')}>
										{copied === 'estado' ? '✓' : 'copiar'}
									</button>
								</label>
								<select
									class="input mt-1"
									value={personaFisica.estadoNacimiento}
									onchange={(e) => {
										const selectedState = states.find(s => s.code === e.currentTarget.value);
										if (selectedState) {
											personaFisica = {
												...personaFisica!,
												estadoNacimiento: selectedState.code,
												estadoNacimientoNombre: selectedState.name
											};
											recalculatePersonaFisica();
										}
									}}
								>
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
						<div class="space-y-3">
							<div class="flex justify-between items-center group">
								<span class="text-slate-600 dark:text-slate-400">RFC</span>
								<button
									class="font-mono font-medium text-slate-900 dark:text-white hover:text-brand-500 flex items-center gap-1"
									onclick={() => copyToClipboard(personaFisica!.rfc, 'rfc')}
								>
									{personaFisica.rfc}
									<Copy class="h-3 w-3 opacity-0 group-hover:opacity-100" />
								</button>
							</div>
							<div class="flex justify-between items-center group">
								<span class="text-slate-600 dark:text-slate-400">CURP</span>
								<button
									class="font-mono font-medium text-slate-900 dark:text-white hover:text-brand-500 flex items-center gap-1 text-sm"
									onclick={() => copyToClipboard(personaFisica!.curp, 'curp')}
								>
									{personaFisica.curp}
									<Copy class="h-3 w-3 opacity-0 group-hover:opacity-100" />
								</button>
							</div>
							<div class="flex justify-between items-center group">
								<span class="text-slate-600 dark:text-slate-400">NSS</span>
								<button
									class="font-mono font-medium text-slate-900 dark:text-white hover:text-brand-500 flex items-center gap-1"
									onclick={() => copyToClipboard(personaFisica!.nss, 'nss')}
								>
									{personaFisica.nss}
									<Copy class="h-3 w-3 opacity-0 group-hover:opacity-100" />
								</button>
							</div>
							<!-- Régimen Fiscal (embedded) -->
							<RegimenesEditor
								regimenes={personaFisica.regimenes}
								availableRegimenes={regimenesFisica}
								embedded={true}
								onchange={(regs) => {
									personaFisica = { ...personaFisica!, regimenes: regs };
								}}
							/>
						</div>
					</div>

					<!-- Datos Bancarios -->
					<DatosBancarios
						datos={{
							banco: personaFisica.banco,
							bancoNombre: personaFisica.bancoNombre,
							plaza: personaFisica.plaza,
							plazaLocalidad: personaFisica.plazaLocalidad,
							clabe: personaFisica.clabe,
							cuenta: personaFisica.cuenta,
							tarjeta: personaFisica.tarjeta,
							tarjetaTipo: personaFisica.tarjetaTipo
						}}
						{banks}
						{plazas}
						{clabeFormat}
						{copied}
						onBankChange={regenerateClabePersonaFisica}
						onPlazaChange={regenerateClabeFromPlazaPersonaFisica}
						onCopy={copyToClipboard}
						onFormatChange={(f) => (clabeFormat = f)}
						onCardTypeChange={regenerateCardPersonaFisica}
					/>

					<!-- Dirección (Editable) -->
					<DireccionEditor
						direccion={personaFisica.direccion}
						copied={copied === 'direccion-fisica'}
						onchange={(dir) => {
							personaFisica = { ...personaFisica!, direccion: dir };
						}}
						onCopy={(text) => copyToClipboard(text, 'direccion-fisica')}
					/>

					<!-- Contacto (Editable) -->
					<div class="card p-6 lg:col-span-2">
						<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<Phone class="h-5 w-5 text-teal-500" />
							Contacto
							<span class="text-xs font-normal text-slate-400">(editable)</span>
						</h3>
						<div class="grid gap-4 sm:grid-cols-2">
							<div>
								<label for="pf-telefono" class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Teléfono (10 dígitos)
									<span class="text-xs text-slate-400">
										{personaFisica.telefono.length === 10
											? (['55', '56', '33', '81'].includes(personaFisica.telefono.substring(0, 2)) ? '2-4-4' : '3-3-4')
											: ''}
									</span>
								</label>
								<div class="flex gap-2 mt-1">
									<input
										id="pf-telefono"
										type="tel"
										class="input font-mono flex-1"
										value={personaFisica.telefono}
										maxlength="10"
										placeholder="5512345678"
										oninput={(e) => updatePersonaFisica('telefono', e.currentTarget.value.replace(/\D/g, '').slice(0, 10))}
									/>
								</div>
								{#if personaFisica.telefono.length === 10}
									<div class="flex items-center justify-between mt-2 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg text-sm">
										<span class="font-mono text-slate-700 dark:text-slate-300 tracking-wider">
											{formatPhone(personaFisica.telefono)}
										</span>
										<div class="flex items-center gap-1 text-xs">
											<span class="text-slate-400">copiar:</span>
											<button
												class="text-brand-500 hover:text-brand-600 px-1"
												onclick={() => copyToClipboard(personaFisica!.telefono, 'tel-fisica-10')}
											>
												{copied === 'tel-fisica-10' ? '✓' : '10 dígitos'}
											</button>
											<span class="text-slate-300">|</span>
											<button
												class="text-brand-500 hover:text-brand-600 px-1"
												onclick={() => copyToClipboard(`+52${personaFisica!.telefono}`, 'tel-fisica-e164')}
											>
												{copied === 'tel-fisica-e164' ? '✓' : 'E.164'}
											</button>
										</div>
									</div>
								{/if}
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Email
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaFisica!.email, 'email')}>
										{copied === 'email' ? '✓' : 'copiar'}
									</button>
								</label>
								<input
									type="email"
									class="input mt-1"
									value={personaFisica.email}
									oninput={(e) => updatePersonaFisica('email', e.currentTarget.value)}
								/>
							</div>
						</div>
					</div>
				</div>
			</div>
		{:else if personType === 'moral' && personaMoral}
			<div class="space-y-6">
				<!-- Header with copy all -->
				<div class="flex items-center justify-between">
					<h2 class="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
						<CheckCircle2 class="h-5 w-5 text-green-500" />
						Empresa Generada
					</h2>
					<button
						class="btn btn-secondary text-sm flex items-center gap-2"
						onclick={copyAll}
					>
						<Copy class="h-4 w-4" />
						{copied === 'all' ? 'Copiado!' : 'Copiar Todo'}
					</button>
				</div>

				<div class="grid gap-6 lg:grid-cols-2">
					<!-- Datos de la Empresa (Editables) -->
					<div class="card p-6">
						<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<Building2 class="h-5 w-5 text-purple-500" />
							Datos de la Empresa
							<span class="text-xs font-normal text-slate-400">(editables)</span>
						</h3>
						<div class="space-y-4">
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Denominación
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.denominacion, 'denominacion')}>
										{copied === 'denominacion' ? '✓' : 'copiar'}
									</button>
								</label>
								<input
									type="text"
									class="input mt-1"
									value={personaMoral.denominacion}
									oninput={(e) => updatePersonaMoral('denominacion', e.currentTarget.value)}
								/>
							</div>
							<div>
								<label for="pm-tipo-sociedad" class="text-sm text-slate-600 dark:text-slate-400">Tipo de Sociedad</label>
								<select
									id="pm-tipo-sociedad"
									class="input mt-1"
									value={personaMoral.tipoSociedad}
									onchange={(e) => {
										const selected = tiposSociedad.find(t => t.code === e.currentTarget.value);
										if (selected) {
											personaMoral = {
												...personaMoral!,
												tipoSociedad: selected.code,
												tipoSociedadNombre: selected.name,
												razonSocial: `${personaMoral!.denominacion} ${selected.name}`
											};
											recalculatePersonaMoral();
										}
									}}
								>
									{#each tiposSociedad as tipo}
										<option value={tipo.code} title={tipo.full}>{tipo.name} - {tipo.full}</option>
									{/each}
								</select>
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Razón Social
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.razonSocial, 'razonSocial')}>
										{copied === 'razonSocial' ? '✓' : 'copiar'}
									</button>
								</label>
								<div class="text-sm font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-md mt-1">
									{personaMoral.razonSocial}
								</div>
							</div>
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Fecha de constitución
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.fechaConstitucion, 'fechaConstitucion')}>
											{copied === 'fechaConstitucion' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="date"
										class="input mt-1"
										value={personaMoral.fechaConstitucion}
										oninput={(e) => updatePersonaMoral('fechaConstitucion', e.currentTarget.value)}
									/>
								</div>
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										RFC
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.rfc, 'rfc')}>
											{copied === 'rfc' ? '✓' : 'copiar'}
										</button>
									</label>
									<div class="text-sm font-mono font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-md mt-1">
										{personaMoral.rfc}
									</div>
								</div>
							</div>
							<div>
								<label for="pm-giro" class="text-sm text-slate-600 dark:text-slate-400">Giro</label>
								<select
									id="pm-giro"
									class="input mt-1"
									value={personaMoral.giro}
									onchange={(e) => updatePersonaMoral('giro', e.currentTarget.value)}
								>
									{#each girosComerciales as giro}
										<option value={giro}>{giro}</option>
									{/each}
								</select>
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Sitio Web
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.sitioWeb, 'sitioWeb')}>
										{copied === 'sitioWeb' ? '✓' : 'copiar'}
									</button>
								</label>
								<input
									type="text"
									class="input mt-1"
									value={personaMoral.sitioWeb}
									oninput={(e) => updatePersonaMoral('sitioWeb', e.currentTarget.value)}
									placeholder="www.empresa.com.mx"
								/>
							</div>
							<!-- Régimen Fiscal (embedded) -->
							<RegimenesEditor
								regimenes={personaMoral.regimenes}
								availableRegimenes={regimenesMoral}
								embedded={true}
								onchange={(regs) => {
									personaMoral = { ...personaMoral!, regimenes: regs };
								}}
							/>
						</div>
					</div>

					<!-- Datos Bancarios -->
					<DatosBancarios
						datos={{
							banco: personaMoral.banco,
							bancoNombre: personaMoral.bancoNombre,
							plaza: personaMoral.plaza,
							plazaLocalidad: personaMoral.plazaLocalidad,
							clabe: personaMoral.clabe,
							cuenta: personaMoral.cuenta,
							tarjeta: personaMoral.tarjeta,
							tarjetaTipo: personaMoral.tarjetaTipo
						}}
						{banks}
						{plazas}
						{clabeFormat}
						{copied}
						onBankChange={regenerateClabePersonaMoral}
						onPlazaChange={regenerateClabeFromPlazaPersonaMoral}
						onCopy={copyToClipboard}
						onFormatChange={(f) => (clabeFormat = f)}
						onCardTypeChange={regenerateCardPersonaMoral}
					/>

					<!-- Domicilio Fiscal -->
					<DireccionEditor
						direccion={personaMoral.direccion}
						title="Domicilio Fiscal"
						copied={copied === 'direccion-moral'}
						onchange={(dir) => {
							personaMoral = { ...personaMoral!, direccion: dir };
						}}
						onCopy={(text) => copyToClipboard(text, 'direccion-moral')}
					/>

					<!-- Contacto (Editable) -->
					<div class="card p-6">
						<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<Phone class="h-5 w-5 text-teal-500" />
							Contacto
							<span class="text-xs font-normal text-slate-400">(editable)</span>
						</h3>
						<div class="space-y-4">
							<div>
								<label for="pm-telefono" class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Teléfono (10 dígitos)
									<span class="text-xs text-slate-400">
										{personaMoral.telefono.length === 10
											? (['55', '56', '33', '81'].includes(personaMoral.telefono.substring(0, 2)) ? '2-4-4' : '3-3-4')
											: ''}
									</span>
								</label>
								<div class="flex gap-2 mt-1">
									<input
										id="pm-telefono"
										type="tel"
										class="input font-mono flex-1"
										value={personaMoral.telefono}
										maxlength="10"
										placeholder="5512345678"
										oninput={(e) => updatePersonaMoral('telefono', e.currentTarget.value.replace(/\D/g, '').slice(0, 10))}
									/>
								</div>
								{#if personaMoral.telefono.length === 10}
									<div class="flex items-center justify-between mt-2 p-2 bg-slate-50 dark:bg-slate-800 rounded-lg text-sm">
										<span class="font-mono text-slate-700 dark:text-slate-300 tracking-wider">
											{formatPhone(personaMoral.telefono)}
										</span>
										<div class="flex items-center gap-1 text-xs">
											<span class="text-slate-400">copiar:</span>
											<button
												class="text-brand-500 hover:text-brand-600 px-1"
												onclick={() => copyToClipboard(personaMoral!.telefono, 'tel-moral-10')}
											>
												{copied === 'tel-moral-10' ? '✓' : '10 dígitos'}
											</button>
											<span class="text-slate-300">|</span>
											<button
												class="text-brand-500 hover:text-brand-600 px-1"
												onclick={() => copyToClipboard(`+52${personaMoral!.telefono}`, 'tel-moral-e164')}
											>
												{copied === 'tel-moral-e164' ? '✓' : 'E.164'}
											</button>
										</div>
									</div>
								{/if}
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Email
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.email, 'email')}>
										{copied === 'email' ? '✓' : 'copiar'}
									</button>
								</label>
								<input
									type="email"
									class="input mt-1"
									value={personaMoral.email}
									oninput={(e) => updatePersonaMoral('email', e.currentTarget.value)}
								/>
							</div>
						</div>
					</div>

					<!-- Representante Legal (Editable) -->
					<div class="card p-6 lg:col-span-2">
						<h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
							<User class="h-5 w-5 text-blue-500" />
							Representante Legal
							<span class="text-xs font-normal text-slate-400">(editable)</span>
						</h3>
						<div class="space-y-4">
							<div class="grid gap-4 sm:grid-cols-3">
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Nombre(s)
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.representante.nombre, 'rep-nombre')}>
											{copied === 'rep-nombre' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="text"
										class="input mt-1"
										value={personaMoral.representante.nombre}
										oninput={(e) => updateRepresentante('nombre', e.currentTarget.value)}
									/>
								</div>
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Apellido Paterno
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.representante.apellidoPaterno, 'rep-paterno')}>
											{copied === 'rep-paterno' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="text"
										class="input mt-1"
										value={personaMoral.representante.apellidoPaterno}
										oninput={(e) => updateRepresentante('apellidoPaterno', e.currentTarget.value)}
									/>
								</div>
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Apellido Materno
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.representante.apellidoMaterno, 'rep-materno')}>
											{copied === 'rep-materno' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="text"
										class="input mt-1"
										value={personaMoral.representante.apellidoMaterno}
										oninput={(e) => updateRepresentante('apellidoMaterno', e.currentTarget.value)}
										placeholder="(opcional)"
									/>
								</div>
							</div>
							<div>
								<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
									Nombre completo
									<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(`${personaMoral!.representante.nombre} ${personaMoral!.representante.apellidoPaterno} ${personaMoral!.representante.apellidoMaterno}`.trim(), 'rep-fullname')}>
										{copied === 'rep-fullname' ? '✓' : 'copiar'}
									</button>
								</label>
								<div class="text-sm font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-md">
									{personaMoral.representante.nombre} {personaMoral.representante.apellidoPaterno} {personaMoral.representante.apellidoMaterno}
								</div>
							</div>
							<div class="grid gap-4 sm:grid-cols-3">
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										Fecha de nacimiento
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.representante.fechaNacimiento, 'rep-fecha')}>
											{copied === 'rep-fecha' ? '✓' : 'copiar'}
										</button>
									</label>
									<input
										type="date"
										class="input mt-1"
										value={personaMoral.representante.fechaNacimiento}
										oninput={(e) => updateRepresentante('fechaNacimiento', e.currentTarget.value)}
									/>
								</div>
								<div>
									<label for="rep-sexo" class="text-sm text-slate-600 dark:text-slate-400">Sexo</label>
									<select
										id="rep-sexo"
										class="input mt-1"
										value={personaMoral.representante.sexo}
										onchange={(e) => updateRepresentante('sexo', e.currentTarget.value as 'H' | 'M')}
									>
										<option value="H">Masculino</option>
										<option value="M">Femenino</option>
									</select>
								</div>
								<div>
									<label for="rep-estado" class="text-sm text-slate-600 dark:text-slate-400">Estado de nacimiento</label>
									<select
										id="rep-estado"
										class="input mt-1"
										value={personaMoral.representante.estadoNacimiento}
										onchange={(e) => {
											const selectedState = states.find(s => s.code === e.currentTarget.value);
											if (selectedState) {
												personaMoral = {
													...personaMoral!,
													representante: {
														...personaMoral!.representante,
														estadoNacimiento: selectedState.code,
														estadoNacimientoNombre: selectedState.name
													}
												};
												recalculateRepresentante();
											}
										}}
									>
										{#each states as state}
											<option value={state.code}>{state.name}</option>
										{/each}
									</select>
								</div>
							</div>
							<div class="grid gap-4 sm:grid-cols-2 pt-2 border-t border-slate-200 dark:border-slate-700">
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										RFC
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.representante.rfc, 'rep-rfc')}>
											{copied === 'rep-rfc' ? '✓' : 'copiar'}
										</button>
									</label>
									<div class="text-sm font-mono font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-md mt-1">
										{personaMoral.representante.rfc}
									</div>
								</div>
								<div>
									<label class="text-sm text-slate-600 dark:text-slate-400 flex items-center justify-between">
										CURP
										<button class="text-xs text-brand-500 hover:text-brand-600" onclick={() => copyToClipboard(personaMoral!.representante.curp, 'rep-curp')}>
											{copied === 'rep-curp' ? '✓' : 'copiar'}
										</button>
									</label>
									<div class="text-xs font-mono font-medium text-slate-700 dark:text-slate-300 bg-slate-50 dark:bg-slate-800 px-3 py-2 rounded-md mt-1">
										{personaMoral.representante.curp}
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		{:else}
			<!-- Empty state -->
			<div class="card p-12 text-center">
				<div class="mx-auto w-16 h-16 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
					{#if personType === 'fisica'}
						<User class="h-8 w-8 text-slate-400" />
					{:else}
						<Building2 class="h-8 w-8 text-slate-400" />
					{/if}
				</div>
				<h3 class="text-lg font-medium text-slate-900 dark:text-white mb-2">
					{personType === 'fisica' ? 'Genera una identidad de persona física' : 'Genera una identidad de persona moral'}
				</h3>
				<p class="text-slate-500 dark:text-slate-400 mb-6 max-w-md mx-auto">
					{personType === 'fisica'
						? 'Incluye nombre, RFC, CURP, NSS, CLABE bancaria, dirección y contacto.'
						: 'Incluye razón social, RFC, domicilio fiscal y representante legal con sus datos.'}
				</p>
				<button
					class="btn btn-primary"
					onclick={generate}
					disabled={loading || !dataReady}
				>
					<RefreshCw class="h-4 w-4 mr-2 {loading ? 'animate-spin' : ''}" />
					{loading ? 'Generando...' : 'Generar Identidad'}
				</button>
			</div>
		{/if}

		<!-- Info -->
		<div class="mt-8 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-slate-200 dark:border-slate-700">
			<p class="text-xs text-slate-500 dark:text-slate-400">
				<strong>Aviso:</strong> Esta herramienta genera datos ficticios para pruebas de desarrollo.
				Los RFC y CURP se calculan con algoritmos oficiales pero con datos aleatorios.
				No usar estos datos para propósitos legales, fiscales o de identificación real.
				Los códigos postales y colonias provienen del catálogo oficial de SEPOMEX, pero las calles y números son ficticios.
			</p>
		</div>
	</div>
</section>
