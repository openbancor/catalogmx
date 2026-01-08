/// Tax Calculators for Mexico: IVA, IEPS, Retenciones, and Impuestos Locales
///
/// Provides methods to calculate:
/// - IVA (Value Added Tax)
/// - IEPS (Special Production and Services Tax)
/// - ISR and IVA Withholdings
/// - State and Municipal Taxes (Payroll, Lodging)
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

// ============================================================================
// IVA (Value Added Tax) Calculator
// ============================================================================

/// IVA rate types
enum IVATipoTasa {
  general('general'),
  frontera('frontera'),
  tasaCero('tasa_cero');

  const IVATipoTasa(this.value);
  final String value;
}

/// IVA tax rate structure
class IVATasa {
  const IVATasa({
    required this.tipo,
    required this.tasa,
    required this.vigenciaInicio,
    required this.descripcion,
    required this.aplicaEn,
    this.vigenciaFin,
  });

  factory IVATasa.fromJson(Map<String, dynamic> json) {
    return IVATasa(
      tipo: json['tipo'] as String,
      tasa: (json['tasa'] as num).toDouble(),
      vigenciaInicio: json['vigencia_inicio'] as String,
      vigenciaFin: json['vigencia_fin'] as String?,
      descripcion: json['descripcion'] as String,
      aplicaEn: json['aplica_en'] as String,
    );
  }

  final String tipo;
  final double tasa;
  final String vigenciaInicio;
  final String? vigenciaFin;
  final String descripcion;
  final String aplicaEn;

  Map<String, dynamic> toJson() => {
        'tipo': tipo,
        'tasa': tasa,
        'vigencia_inicio': vigenciaInicio,
        'vigencia_fin': vigenciaFin,
        'descripcion': descripcion,
        'aplica_en': aplicaEn,
      };
}

/// IVA calculation result
class IVACalculationResult {
  const IVACalculationResult({
    required this.base,
    required this.tasa,
    required this.iva,
    required this.totalConIva,
    required this.tipoTasa,
  });

  final double base;
  final double tasa;
  final double iva;
  final double totalConIva;
  final String tipoTasa;

  Map<String, dynamic> toJson() => {
        'base': base,
        'tasa': tasa,
        'iva': iva,
        'total_con_iva': totalConIva,
        'tipo_tasa': tipoTasa,
      };
}

/// IVA Calculator
class IVACalculator {
  static Map<String, dynamic>? _data;

  /// Load IVA data from JSON file
  static Map<String, dynamic> _loadData() {
    if (_data != null) return _data!;

    // Set correct path for shared-data (../shared-data from dart package)
    BaseCatalog.sharedDataPath = '../shared-data';

    try {
      final jsonData =
          BaseCatalog.loadJsonDataSync('sat/impuestos/iva_tasas.json');
      if (jsonData.isEmpty) {
        throw Exception('IVA tasas JSON file not found or empty');
      }
      // The file is a dict, so take the first item which contains the full structure
      _data = jsonData.first;
      return _data!;
    } catch (e) {
      throw Exception('Error loading IVA tasas: $e');
    }
  }

  /// Get current IVA rate for a date
  ///
  /// Parameters:
  /// - [fecha]: Date to check (defaults to current date)
  /// - [tipoTasa]: Type of rate (general, frontera, tasa_cero)
  ///
  /// Returns: IVA rate or null if not found
  static IVATasa? getTasaVigente({
    DateTime? fecha,
    IVATipoTasa tipoTasa = IVATipoTasa.general,
  }) {
    final data = _loadData();
    final fechaCheck = fecha ?? DateTime.now();
    final tasas = (data['tasas'] as List)
        .map((t) => IVATasa.fromJson(t))
        .where((t) => t.tipo == tipoTasa.value)
        .toList();

    for (final tasa in tasas) {
      final inicioDate = DateTime.parse(tasa.vigenciaInicio);
      final finDate =
          tasa.vigenciaFin != null ? DateTime.parse(tasa.vigenciaFin!) : null;

      final despuesInicio = fechaCheck.isAfter(inicioDate) ||
          fechaCheck.isAtSameMomentAs(inicioDate);
      final antesFin = finDate == null ||
          fechaCheck.isBefore(finDate) ||
          fechaCheck.isAtSameMomentAs(finDate);

      if (despuesInicio && antesFin) {
        return tasa;
      }
    }

    return null;
  }

