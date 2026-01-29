#!/usr/bin/env npx ts-node
/**
 * Validators App - TypeScript
 *
 * Demuestra los validadores de RFC, CURP, CLABE y NSS.
 *
 * Uso:
 *   npx ts-node examples/validators-app.ts
 */

import { validateRfc, getRfcInfo, generateRfcFisica, generateRfcMoral } from '../src/validators/rfc';
import { validateCurp, getCurpInfo, generateCurp } from '../src/validators/curp';
import { validateClabe, getClabeInfo, generateClabe } from '../src/validators/clabe';
import { validateNss, getNssInfo, generateNss } from '../src/validators/nss';

function printHeader(): void {
  console.log();
  console.log('╔══════════════════════════════════════════════════════╗');
  console.log('║     🪪 Validadores Mexicanos - catalogmx             ║');
  console.log('╚══════════════════════════════════════════════════════╝');
  console.log();
}

function demoRfc(): void {
  console.log('  📋 RFC (Registro Federal de Contribuyentes)');
  console.log('  ───────────────────────────────────────────');
  console.log();

  // Generar RFC persona física
  const rfcFisica = generateRfcFisica({
    nombre: 'Juan',
    apellidoPaterno: 'García',
    apellidoMaterno: 'López',
    fechaNacimiento: new Date(1990, 4, 15), // 15 mayo 1990
  });

  console.log('  Persona Física:');
  console.log(`    Nombre: Juan García López`);
  console.log(`    Fecha:  1990-05-15`);
  console.log(`    RFC:    ${rfcFisica}`);
  console.log(`    Válido: ${validateRfc(rfcFisica) ? '✅' : '❌'}`);

  const infoFisica = getRfcInfo(rfcFisica);
  if (infoFisica) {
    console.log(`    Tipo:   ${infoFisica.type}`);
  }
  console.log();

  // Generar RFC persona moral
  const rfcMoral = generateRfcMoral({
    razonSocial: 'Tecnologías Avanzadas',
    fechaConstitucion: new Date(2010, 5, 1), // 1 junio 2010
  });

  console.log('  Persona Moral:');
  console.log(`    Razón Social: Tecnologías Avanzadas`);
  console.log(`    Constitución: 2010-06-01`);
  console.log(`    RFC:          ${rfcMoral}`);
  console.log(`    Válido:       ${validateRfc(rfcMoral) ? '✅' : '❌'}`);
  console.log();
}

function demoCurp(): void {
  console.log('  🆔 CURP (Clave Única de Registro de Población)');
  console.log('  ──────────────────────────────────────────────');
  console.log();

  // Generar CURP
  const curp = generateCurp({
    nombre: 'María',
    apellidoPaterno: 'Hernández',
    apellidoMaterno: 'Sánchez',
    fechaNacimiento: new Date(1985, 2, 20), // 20 marzo 1985
    sexo: 'M',
    estado: 'Jalisco',
  });

  console.log('  Datos:');
  console.log(`    Nombre: María Hernández Sánchez`);
  console.log(`    Fecha:  1985-03-20`);
  console.log(`    Sexo:   Mujer`);
  console.log(`    Estado: Jalisco`);
  console.log();
  console.log(`    CURP:   ${curp}`);
  console.log(`    Válido: ${validateCurp(curp) ? '✅' : '❌'}`);

  const info = getCurpInfo(curp);
  if (info) {
    console.log(`    Género: ${info.gender === 'M' ? 'Mujer' : 'Hombre'}`);
    console.log(`    Estado: ${info.stateCode}`);
  }
  console.log();
}

