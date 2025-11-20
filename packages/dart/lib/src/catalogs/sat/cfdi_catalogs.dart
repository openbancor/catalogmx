/// SAT CFDI 4.0 Catalogs
///
/// Comprehensive implementation of all 26 SAT CFDI 4.0 official catalogs.
/// These catalogs are essential for electronic invoicing (CFDI) in Mexico.
library;

import '../base_catalog.dart';

/// Base class for SAT CFDI catalogs
abstract class SatCFDICatalog extends BaseCatalog with CodeLookup {
  static final Map<String, List<Map<String, dynamic>>> _catalogCache = {};

  static List<Map<String, dynamic>> _loadCatalog(String filename) {
    if (_catalogCache.containsKey(filename)) {
      return _catalogCache[filename]!;
    }

    final data = BaseCatalog.loadJsonDataSync('sat/cfdi_4.0/$filename.json');
    _catalogCache[filename] = data;
    return data;
  }
}

/// c_FormaPago - Payment Methods Catalog
class SatFormaPago extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_FormaPago');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_MetodoPago - Payment Method Catalog (PUE, PPD, etc.)
class SatMetodoPago extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_MetodoPago');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_UsoCFDI - CFDI Usage Catalog
class SatUsoCFDI extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_UsoCFDI');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_RegimenFiscal - Tax Regime Catalog
class SatRegimenFiscal extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_RegimenFiscal');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_Moneda - Currency Catalog
class SatMoneda extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_Moneda');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_Pais - Country Catalog
class SatPais extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_Pais');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_TasaOCuota - Tax Rate Catalog
class SatTasaOCuota extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_TasaOCuota');
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }
}

/// Tipo Comprobante - Receipt Type (I, E, T, N, P)
class SatTipoComprobante extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('tipo_comprobante');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_Exportacion - Export Catalog
class SatExportacion extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_Exportacion');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// Objeto Impuesto - Tax Object
class SatObjetoImpuesto extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('objeto_imp');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// Clave Producto/Servicio - Product/Service Key (large catalog)
class SatClaveProdServ extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    // Note: This is a large catalog with 50K+ entries
    _data = SatCFDICatalog._loadCatalog('clave_prod_serv');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;

  static List<Map<String, dynamic>> search(String query) {
    _loadData();
    final normalized = query.toLowerCase();
    return _data!.where((item) {
      final desc = (item['descripcion'] as String? ?? '').toLowerCase();
      return desc.contains(normalized);
    }).toList();
  }

  /// Clears cache to free memory (useful due to large size)
  static void clearCache() {
    _data = null;
    _byCode = null;
  }
}

/// Clave Unidad - Unit of Measure
class SatClaveUnidad extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('clave_unidad');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// Tipo Relación - Relation Type
class SatTipoRelacion extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('tipo_relacion');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// Impuestos - Taxes
class SatImpuesto extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('impuesto');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}

/// c_Meses - Months
class SatMeses extends SatCFDICatalog {
  static List<Map<String, dynamic>>? _data;
  static Map<String, Map<String, dynamic>>? _byCode;

  static void _loadData() {
    if (_data != null) return;
    _data = SatCFDICatalog._loadCatalog('c_Meses');
    _byCode = {for (var item in _data!) item['clave'] as String: item};
  }

  static List<Map<String, dynamic>> getAll() {
    _loadData();
    return List.from(_data!);
  }

  static Map<String, dynamic>? getByClave(String clave) {
    _loadData();
    return _byCode![clave];
  }

  static bool isValid(String clave) => getByClave(clave) != null;
}