  /// Calculate IVA for a base amount
  ///
  /// Parameters:
  /// - [base]: Base amount without IVA
  /// - [tipoTasa]: Type of rate (general, frontera, tasa_cero)
  /// - [fecha]: Date to determine current rate
  ///
  /// Returns: Calculation result with breakdown
  ///
  /// Example:
  /// ```dart
  /// final result = IVACalculator.calcular(1000.0);
  /// print('IVA: \$${result.iva}');
  /// print('Total: \$${result.totalConIva}');
  /// ```
  static IVACalculationResult calcular(
    double base, {
    IVATipoTasa tipoTasa = IVATipoTasa.general,
    DateTime? fecha,
  }) {
    final tasaObj = getTasaVigente(fecha: fecha, tipoTasa: tipoTasa);

    if (tasaObj == null) {
      throw Exception(
          'No se encontró tasa de IVA vigente para tipo ${tipoTasa.value}');
    }

    final tasa = tasaObj.tasa;
    final iva = base * (tasa / 100);
    final totalConIva = base + iva;

    return IVACalculationResult(
      base: base,
      tasa: tasa,
      iva: iva,
      totalConIva: totalConIva,
      tipoTasa: tipoTasa.value,
    );
  }

  /// Calculate IVA already included in a total
  /// (Breakdown IVA when price includes IVA)
  ///
  /// Parameters:
  /// - [totalConIva]: Total amount including IVA
  /// - [tipoTasa]: Type of rate
  /// - [fecha]: Date to determine current rate
  ///
  /// Returns: Calculation result with breakdown
  ///
  /// Example:
  /// ```dart
  /// final result = IVACalculator.calcularIncluido(1160.0);
  /// print('Base: \$${result.base}'); // 1000.0
  /// print('IVA: \$${result.iva}'); // 160.0
  /// ```
  static IVACalculationResult calcularIncluido(
    double totalConIva, {
    IVATipoTasa tipoTasa = IVATipoTasa.general,
    DateTime? fecha,
  }) {
    final tasaObj = getTasaVigente(fecha: fecha, tipoTasa: tipoTasa);

    if (tasaObj == null) {
      throw Exception('No se encontró tasa de IVA vigente');
    }

    final tasa = tasaObj.tasa;
    final base = totalConIva / (1 + tasa / 100);
    final iva = totalConIva - base;

    return IVACalculationResult(
      base: base,
      tasa: tasa,
      iva: iva,
      totalConIva: totalConIva,
      tipoTasa: tipoTasa.value,
    );
  }

  /// Get all historical IVA rates
  static List<IVATasa> getAllTasas() {
    final data = _loadData();
    return (data['tasas'] as List).map((t) => IVATasa.fromJson(t)).toList();
  }
}

// ============================================================================
// IEPS (Special Production and Services Tax) Calculator
// ============================================================================

/// IEPS calculation type
enum IEPSTipoCalculo {
  adValorem('ad_valorem'),
  cuotaFija('cuota_fija');

  const IEPSTipoCalculo(this.value);
  final String value;
}

/// IEPS category structure
class IEPSCategoria {
  const IEPSCategoria({
    required this.categoria,
    required this.descripcion,
    required this.tasas,
  });

  factory IEPSCategoria.fromJson(Map<String, dynamic> json) {
    return IEPSCategoria(
      categoria: json['categoria'] as String,
      descripcion: json['descripcion'] as String,
      tasas: (json['tasas'] as List).cast<Map<String, dynamic>>(),
    );
  }

  final String categoria;
  final String descripcion;
  final List<Map<String, dynamic>> tasas;

  Map<String, dynamic> toJson() => {
        'categoria': categoria,
        'descripcion': descripcion,
        'tasas': tasas,
      };
}

/// IEPS calculation result
class IEPSCalculationResult {
  const IEPSCalculationResult({
    required this.base,
    required this.tasa,
    required this.ieps,
    required this.tipoCalculo,
    this.unidad,
    this.cantidad,
  });

  final double base;
  final double tasa;
  final double ieps;
  final String tipoCalculo;
  final String? unidad;
  final double? cantidad;

  Map<String, dynamic> toJson() => {
        'base': base,
        'tasa': tasa,
        'ieps': ieps,
        'tipo_calculo': tipoCalculo,
        if (unidad != null) 'unidad': unidad,
        if (cantidad != null) 'cantidad': cantidad,
      };
}

