import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const EXAMPLES = [
  {
    title: 'Validate RFC',
    typescript: `import { validateRfc, detectRfcType } from 'catalogmx';

// Validate an RFC
const isValid = validateRfc('GODE561231GR8');
console.log(isValid); // true

// Detect RFC type
const type = detectRfcType('GODE561231GR8');
console.log(type); // 'persona_fisica'`,
    python: `from catalogmx import validate_rfc, detect_rfc_type

# Validate an RFC
is_valid = validate_rfc("GODE561231GR8")
print(is_valid)  # True

# Detect RFC type
rfc_type = detect_rfc_type("GODE561231GR8")
print(rfc_type)  # "persona_fisica"`,
    dart: `import 'package:catalogmx/catalogmx.dart';

// Validate an RFC
final isValid = validateRfc('GODE561231GR8');
print(isValid); // true

// Detect RFC type
final type = detectRfcType('GODE561231GR8');
print(type); // RfcType.personaFisica`
  },
  {
    title: 'Generate RFC',
    typescript: `import { generateRfcPersonaFisica } from 'catalogmx';

const rfc = generateRfcPersonaFisica({
  nombre: 'Juan',
  apellidoPaterno: 'Garcia',
  apellidoMaterno: 'Lopez',
  fechaNacimiento: new Date(1990, 4, 15)
});

console.log(rfc); // e.g., GALJ900515XXX`,
    python: `from catalogmx import generate_rfc_persona_fisica
from datetime import date

rfc = generate_rfc_persona_fisica(
    nombre="Juan",
    apellido_paterno="Garcia",
    apellido_materno="Lopez",
    fecha_nacimiento=date(1990, 5, 15)
)

print(rfc)  # e.g., GALJ900515XXX`,
    dart: `import 'package:catalogmx/catalogmx.dart';

final rfc = generateRfcPersonaFisica(
  nombre: 'Juan',
  apellidoPaterno: 'Garcia',
  apellidoMaterno: 'Lopez',
  fechaNacimiento: DateTime(1990, 5, 15),
);

print(rfc); // e.g., GALJ900515XXX`
  },
  {
    title: 'Validate CLABE',
    typescript: `import { validateClabe, CLABEValidator } from 'catalogmx';

// Quick validation
const isValid = validateClabe('002010077777777771');

// Extract bank info
const clabe = new CLABEValidator('002010077777777771');
if (clabe.isValid()) {
  console.log(clabe.getBankCode());   // '002'
  console.log(clabe.getBankName());   // 'BANAMEX'
  console.log(clabe.getPlazaCode());  // '010'
}`,
    python: `from catalogmx import validate_clabe, CLABEValidator

# Quick validation
is_valid = validate_clabe("002010077777777771")

# Extract bank info
clabe = CLABEValidator("002010077777777771")
if clabe.is_valid():
    print(clabe.get_bank_code())   # "002"
    print(clabe.get_bank_name())   # "BANAMEX"
    print(clabe.get_plaza_code())  # "010"`,
    dart: `import 'package:catalogmx/catalogmx.dart';

// Quick validation
final isValid = validateClabe('002010077777777771');

// Extract bank info
final clabe = ClabeValidator('002010077777777771');
if (clabe.isValid()) {
  print(clabe.bankCode);   // '002'
  print(clabe.bankName);   // 'BANAMEX'
  print(clabe.plazaCode);  // '010'
}`
  },
  {
    title: 'Bank Catalog',
    typescript: `import { BankCatalog } from 'catalogmx';

// Get all banks
const banks = BankCatalog.getAll();

// Get bank by code
const banamex = BankCatalog.getBankByCode('002');
console.log(banamex.name); // 'BANAMEX'

// Get only SPEI-enabled banks
const speiBanks = BankCatalog.getSPEIBanks();

// Search banks
const results = BankCatalog.searchBanks('BBVA');`,
    python: `from catalogmx import BankCatalog

# Get all banks
banks = BankCatalog.get_all()

# Get bank by code
banamex = BankCatalog.get_by_code("002")
print(banamex.name)  # "BANAMEX"

# Get only SPEI-enabled banks
spei_banks = BankCatalog.get_spei_banks()

# Search banks
results = BankCatalog.search("BBVA")`,
    dart: `import 'package:catalogmx/catalogmx.dart';

// Get all banks
final banks = BankCatalog.getAll();

// Get bank by code
final banamex = BankCatalog.getByCode('002');
print(banamex?.name); // 'BANAMEX'

// Get only SPEI-enabled banks
final speiBanks = BankCatalog.getSpeiBanks();

// Search banks
final results = BankCatalog.search('BBVA');`
  },
  {
    title: 'SAT CFDI Catalogs',
    typescript: `import {
  RegimenFiscalCatalog,
  UsoCFDICatalog,
  FormaPagoCatalog
} from 'catalogmx';

// Tax regimes
const regimes = RegimenFiscalCatalog.getAll();
const regime = RegimenFiscalCatalog.getByCode('601');
console.log(regime.description);
// 'General de Ley Personas Morales'

// Invoice usage
const uso = UsoCFDICatalog.getByCode('G03');
console.log(uso.description); // 'Gastos en general'

// Payment methods
const formas = FormaPagoCatalog.getAll();`,
    python: `from catalogmx import (
    RegimenFiscalCatalog,
    UsoCFDICatalog,
    FormaPagoCatalog
)

# Tax regimes
regimes = RegimenFiscalCatalog.get_all()
regime = RegimenFiscalCatalog.get_by_code("601")
print(regime.description)
# "General de Ley Personas Morales"

# Invoice usage
uso = UsoCFDICatalog.get_by_code("G03")
print(uso.description)  # "Gastos en general"

# Payment methods
formas = FormaPagoCatalog.get_all()`,
    dart: `import 'package:catalogmx/catalogmx.dart';

// Tax regimes
final regimes = RegimenFiscalCatalog.getAll();
final regime = RegimenFiscalCatalog.getByCode('601');
print(regime?.description);
// 'General de Ley Personas Morales'

// Invoice usage
final uso = UsoCfdiCatalog.getByCode('G03');
print(uso?.description); // 'Gastos en general'

// Payment methods
final formas = FormaPagoCatalog.getAll();`
  },
  {
    title: 'Postal Codes',
    typescript: `import { CodigosPostales } from 'catalogmx';

// Get localities by postal code
const localities = CodigosPostales.getByPostalCode('06600');
console.log(localities);
// [{ cp: '06600', colonia: 'Roma Norte', ... }]

// Search by colony name
const results = CodigosPostales.searchByColony('Condesa');

// Get all postal codes for a state
const cdmxCodes = CodigosPostales.getByState('Ciudad de Mexico');`,
    python: `from catalogmx import CodigosPostales

# Get localities by postal code
localities = CodigosPostales.get_by_postal_code("06600")
print(localities)
# [{"cp": "06600", "colonia": "Roma Norte", ...}]

# Search by colony name
results = CodigosPostales.search_by_colony("Condesa")

# Get all postal codes for a state
cdmx_codes = CodigosPostales.get_by_state("Ciudad de Mexico")`,
    dart: `import 'package:catalogmx/catalogmx.dart';

// Get localities by postal code
final localities = CodigosPostales.getByPostalCode('06600');
print(localities);
// [{cp: '06600', colonia: 'Roma Norte', ...}]

// Search by colony name
final results = CodigosPostales.searchByColony('Condesa');

// Get all postal codes for a state
final cdmxCodes = CodigosPostales.getByState('Ciudad de Mexico');`
  }
];

