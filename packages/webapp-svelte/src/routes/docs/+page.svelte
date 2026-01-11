<script lang="ts">
	import { Book, Code, Terminal, Package, Copy, Check, ChevronRight } from 'lucide-svelte';

	let copiedIndex = $state<number | null>(null);

	function copyCode(code: string, index: number) {
		navigator.clipboard.writeText(code);
		copiedIndex = index;
		setTimeout(() => copiedIndex = null, 2000);
	}

	const pythonExamples = [
		{
			title: 'Validadores',
			description: 'Validar RFC, CURP, CLABE y NSS',
			code: `from catalogmx import is_valid_rfc, is_valid_curp, is_valid_clabe, is_valid_nss

# Validar RFC
is_valid_rfc('GODE561231GR8')  # True

# Validar CURP
is_valid_curp('GORS561231HVZNNL00')  # True

# Validar CLABE
is_valid_clabe('002010077777777771')  # True

# Validar NSS
is_valid_nss('12345678903')  # True`
		},
		{
			title: 'Generadores',
			description: 'Generar RFC, CURP y CLABE con dígito verificador',
			code: `from catalogmx import (
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
    generate_curp,
    generate_clabe
)

# Generar RFC persona física
rfc = generate_rfc_persona_fisica(
    nombre='Juan',
    apellido_paterno='García',
    apellido_materno='López',
    fecha_nacimiento='1990-05-15'
)
print(rfc)  # GALJ900515XXX

# Generar RFC persona moral
rfc_moral = generate_rfc_persona_moral(
    razon_social='Tecnología Sistemas S.A.',
    fecha_constitucion='2020-01-15'
)
print(rfc_moral)  # TSI200115XXX

# Generar CURP
curp = generate_curp(
    nombre='Juan',
    apellido_paterno='García',
    apellido_materno='López',
    fecha_nacimiento='1990-05-15',
    sexo='H',
    estado='Jalisco'
)

# Generar CLABE con dígito verificador
clabe = generate_clabe(
    bank_code='002',      # Banamex
    branch_code='010',
    account_number='07777777777'
)
print(clabe)  # 002010077777777771`
		},
		{
			title: 'Calculadoras Fiscales',
			description: 'Calcular ISR, RESICO, IVA, IMSS y costo del trabajador',
			code: `from catalogmx.calculators import (
    calculate_isr,
    calculate_resico,
    calcular_cuotas_obrero_patronales,
    IVACalculator,
    calcular_costo_total
)

# Calcular ISR
result = calculate_isr(
    ingreso_gravable=50000,
    year=2025,
    periodo='mensual'
)
print(f"ISR: {result['isrFinal']:,.2f}")
print(f"Tasa efectiva: {result['tasaEfectiva']:.2%}")

# Calcular RESICO
resico = calculate_resico(
    ingreso=100000,
    year=2025,
    periodo='mensual'
)
print(f"RESICO: {resico['resicoCalculado']:,.2f}")

# Calcular cuotas IMSS
imss = calcular_cuotas_obrero_patronales(
    salario_diario=500,
    dias=30,
    year=2025,
    zona='general',
    clase_riesgo=3
)
print(f"Cuota patronal: {imss['total_patron']:,.2f}")
print(f"Cuota trabajador: {imss['total_trabajador']:,.2f}")

# Calcular IVA
iva = IVACalculator()
resultado = iva.calcular(base=1000, tipo_tasa='general')
print(f"IVA 16%: {resultado['iva']:,.2f}")

# Costo total del trabajador
costo = calcular_costo_total(
    salario_mensual=30000,
    year=2025
)
print(f"Costo total mensual: {costo['costo_total_mensual']:,.2f}")`
		},
		{
			title: 'Catálogos SAT',
			description: 'Acceder a catálogos de CFDI, nómina, comercio exterior',
			code: `from catalogmx.catalogs.sat.cfdi_4 import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog,
    ClaveProdServCatalog
)

# Obtener régimen fiscal
regimen = RegimenFiscalCatalog.get_regimen_fiscal('605')
print(regimen)  # Sueldos y Salarios

# Validar régimen
is_valid = RegimenFiscalCatalog.is_valid('605')

# Buscar productos/servicios
productos = ClaveProdServCatalog.search('software')

# Uso de CFDI
uso = UsoCFDICatalog.get_by_code('G01')  # Adquisición de mercancías`
		},
		{
			title: 'Catálogos Banxico',
			description: 'Bancos, plazas, tipo de cambio, UDI',
			code: `from catalogmx.catalogs.banxico import (
    BankCatalog,
    CodigosPlazaCatalog
)

# Obtener banco por código
bank = BankCatalog.get_by_code('002')
print(bank['name'])  # BANAMEX

# Listar todos los bancos con SPEI
banks = BankCatalog.get_all()
spei_banks = [b for b in banks if b['spei']]

# Obtener plaza bancaria
plaza = CodigosPlazaCatalog.get_by_code('010')`
		},
		{
			title: 'Catálogos INEGI',
			description: 'Estados, municipios, localidades, SCIAN',
			code: `from catalogmx.catalogs.inegi import States, Municipios, SCIAN

# Obtener todos los estados
states = States.get_all()

# Obtener estado por código
cdmx = States.get_by_code('09')

# Obtener municipios de un estado
municipios_jal = Municipios.get_by_state('14')

# Buscar en SCIAN
sectores = SCIAN.search('tecnología')`
		},
		{
			title: 'Catálogos SEPOMEX',
			description: 'Códigos postales con colonias y municipios',
			code: `from catalogmx.catalogs.sepomex import CodigosPostales

# Buscar por código postal
cp_data = CodigosPostales.get_by_cp('06600')
for colonia in cp_data:
    print(f"{colonia['asentamiento']}, {colonia['municipio']}")

# Buscar colonias
resultados = CodigosPostales.search('Roma')`
		}
	];

	const typescriptExamples = [
		{
			title: 'Validadores y Generadores',
			description: 'Validar y generar identificadores mexicanos',
			code: `import {
  validateRFC, validateCURP, validateCLABE, validateNSS,
  generateRFC, generateCURP, generateClabe
} from 'catalogmx';

// Validar RFC
const isValidRfc = validateRFC('GODE561231GR8'); // true

// Validar CURP
const isValidCurp = validateCURP('GORS561231HVZNNL00'); // true

// Validar CLABE
const isValidClabe = validateCLABE('002010077777777771'); // true

// Generar RFC
const rfc = generateRFC({
  nombre: 'Juan',
  apellidoPaterno: 'García',
  apellidoMaterno: 'López',
  fechaNacimiento: new Date(1990, 4, 15)
});

// Generar CLABE
const clabe = generateClabe('002', '010', '07777777777');
console.log(clabe); // 002010077777777771`
		},
		{
			title: 'Calculadoras',
			description: 'Calcular impuestos y cuotas',
			code: `import { calculateISR, calculateRESICO, calculateIMSS } from 'catalogmx';

// Calcular ISR
const isr = calculateISR({
  ingresoGravable: 50000,
  year: 2025,
  periodo: 'mensual'
});
console.log(\`ISR: $\${isr.isrFinal.toFixed(2)}\`);

// Calcular RESICO
const resico = calculateRESICO({
  ingreso: 100000,
  year: 2025,
  periodo: 'mensual'
});

// Calcular IMSS
const imss = calculateIMSS({
  salarioDiario: 500,
  dias: 30,
  year: 2025,
  zona: 'general',
  claseRiesgo: 3
});`
		}
	];

	const dartExamples = [
		{
			title: 'Validadores y Generadores',
			description: 'Uso en Flutter/Dart',
			code: `import 'package:catalogmx/catalogmx.dart';

// Validar RFC
final isValidRfc = validateRFC('GODE561231GR8'); // true

// Validar CURP
final isValidCurp = validateCURP('GORS561231HVZNNL00'); // true

// Validar CLABE
final isValidClabe = validateCLABE('002010077777777771'); // true

// Generar CLABE
final clabe = generateCLABE(
  bankCode: '002',
  branchCode: '010',
  accountNumber: '07777777777',
);
print(clabe); // 002010077777777771

// Acceder a catálogos
final states = INEGIStates.getAll();
final banks = BanxicoBanks.getAll();`
		}
	];