/// IEPS Calculator
class IEPSCalculator {
  static List<IEPSCategoria>? _data;

  /// Load IEPS data from JSON file
  static List<IEPSCategoria> _loadData() {
    if (_data != null) return _data!;

    // Set correct path for shared-data (../shared-data from dart package)
    BaseCatalog.sharedDataPath = '../shared-data';

    try {
      final jsonData =
          BaseCatalog.loadJsonDataSync('sat/impuestos/ieps_tasas.json');
      if (jsonData.isEmpty) {
        throw Exception('IEPS tasas JSON file not found or empty');
      }
      _data = jsonData.map((c) => IEPSCategoria.fromJson(c)).toList();
      return _data!;
    } catch (e) {
      throw Exception('Error loading IEPS tasas: $e');
    }
  }

  /// Get IEPS category by name
  static IEPSCategoria? getCategoria(String categoria) {
    final data = _loadData();
    return data.where((c) => c.categoria == categoria).firstOrNull;
  }

  /// Calculate ad-valorem IEPS (percentage on value)
  ///
  /// Parameters:
  /// - [base]: Base value
  /// - [tasa]: IEPS rate as percentage
  ///
  /// Returns: Calculation result
  ///
  /// Example:
  /// ```dart
  /// final result = IEPSCalculator.calcularAdValorem(1000.0, 53.0);
  /// print('IEPS: \$${result.ieps}'); // 530.0
  /// ```
  static IEPSCalculationResult calcularAdValorem(double base, double tasa) {
    final ieps = base * (tasa / 100);

    return IEPSCalculationResult(
      base: base,
      tasa: tasa,
      ieps: ieps,
      tipoCalculo: IEPSTipoCalculo.adValorem.value,
    );
  }

  /// Calculate fixed-fee IEPS (quantity * rate)
  ///
  /// Parameters:
  /// - [cantidad]: Quantity of units
  /// - [cuotaPorUnidad]: Fixed fee per unit
  /// - [unidad]: Unit of measure (default: 'litro')
  ///
  /// Returns: Calculation result
  ///
  /// Example:
  /// ```dart
  /// final result = IEPSCalculator.calcularCuotaFija(100.0, 5.117);
  /// print('IEPS: \$${result.ieps}'); // 511.70
  /// ```
  static IEPSCalculationResult calcularCuotaFija(
    double cantidad,
    double cuotaPorUnidad, {
    String unidad = 'litro',
  }) {
    final ieps = cantidad * cuotaPorUnidad;

    return IEPSCalculationResult(
      base: cantidad,
      tasa: cuotaPorUnidad,
      ieps: ieps,
      tipoCalculo: IEPSTipoCalculo.cuotaFija.value,
      unidad: unidad,
      cantidad: cantidad,
    );
  }

  /// Calculate IEPS for alcoholic beverages
  ///
  /// Parameters:
  /// - [valor]: Product value
  /// - [gradosAlcohol]: Alcohol degrees
  ///
  /// Returns: Calculation result
  ///
  /// Example:
  /// ```dart
  /// final result = IEPSCalculator.calcularBebidasAlcoholicas(1000.0, 25.0);
  /// print('IEPS: \$${result.ieps}'); // Beer <= 14°: 26.5%, 14-20°: 30%, >20°: 53%
  /// ```
  static IEPSCalculationResult calcularBebidasAlcoholicas(
    double valor,
    double gradosAlcohol,
  ) {
    double tasa;

    if (gradosAlcohol <= 14) {
      tasa = 26.5; // Beer and beverages up to 14°
    } else if (gradosAlcohol <= 20) {
      tasa = 30.0; // Beverages from 14° to 20°
    } else {
      tasa = 53.0; // Beverages over 20°
    }

    return calcularAdValorem(valor, tasa);
  }

  /// Calculate IEPS for cigarettes
  ///
  /// Parameters:
  /// - [valor]: Sale value
  /// - [numeroCigarros]: Number of cigarettes
  ///
  /// Returns: Calculation result
  ///
  /// Example:
  /// ```dart
  /// final result = IEPSCalculator.calcularCigarros(50.0, 20);
  /// // IEPS = 160% of value + \$0.508 per cigarette
  /// ```
  static IEPSCalculationResult calcularCigarros(
    double valor,
    int numeroCigarros,
  ) {
    // IEPS = 160% of value + $0.508 per cigarette
    final iepsAdValorem = valor * (160 / 100);
    final iepsCuotaFija = numeroCigarros * 0.508;
    final iepsTotal = iepsAdValorem + iepsCuotaFija;

    return IEPSCalculationResult(
      base: valor,
      tasa: 160,
      ieps: iepsTotal,
      tipoCalculo: IEPSTipoCalculo.adValorem.value,
      cantidad: numeroCigarros.toDouble(),
    );
  }

