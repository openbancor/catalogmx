/// IMSS (Instituto Mexicano del Seguro Social) calculator for Mexico.
///
/// Uses centralized shared-data tables. Exercise-specific CEAV rates are
/// selected from the historical schedule. Modalidad 40 uses monthly amounts
/// and requires the last registered monthly SBC.
library;

import 'dart:convert';
import 'dart:io';

/// Supported years.
enum IMSSYear {
  year2024(2024),
  year2025(2025),
  year2026(2026);

  const IMSSYear(this.value);
  final int value;
}

/// Salary zone types.
enum ZonaSalario {
  general('general'),
  frontera('frontera');

  const ZonaSalario(this.value);
  final String value;
}

/// Work risk classes (1-5, where 1 is minimum risk).
enum ClaseRiesgo {
  clase1(1),
  clase2(2),
  clase3(3),
  clase4(4),
  clase5(5);

  const ClaseRiesgo(this.value);
  final int value;
}

/// UMA (Unidad de Medida y Actualización) information.
class UMAInfo {
  const UMAInfo({
    required this.diaria,
    required this.mensual,
    required this.anual,
  });

  factory UMAInfo.fromJson(Map<String, dynamic> json) {
    return UMAInfo(
      diaria: (json['diaria'] as num).toDouble(),
      mensual: (json['mensual'] as num).toDouble(),
      anual: (json['anual'] as num).toDouble(),
    );
  }

  final double diaria;
  final double mensual;
  final double anual;

  Map<String, dynamic> toJson() => {
    'diaria': diaria,
    'mensual': mensual,
    'anual': anual,
  };
}

/// IMSS contributions breakdown result.
class CuotasIMSSResult {
  const CuotasIMSSResult({
    required this.salarioDiario,
    required this.dias,
    required this.salarioBaseCotizacion,
    required this.year,
    required this.umaDiaria,
    required this.ceavPatronRate,
    required this.cuotasPatron,
    required this.cuotasTrabajador,
    required this.totalPatron,
    required this.totalTrabajador,
    required this.totalIMSS,
  });

  final double salarioDiario;
  final int dias;
  final double salarioBaseCotizacion;
  final int year;
  final double umaDiaria;
  final double ceavPatronRate;
  final Map<String, double> cuotasPatron;
  final Map<String, double> cuotasTrabajador;
  final double totalPatron;
  final double totalTrabajador;
  final double totalIMSS;

  Map<String, dynamic> toJson() => {
    'salario_diario': salarioDiario,
    'dias': dias,
    'salario_base_cotizacion': salarioBaseCotizacion,
    'year': year,
    'uma_diaria': umaDiaria,
    'ceav_patron_rate': ceavPatronRate,
    'cuotas_patron': cuotasPatron,
    'cuotas_trabajador': cuotasTrabajador,
    'total_patron': totalPatron,
    'total_trabajador': totalTrabajador,
    'total_imss': totalIMSS,
  };
}

/// Modalidad 40 calculation result.
class Modalidad40Result {
  const Modalidad40Result({
    required this.salarioBaseCotizacion,
    required this.ultimoSbcMensual,
    required this.year,
    required this.umaMensual,
    required this.cuotaMensual,
    required this.porcentajeTotal,
    required this.componentes,
  });

  final double salarioBaseCotizacion;
  final double ultimoSbcMensual;
  final int year;
  final double umaMensual;
  final double cuotaMensual;
  final double porcentajeTotal;
  final Map<String, double> componentes;

  Map<String, dynamic> toJson() => {
    'salario_base_cotizacion': salarioBaseCotizacion,
    'ultimo_sbc_mensual': ultimoSbcMensual,
    'year': year,
    'uma_mensual': umaMensual,
    'cuota_mensual': cuotaMensual,
    'porcentaje_total': porcentajeTotal,
    'componentes': componentes,
  };
}

/// Legacy Modalidad 10 result pending its dedicated source audit.
class Modalidad10Result {
  const Modalidad10Result({
    required this.salarioBaseCotizacion,
    required this.year,
    required this.cuotaMensual,
    required this.cuotaFijaUma,
    required this.cuotaVariable,
    required this.porcentajeVariable,
    required this.componentes,
  });

