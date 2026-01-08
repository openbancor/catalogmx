/// CNBV - Sectores del Sistema Financiero Mexicano
///
/// Catálogo de sectores y entidades reguladas por la
/// Comisión Nacional Bancaria y de Valores (CNBV).
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Sector CNBV
class SectorCNBV {
  final String id;
  final String nombre;
  final String nombreCorto;
  final String descripcion;
  final String leyAplicable;
  final String reguladorPrincipal;
  final List<String> supervisoresAdicionales;
  final List<String> ejemplos;

  SectorCNBV({
    required this.id,
    required this.nombre,
    required this.nombreCorto,
    required this.descripcion,
    required this.leyAplicable,
    required this.reguladorPrincipal,
    required this.supervisoresAdicionales,
    required this.ejemplos,
  });

  factory SectorCNBV.fromJson(Map<String, dynamic> json) {
    return SectorCNBV(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      nombreCorto: json['nombre_corto'] as String,
      descripcion: json['descripcion'] as String,
      leyAplicable: json['ley_aplicable'] as String,
      reguladorPrincipal: json['regulador_principal'] as String,
      supervisoresAdicionales: (json['supervisores_adicionales'] as List?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      ejemplos:
          (json['ejemplos'] as List?)?.map((e) => e as String).toList() ?? [],
    );
  }
}

/// Regulador Financiero
class ReguladorFinanciero {
  final String id;
  final String nombre;
  final String siglas;
  final String funcion;

  ReguladorFinanciero({
    required this.id,
    required this.nombre,
    required this.siglas,
    required this.funcion,
  });

  factory ReguladorFinanciero.fromJson(Map<String, dynamic> json) {
    return ReguladorFinanciero(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      siglas: json['siglas'] as String,
      funcion: json['funcion'] as String,
    );
  }
}

/// Catálogo de Sectores CNBV
class SectoresCNBVCatalog {
  static List<SectorCNBV>? _sectores;
  static List<ReguladorFinanciero>? _reguladores;
  static Map<String, SectorCNBV>? _byId;
  static Map<String, ReguladorFinanciero>? _reguladoresById;

  static void _loadData() {
    if (_sectores != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('cnbv/sectores.json');

    if (jsonData.isNotEmpty) {
      final data = jsonData.first;

      // Load sectores
      final sectoresJson = data['sectores'] as List?;
      _sectores = sectoresJson
              ?.map((e) => SectorCNBV.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];

      // Load reguladores
      final reguladoresJson = data['reguladores'] as List?;
      _reguladores = reguladoresJson
              ?.map(
                (e) => ReguladorFinanciero.fromJson(e as Map<String, dynamic>),
              )
              .toList() ??
          [];

      // Build indexes
      _byId = {for (var s in _sectores!) s.id: s};
      _reguladoresById = {for (var r in _reguladores!) r.id: r};
    } else {
      _sectores = [];
      _reguladores = [];
      _byId = {};
      _reguladoresById = {};
    }
  }

  /// Obtiene todos los sectores CNBV
  static List<SectorCNBV> getAll() {
    _loadData();
    return List.from(_sectores!);
  }

  /// Obtiene un sector por ID
  static SectorCNBV? getById(String id) {
    _loadData();
    return _byId![id];
  }

  /// Valida si un ID de sector existe
  static bool isValid(String id) {
    return getById(id) != null;
  }

  /// Busca sectores por nombre o descripción
  static List<SectorCNBV> search(String query) {
    _loadData();
    final queryLower = query.toLowerCase();
    return _sectores!
        .where(
          (s) =>
              s.nombre.toLowerCase().contains(queryLower) ||
              s.nombreCorto.toLowerCase().contains(queryLower) ||
              s.descripcion.toLowerCase().contains(queryLower),
        )
        .toList();
  }

  /// Obtiene sectores por regulador principal
  static List<SectorCNBV> getByRegulador(String regulador) {
    _loadData();
    final reguladorUpper = regulador.toUpperCase();
    return _sectores!
        .where((s) => s.reguladorPrincipal.toUpperCase() == reguladorUpper)
        .toList();
  }

  /// Obtiene todos los reguladores
  static List<ReguladorFinanciero> getAllReguladores() {
    _loadData();
    return List.from(_reguladores!);
  }

  /// Obtiene un regulador por ID
  static ReguladorFinanciero? getReguladorById(String id) {
    _loadData();
    return _reguladoresById![id];
  }

  /// Obtiene un regulador por siglas
  static ReguladorFinanciero? getReguladorBySiglas(String siglas) {
    _loadData();
    final siglasUpper = siglas.toUpperCase();
    return _reguladores!.cast<ReguladorFinanciero?>().firstWhere(
          (r) => r!.siglas.toUpperCase() == siglasUpper,
          orElse: () => null,
        );
  }

  /// Número total de sectores
  static int get count {
    _loadData();
    return _sectores!.length;
  }

  /// Número total de reguladores
  static int get reguladoresCount {
    _loadData();
    return _reguladores!.length;
  }
}
