/// SCIAN - Sistema de Clasificación Industrial de América del Norte
///
/// Catálogo de sectores económicos según la clasificación SCIAN de INEGI.
/// Clasificación utilizada en México, EE.UU. y Canadá.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Sector SCIAN
class SectorSCIAN {
  final String codigo;
  final String nombre;
  final String nombreCorto;
  final int subsectores;
  final int ramas;
  final String descripcion;

  SectorSCIAN({
    required this.codigo,
    required this.nombre,
    required this.nombreCorto,
    required this.subsectores,
    required this.ramas,
    required this.descripcion,
  });

  factory SectorSCIAN.fromJson(Map<String, dynamic> json) {
    return SectorSCIAN(
      codigo: json['codigo'] as String,
      nombre: json['nombre'] as String,
      nombreCorto: json['nombre_corto'] as String,
      subsectores: json['subsectores'] as int,
      ramas: json['ramas'] as int,
      descripcion: json['descripcion'] as String,
    );
  }
}

/// Catálogo SCIAN (Sistema de Clasificación Industrial de América del Norte)
class SCIANCatalog {
  static List<SectorSCIAN>? _sectores;
  static Map<String, SectorSCIAN>? _byCodigo;
  static Map<String, int>? _totales;

  static void _loadData() {
    if (_sectores != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync('inegi/scian/sectores.json');

    if (jsonData.isNotEmpty) {
      final data = jsonData.first;

      // Load sectores
      final sectoresJson = data['sectores'] as List?;
      _sectores = sectoresJson
              ?.map((e) => SectorSCIAN.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];

      // Load totales
      final totalesJson = data['totales'] as Map<String, dynamic>?;
      _totales = totalesJson?.map((k, v) => MapEntry(k, v as int)) ?? {};

      // Build index by codigo
      _byCodigo = {for (var s in _sectores!) s.codigo: s};
    } else {
      _sectores = [];
      _byCodigo = {};
      _totales = {};
    }
  }

  /// Obtiene todos los sectores SCIAN (20 sectores)
  static List<SectorSCIAN> getAllSectores() {
    _loadData();
    return List.from(_sectores!);
  }

  /// Obtiene un sector por código (2 dígitos)
  static SectorSCIAN? getSectorByCodigo(String codigo) {
    _loadData();
    return _byCodigo![codigo];
  }

  /// Valida si un código de sector existe
  static bool isValidSector(String codigo) {
    return getSectorByCodigo(codigo) != null;
  }

  /// Busca sectores por nombre o descripción
  static List<SectorSCIAN> search(String query) {
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

  /// Obtiene el sector al que pertenece un código SCIAN de cualquier nivel
  ///
  /// Por ejemplo: para código "311811" (Panaderías) retorna sector "31-33" (Manufactura).
  static SectorSCIAN? getSectorForCode(String codigo) {
    _loadData();
    if (_sectores == null || codigo.length < 2) return null;

    final codigo2 = codigo.substring(0, 2);

    for (var sector in _sectores!) {
      final sectorCodigo = sector.codigo;

      // Handle ranges like "31-33" or "48-49"
      if (sectorCodigo.contains('-')) {
        final parts = sectorCodigo.split('-');
        if (parts.length == 2) {
          final inicio = parts[0];
          final fin = parts[1];
          if (codigo2.compareTo(inicio) >= 0 && codigo2.compareTo(fin) <= 0) {
            return sector;
          }
        }
      } else if (sectorCodigo == codigo2) {
        return sector;
      }
    }

    return null;
  }

  /// Obtiene los totales de la estructura SCIAN
  static Map<String, int> getTotales() {
    _loadData();
    return Map.from(_totales!);
  }

  /// Número total de sectores
  static int get countSectores {
    _loadData();
    return _sectores!.length;
  }
}