  final double salarioBaseCotizacion;
  final int year;
  final double cuotaMensual;
  final double cuotaFijaUma;
  final double cuotaVariable;
  final double porcentajeVariable;
  final Map<String, double> componentes;

  Map<String, dynamic> toJson() => {
    'salario_base_cotizacion': salarioBaseCotizacion,
    'year': year,
    'cuota_mensual': cuotaMensual,
    'cuota_fija_uma': cuotaFijaUma,
    'cuota_variable': cuotaVariable,
    'porcentaje_variable': porcentajeVariable,
    'componentes': componentes,
  };
}

/// IMSS calculator class.
class IMSSCalculator {
  static Map<String, dynamic>? _imssTables;
  static Map<String, dynamic>? _imssCatalogs;

  static Map<String, dynamic> _loadIMSSTables() {
    if (_imssTables != null) return _imssTables!;

    final candidates = [
      '../shared-data/imss-tables.json',
      '../../shared-data/imss-tables.json',
      '../../../shared-data/imss-tables.json',
      'packages/shared-data/imss-tables.json',
    ];

    for (final path in candidates) {
      final file = File(path);
      if (!file.existsSync()) continue;
      _imssTables = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
      return _imssTables!;
    }

    throw Exception('IMSS tables JSON file not found');
  }

  static Map<String, dynamic> _loadIMSSCatalogs() {
    if (_imssCatalogs != null) return _imssCatalogs!;

    final candidates = [
      '../shared-data/imss-catalogs.json',
      '../../shared-data/imss-catalogs.json',
      '../../../shared-data/imss-catalogs.json',
      'packages/shared-data/imss-catalogs.json',
    ];

    for (final path in candidates) {
      final file = File(path);
      if (!file.existsSync()) continue;
      _imssCatalogs =
          jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;
      return _imssCatalogs!;
    }

    throw Exception('IMSS catalogs JSON file not found');
  }

  /// Get UMA values for a specific exercise.
  static UMAInfo getUMA(IMSSYear year) {
    final tables = _loadIMSSTables();
    return UMAInfo.fromJson(tables['uma']![year.value.toString()]!);
  }

  /// Get the UMA legally in force on a concrete date.
  static UMAInfo getUMAForDate(DateTime fecha) {
    final tables = _loadIMSSTables();
    final rows = tables['uma']! as Map<String, dynamic>;
    final target = DateTime(fecha.year, fecha.month, fecha.day);

    for (final raw in rows.values) {
      final row = raw as Map<String, dynamic>;
      final desdeText = row['vigencia_desde'] as String?;
      final hastaText = row['vigencia_hasta'] as String?;
      if (desdeText == null || hastaText == null) continue;

      final desde = DateTime.parse(desdeText);
      final hasta = DateTime.parse(hastaText);
      if (!target.isBefore(desde) && !target.isAfter(hasta)) {
        return UMAInfo.fromJson(row);
      }
    }

    throw StateError(
      'No se encontró UMA vigente para ${target.toIso8601String().substring(0, 10)}',
    );
  }

  /// Get minimum wage for a specific exercise and zone.
  static double getSalarioMinimo(
    IMSSYear year, [
    ZonaSalario zona = ZonaSalario.general,
  ]) {
    final tables = _loadIMSSTables();
    return (tables['salario_minimo']![year.value.toString()]![zona.value]!
            as num)
        .toDouble();
  }

  static void _assertFechaMatchesExercise(IMSSYear year, DateTime? fecha) {
    if (fecha != null && fecha.year != year.value) {
      throw ArgumentError('La fecha no pertenece al ejercicio ${year.value}');
    }
  }

  static bool _almostEqual(double left, double right) {
    return (left - right).abs() < 0.005;
  }

