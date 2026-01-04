/// Catálogo de monedas y divisas internacionales (Banxico)
///
/// Este módulo proporciona acceso al catálogo de monedas y divisas
/// internacionales utilizadas en operaciones cambiarias en México,
/// basado en códigos ISO 4217.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Monedas y Divisas Catalog
class MonedasDivisasCatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCodigoISO;
  static Map<String, Map<String, dynamic>>? _byNumeroISO;

  static void _loadData() {
    if (_data != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'banxico/monedas_divisas.json',
    );

    // Handle both list and dict formats
    if (jsonData.isNotEmpty && jsonData.first.containsKey('monedas')) {
      _data = (jsonData.first['monedas'] as List)
          .map((e) => e as Map<String, dynamic>)
          .toList();
    } else {
      _data = jsonData;
    }

    // Build indices
    _byCodigoISO = {
      for (var moneda in _data!)
        (moneda['codigo_iso'] as String).toUpperCase(): moneda,
    };

    _byNumeroISO = {
      for (var moneda in _data!) moneda['numero_iso'] as String: moneda,
    };
  }

  /// Obtiene todas las monedas
  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  /// Busca moneda por código ISO
  ///
  /// Args:
  ///   codigoISO: Código ISO 4217 de la moneda (ej: "USD", "EUR", "MXN")
  ///
  /// Returns:
  ///   Información de la moneda o null si no existe
  static Map<String, dynamic>? getPorCodigo(String codigoISO) {
    _loadData();
    return _byCodigoISO![codigoISO.toUpperCase()];
  }

  /// Busca moneda por número ISO
  ///
  /// Args:
  ///   numeroISO: Número ISO 4217 de la moneda
  ///
  /// Returns:
  ///   Información de la moneda o null si no existe
  static Map<String, dynamic>? getPorNumeroISO(String numeroISO) {
    _loadData();
    return _byNumeroISO![numeroISO];
  }

  /// Busca monedas por país
  ///
  /// Args:
  ///   pais: Nombre del país (búsqueda parcial, case-insensitive)
  ///
  /// Returns:
  ///   Lista de monedas del país
  static List<Map<String, dynamic>> getPorPais(String pais) {
    _loadData();
    final paisLower = pais.toLowerCase();
    return _data!
        .where((m) => (m['pais'] as String).toLowerCase().contains(paisLower))
        .toList();
  }

  /// Obtiene monedas con tipo de cambio publicado por Banxico
  static List<Map<String, dynamic>> getConTipoCambioBanxico() {
    _loadData();
    return _data!.where((m) => m['tipo_cambio_banxico'] == true).toList();
  }

  /// Obtiene monedas con tipo de cambio FIX
  static List<Map<String, dynamic>> getConTipoCambioFIX() {
    _loadData();
    return _data!.where((m) => m['tipo_cambio_fix'] == true).toList();
  }

  /// Obtiene monedas principales para operaciones en México
  ///
  /// Returns:
  ///   Lista de monedas principales (MXN, USD, EUR, CAD, GBP, JPY, CHF)
  static List<Map<String, dynamic>> getPrincipales() {
    _loadData();
    const principales = ['MXN', 'USD', 'EUR', 'CAD', 'GBP', 'JPY', 'CHF'];
    return _data!.where((m) => principales.contains(m['codigo_iso'])).toList();
  }

  /// Obtiene monedas latinoamericanas
  static List<Map<String, dynamic>> getLatam() {
    _loadData();
    const latam = [
      'MXN',
      'ARS',
      'BRL',
      'CLP',
      'COP',
      'PEN',
      'GTQ',
      'CRC',
      'UYU',
      'VES',
    ];
    return _data!.where((m) => latam.contains(m['codigo_iso'])).toList();
  }

  /// Valida código ISO de moneda
  ///
  /// Args:
  ///   codigo: Código ISO a validar
  ///
  /// Returns:
  ///   true si el código existe, false en caso contrario
  static bool validarCodigoISO(String codigo) {
    return getPorCodigo(codigo) != null;
  }

  /// Formatea monto en una moneda específica
  ///
  /// Args:
  ///   monto: Monto a formatear
  ///   codigoISO: Código ISO de la moneda
  ///
  /// Returns:
  ///   Monto formateado con símbolo de moneda
  static String formatearMonto(double monto, String codigoISO) {
    final moneda = getPorCodigo(codigoISO);
    if (moneda == null) return monto.toString();

    final decimales = moneda['decimales'] as int;
    final simbolo = moneda['simbolo'] as String;

    final montoFormateado = decimales == 0
        ? monto.round().toString()
        : monto.toStringAsFixed(decimales);

    return '$simbolo $montoFormateado';
  }

  /// Obtiene peso mexicano (MXN)
  static Map<String, dynamic>? getMXN() => getPorCodigo('MXN');

  /// Obtiene dólar estadounidense (USD)
  static Map<String, dynamic>? getUSD() => getPorCodigo('USD');

  /// Obtiene euro (EUR)
  static Map<String, dynamic>? getEUR() => getPorCodigo('EUR');

  /// Busca monedas por nombre
  ///
  /// Args:
  ///   nombre: Texto a buscar en el nombre de la moneda
  ///
  /// Returns:
  ///   Lista de monedas que coinciden
  static List<Map<String, dynamic>> buscarPorNombre(String nombre) {
    _loadData();
    final nombreLower = nombre.toLowerCase();
    return _data!
        .where(
          (m) => (m['moneda'] as String).toLowerCase().contains(nombreLower),
        )
        .toList();
  }

  /// Obtiene monedas activas
  static List<Map<String, dynamic>> getActivas() {
    _loadData();
    return _data!.where((m) => m['activa'] == true).toList();
  }
}
