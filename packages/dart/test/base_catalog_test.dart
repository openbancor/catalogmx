import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('BaseCatalog', () {
    test('loadJsonDataSync returns empty list when file not found', () {
      final data = BaseCatalog.loadJsonDataSync('nonexistent/file.json');
      expect(data, isEmpty);
    });

    test('cache is populated after first load', () {
      // First load returns empty (file not found)
      BaseCatalog.loadJsonDataSync('test/cache/file.json');

      // Second load should return cached empty list
      final data = BaseCatalog.loadJsonDataSync('test/cache/file.json');
      expect(data, isEmpty);
    });

    test('clearCache clears all cached data', () {
      // Load something to cache it
      BaseCatalog.loadJsonDataSync('test/clear/file.json');

      // Clear cache
      BaseCatalog.clearCache();

      // Should work without error
      expect(() => BaseCatalog.clearCache(), returnsNormally);
    });

    test('clearCacheFor clears specific path', () {
      // Load something to cache it
      BaseCatalog.loadJsonDataSync('test/specific/file.json');

      // Clear specific cache
      BaseCatalog.clearCacheFor('test/specific/file.json');

      // Should work without error
      expect(() => BaseCatalog.clearCacheFor('nonexistent'), returnsNormally);
    });
  });

  group('CodeLookup mixin', () {
    test('getByCode returns null for non-existent code', () {
      final lookup = TestCodeLookup();
      lookup.buildCodeIndex([
        {'code': 'ABC', 'value': 1},
        {'code': 'DEF', 'value': 2},
      ], 'code');

      expect(lookup.getByCode('ABC'), isNotNull);
      expect(lookup.getByCode('XYZ'), isNull);
    });

    test('getByCode is case insensitive', () {
      final lookup = TestCodeLookup();
      lookup.buildCodeIndex([
        {'code': 'ABC', 'value': 1},
      ], 'code');

      expect(lookup.getByCode('abc'), isNotNull);
      expect(lookup.getByCode('ABC'), isNotNull);
    });

    test('isValidCode returns correct boolean', () {
      final lookup = TestCodeLookup();
      lookup.buildCodeIndex([
        {'code': 'ABC', 'value': 1},
      ], 'code');

      expect(lookup.isValidCode('ABC'), isTrue);
      expect(lookup.isValidCode('XYZ'), isFalse);
    });
  });

  group('NameSearch mixin', () {
    test('searchByName finds items containing query', () {
      final search = TestNameSearch();
      final data = [
        {'name': 'Ciudad de México', 'code': 'CDMX'},
        {'name': 'Estado de México', 'code': 'MEX'},
        {'name': 'Jalisco', 'code': 'JAL'},
      ];

      final results = search.searchByName(data, 'méxico', 'name');
      expect(results.length, equals(2));
    });

    test('searchByName is case insensitive', () {
      final search = TestNameSearch();
      final data = [
        {'name': 'JALISCO', 'code': 'JAL'},
      ];

      expect(search.searchByName(data, 'jalisco', 'name').length, equals(1));
      expect(search.searchByName(data, 'JALISCO', 'name').length, equals(1));
    });

    test('getByName returns exact match', () {
      final search = TestNameSearch();
      final data = [
        {'name': 'Ciudad de México', 'code': 'CDMX'},
        {'name': 'Jalisco', 'code': 'JAL'},
      ];

      final result = search.getByName(data, 'jalisco', 'name');
      expect(result, isNotNull);
      expect(result!['code'], equals('JAL'));
    });

    test('getByName returns null for no match', () {
      final search = TestNameSearch();
      final data = [
        {'name': 'Jalisco', 'code': 'JAL'},
      ];

      expect(search.getByName(data, 'Oaxaca', 'name'), isNull);
    });
  });
}

// Test classes for mixins
class TestCodeLookup with CodeLookup {}

class TestNameSearch with NameSearch {}