  static double _getCEAVPatronRate(
    double salarioDiario,
    IMSSYear year, [
    DateTime? fecha,
  ]) {
    _assertFechaMatchesExercise(year, fecha);
    final tables = _loadIMSSTables();
    final cuotas = tables['cuotas_imss']! as Map<String, dynamic>;
    final rcv = cuotas['retiro_cesantia_vejez']! as Map<String, dynamic>;
    final ceav = rcv['cesantia_vejez']! as Map<String, dynamic>;
    final schedules = ceav['patron_por_ejercicio']! as Map<String, dynamic>;
    final rates = schedules[year.value.toString()]! as List<dynamic>;
    if (rates.length != 8) {
      throw StateError(
        'No se encontró tarifa CEAV patronal para ${year.value}',
      );
    }

    final minimum =
        tables['salario_minimo']![year.value.toString()]!
            as Map<String, dynamic>;
    final general = (minimum['general']! as num).toDouble();
    final frontera = (minimum['frontera']! as num).toDouble();
    if (_almostEqual(salarioDiario, general) ||
        _almostEqual(salarioDiario, frontera)) {
      return ((rates[0] as Map<String, dynamic>)['tasa']! as num).toDouble();
    }

    final uma = fecha == null ? getUMA(year) : getUMAForDate(fecha);
    final ratio = salarioDiario / uma.diaria;
    final int index;
    if (ratio <= 1.5) {
      index = 1;
    } else if (ratio <= 2.0) {
      index = 2;
    } else if (ratio <= 2.5) {
      index = 3;
    } else if (ratio <= 3.0) {
      index = 4;
    } else if (ratio <= 3.5) {
      index = 5;
    } else if (ratio <= 4.0) {
      index = 6;
    } else {
      index = 7;
    }
    return ((rates[index] as Map<String, dynamic>)['tasa']! as num).toDouble();
  }

  /// Calculate IMSS employer and employee contributions.
  static CuotasIMSSResult calcularCuotasObreroPatronales(
    double salarioDiario, {
    int dias = 30,
    IMSSYear year = IMSSYear.year2026,
    ClaseRiesgo claseRiesgo = ClaseRiesgo.clase1,
    DateTime? fecha,
  }) {
    _assertFechaMatchesExercise(year, fecha);
    final tables = _loadIMSSTables();
    final uma = fecha == null ? getUMA(year) : getUMAForDate(fecha);
    final cuotas = tables['cuotas_imss']! as Map<String, dynamic>;
    final salarioBase = salarioDiario * dias;
    final umaDiaria = uma.diaria;

    final cuotasPatron = <String, double>{};
    final cuotasTrabajador = <String, double>{};
    final em = cuotas['enfermedad_maternidad']! as Map<String, dynamic>;
    final prestacionesEspecie =
        em['prestaciones_en_especie']! as Map<String, dynamic>;
    final prestacionesExcedente =
        em['prestaciones_en_especie_excedente']! as Map<String, dynamic>;

    cuotasPatron['enfermedad_mat_cuota_fija'] =
        umaDiaria * dias * (prestacionesEspecie['patron']! as num).toDouble();

    final thresholdFactor =
        (prestacionesExcedente['umbral_uma'] as num?)?.toDouble() ?? 3.0;
    final threshold = thresholdFactor * umaDiaria;
    final excedenteBase =
        (salarioDiario > threshold ? salarioDiario - threshold : 0.0) * dias;
    cuotasPatron['enfermedad_mat_excedente'] =
        excedenteBase * (prestacionesExcedente['patron']! as num).toDouble();
    cuotasTrabajador['enfermedad_mat_excedente'] =
        excedenteBase *
        (prestacionesExcedente['trabajador']! as num).toDouble();

    final prestacionesDinero =
        em['prestaciones_en_dinero']! as Map<String, dynamic>;
    cuotasPatron['enfermedad_mat_dinero'] =
        salarioBase * (prestacionesDinero['patron']! as num).toDouble();
    cuotasTrabajador['enfermedad_mat_dinero'] =
        salarioBase * (prestacionesDinero['trabajador']! as num).toDouble();

    final gastosPensionados =
        em['gastos_medicos_pensionados']! as Map<String, dynamic>;
    cuotasPatron['gastos_medicos_pensionados'] =
        salarioBase * (gastosPensionados['patron']! as num).toDouble();
    cuotasTrabajador['gastos_medicos_pensionados'] =
        salarioBase * (gastosPensionados['trabajador']! as num).toDouble();

    final iv = cuotas['invalidez_vida']! as Map<String, dynamic>;
    cuotasPatron['invalidez_vida'] =
        salarioBase * (iv['patron']! as num).toDouble();
    cuotasTrabajador['invalidez_vida'] =
        salarioBase * (iv['trabajador']! as num).toDouble();

    final rcv = cuotas['retiro_cesantia_vejez']! as Map<String, dynamic>;
    final retiro = rcv['retiro']! as Map<String, dynamic>;
    final ceav = rcv['cesantia_vejez']! as Map<String, dynamic>;
    cuotasPatron['retiro'] =
        salarioBase * (retiro['patron']! as num).toDouble();
    final ceavPatronRate = _getCEAVPatronRate(salarioDiario, year, fecha);
    cuotasPatron['cesantia_vejez'] = salarioBase * ceavPatronRate;
    cuotasTrabajador['cesantia_vejez'] =
        salarioBase * (ceav['trabajador']! as num).toDouble();

    final gps =
        cuotas['guarderias_prestaciones_sociales']! as Map<String, dynamic>;
    cuotasPatron['guarderias'] =
        salarioBase * (gps['patron']! as num).toDouble();

    final rt = cuotas['riesgo_trabajo']! as Map<String, dynamic>;
    final primaRiesgo = (rt['clase_${claseRiesgo.value}']! as num).toDouble();
    cuotasPatron['riesgo_trabajo'] = salarioBase * primaRiesgo;

    final totalPatron = cuotasPatron.values.fold(0.0, (sum, val) => sum + val);
    final totalTrabajador = cuotasTrabajador.values.fold(
      0.0,
      (sum, val) => sum + val,
    );

    return CuotasIMSSResult(
      salarioDiario: salarioDiario,
      dias: dias,
      salarioBaseCotizacion: salarioBase,
      year: year.value,
      umaDiaria: umaDiaria,
      ceavPatronRate: ceavPatronRate,
      cuotasPatron: cuotasPatron,
      cuotasTrabajador: cuotasTrabajador,
      totalPatron: totalPatron,
      totalTrabajador: totalTrabajador,
      totalIMSS: totalPatron + totalTrabajador,
    );
  }

