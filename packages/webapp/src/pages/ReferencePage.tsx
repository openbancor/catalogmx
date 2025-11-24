import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Code, Copy, Check, Terminal, BookOpen } from 'lucide-react';
import { Button } from '@/components/ui/button';

type Tab = 'typescript' | 'python' | 'dart';

function CodeBlock({ code, language }: { code: string; language: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="sm"
        className="absolute top-2 right-2 h-8 w-8 p-0"
        onClick={handleCopy}
      >
        {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
      </Button>
      <pre className="p-4 bg-muted rounded-lg overflow-x-auto text-sm font-mono">
        <code>{code}</code>
      </pre>
      <div className="absolute bottom-2 right-2">
        <Badge variant="secondary" className="text-xs">{language}</Badge>
      </div>
    </div>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${
        active ? 'bg-muted text-foreground' : 'text-muted-foreground hover:text-foreground'
      }`}
    >
      {children}
    </button>
  );
}

export default function ReferencePage() {
  const [validatorTab, setValidatorTab] = useState<Tab>('typescript');
  const [catalogTab, setCatalogTab] = useState<Tab>('typescript');
  const [calcTab, setCalcTab] = useState<Tab>('typescript');

  const validatorCode = {
    typescript: `import {
  validateRFC, validateCURP, validateCLABE, validateNSS,
  generateRFC, generateCURP
} from 'catalogmx';

// Validate RFC
const rfcResult = validateRFC('GARC850101HDFRRL09');
console.log(rfcResult.isValid);     // true
console.log(rfcResult.type);        // 'persona_fisica'
console.log(rfcResult.parsed.date); // '850101'

// Validate CURP
const curpResult = validateCURP('GARC850101HDFRRL09');
if (curpResult.isValid) {
  console.log(curpResult.parsed.birthDate);  // '1985-01-01'
  console.log(curpResult.parsed.gender);     // 'Masculino'
  console.log(curpResult.parsed.stateName);  // 'Ciudad de México'
}

// Validate CLABE
const clabeResult = validateCLABE('002010077777777771');
console.log(clabeResult.parsed.bankName);    // 'BANAMEX'
console.log(clabeResult.parsed.branchCode);  // '010'

// Validate NSS
const nssResult = validateNSS('12345678901');
console.log(nssResult.parsed.subdelegation); // '12'

// Generate RFC
const rfc = generateRFC({
  nombre: 'Juan',
  paterno: 'Garcia',
  materno: 'Lopez',
  fecha: new Date('1985-01-01')
});
console.log(rfc); // 'GALJ850101XXX'`,
    python: `from catalogmx import (
    validate_rfc, validate_curp, validate_clabe, validate_nss,
    generate_rfc, generate_curp
)
from datetime import date

# Validate RFC
rfc_result = validate_rfc('GARC850101HDFRRL09')
print(rfc_result['is_valid'])      # True
print(rfc_result['type'])          # 'persona_fisica'
print(rfc_result['parsed']['date'])# '850101'

# Validate CURP
curp_result = validate_curp('GARC850101HDFRRL09')
if curp_result['is_valid']:
    print(curp_result['parsed']['birth_date'])   # '1985-01-01'
    print(curp_result['parsed']['gender'])       # 'Masculino'
    print(curp_result['parsed']['state_name'])   # 'Ciudad de México'

# Validate CLABE
clabe_result = validate_clabe('002010077777777771')
print(clabe_result['parsed']['bank_name'])   # 'BANAMEX'
print(clabe_result['parsed']['branch_code']) # '010'

# Validate NSS
nss_result = validate_nss('12345678901')
print(nss_result['parsed']['subdelegation']) # '12'

# Generate RFC
rfc = generate_rfc(
    nombre='Juan',
    paterno='Garcia',
    materno='Lopez',
    fecha=date(1985, 1, 1)
)
print(rfc)  # 'GALJ850101XXX'`,
    dart: `import 'package:catalogmx/catalogmx.dart';

void main() {
  // Validate RFC
  final rfcResult = validateRFC('GARC850101HDFRRL09');
  print(rfcResult.isValid);     // true
  print(rfcResult.type);        // RFCType.personaFisica
  print(rfcResult.parsed?.date);// '850101'

  // Validate CURP
  final curpResult = validateCURP('GARC850101HDFRRL09');
  if (curpResult.isValid) {
    print(curpResult.parsed?.birthDate);  // '1985-01-01'
    print(curpResult.parsed?.gender);     // 'Masculino'
    print(curpResult.parsed?.stateName);  // 'Ciudad de México'
  }

  // Validate CLABE
  final clabeResult = validateCLABE('002010077777777771');
  print(clabeResult.parsed?.bankName);    // 'BANAMEX'
  print(clabeResult.parsed?.branchCode);  // '010'

  // Validate NSS
  final nssResult = validateNSS('12345678901');
  print(nssResult.parsed?.subdelegation); // '12'

  // Generate RFC
  final rfc = generateRFC(
    nombre: 'Juan',
    paterno: 'Garcia',
    materno: 'Lopez',
    fecha: DateTime(1985, 1, 1),
  );
  print(rfc); // 'GALJ850101XXX'
}`
  };

  const catalogCode = {
    typescript: `import { catalogs } from 'catalogmx';

// Get all banks
const banks = catalogs.banxico.banks.getAll();
console.log(banks.length); // 145

// Get bank by code
const bank = catalogs.banxico.banks.getByCode('002');
console.log(bank?.nombre); // 'BANAMEX'

// Validate bank code
const isValidBank = catalogs.banxico.banks.isValid('012');
console.log(isValidBank); // true

// Get all tax regimes
const regimes = catalogs.sat.regimenes.getAll();

// Get regime by code
const regime = catalogs.sat.regimenes.getByCode('601');
console.log(regime?.descripcion);
// 'General de Ley Personas Morales'

// Get all states
const states = catalogs.inegi.estados.getAll();
console.log(states[0]);
// { clave: '01', nombre: 'Aguascalientes' }

// Search postal codes (if using SQLite)
const postalCodes = await catalogs.sepomex.search('06600');
console.log(postalCodes[0].d_asenta); // 'Juarez'`,
    python: `from catalogmx import catalogs

# Get all banks
banks = catalogs.banxico.banks.get_all()
print(len(banks))  # 145

# Get bank by code
bank = catalogs.banxico.banks.get_by_code('002')
print(bank['nombre'])  # 'BANAMEX'

# Validate bank code
is_valid_bank = catalogs.banxico.banks.is_valid('012')
print(is_valid_bank)  # True

# Get all tax regimes
regimes = catalogs.sat.regimenes.get_all()

# Get regime by code
regime = catalogs.sat.regimenes.get_by_code('601')
print(regime['descripcion'])
# 'General de Ley Personas Morales'

# Get all states
states = catalogs.inegi.estados.get_all()
print(states[0])
# {'clave': '01', 'nombre': 'Aguascalientes'}

# Search postal codes (if using SQLite)
postal_codes = catalogs.sepomex.search('06600')
print(postal_codes[0]['d_asenta'])  # 'Juarez'`,
    dart: `import 'package:catalogmx/catalogmx.dart';

void main() async {
  // Get all banks
  final banks = Catalogs.banxico.banks.getAll();
  print(banks.length); // 145

  // Get bank by code
  final bank = Catalogs.banxico.banks.getByCode('002');
  print(bank?.nombre); // 'BANAMEX'

  // Validate bank code
  final isValidBank = Catalogs.banxico.banks.isValid('012');
  print(isValidBank); // true

  // Get all tax regimes
  final regimes = Catalogs.sat.regimenes.getAll();

  // Get regime by code
  final regime = Catalogs.sat.regimenes.getByCode('601');
  print(regime?.descripcion);
  // 'General de Ley Personas Morales'

  // Get all states
  final states = Catalogs.inegi.estados.getAll();
  print(states[0]);
  // {clave: '01', nombre: 'Aguascalientes'}
}`
  };

  const calcCode = {
    typescript: `import { calculateISR, calculateIVA, calculateIEPS } from 'catalogmx';

// Calculate ISR (Income Tax)
const isrResult = calculateISR(15000, 'mensual');
console.log(isrResult.isrFinal);      // Tax amount
console.log(isrResult.tasaEfectiva);  // Effective rate %
console.log(isrResult.subsidio);      // Employment subsidy
console.log(isrResult.steps);         // Step-by-step breakdown

// Step-by-step breakdown
isrResult.steps.forEach(step => {
  console.log('Step ' + step.step + ': ' + step.description);
  console.log('  Formula: ' + step.formula);
  console.log('  Result: $' + step.result.toFixed(2));
});

// Calculate IVA (VAT)
const ivaResult = calculateIVA(1000, 16); // 16% rate
console.log(ivaResult.base);   // 1000
console.log(ivaResult.iva);    // 160
console.log(ivaResult.total);  // 1160

// Calculate IEPS (Special Tax)
const iepsResult = calculateIEPS(1000, 'bebidas_azucaradas');
console.log(iepsResult.ieps);  // 80 (8%)
console.log(iepsResult.total); // 1080`,
    python: `from catalogmx import calculate_isr, calculate_iva, calculate_ieps

# Calculate ISR (Income Tax)
isr_result = calculate_isr(15000, 'mensual')
print(isr_result['isr_final'])      # Tax amount
print(isr_result['tasa_efectiva'])  # Effective rate %
print(isr_result['subsidio'])       # Employment subsidy
print(isr_result['steps'])          # Step-by-step breakdown

# Step-by-step breakdown
for step in isr_result['steps']:
    print("Step " + str(step['step']) + ": " + step['description'])
    print("  Formula: " + step['formula'])
    print("  Result: $" + str(step['result']))

# Calculate IVA (VAT)
iva_result = calculate_iva(1000, 16)  # 16% rate
print(iva_result['base'])   # 1000
print(iva_result['iva'])    # 160
print(iva_result['total'])  # 1160

# Calculate IEPS (Special Tax)
ieps_result = calculate_ieps(1000, 'bebidas_azucaradas')
print(ieps_result['ieps'])   # 80 (8%)
print(ieps_result['total'])  # 1080`,
    dart: `import 'package:catalogmx/catalogmx.dart';

void main() {
  // Calculate ISR (Income Tax)
  final isrResult = calculateISR(15000, periodo: 'mensual');
  print(isrResult.isrFinal);      // Tax amount
  print(isrResult.tasaEfectiva);  // Effective rate %
  print(isrResult.subsidio);      // Employment subsidy
  print(isrResult.steps);         // Step-by-step breakdown

  // Step-by-step breakdown
  for (final step in isrResult.steps) {
    print('Step ' + step.step.toString() + ': ' + step.description);
    print('  Formula: ' + step.formula);
    print('  Result: ' + step.result.toStringAsFixed(2));
  }

  // Calculate IVA (VAT)
  final ivaResult = calculateIVA(1000, tasa: 16); // 16% rate
  print(ivaResult.base);   // 1000
  print(ivaResult.iva);    // 160
  print(ivaResult.total);  // 1160

  // Calculate IEPS (Special Tax)
  final iepsResult = calculateIEPS(1000, 'bebidas_azucaradas');
  print(iepsResult.ieps);   // 80 (8%)
  print(iepsResult.total);  // 1080
}`
  };

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-bold">Code Reference</h1>
        <p className="text-muted-foreground mt-1">
          Usage examples for catalogmx in TypeScript, Python, and Dart
        </p>
      </div>

      {/* Installation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Terminal className="h-5 w-5" />
            Installation
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <div className="font-medium mb-2 flex items-center gap-2">
                <Badge>npm</Badge> TypeScript/JavaScript
              </div>
              <pre className="p-3 bg-muted rounded text-sm font-mono">npm install catalogmx</pre>
            </div>
            <div>
              <div className="font-medium mb-2 flex items-center gap-2">
                <Badge>pip</Badge> Python
              </div>
              <pre className="p-3 bg-muted rounded text-sm font-mono">pip install catalogmx</pre>
            </div>
            <div>
              <div className="font-medium mb-2 flex items-center gap-2">
                <Badge>pub</Badge> Dart/Flutter
              </div>
              <pre className="p-3 bg-muted rounded text-sm font-mono">dart pub add catalogmx</pre>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Validators */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code className="h-5 w-5" />
            Validators
          </CardTitle>
          <CardDescription>
            Validate and generate RFC, CURP, CLABE, and NSS
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-1 border-b mb-4">
            <TabButton active={validatorTab === 'typescript'} onClick={() => setValidatorTab('typescript')}>
              TypeScript
            </TabButton>
            <TabButton active={validatorTab === 'python'} onClick={() => setValidatorTab('python')}>
              Python
            </TabButton>
            <TabButton active={validatorTab === 'dart'} onClick={() => setValidatorTab('dart')}>
              Dart
            </TabButton>
          </div>
          <CodeBlock code={validatorCode[validatorTab]} language={validatorTab} />
        </CardContent>
      </Card>

      {/* Catalogs */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Catalogs
          </CardTitle>
          <CardDescription>
            Access 58 official Mexican government catalogs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-1 border-b mb-4">
            <TabButton active={catalogTab === 'typescript'} onClick={() => setCatalogTab('typescript')}>
              TypeScript
            </TabButton>
            <TabButton active={catalogTab === 'python'} onClick={() => setCatalogTab('python')}>
              Python
            </TabButton>
            <TabButton active={catalogTab === 'dart'} onClick={() => setCatalogTab('dart')}>
              Dart
            </TabButton>
          </div>
          <CodeBlock code={catalogCode[catalogTab]} language={catalogTab} />
        </CardContent>
      </Card>

      {/* Calculators */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code className="h-5 w-5" />
            Tax Calculators
          </CardTitle>
          <CardDescription>
            Calculate ISR, IVA, and IEPS with step-by-step breakdowns
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-1 border-b mb-4">
            <TabButton active={calcTab === 'typescript'} onClick={() => setCalcTab('typescript')}>
              TypeScript
            </TabButton>
            <TabButton active={calcTab === 'python'} onClick={() => setCalcTab('python')}>
              Python
            </TabButton>
            <TabButton active={calcTab === 'dart'} onClick={() => setCalcTab('dart')}>
              Dart
            </TabButton>
          </div>
          <CodeBlock code={calcCode[calcTab]} language={calcTab} />
        </CardContent>
      </Card>

      {/* Links */}
      <Card>
        <CardHeader>
          <CardTitle>Resources</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid sm:grid-cols-3 gap-4">
            <a
              href="https://github.com/openbancor/catalogmx"
              target="_blank"
              rel="noopener noreferrer"
              className="p-4 border rounded-lg hover:border-primary transition-colors"
            >
              <div className="font-medium">GitHub Repository</div>
              <div className="text-sm text-muted-foreground">Source code and issues</div>
            </a>
            <a
              href="https://www.npmjs.com/package/catalogmx"
              target="_blank"
              rel="noopener noreferrer"
              className="p-4 border rounded-lg hover:border-primary transition-colors"
            >
              <div className="font-medium">npm Package</div>
              <div className="text-sm text-muted-foreground">TypeScript/JavaScript</div>
            </a>
            <a
              href="https://pypi.org/project/catalogmx/"
              target="_blank"
              rel="noopener noreferrer"
              className="p-4 border rounded-lg hover:border-primary transition-colors"
            >
              <div className="font-medium">PyPI Package</div>
              <div className="text-sm text-muted-foreground">Python</div>
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