function demoClabe(): void {
  console.log('  🏦 CLABE (Clave Bancaria Estandarizada)');
  console.log('  ───────────────────────────────────────');
  console.log();

  // Generar CLABE
  const clabe = generateClabe('012', '180', '12345678901');

  console.log('  Datos:');
  console.log(`    Banco:   012 (BBVA México)`);
  console.log(`    Plaza:   180`);
  console.log(`    Cuenta:  12345678901`);
  console.log();
  console.log(`    CLABE:   ${clabe}`);
  console.log(`    Válida:  ${validateClabe(clabe) ? '✅' : '❌'}`);

  const info = getClabeInfo(clabe);
  if (info) {
    console.log(`    Banco:   ${info.bankCode}`);
    console.log(`    Check:   ${info.checkDigit}`);
  }
  console.log();
}

function demoNss(): void {
  console.log('  🏥 NSS (Número de Seguridad Social)');
  console.log('  ────────────────────────────────────');
  console.log();

  // Generar NSS
  const nss = generateNss(45, 90, 85, 1234);

  console.log('  Datos:');
  console.log(`    Subdelegación:   45`);
  console.log(`    Año registro:    90`);
  console.log(`    Año nacimiento:  85`);
  console.log(`    Secuencial:      1234`);
  console.log();
  console.log(`    NSS:     ${nss}`);
  console.log(`    Válido:  ${validateNss(nss) ? '✅' : '❌'}`);

  const info = getNssInfo(nss);
  if (info) {
    console.log(`    Subdel:  ${info.subdelegacion}`);
  }
  console.log();
}

function validarCodigo(codigo: string): void {
  console.log(`  Validando: ${codigo}`);
  console.log('  ─────────────────────────────────');

  const len = codigo.length;

  if (len === 18) {
    // Puede ser CURP o CLABE
    if (/^\d+$/.test(codigo)) {
      // CLABE (solo dígitos)
      const esValido = validateClabe(codigo);
      console.log(`  Tipo:   CLABE`);
      console.log(`  Válido: ${esValido ? '✅' : '❌'}`);
      if (esValido) {
        const info = getClabeInfo(codigo);
        console.log(`  Banco:  ${info?.bankCode}`);
      }
    } else {
      // CURP
      const esValido = validateCurp(codigo);
      console.log(`  Tipo:   CURP`);
      console.log(`  Válido: ${esValido ? '✅' : '❌'}`);
    }
  } else if (len === 13) {
    // RFC persona física
    const esValido = validateRfc(codigo);
    console.log(`  Tipo:   RFC (persona física)`);
    console.log(`  Válido: ${esValido ? '✅' : '❌'}`);
  } else if (len === 12) {
    // RFC persona moral
    const esValido = validateRfc(codigo);
    console.log(`  Tipo:   RFC (persona moral)`);
    console.log(`  Válido: ${esValido ? '✅' : '❌'}`);
  } else if (len === 11) {
    // NSS
    const esValido = validateNss(codigo);
    console.log(`  Tipo:   NSS`);
    console.log(`  Válido: ${esValido ? '✅' : '❌'}`);
  } else {
    console.log(`  ❓ Código no reconocido (longitud: ${len})`);
  }
  console.log();
}

// Main
async function main(): Promise<void> {
  printHeader();

  const args = process.argv.slice(2);
  const comando = args[0]?.toLowerCase() || 'demo';

  switch (comando) {
    case 'demo':
      demoRfc();
      demoCurp();
      demoClabe();
      demoNss();
      break;

    case 'rfc':
      demoRfc();
      break;

    case 'curp':
      demoCurp();
      break;

    case 'clabe':
      demoClabe();
      break;

    case 'nss':
      demoNss();
      break;

    case 'validar':
      if (args[1]) {
        validarCodigo(args[1].toUpperCase());
      } else {
        console.log('  Uso: npx ts-node validators-app.ts validar <código>');
      }
      break;

    default:
      console.log('  Uso:');
      console.log('    npx ts-node validators-app.ts demo');
      console.log('    npx ts-node validators-app.ts rfc');
      console.log('    npx ts-node validators-app.ts curp');
      console.log('    npx ts-node validators-app.ts clabe');
      console.log('    npx ts-node validators-app.ts nss');
      console.log('    npx ts-node validators-app.ts validar GALO850320HJCRPN07');
  }
}

main().catch(console.error);