  /// Calculate Modalidad 40 using explicit monthly salary amounts.
  static Modalidad40Result calcularModalidad40(
    double salarioBaseCotizacion, {
    required double ultimoSbcMensual,
    IMSSYear year = IMSSYear.year2026,
    DateTime? fecha,
  }) {
    _assertFechaMatchesExercise(year, fecha);
    final tables = _loadIMSSTables();
    final uma = fecha == null ? getUMA(year) : getUMAForDate(fecha);
    final mod40 = tables['modalidad_40']! as Map<String, dynamic>;
    final references =
        mod40['referencia_por_ejercicio']! as Map<String, dynamic>;
    if (!references.containsKey(year.value.toString())) {
      throw StateError(
        'No se encontró tarifa de Modalidad 40 para ${year.value}',
      );
    }

    final limits = mod40['limites_salario']! as Map<String, dynamic>;
    final salarioMaximo =
        uma.mensual * (limits['maximo_uma']! as num).toDouble();
    if (!salarioBaseCotizacion.isFinite || salarioBaseCotizacion <= 0) {
      throw ArgumentError(
        'El SBC mensual de Modalidad 40 debe ser mayor que cero',
      );
    }
    if (!ultimoSbcMensual.isFinite || ultimoSbcMensual <= 0) {
      throw ArgumentError('El último SBC mensual debe ser mayor que cero');
    }
    if (ultimoSbcMensual > salarioMaximo) {
      throw ArgumentError('El último SBC mensual excede el tope de 25 UMA');
    }
    if (salarioBaseCotizacion < ultimoSbcMensual) {
      throw ArgumentError(
        'El SBC de Modalidad 40 no puede ser menor al último SBC registrado',
      );
    }
    if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    final diasUmaMensual = uma.mensual / uma.diaria;
    final salarioDiarioEquivalente = salarioBaseCotizacion / diasUmaMensual;
    final ceavPatronRate = _getCEAVPatronRate(
      salarioDiarioEquivalente,
      year,
      fecha,
    );

    final componentes = <String, double>{
      'cesantia_vejez_patron': salarioBaseCotizacion * ceavPatronRate,
    };
    var porcentajeTotal = ceavPatronRate;
    final calculo = mod40['calculo']! as Map<String, dynamic>;
    final constantes =
        calculo['componentes_constantes']! as Map<String, dynamic>;
    for (final entry in constantes.entries) {
      final rate = (entry.value as num).toDouble();
      porcentajeTotal += rate;
      componentes[entry.key] = salarioBaseCotizacion * rate;
    }

    return Modalidad40Result(
      salarioBaseCotizacion: salarioBaseCotizacion,
      ultimoSbcMensual: ultimoSbcMensual,
      year: year.value,
      umaMensual: uma.mensual,
      cuotaMensual: salarioBaseCotizacion * porcentajeTotal,
      porcentajeTotal: porcentajeTotal,
      componentes: componentes,
    );
  }

