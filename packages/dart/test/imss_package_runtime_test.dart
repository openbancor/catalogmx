import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

void main() {
  test('IMSS runtime data is independent from the process working directory',
      () {
    final original = Directory.current;
    final temporary = Directory.systemTemp.createTempSync('catalogmx-imss-');

    try {
      Directory.current = temporary;

      final uma = IMSSCalculator.getUMA(IMSSYear.year2026);
      final cuotas = IMSSCalculator.calcularCuotasObreroPatronales(500);
      final modalidad40 = IMSSCalculator.calcularModalidad40(
        15000,
        ultimoSbcMensual: 12000,
      );
      final modalidad10 = IMSSCalculator.calcularModalidad10(10000);

      expect(uma.diaria, greaterThan(0));
      expect(cuotas.totalIMSS, greaterThan(0));
      expect(modalidad40.cuotaMensual, greaterThan(0));
      expect(modalidad10.cuotaMensual, greaterThan(0));
      expect(IMSSCalculator.getTiposTrabajador(), isNotEmpty);
    } finally {
      Directory.current = original;
      temporary.deleteSync(recursive: true);
    }
  });
}