  /// Get all IEPS categories
  static List<IEPSCategoria> getAllCategorias() {
    return _loadData();
  }
}

// ============================================================================
// Retenciones (Withholdings) Calculator
// ============================================================================

/// ISR withholding structure
class RetencionISR {
  const RetencionISR({
    required this.concepto,
    required this.tasa,
    required this.descripcion,
    required this.base,
    required this.articulo,
  });

  factory RetencionISR.fromJson(Map<String, dynamic> json) {
    return RetencionISR(
      concepto: json['concepto'] as String,
      tasa: json['tasa'], // Can be num or String
      descripcion: json['descripcion'] as String,
      base: json['base'] as String,
      articulo: json['articulo'] as String,
    );
  }

  final String concepto;
  final dynamic tasa; // Can be double or String for variable rates
  final String descripcion;
  final String base;
  final String articulo;

  Map<String, dynamic> toJson() => {
        'concepto': concepto,
        'tasa': tasa,
        'descripcion': descripcion,
        'base': base,
        'articulo': articulo,
      };
}

/// IVA withholding structure
class RetencionIVA {
  const RetencionIVA({
    required this.concepto,
    required this.tasa,
    required this.descripcion,
    required this.base,
    required this.articulo,
  });

  factory RetencionIVA.fromJson(Map<String, dynamic> json) {
    return RetencionIVA(
      concepto: json['concepto'] as String,
      tasa: (json['tasa'] as num).toDouble(),
      descripcion: json['descripcion'] as String,
      base: json['base'] as String,
      articulo: json['articulo'] as String,
    );
  }

  final String concepto;
  final double tasa;
  final String descripcion;
  final String base;
  final String articulo;

  Map<String, dynamic> toJson() => {
        'concepto': concepto,
        'tasa': tasa,
        'descripcion': descripcion,
        'base': base,
        'articulo': articulo,
      };
}

/// Withholding calculation result
class RetencionCalculationResult {
  const RetencionCalculationResult({
    required this.concepto,
    required this.base,
    required this.tasa,
    required this.retencion,
    this.impuestoBase,
  });

  final String concepto;
  final double base;
  final double tasa;
  final double retencion;
  final double? impuestoBase;

  Map<String, dynamic> toJson() => {
        'concepto': concepto,
        'base': base,
        'tasa': tasa,
        'retencion': retencion,
        if (impuestoBase != null) 'impuesto_base': impuestoBase,
      };
}

/// Retenciones Calculator
class RetencionCalculator {
  static Map<String, dynamic>? _data;

  /// Load retenciones data from JSON file
  static Map<String, dynamic> _loadData() {
    if (_data != null) return _data!;

    // Set correct path for shared-data (../shared-data from dart package)
    BaseCatalog.sharedDataPath = '../shared-data';

    try {
      final jsonData =
          BaseCatalog.loadJsonDataSync('sat/impuestos/retenciones.json');
      if (jsonData.isEmpty) {
        throw Exception('Retenciones JSON file not found or empty');
      }
      // The file is a dict, so take the first item which contains the full structure
      _data = jsonData.first;
      return _data!;
    } catch (e) {
      throw Exception('Error loading retenciones: $e');
    }
  }

  /// Get ISR withholding information by concept
  static RetencionISR? getRetencionISR(String concepto) {
    final data = _loadData();
    final retenciones = (data['isr_retenciones'] as List)
        .map((r) => RetencionISR.fromJson(r))
        .toList();
    return retenciones.where((r) => r.concepto == concepto).firstOrNull;
  }

  /// Get IVA withholding information by concept
  static RetencionIVA? getRetencionIVA(String concepto) {
    final data = _loadData();
    final retenciones = (data['iva_retenciones'] as List)
        .map((r) => RetencionIVA.fromJson(r))
        .toList();
    return retenciones.where((r) => r.concepto == concepto).firstOrNull;
  }

