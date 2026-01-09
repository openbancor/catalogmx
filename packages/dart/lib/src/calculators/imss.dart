/// IMSS (Instituto Mexicano del Seguro Social) Calculator for Mexico
/// Calculates employer/employee contributions and voluntary modalities (10, 40)
/// Uses centralized JSON tables from shared-data
///
/// Official sources:
/// - Ley del Seguro Social
/// - Sistema Único de Autodeterminación (SUA)
library;

import 'dart:convert';
import 'dart:io';

/// Supported years
enum IMSSYear {
  year2024(2024),
  year2025(2025),
  year2026(2026);

  const IMSSYear(this.value);
  final int value;
}

/// Salary zone types
enum ZonaSalario {
  general('general'),
  frontera('frontera');

  const ZonaSalario(this.value);
  final String value;
}

/// Work risk classes (1-5, where 1 is minimum risk)
enum ClaseRiesgo {
  clase1(1),
  clase2(2),
  clase3(3),
  clase4(4),
  clase5(5);

  const ClaseRiesgo(this.value);
  final int value;
}

/// UMA (Unidad de Medida y Actualización) information
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

/// IMSS contributions breakdown result
class CuotasIMSSResult {
  const CuotasIMSSResult({
    required this.salarioDiario,
    required this.dias,
    required this.salarioBaseCotizacion,
    required this.year,
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
        'cuotas_patron': cuotasPatron,
        'cuotas_trabajador': cuotasTrabajador,
        'total_patron': totalPatron,
        'total_trabajador': totalTrabajador,
        'total_imss': totalIMSS,
      };
}

/// Modalidad 40 calculation result
class Modalidad40Result {
  const Modalidad40Result({
    required this.salarioBaseCotizacion,
    required this.year,
    required this.cuotaMensual,
    required this.porcentajeTotal,
    required this.componentes,
  });

  final double salarioBaseCotizacion;
  final int year;
  final double cuotaMensual;
  final double porcentajeTotal;
  final Map<String, double> componentes;

  Map<String, dynamic> toJson() => {
        'salario_base_cotizacion': salarioBaseCotizacion,
        'year': year,
        'cuota_mensual': cuotaMensual,
        'porcentaje_total': porcentajeTotal,
        'componentes': componentes,
      };
}

/// Modalidad 10 calculation result
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

/// IMSS Calculator class
class IMSSCalculator {
  static Map<String, dynamic>? _imssTables;
  static Map<String, dynamic>? _imssCatalogs;

  /// Load IMSS tables from centralized JSON file
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
      if (!file.existsSync()) {
        continue;
      }
      final jsonString = file.readAsStringSync();
      _imssTables = jsonDecode(jsonString) as Map<String, dynamic>;
      return _imssTables!;
    }

