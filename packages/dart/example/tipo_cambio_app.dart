#!/usr/bin/env dart
/// Tipo de Cambio App - Dart
///
/// Consulta y convierte USD/MXN usando los catálogos de Banxico.
///
/// Uso:
///   dart run example/tipo_cambio_app.dart
library;

import 'package:catalogmx/catalogmx.dart';

void printHeader() {
  print('');
  print('╔══════════════════════════════════════════════════════╗');
  print('║     💵 Tipo de Cambio USD/MXN - catalogmx            ║');
  print('╚══════════════════════════════════════════════════════╝');
  print('');
}

String formatCurrency(double amount, {int decimals = 2}) {
  return amount.toStringAsFixed(decimals);
}

void showActual() {
  print('  📊 Tipo de Cambio Actual');
  print('  ─────────────────────────');

  final actual = TipoCambioUsdCatalog.getActual();

  if (actual == null) {
    print('  ❌ No se pudo obtener el tipo de cambio');
    return;
  }

  final tc = actual['tipo_cambio'] as double;
  final fecha = actual['fecha'] as String;

  print('  📅 Fecha:        $fecha');
  print('  💱 Tipo cambio:  \$${formatCurrency(tc, decimals: 4)} MXN por 1 USD');
  print('');
  print('  Ejemplos de conversión:');
  print('    \$1 USD     = \$${formatCurrency(tc)} MXN');
  print('    \$100 USD   = \$${formatCurrency(tc * 100)} MXN');
  print('    \$1,000 USD = \$${formatCurrency(tc * 1000)} MXN');
  print('');
  print('    \$100 MXN   = \$${formatCurrency(100 / tc)} USD');
  print('    \$1,000 MXN = \$${formatCurrency(1000 / tc)} USD');
}

void showHistorico(String fecha) {
  print('  📅 Tipo de Cambio del $fecha');
  print('  ─────────────────────────────');

  final tc = TipoCambioUsdCatalog.getByFecha(fecha);

  if (tc == null) {
    print('  ❌ No hay datos para $fecha');
    print('     (Solo días hábiles tienen tipo de cambio)');
    return;
  }

  final valor = tc['tipo_cambio'] as double;
  print('  💱 Tipo cambio: \$${formatCurrency(valor, decimals: 4)} MXN/USD');
}

void convertir(double cantidad, String direccion) {
  final actual = TipoCambioUsdCatalog.getActual();

  if (actual == null) {
    print('  ❌ No se pudo obtener el tipo de cambio');
    return;
  }

  final tc = actual['tipo_cambio'] as double;

  if (direccion == 'usd_mxn') {
    final resultado = cantidad * tc;
    print('  💵 \$${formatCurrency(cantidad)} USD = \$${formatCurrency(resultado)} MXN');
  } else {
    final resultado = cantidad / tc;
    print('  🇲🇽 \$${formatCurrency(cantidad)} MXN = \$${formatCurrency(resultado)} USD');
  }
  print('     (Tipo de cambio: ${formatCurrency(tc, decimals: 4)})');
}

void showEstadisticas() {
  print('  📊 Estadísticas Recientes');
  print('  ─────────────────────────');

  final datos = TipoCambioUsdCatalog.getAll();

  if (datos.isEmpty) {
    print('  ❌ No hay datos disponibles');
    return;
  }

  // Últimos 30 registros
  final ultimos = datos.length > 30 ? datos.sublist(datos.length - 30) : datos;
  final valores = ultimos.map((d) => d['tipo_cambio'] as double).toList();

  final minimo = valores.reduce((a, b) => a < b ? a : b);
  final maximo = valores.reduce((a, b) => a > b ? a : b);
  final promedio = valores.reduce((a, b) => a + b) / valores.length;
  final primero = valores.first;
  final ultimo = valores.last;
  final variacion = ((ultimo - primero) / primero) * 100;

  print('  Registros analizados: ${ultimos.length}');
  print('  Período: ${ultimos.first['fecha']} a ${ultimos.last['fecha']}');
  print('');
  print('  Mínimo:    \$${formatCurrency(minimo, decimals: 4)}');
  print('  Máximo:    \$${formatCurrency(maximo, decimals: 4)}');
  print('  Promedio:  \$${formatCurrency(promedio, decimals: 4)}');
  print('  Variación: ${variacion >= 0 ? '+' : ''}${formatCurrency(variacion)}%');
}

void main(List<String> args) {
  printHeader();

  final comando = args.isNotEmpty ? args[0].toLowerCase() : 'actual';

  switch (comando) {
    case 'actual':
      showActual();
      break;

    case 'historico':
      final fecha = args.length > 1
          ? args[1]
          : DateTime.now().toIso8601String().split('T')[0];
      showHistorico(fecha);
      break;

    case 'usd':
      final cantidad = args.length > 1 ? double.parse(args[1]) : 100.0;
      convertir(cantidad, 'usd_mxn');
      break;

    case 'mxn':
      final cantidad = args.length > 1 ? double.parse(args[1]) : 1000.0;
      convertir(cantidad, 'mxn_usd');
      break;

    case 'stats':
      showEstadisticas();
      break;

    default:
      print('  Uso:');
      print('    dart run example/tipo_cambio_app.dart actual');
      print('    dart run example/tipo_cambio_app.dart historico 2024-06-15');
      print('    dart run example/tipo_cambio_app.dart usd 100');
      print('    dart run example/tipo_cambio_app.dart mxn 1000');
      print('    dart run example/tipo_cambio_app.dart stats');
  }

  print('');
}
