# 🇲🇽 catalogmx (TypeScript/JavaScript)

**Comprehensive Mexican Data Validators and Official Catalogs**

A complete TypeScript/JavaScript library for validating Mexican identifiers and accessing official catalogs from SAT, Banxico, INEGI, SEPOMEX, and other government agencies.

[![npm version](https://img.shields.io/npm/v/catalogmx)](https://www.npmjs.com/package/catalogmx)
[![License](https://img.shields.io/badge/license-BSD-blue)](../../LICENSE)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)](https://www.typescriptlang.org/)

---

## ✨ Features

### 🔐 Validators

- **RFC** - Registro Federal de Contribuyentes (Mexican Tax ID)
  - Persona Física (13 characters) and Persona Moral (12 characters)
  - Check digit validation (Módulo 11)
  - Cacophonic word replacement
  - Generation and validation

- **CURP** - Clave Única de Registro de Población
  - 18-character validation with check digit
  - Complete RENAPO algorithm
  - State code validation
  - Generation from personal data

- **CLABE** - Clave Bancaria Estandarizada
  - 18-digit bank account validator
  - Modulo 10 check digit (Luhn-like)
  - Bank/branch code extraction

- **NSS** - Número de Seguridad Social (IMSS)
  - 11-digit validation
  - Modified Luhn algorithm check digit

### 📚 Official Catalogs

- **Banxico** - 100+ Mexican banks with SPEI status
- **INEGI** - States and municipalities
- **SEPOMEX** - Postal codes
- **SAT CFDI 4.0** - Tax catalogs (Régimen Fiscal, Uso CFDI, Forma de Pago)

---

## 🚀 Installation

```bash
npm install catalogmx
# or
yarn add catalogmx
# or
pnpm add catalogmx
```

---

## 📖 Usage

### Validators

```typescript
import {
  generateRfcPersonaFisica,
  generateCurp,
  validateClabe,
  validateNss
} from 'catalogmx';

// Generate RFC for individual
const rfc = generateRfcPersonaFisica({
  nombre: 'Juan',
  apellidoPaterno: 'Pérez',
  apellidoMaterno: 'García',
  fechaNacimiento: new Date('1990-05-15')
});
console.log(rfc);  // PEGJ900515XXX

// Generate CURP
const curp = generateCurp({
  nombre: 'Juan',
  apellidoPaterno: 'Pérez',
  apellidoMaterno: 'García',
  fechaNacimiento: new Date('1990-05-12'),
  sexo: 'H',
  estado: 'JALISCO'
});
console.log(curp);  // PEGJ900512HJCRRS04

// Validate CLABE
const isValid = validateClabe('002010077777777771');
console.log(isValid);  // true

// Validate NSS
const validNss = validateNss('12345678903');
console.log(validNss);  // true
```

### Catalogs

```typescript
import {
  BankCatalog,
  StateCatalog,
  CodigosPostales,
  RegimenFiscalCatalog,
  UsoCFDICatalog
} from 'catalogmx';

// Get bank info
const bank = BankCatalog.getBankByCode('002');
console.log(bank?.name);  // BANAMEX
console.log(bank?.spei);  // true

// Get state info
const state = StateCatalog.getStateByName('JALISCO');
console.log(state?.code);  // JC
console.log(state?.clave_inegi);  // 14

// Get postal code info
const postalCodes = CodigosPostales.getByCp('06700');
console.log(postalCodes[0]?.asentamiento);  // Roma Norte

// Validate tax regime
const regimen = RegimenFiscalCatalog.getRegimen('601');
console.log(regimen?.description);  // General de Ley Personas Morales
console.log(RegimenFiscalCatalog.isValidForPersonaMoral('601'));  // true

// Validate CFDI usage
const uso = UsoCFDICatalog.getUso('G03');
console.log(uso?.description);  // Gastos en general
```

---

## 🧪 Testing

```bash
npm test
# or
yarn test
```

---

## 🏗️ Building

```bash
npm run build
# or
yarn build
```

This will generate the `dist/` directory with compiled JavaScript and type declarations.

---

## 📚 Documentation

For complete documentation, see the main project README at the repository root.

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.rst](../../CONTRIBUTING.rst) for details.

---

## 📝 License

BSD 2-Clause License - See [LICENSE](../../LICENSE) for details.

---

## 🙏 Acknowledgments

All catalog data comes from official Mexican government sources:
- **SAT** - Servicio de Administración Tributaria
- **INEGI** - Instituto Nacional de Estadística y Geografía
- **SEPOMEX** - Servicio Postal Mexicano
- **Banxico** - Banco de México

---

Made with ❤️ for the Mexican developer community
