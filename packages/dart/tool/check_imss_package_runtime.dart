import 'package:catalogmx/catalogmx.dart';

void _require(bool condition, String message) {
  if (!condition) throw StateError(message);
}

void main() {
  final uma = IMSSCalculator.getUMA(IMSSYear.year2026);
  final cuotas = IMSSCalculator.calcularCuotasObreroPatronales(500);
  final modalidad40 = IMSSCalculator.calcularModalidad40(
    15000,
    ultimoSbcMensual: 12000,
  );
  final modalidad10 = IMSSCalculator.calcularModalidad10(10000);

  _require(uma.diaria > 0, 'UMA package data is unavailable');
  _require(cuotas.totalIMSS > 0, 'IMSS contribution tables are unavailable');
  _require(modalidad40.cuotaMensual > 0, 'Modalidad 40 tables are unavailable');
  _require(modalidad10.cuotaMensual > 0, 'Modalidad 10 tables are unavailable');
  _require(
    IMSSCalculator.getTiposTrabajador().isNotEmpty,
    'IMSS package catalogs are unavailable',
  );
}