  /// Calculate ISR withholding
  ///
  /// Parameters:
  /// - [base]: Base for withholding
  /// - [concepto]: Withholding concept
  ///
  /// Returns: Calculation result
  ///
  /// Example:
  /// ```dart
  /// final result = RetencionCalculator.calcularRetencionISR(10000.0, 'honorarios');
  /// print('Withholding: \$${result.retencion}'); // 1000.0 (10%)
  /// ```
  static RetencionCalculationResult calcularRetencionISR(
    double base,
    String concepto,
  ) {
    final retencion = getRetencionISR(concepto);

    if (retencion == null) {
      throw Exception('No se encontró retención ISR para concepto: $concepto');
    }

    if (retencion.tasa is String) {
      throw Exception(
          'La tasa de $concepto es variable. Use método específico.');
    }

    final tasa = (retencion.tasa as num).toDouble();
    final montoRetencion = base * (tasa / 100);

    return RetencionCalculationResult(
      concepto: retencion.concepto,
      base: base,
      tasa: tasa,
      retencion: montoRetencion,
    );
  }

  /// Calculate IVA withholding (2/3 parts)
  ///
  /// Parameters:
  /// - [ivaTrasladado]: Transferred IVA
  /// - [concepto]: Withholding concept
  ///
  /// Returns: Calculation result
  ///
  /// Example:
  /// ```dart
  /// final result = RetencionCalculator.calcularRetencionIVA(160.0, 'servicios_profesionales');
  /// print('Withholding: \$${result.retencion}'); // 106.67 (2/3 of IVA)
  /// ```
  static RetencionCalculationResult calcularRetencionIVA(
    double ivaTrasladado,
    String concepto,
  ) {
    final retencion = getRetencionIVA(concepto);

    if (retencion == null) {
      throw Exception('No se encontró retención IVA para concepto: $concepto');
    }

    final montoRetencion = ivaTrasladado * (retencion.tasa / 100);

    return RetencionCalculationResult(
      concepto: retencion.concepto,
      base: ivaTrasladado,
      tasa: retencion.tasa,
      retencion: montoRetencion,
      impuestoBase: ivaTrasladado,
    );
  }

  /// Calculate withholding for professional fees (10% ISR)
  ///
  /// Example:
  /// ```dart
  /// final result = RetencionCalculator.calcularHonorarios(10000.0);
  /// print('Withholding: \$${result.retencion}'); // 1000.0
  /// ```
  static RetencionCalculationResult calcularHonorarios(double montoSinIVA) {
    return calcularRetencionISR(montoSinIVA, 'honorarios');
  }

  /// Calculate withholding for rent (10% ISR)
  ///
  /// Example:
  /// ```dart
  /// final result = RetencionCalculator.calcularArrendamiento(5000.0);
  /// print('Withholding: \$${result.retencion}'); // 500.0
  /// ```
  static RetencionCalculationResult calcularArrendamiento(double montoSinIVA) {
    return calcularRetencionISR(montoSinIVA, 'arrendamiento');
  }

  /// Calculate withholding for freight (4% ISR)
  ///
  /// Example:
  /// ```dart
  /// final result = RetencionCalculator.calcularFletes(10000.0);
  /// print('Withholding: \$${result.retencion}'); // 400.0
  /// ```
  static RetencionCalculationResult calcularFletes(double montoSinIVA) {
    return calcularRetencionISR(montoSinIVA, 'fletes');
  }

  /// Get all ISR withholdings
  static List<RetencionISR> getAllRetencionesISR() {
    final data = _loadData();
    return (data['isr_retenciones'] as List)
        .map((r) => RetencionISR.fromJson(r))
        .toList();
  }

  /// Get all IVA withholdings
  static List<RetencionIVA> getAllRetencionesIVA() {
    final data = _loadData();
    return (data['iva_retenciones'] as List)
        .map((r) => RetencionIVA.fromJson(r))
        .toList();
  }
}

// ============================================================================
// Impuestos Locales (State and Municipal Taxes) Calculator
// ============================================================================

/// State tax structure
class ImpuestoEstatal {
  const ImpuestoEstatal({
    required this.estado,
    required this.cveEstado,
    required this.tasa,
    required this.base,
  });

  factory ImpuestoEstatal.fromJson(Map<String, dynamic> json) {
    return ImpuestoEstatal(
      estado: json['estado'] as String,
      cveEstado: json['cve_estado'] as String,
      tasa: (json['tasa'] as num).toDouble(),
      base: json['base'] as String,
    );
  }

  final String estado;
  final String cveEstado;
  final double tasa;
  final String base;

