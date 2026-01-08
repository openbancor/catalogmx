/// Giros Mercantiles - Catálogo de giros comerciales comunes
///
/// Catálogo de giros mercantiles comunes en México para clasificación
/// de negocios, licencias de funcionamiento y registros comerciales.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

/// Categoría de giro mercantil
class CategoriaGiro {
  final String id;
  final String nombre;
  final String descripcion;

  CategoriaGiro({
    required this.id,
    required this.nombre,
    required this.descripcion,
  });

  factory CategoriaGiro.fromJson(Map<String, dynamic> json) {
    return CategoriaGiro(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      descripcion: json['descripcion'] as String,
    );
  }
}

/// Giro mercantil
class GiroMercantil {
  final String id;
  final String nombre;
  final String categoria;
  final bool requiereLicenciaAlcohol;

  GiroMercantil({
    required this.id,
    required this.nombre,
    required this.categoria,
    required this.requiereLicenciaAlcohol,
  });

  factory GiroMercantil.fromJson(Map<String, dynamic> json) {
    return GiroMercantil(
      id: json['id'] as String,
      nombre: json['nombre'] as String,
      categoria: json['categoria'] as String,
      requiereLicenciaAlcohol: json['requiere_licencia_alcohol'] as bool,
    );
  }
}

/// Catálogo de Giros Mercantiles
class GirosMercantilesCatalog {
  static List<GiroMercantil>? _giros;
  static List<CategoriaGiro>? _categorias;
  static Map<String, GiroMercantil>? _byId;
  static Map<String, CategoriaGiro>? _categoriasById;

  static void _loadData() {
    if (_giros != null) return;

    final jsonData = BaseCatalog.loadJsonDataSync(
      'mexico/giros_mercantiles.json',
    );

    if (jsonData.isNotEmpty) {
      final data = jsonData.first;

      // Load categorias
      final categoriasJson = data['categorias'] as List?;
      _categorias = categoriasJson
              ?.map((e) => CategoriaGiro.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];

      // Load giros
      final girosJson = data['giros'] as List?;
      _giros = girosJson
              ?.map((e) => GiroMercantil.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [];

      // Build indexes
      _byId = {for (var g in _giros!) g.id: g};
      _categoriasById = {for (var c in _categorias!) c.id: c};
    } else {
      _giros = [];
      _categorias = [];
      _byId = {};
      _categoriasById = {};
    }
  }

  /// Obtiene todos los giros mercantiles
  static List<GiroMercantil> getAll() {
    _loadData();
    return List.from(_giros!);
  }

  /// Obtiene todas las categorías
  static List<CategoriaGiro> getAllCategorias() {
    _loadData();
    return List.from(_categorias!);
  }

  /// Obtiene un giro por ID
  static GiroMercantil? getById(String id) {
    _loadData();
    return _byId![id];
  }

  /// Obtiene una categoría por ID
  static CategoriaGiro? getCategoriaById(String id) {
    _loadData();
    return _categoriasById![id];
  }

  /// Valida si un ID de giro existe
  static bool isValid(String id) {
    return getById(id) != null;
  }

  /// Busca giros por nombre
  static List<GiroMercantil> search(String query) {
    _loadData();
    final queryLower = query.toLowerCase();
    return _giros!
        .where((g) => g.nombre.toLowerCase().contains(queryLower))
        .toList();
  }

  /// Obtiene giros por categoría
  static List<GiroMercantil> getByCategoria(String categoriaId) {
    _loadData();
    return _giros!.where((g) => g.categoria == categoriaId).toList();
  }

  /// Obtiene giros que requieren licencia de alcohol
  static List<GiroMercantil> getRequierenLicenciaAlcohol() {
    _loadData();
    return _giros!.where((g) => g.requiereLicenciaAlcohol).toList();
  }

  /// Número total de giros
  static int get count {
    _loadData();
    return _giros!.length;
  }

  /// Número total de categorías
  static int get categoriasCount {
    _loadData();
    return _categorias!.length;
  }
}
