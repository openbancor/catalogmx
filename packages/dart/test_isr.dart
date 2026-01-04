import 'lib/src/calculators/isr.dart';

void main() {
  // Test 2026 monthly calculation
  final result = ISRCalculator.calculateISR(
    15000,
    periodo: ISRPeriod.mensual,
    year: ISRYear.year2026,
  );
  print('ISR 2026 Mensual (\$15,000): \$${result.isrFinal.toStringAsFixed(2)}');
  print('Tasa efectiva: ${result.tasaEfectiva.toStringAsFixed(2)}%');

  // Test 2024 monthly calculation
  final result24 = ISRCalculator.calculateISR(
    15000,
    periodo: ISRPeriod.mensual,
    year: ISRYear.year2024,
  );
  print(
    '\nISR 2024 Mensual (\$15,000): \$${result24.isrFinal.toStringAsFixed(2)}',
  );
  print('Tasa efectiva: ${result24.tasaEfectiva.toStringAsFixed(2)}%');

  // Test daily calculation
  final resultDaily = ISRCalculator.calculateISR(
    500,
    periodo: ISRPeriod.diaria,
    year: ISRYear.year2026,
  );
  print(
    '\nISR 2026 Diaria (\$500): \$${resultDaily.isrFinal.toStringAsFixed(2)}',
  );

  print('\n✅ Dart calculator working!');
}