  Map<String, dynamic> toJson() => {
        'estado': estado,
        'cve_estado': cveEstado,
        'tasa': tasa,
        'base': base,
      };
}

/// Impuestos Locales Calculator
class ImpuestosLocalesCalculator {
  static Map<String, dynamic>? _data;

  /// Load impuestos locales data from JSON file
  static Map<String, dynamic> _loadData() {
    if (_data != null) return _data!;

    // Set correct path for shared-data (../shared-data from dart package)
    BaseCatalog.sharedDataPath = '../shared-data';

    try {
      final jsonData =
          BaseCatalog.loadJsonDataSync('sat/impuestos/impuestos_locales.json');
      if (jsonData.isEmpty) {
        throw Exception('Impuestos locales JSON file not found or empty');
      }
      // The file is a dict, so take the first item which contains the full structure
      _data = jsonData.first;
      return _data!;
    } catch (e) {
      throw Exception('Error loading impuestos locales: $e');
    }
  }

  /// Get payroll tax rate for a state
  ///
  /// Parameters:
  /// - [cveEstado]: State code (01-32)
  ///
  /// Returns: State tax information or null
  static ImpuestoEstatal? getImpuestoNomina(String cveEstado) {
    final data = _loadData();
    final impuestos = (data['impuesto_nomina'] as List)
        .map((i) => ImpuestoEstatal.fromJson(i))
        .toList();
    final cvePadded = cveEstado.padLeft(2, '0');
    return impuestos.where((i) => i.cveEstado == cvePadded).firstOrNull;
  }

  /// Calculate payroll tax
  ///
  /// Parameters:
  /// - [totalPercepciones]: Total payroll for the period
  /// - [cveEstado]: State code
  ///
  /// Returns: Tax amount
  ///
  /// Example:
  /// ```dart
  /// final tax = ImpuestosLocalesCalculator.calcularImpuestoNomina(100000.0, '09');
  /// print('Payroll tax: \$${tax}'); // 3000.0 (3% for CDMX)
  /// ```
  static double calcularImpuestoNomina(
    double totalPercepciones,
    String cveEstado,
  ) {
    final impuesto = getImpuestoNomina(cveEstado);

    if (impuesto == null) {
      throw Exception(
          'No se encontró tasa de impuesto sobre nómina para estado: $cveEstado');
    }

    return totalPercepciones * (impuesto.tasa / 100);
  }

  /// Get lodging tax rate for a state
  ///
  /// Parameters:
  /// - [cveEstado]: State code (01-32)
  ///
  /// Returns: State tax information or null
  static ImpuestoEstatal? getImpuestoHospedaje(String cveEstado) {
    final data = _loadData();
    final impuestos = (data['impuesto_hospedaje'] as List)
        .map((i) => ImpuestoEstatal.fromJson(i))
        .toList();
    final cvePadded = cveEstado.padLeft(2, '0');
    return impuestos.where((i) => i.cveEstado == cvePadded).firstOrNull;
  }

  /// Calculate lodging tax
  ///
  /// Parameters:
  /// - [montoHospedaje]: Lodging service amount
  /// - [cveEstado]: State code
  ///
  /// Returns: Tax amount
  ///
  /// Example:
  /// ```dart
  /// final tax = ImpuestosLocalesCalculator.calcularImpuestoHospedaje(1000.0, '23');
  /// print('Lodging tax: \$${tax}'); // 30.0 (3% for Quintana Roo)
  /// ```
  static double calcularImpuestoHospedaje(
    double montoHospedaje,
    String cveEstado,
  ) {
    final impuesto = getImpuestoHospedaje(cveEstado);

    if (impuesto == null) {
      throw Exception(
          'No se encontró tasa de impuesto sobre hospedaje para estado: $cveEstado');
    }

    return montoHospedaje * (impuesto.tasa / 100);
  }

  /// Get all payroll tax rates
  static List<ImpuestoEstatal> getAllImpuestosNomina() {
    final data = _loadData();
    return (data['impuesto_nomina'] as List)
        .map((i) => ImpuestoEstatal.fromJson(i))
        .toList();
  }

  /// Get all lodging tax rates
  static List<ImpuestoEstatal> getAllImpuestosHospedaje() {
    final data = _loadData();
    return (data['impuesto_hospedaje'] as List)
        .map((i) => ImpuestoEstatal.fromJson(i))
        .toList();
  }
}