    throw Exception('IMSS tables JSON file not found');
  }

  /// Load IMSS catalogs from centralized JSON file
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
      if (!file.existsSync()) {
        continue;
      }
      final jsonString = file.readAsStringSync();
      _imssCatalogs = jsonDecode(jsonString) as Map<String, dynamic>;
      return _imssCatalogs!;
    }

    throw Exception('IMSS catalogs JSON file not found');
  }

  /// Get UMA values for a specific year
  ///
  /// Examples:
  /// ```dart
  /// final uma = IMSSCalculator.getUMA(IMSSYear.year2026);
  /// print('UMA diaria 2026: \$${uma.diaria}');
  /// ```
  static UMAInfo getUMA(IMSSYear year) {
    final tables = _loadIMSSTables();
    final yearStr = year.value.toString();
    return UMAInfo.fromJson(tables['uma']![yearStr]!);
  }

  /// Get minimum wage for a specific year and zone
  ///
  /// Examples:
  /// ```dart
  /// final salario = IMSSCalculator.getSalarioMinimo(IMSSYear.year2026, ZonaSalario.general);
  /// print('Salario mínimo general 2026: \$${salario}');
  /// ```
  static double getSalarioMinimo(IMSSYear year,
      [ZonaSalario zona = ZonaSalario.general]) {
    final tables = _loadIMSSTables();
    final yearStr = year.value.toString();
    return (tables['salario_minimo']![yearStr]![zona.value]! as num).toDouble();
  }

  /// Calculate IMSS employer and employee contributions
  ///
  /// Parameters:
  /// - [salarioDiario]: Daily wage
  /// - [dias]: Number of days (default: 30)
  /// - [year]: Year (default: 2026)
  /// - [claseRiesgo]: Work risk class 1-5 (default: 1 - minimum risk)
  ///
  /// Returns: Complete breakdown of IMSS contributions
  ///
  /// Examples:
  /// ```dart
  /// final result = IMSSCalculator.calcularCuotasObreroPatronales(500.0, 30, IMSSYear.year2026);
  /// print('Total patrón: \$${result.totalPatron.toStringAsFixed(2)}');
  /// print('Total trabajador: \$${result.totalTrabajador.toStringAsFixed(2)}');
  /// ```
  static CuotasIMSSResult calcularCuotasObreroPatronales(
    double salarioDiario, {
    int dias = 30,
    IMSSYear year = IMSSYear.year2026,
    ClaseRiesgo claseRiesgo = ClaseRiesgo.clase1,
  }) {
    final tables = _loadIMSSTables();
    final uma = getUMA(year);
    final cuotas = tables['cuotas_imss']!;

    // Calculate base salary for contributions
    final salarioBase = salarioDiario * dias;

    // Límite de 3 UMAs diario para algunas cuotas
    final umaDiaria = uma.diaria;
    final tresUmaMensual = umaDiaria * 3 * 30;

    // Initialize contribution maps
    final cuotasPatron = <String, double>{};
    final cuotasTrabajador = <String, double>{};

    // 1. Enfermedad y Maternidad
    final em = cuotas['enfermedad_maternidad']!;

    // Cuota fija (sobre 3 UMAs)
    cuotasPatron['enfermedad_mat_cuota_fija'] = umaDiaria *
        3 *
        dias *
        (em['prestaciones_en_especie']!['patron']! as num).toDouble();

    // Excedente de 3 UMAs
    if (salarioDiario > tresUmaMensual / 30) {
      final excedenteBase = salarioBase - tresUmaMensual;
      cuotasPatron['enfermedad_mat_excedente'] = excedenteBase *
          (em['prestaciones_en_especie_excedente']!['patron']! as num)
              .toDouble();
      cuotasTrabajador['enfermedad_mat_excedente'] = excedenteBase *
          (em['prestaciones_en_especie_excedente']!['trabajador']! as num)
              .toDouble();
    } else {
      cuotasPatron['enfermedad_mat_excedente'] = 0.0;
      cuotasTrabajador['enfermedad_mat_excedente'] = 0.0;
    }

    // Prestaciones en dinero
    cuotasPatron['enfermedad_mat_dinero'] = salarioBase *
        (em['prestaciones_en_dinero']!['patron']! as num).toDouble();
    cuotasTrabajador['enfermedad_mat_dinero'] = salarioBase *
        (em['prestaciones_en_dinero']!['trabajador']! as num).toDouble();

    // Gastos médicos pensionados
    cuotasPatron['gastos_medicos_pensionados'] = salarioBase *
        (em['gastos_medicos_pensionados']!['patron']! as num).toDouble();
    cuotasTrabajador['gastos_medicos_pensionados'] = salarioBase *
        (em['gastos_medicos_pensionados']!['trabajador']! as num).toDouble();

    // 2. Invalidez y Vida
    final iv = cuotas['invalidez_vida']!;
    cuotasPatron['invalidez_vida'] =
        salarioBase * (iv['patron']! as num).toDouble();
    cuotasTrabajador['invalidez_vida'] =
        salarioBase * (iv['trabajador']! as num).toDouble();

    // 3. Retiro, Cesantía y Vejez
    final rcv = cuotas['retiro_cesantia_vejez']!;
    cuotasPatron['retiro'] =
        salarioBase * (rcv['retiro']!['patron']! as num).toDouble();
    cuotasPatron['cesantia_vejez'] =
        salarioBase * (rcv['cesantia_vejez']!['patron']! as num).toDouble();
    cuotasTrabajador['cesantia_vejez'] =
        salarioBase * (rcv['cesantia_vejez']!['trabajador']! as num).toDouble();

    // 4. Guarderías y Prestaciones Sociales
    final gps = cuotas['guarderias_prestaciones_sociales']!;
    cuotasPatron['guarderias'] =
        salarioBase * (gps['patron']! as num).toDouble();

    // 5. Riesgos de Trabajo
    final rt = cuotas['riesgo_trabajo']!;
    final primaRiesgo = (rt['clase_${claseRiesgo.value}']! as num).toDouble();
    cuotasPatron['riesgo_trabajo'] = salarioBase * primaRiesgo;

    // Calculate totals
    final totalPatron = cuotasPatron.values.fold(0.0, (sum, val) => sum + val);
    final totalTrabajador =
        cuotasTrabajador.values.fold(0.0, (sum, val) => sum + val);

    return CuotasIMSSResult(
      salarioDiario: salarioDiario,
      dias: dias,
      salarioBaseCotizacion: salarioBase,
      year: year.value,
      cuotasPatron: cuotasPatron,
      cuotasTrabajador: cuotasTrabajador,
      totalPatron: totalPatron,
      totalTrabajador: totalTrabajador,
      totalIMSS: totalPatron + totalTrabajador,
    );
  }

  /// Calculate Modalidad 40 voluntary IMSS contributions
  /// (Continuación voluntaria en el régimen obligatorio)
  ///
  /// Modalidad 40 allows workers who left formal employment to continue
  /// contributing to IMSS to increase their pension amount.
  ///
  /// Parameters:
  /// - [salarioBaseCotizacion]: Monthly base salary (between 1 and 25 UMAs)
  /// - [year]: Year (default: 2026)
  ///
  /// Returns: Modalidad 40 calculation result
  ///
  /// Examples:
  /// ```dart
  /// final result = IMSSCalculator.calcularModalidad40(15000.0, IMSSYear.year2026);
  /// print('Cuota mensual: \$${result.cuotaMensual.toStringAsFixed(2)}');
  /// ```
  static Modalidad40Result calcularModalidad40(
    double salarioBaseCotizacion, {
    IMSSYear year = IMSSYear.year2026,
  }) {
    final tables = _loadIMSSTables();
    final uma = getUMA(year);
    final mod40 = tables['modalidad_40']!;

    // Validate salary limits
    final umaMensual = uma.mensual;
    final salarioMinimo = umaMensual *
        (mod40['limites_salario']!['minimo_uma']! as num).toDouble();
    final salarioMaximo = umaMensual *
        (mod40['limites_salario']!['maximo_uma']! as num).toDouble();

    if (salarioBaseCotizacion < salarioMinimo) {
      salarioBaseCotizacion = salarioMinimo;
    } else if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    // Calculate monthly contribution (10.47% total)
    final porcentajeTotal =
        (mod40['cuota_mensual']!['porcentaje_total']! as num).toDouble();
    final cuotaMensual = salarioBaseCotizacion * porcentajeTotal;

    // Get component breakdown
    final componentes = <String, double>{};
    final componentesData =
        mod40['cuota_mensual']!['componentes']! as Map<String, dynamic>;
    for (final entry in componentesData.entries) {
      componentes[entry.key] =
          salarioBaseCotizacion * (entry.value as num).toDouble();
    }

    return Modalidad40Result(
      salarioBaseCotizacion: salarioBaseCotizacion,
      year: year.value,
      cuotaMensual: cuotaMensual,
      porcentajeTotal: porcentajeTotal,
      componentes: componentes,
    );
  }

  /// Calculate Modalidad 10 voluntary IMSS contributions
  /// (Incorporación voluntaria al régimen obligatorio - trabajadores independientes)
  ///
  /// Modalidad 10 allows independent workers to enroll in IMSS and access
  /// all social security benefits including healthcare, retirement, and more.
  ///
  /// Parameters:
  /// - [salarioBaseCotizacion]: Monthly base salary (between 1 and 25 UMAs)
  /// - [year]: Year (default: 2026)
  ///
  /// Returns: Modalidad 10 calculation result
  ///
  /// Examples:
  /// ```dart
  /// final result = IMSSCalculator.calcularModalidad10(10000.0, IMSSYear.year2026);
  /// print('Cuota mensual: \$${result.cuotaMensual.toStringAsFixed(2)}');
  /// ```
  static Modalidad10Result calcularModalidad10(
    double salarioBaseCotizacion, {
    IMSSYear year = IMSSYear.year2026,
  }) {
    final tables = _loadIMSSTables();
    final uma = getUMA(year);
    final mod10 = tables['modalidad_10']!;

    // Validate salary limits
    final umaMensual = uma.mensual;
    final salarioMinimo = umaMensual *
        (mod10['limites_salario']!['minimo_uma']! as num).toDouble();
    final salarioMaximo = umaMensual *
        (mod10['limites_salario']!['maximo_uma']! as num).toDouble();

    if (salarioBaseCotizacion < salarioMinimo) {
      salarioBaseCotizacion = salarioMinimo;
    } else if (salarioBaseCotizacion > salarioMaximo) {
      salarioBaseCotizacion = salarioMaximo;
    }

    // Fixed fee: 3.3 UMAs for healthcare
    final cuotaFijaUma = uma.diaria *
        (mod10['cuota_mensual']!['cuota_fija_uma_factor']! as num).toDouble();

    // Variable percentage: 10.47%
    final porcentajeVariable =
        (mod10['cuota_mensual']!['porcentaje_variable']! as num).toDouble();
    final cuotaVariable = salarioBaseCotizacion * porcentajeVariable;

    // Total monthly contribution
    final cuotaMensual = cuotaFijaUma + cuotaVariable;

    // Get component breakdown
    final componentes = <String, double>{
      'prestaciones_en_especie_fija': cuotaFijaUma,
    };

    final componentesData =
        mod10['cuota_mensual']!['componentes']! as Map<String, dynamic>;
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

  /// Get all worker types from IMSS catalogs
  static List<Map<String, dynamic>> getTiposTrabajador() {
    final catalogs = _loadIMSSCatalogs();
    return List<Map<String, dynamic>>.from(catalogs['tipos_trabajador']!);
  }

  /// Get all IMSS insurance types
  static List<Map<String, dynamic>> getSegurosIMSS() {
    final catalogs = _loadIMSSCatalogs();
    return List<Map<String, dynamic>>.from(catalogs['seguros_imss']!);
  }

  /// Get all work risk classes with their premiums
  static List<Map<String, dynamic>> getClasesRiesgoTrabajo() {
    final tables = _loadIMSSTables();
    return List<Map<String, dynamic>>.from(tables['riesgos_trabajo_clases']!);
  }
}