</script>

<svelte:head>
	<title>Documentación - catalogmx</title>
	<meta name="description" content="Documentación y ejemplos de código para catalogmx. Validadores, generadores, calculadoras y catálogos para Python, TypeScript y Dart." />
</svelte:head>

<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
	<!-- Header -->
	<div class="mb-12">
		<div class="flex items-center gap-3 mb-4">
			<div class="bg-brand-100 dark:bg-brand-900/30 p-3 rounded-lg">
				<Book class="h-6 w-6 text-brand-600 dark:text-brand-400" />
			</div>
			<h1 class="text-3xl font-bold text-slate-900 dark:text-white">
				Documentación
			</h1>
		</div>
		<p class="text-lg text-slate-600 dark:text-slate-300 max-w-3xl">
			Ejemplos de código para usar catalogmx en Python, TypeScript y Dart.
			Copia y pega estos ejemplos en tu proyecto.
		</p>
	</div>

	<!-- Installation -->
	<section id="instalacion" class="mb-12">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
			<Package class="h-6 w-6 text-green-500" />
			Instalación
		</h2>

		<div class="grid gap-4 sm:grid-cols-3">
			<div class="card p-4">
				<div class="flex items-center gap-2 mb-3">
					<span class="bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-medium px-2 py-1 rounded">Python</span>
				</div>
				<div class="bg-slate-900 rounded-lg p-3 font-mono text-sm text-green-400 relative group">
					<code>pip install catalogmx</code>
					<button
						onclick={() => copyCode('pip install catalogmx', 100)}
						class="absolute right-2 top-2 p-1 rounded hover:bg-slate-700 opacity-0 group-hover:opacity-100 transition-opacity"
					>
						{#if copiedIndex === 100}
							<Check class="h-4 w-4 text-green-400" />
						{:else}
							<Copy class="h-4 w-4 text-slate-400" />
						{/if}
					</button>
				</div>
				<p class="text-xs text-slate-500 mt-2">o con uv: <code class="bg-slate-100 dark:bg-slate-800 px-1 rounded">uv pip install catalogmx</code></p>
			</div>

			<div class="card p-4">
				<div class="flex items-center gap-2 mb-3">
					<span class="bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs font-medium px-2 py-1 rounded">TypeScript</span>
				</div>
				<div class="bg-slate-900 rounded-lg p-3 font-mono text-sm text-green-400 relative group">
					<code>npm install catalogmx</code>
					<button
						onclick={() => copyCode('npm install catalogmx', 101)}
						class="absolute right-2 top-2 p-1 rounded hover:bg-slate-700 opacity-0 group-hover:opacity-100 transition-opacity"
					>
						{#if copiedIndex === 101}
							<Check class="h-4 w-4 text-green-400" />
						{:else}
							<Copy class="h-4 w-4 text-slate-400" />
						{/if}
					</button>
				</div>
				<p class="text-xs text-slate-500 mt-2">o: <code class="bg-slate-100 dark:bg-slate-800 px-1 rounded">yarn add catalogmx</code></p>
			</div>

			<div class="card p-4">
				<div class="flex items-center gap-2 mb-3">
					<span class="bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300 text-xs font-medium px-2 py-1 rounded">Dart/Flutter</span>
				</div>
				<div class="bg-slate-900 rounded-lg p-3 font-mono text-sm text-green-400 relative group">
					<code>dart pub add catalogmx</code>
					<button
						onclick={() => copyCode('dart pub add catalogmx', 102)}
						class="absolute right-2 top-2 p-1 rounded hover:bg-slate-700 opacity-0 group-hover:opacity-100 transition-opacity"
					>
						{#if copiedIndex === 102}
							<Check class="h-4 w-4 text-green-400" />
						{:else}
							<Copy class="h-4 w-4 text-slate-400" />
						{/if}
					</button>
				</div>
				<p class="text-xs text-slate-500 mt-2">o: <code class="bg-slate-100 dark:bg-slate-800 px-1 rounded">flutter pub add catalogmx</code></p>
			</div>
		</div>
	</section>

	<!-- Python Examples -->
	<section id="python" class="mb-12">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
			<Code class="h-6 w-6 text-blue-500" />
			Python
		</h2>

		<div class="space-y-6">
			{#each pythonExamples as example, i}
				<div class="card overflow-hidden">
					<div class="p-4 border-b border-slate-200 dark:border-slate-700">
						<h3 class="font-semibold text-slate-900 dark:text-white">{example.title}</h3>
						<p class="text-sm text-slate-500 dark:text-slate-400">{example.description}</p>
					</div>
					<div class="relative">
						<pre class="bg-slate-900 p-4 overflow-x-auto text-sm"><code class="text-slate-300">{example.code}</code></pre>
						<button
							onclick={() => copyCode(example.code, i)}
							class="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
						>
							{#if copiedIndex === i}
								<Check class="h-4 w-4 text-green-400" />
							{:else}
								<Copy class="h-4 w-4 text-slate-400" />
							{/if}
						</button>
					</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- TypeScript Examples -->
	<section id="typescript" class="mb-12">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
			<Code class="h-6 w-6 text-yellow-500" />
			TypeScript / Node.js
		</h2>

		<div class="space-y-6">
			{#each typescriptExamples as example, i}
				<div class="card overflow-hidden">
					<div class="p-4 border-b border-slate-200 dark:border-slate-700">
						<h3 class="font-semibold text-slate-900 dark:text-white">{example.title}</h3>
						<p class="text-sm text-slate-500 dark:text-slate-400">{example.description}</p>
					</div>
					<div class="relative">
						<pre class="bg-slate-900 p-4 overflow-x-auto text-sm"><code class="text-slate-300">{example.code}</code></pre>
						<button
							onclick={() => copyCode(example.code, i + 100)}
							class="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
						>
							{#if copiedIndex === i + 100}
								<Check class="h-4 w-4 text-green-400" />
							{:else}
								<Copy class="h-4 w-4 text-slate-400" />
							{/if}
						</button>
					</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- Dart Examples -->
	<section id="dart" class="mb-12">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
			<Code class="h-6 w-6 text-cyan-500" />
			Dart / Flutter
		</h2>

		<div class="space-y-6">
			{#each dartExamples as example, i}
				<div class="card overflow-hidden">
					<div class="p-4 border-b border-slate-200 dark:border-slate-700">
						<h3 class="font-semibold text-slate-900 dark:text-white">{example.title}</h3>
						<p class="text-sm text-slate-500 dark:text-slate-400">{example.description}</p>
					</div>
					<div class="relative">
						<pre class="bg-slate-900 p-4 overflow-x-auto text-sm"><code class="text-slate-300">{example.code}</code></pre>
						<button
							onclick={() => copyCode(example.code, i + 200)}
							class="absolute right-3 top-3 p-2 rounded-lg bg-slate-800 hover:bg-slate-700 transition-colors"
						>
							{#if copiedIndex === i + 200}
								<Check class="h-4 w-4 text-green-400" />
							{:else}
								<Copy class="h-4 w-4 text-slate-400" />
							{/if}
						</button>
					</div>
				</div>
			{/each}
		</div>
	</section>

	<!-- API Reference Links -->
	<section id="recursos" class="mb-12">
		<h2 class="text-2xl font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
			<Terminal class="h-6 w-6 text-purple-500" />
			Recursos adicionales
		</h2>

		<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
			<a href="https://github.com/openbancor/catalogmx" target="_blank" rel="noopener" class="card p-4 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group">
				<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500 flex items-center gap-2">
					GitHub
					<ChevronRight class="h-4 w-4" />
				</h3>
				<p class="text-sm text-slate-500 dark:text-slate-400">Código fuente y contribuciones</p>
			</a>

			<a href="https://pypi.org/project/catalogmx/" target="_blank" rel="noopener" class="card p-4 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group">
				<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500 flex items-center gap-2">
					PyPI
					<ChevronRight class="h-4 w-4" />
				</h3>
				<p class="text-sm text-slate-500 dark:text-slate-400">Paquete Python</p>
			</a>

			<a href="https://www.npmjs.com/package/catalogmx" target="_blank" rel="noopener" class="card p-4 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group">
				<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500 flex items-center gap-2">
					npm
					<ChevronRight class="h-4 w-4" />
				</h3>
				<p class="text-sm text-slate-500 dark:text-slate-400">Paquete TypeScript/Node.js</p>
			</a>

			<a href="https://pub.dev/packages/catalogmx" target="_blank" rel="noopener" class="card p-4 hover:border-brand-300 dark:hover:border-brand-700 transition-colors group">
				<h3 class="font-semibold text-slate-900 dark:text-white group-hover:text-brand-500 flex items-center gap-2">
					pub.dev
					<ChevronRight class="h-4 w-4" />
				</h3>
				<p class="text-sm text-slate-500 dark:text-slate-400">Paquete Dart/Flutter</p>
			</a>
		</div>
	</section>
</div>