export default function CodeExamples() {
  return (
    <div className="space-y-8">
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-3xl font-bold mb-2">Code Examples</h2>
        <p className="text-muted-foreground">
          Learn how to use catalogmx in TypeScript, Python, and Dart
        </p>
      </div>

      <div className="grid gap-6">
        {EXAMPLES.map((example) => (
          <Card key={example.title}>
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">{example.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="typescript">
                <TabsList className="mb-4">
                  <TabsTrigger value="typescript">
                    TypeScript
                    <Badge variant="secondary" className="ml-2 text-xs">npm</Badge>
                  </TabsTrigger>
                  <TabsTrigger value="python">
                    Python
                    <Badge variant="secondary" className="ml-2 text-xs">PyPI</Badge>
                  </TabsTrigger>
                  <TabsTrigger value="dart">
                    Dart
                    <Badge variant="secondary" className="ml-2 text-xs">pub.dev</Badge>
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="typescript">
                  <pre className="text-sm overflow-x-auto"><code>{example.typescript}</code></pre>
                </TabsContent>
                <TabsContent value="python">
                  <pre className="text-sm overflow-x-auto"><code>{example.python}</code></pre>
                </TabsContent>
                <TabsContent value="dart">
                  <pre className="text-sm overflow-x-auto"><code>{example.dart}</code></pre>
                </TabsContent>
              </Tabs>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
