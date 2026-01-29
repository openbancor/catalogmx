#!/usr/bin/env npx ts-node
/**
 * Tipo de Cambio App - TypeScript
 *
 * Consulta y convierte USD/MXN usando los catálogos de Banxico.
 *
 * Uso:
 *   npx ts-node examples/tipo-cambio-app.ts
 */

import { TipoCambioUsdCatalog } from '../src/catalogs/banxico/tipo-cambio-usd';

function printHeader(): void {
  console.log();
  console.log('╔══════════════════════════════════════════════════════╗');
  console.log('║     💵 Tipo de Cambio USD/MXN - catalogmx            ║');
  console.log('╚══════════════════════════════════════════════════════╝');
  console.log();
}

function formatCurrency(amount: number, decimals = 2): string {
  return amount.toLocaleString('es-MX', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

async function showActual(): Promise<void> {
  console.log('  📊 Tipo de Cambio Actual');
  console.log('  ─────────────────────────');

  const actual = TipoCambioUsdCatalog.getActual();

  if (!actual) {
    console.log('  ❌ No se pudo obtener el tipo de cambio');
    return;
  }

  console.log(`  📅 Fecha:        ${actual.fecha}`);
  console.log(`  💱 Tipo cambio:  $${formatCurrency(actual.tipo_cambio, 4)} MXN por 1 USD`);
  console.log();
  console.log('  Ejemplos de conversión:');
  console.log(`    $1 USD     = $${formatCurrency(actual.tipo_cambio)} MXN`);
  console.log(`    $100 USD   = $${formatCurrency(actual.tipo_cambio * 100)} MXN`);
  console.log(`    $1,000 USD = $${formatCurrency(actual.tipo_cambio * 1000)} MXN`);
  console.log();
  console.log(`    $100 MXN   = $${formatCurrency(100 / actual.tipo_cambio)} USD`);
  console.log(`    $1,000 MXN = $${formatCurrency(1000 / actual.tipo_cambio)} USD`);
}

function showHistorico(fecha: string): void {
  console.log(`  📅 Tipo de Cambio del ${fecha}`);
  console.log('  ─────────────────────────────');

  const tc = TipoCambioUsdCatalog.getByFecha(fecha);

  if (!tc) {
    console.log(`  ❌ No hay datos para ${fecha}`);
    console.log('     (Solo días hábiles tienen tipo de cambio)');
    return;
  }

  console.log(`  💱 Tipo cambio: $${formatCurrency(tc.tipo_cambio, 4)} MXN/USD`);
}

function convertir(cantidad: number, direccion: 'usd_mxn' | 'mxn_usd'): void {
  const actual = TipoCambioUsdCatalog.getActual();

  if (!actual) {
    console.log('  ❌ No se pudo obtener el tipo de cambio');
    return;
  }

  if (direccion === 'usd_mxn') {
    const resultado = cantidad * actual.tipo_cambio;
    console.log(`  💵 $${formatCurrency(cantidad)} USD = $${formatCurrency(resultado)} MXN`);
  } else {
    const resultado = cantidad / actual.tipo_cambio;
    console.log(`  🇲🇽 $${formatCurrency(cantidad)} MXN = $${formatCurrency(resultado)} USD`);
  }
  console.log(`     (Tipo de cambio: ${formatCurrency(actual.tipo_cambio, 4)})`);
}

function showEstadisticas(): void {
  console.log('  📊 Estadísticas Recientes');
  console.log('  ─────────────────────────');

  const datos = TipoCambioUsdCatalog.getAll();

  if (datos.length === 0) {
    console.log('  ❌ No hay datos disponibles');
    return;
  }

  // Últimos 30 registros
  const ultimos = datos.slice(-30);
  const valores = ultimos.map(d => d.tipo_cambio);

  const minimo = Math.min(...valores);
  const maximo = Math.max(...valores);
  const promedio = valores.reduce((a, b) => a + b, 0) / valores.length;
  const primero = valores[0];
  const ultimo = valores[valores.length - 1];
  const variacion = ((ultimo - primero) / primero) * 100;

  console.log(`  Registros analizados: ${ultimos.length}`);
  console.log(`  Período: ${ultimos[0].fecha} a ${ultimos[ultimos.length - 1].fecha}`);
  console.log();
  console.log(`  Mínimo:    $${formatCurrency(minimo, 4)}`);
  console.log(`  Máximo:    $${formatCurrency(maximo, 4)}`);
  console.log(`  Promedio:  $${formatCurrency(promedio, 4)}`);
  console.log(`  Variación: ${variacion >= 0 ? '+' : ''}${formatCurrency(variacion)}%`);
}

// Main
async function main(): Promise<void> {
  printHeader();

  const args = process.argv.slice(2);
  const comando = args[0]?.toLowerCase() || 'actual';

  switch (comando) {
    case 'actual':
      await showActual();
      break;

    case 'historico':
      const fecha = args[1] || new Date().toISOString().split('T')[0];
      showHistorico(fecha);
      break;

    case 'usd':
      const cantidadUsd = parseFloat(args[1] || '100');
      convertir(cantidadUsd, 'usd_mxn');
      break;

    case 'mxn':
      const cantidadMxn = parseFloat(args[1] || '1000');
      convertir(cantidadMxn, 'mxn_usd');
      break;

    case 'stats':
      showEstadisticas();
      break;

    default:
      console.log('  Uso:');
      console.log('    npx ts-node tipo-cambio-app.ts actual');
      console.log('    npx ts-node tipo-cambio-app.ts historico 2024-06-15');
      console.log('    npx ts-node tipo-cambio-app.ts usd 100');
      console.log('    npx ts-node tipo-cambio-app.ts mxn 1000');
      console.log('    npx ts-node tipo-cambio-app.ts stats');
  }

  console.log();
}

main().catch(console.error);