  /// Calculate the legacy Modalidad 10 model pending its dedicated audit.
  static Modalidad10Result calcularModalidad10(
    double salarioBaseCotizacion, {
    IMSSYear year = IMSSYear.year2026,
    DateTime? fecha,
  }) {
    _assertFechaMatchesExercise(year, fecha);
    final tables = _loadIMSSTables();
    final uma = fecha == null ? getUMA(year) : getUMAForDate(fecha);
    final mod10 = tables['modalidad_10']! as Map<String, dynamic>;
    final limits = mod10['limites_salario']! as Map<String, dynamic>;

    final salarioMinimo =
        uma.mensual * (limits['minimo_uma']! as num).toDouble();
    final salarioMaximo =
        uma.mensual * (limits['maximo_uma']! as num).toDouble();
    if (salarioBaseCotizacion < salarioMinimo) {
      salarioBaseCotizacion = salarioMinimo;
    } else if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    final cuotaData = mod10['cuota_mensual']! as Map<String, dynamic>;
    final cuotaFijaUma =
        uma.diaria * (cuotaData['cuota_fija_uma_factor']! as num).toDouble();
    final porcentajeVariable = (cuotaData['porcentaje_variable']! as num)
        .toDouble();
    final cuotaVariable = salarioBaseCotizacion * porcentajeVariable;
    final cuotaMensual = cuotaFijaUma + cuotaVariable;

    final componentes = <String, double>{
      'prestaciones_en_especie_fija': cuotaFijaUma,
    };
    final componentesData = cuotaData['componentes']! as Map<String, dynamic>;
    for (final entry in componentesData.entries) {
      if (entry.value is num) {
        componentes[entry.key] =
            salarioBaseCotizacion * (entry.value as num).toDouble();
      }
    }

    return Modalidad10Result(
      salarioBaseCotizacion: salarioBaseCotizacion,
      year: year.value,
      cuotaMensual: cuotaMensual,
      cuotaFijaUma: cuotaFijaUma,
      cuotaVariable: cuotaVariable,
      porcentajeVariable: porcentajeVariable,
      componentes: componentes,
    );
  }

  /// Get all worker types from IMSS catalogs.
  static List<Map<String, dynamic>> getTiposTrabajador() {
    final catalogs = _loadIMSSCatalogs();
    return List<Map<String, dynamic>>.from(catalogs['tipos_trabajador']!);
  }

  /// Get all IMSS insurance types.
  static List<Map<String, dynamic>> getSegurosIMSS() {
    final catalogs = _loadIMSSCatalogs();
    return List<Map<String, dynamic>>.from(catalogs['seguros_imss']!);
  }

  /// Get all work risk classes with their premiums.
  static List<Map<String, dynamic>> getClasesRiesgoTrabajo() {
    final tables = _loadIMSSTables();
    return List<Map<String, dynamic>>.from(tables['riesgos_trabajo_clases']!);
  }
}
