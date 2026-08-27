/// SAT Nómina 1.2 catalogs.
library;

import 'package:catalogmx/src/catalogs/base_catalog.dart';

class _NominaData {
  static final Map<String, List<Map<String, dynamic>>> _cache = {};

  static List<Map<String, dynamic>> load(String filename) {
    return _cache.putIfAbsent(filename, () {
      final rows = BaseCatalog.loadJsonDataSync('sat/nomina_1.2/$filename');
      return rows.map(_normalize).toList(growable: false);
    });
  }

  static Map<String, dynamic> _normalize(Map<String, dynamic> source) {
    final item = Map<String, dynamic>.from(source);
    final code = (item['code'] ?? item['clave'] ?? item['id'])?.toString();
    if (code == null) {
      throw StateError('SAT Nómina row has no code');
    }
    item['code'] = code;
    item['clave'] ??= code;

    final description =
        item['description'] ?? item['descripcion'] ?? item['texto'];
    if (description != null) {
      item['description'] = description.toString();
      item['descripcion'] ??= description.toString();
    }

    final name = item['name'] ?? item['nombre'];
    if (name != null) {
      item['name'] = name.toString();
      item['nombre'] ??= name.toString();
    }

    final legalName = item['razon_social'] ?? item['full_name'];
    if (legalName != null) {
      item['razon_social'] = legalName.toString();
      item['full_name'] ??= legalName.toString();
    }
    return item;
  }

  static Map<String, dynamic>? byCode(String filename, String code) {
    for (final item in load(filename)) {
      if (item['code'] == code) return item;
    }
    return null;
  }
}

abstract class _SimpleNominaCatalog {
  static List<Map<String, dynamic>> all(String filename) =>
      List<Map<String, dynamic>>.from(_NominaData.load(filename));
  static Map<String, dynamic>? byCode(String filename, String code) =>
      _NominaData.byCode(filename, code);
  static bool valid(String filename, String code) =>
      byCode(filename, code) != null;
}

class TipoNominaCatalog {
  static const _file = 'tipo_nomina.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoContratoCatalog {
  static const _file = 'tipo_contrato.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoJornadaCatalog {
  static const _file = 'tipo_jornada.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoRegimenCatalog {
  static const _file = 'tipo_regimen.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class PeriodicidadPagoCatalog {
  static const _file = 'periodicidad_pago.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class BancoNominaCatalog {
  static const _file = 'banco.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);

  static List<Map<String, dynamic>> search(String query) {
    final q = query.toUpperCase();
    return _NominaData.load(_file).where((item) {
      final name =
          (item['name'] ?? item['nombre'] ?? '').toString().toUpperCase();
      final legal = (item['full_name'] ?? item['razon_social'] ?? '')
          .toString()
          .toUpperCase();
      return name.contains(q) || legal.contains(q);
    }).toList();
  }
}

class RiesgoPuestoCatalog {
  static const _file = 'riesgo_puesto.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class OrigenRecursoCatalog {
  static const _file = 'origen_recurso.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoDeduccionCatalog {
  static const _file = 'tipo_deduccion.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoHorasCatalog {
  static const _file = 'tipo_horas.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoIncapacidadCatalog {
  static const _file = 'tipo_incapacidad.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoOtroPagoCatalog {
  static const _file = 'tipo_otro_pago.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}

class TipoPercepcionCatalog {
  static const _file = 'tipo_percepcion.json';
  static List<Map<String, dynamic>> getAll() => _SimpleNominaCatalog.all(_file);
  static Map<String, dynamic>? getByClave(String clave) =>
      _SimpleNominaCatalog.byCode(_file, clave);
  static Map<String, dynamic>? getByCode(String code) => getByClave(code);
  static bool isValid(String clave) => _SimpleNominaCatalog.valid(_file, clave);
}
