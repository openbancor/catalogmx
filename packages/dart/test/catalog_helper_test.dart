import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('CatalogHelper', () {
    group('loadJsonList (async)', () {
      test('returns empty list for non-existent file', () async {
        final data = await CatalogHelper.loadJsonList('/nonexistent/path.json');
        expect(data, isEmpty);
      });

      test('returns empty list for invalid path', () async {
        final data = await CatalogHelper.loadJsonList('');
        expect(data, isEmpty);
      });
    });

    group('loadJsonListSync', () {
      test('returns empty list for non-existent file', () {
        final data = CatalogHelper.loadJsonListSync('/nonexistent/path.json');
        expect(data, isEmpty);
      });

      test('returns empty list for invalid path', () {
        final data = CatalogHelper.loadJsonListSync('');
        expect(data, isEmpty);
      });

      test('returns empty list for directory path', () {
        final data = CatalogHelper.loadJsonListSync('/tmp');
        expect(data, isEmpty);
      });
    });

    group('getSharedDataPath', () {
      test('returns expected path', () {
        final path = CatalogHelper.getSharedDataPath();
        expect(path, isNotEmpty);
        expect(path, contains('shared-data'));
      });
    });
  });
}
