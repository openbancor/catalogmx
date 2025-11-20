import 'package:test/test.dart';
import 'package:catalogmx/catalogmx.dart';

void main() {
  group('INEGI States Catalog', () {
    test('returns all states', () {
      final states = InegStates.getAll();
      expect(states.length, greaterThan(30));
    });

    test('gets state by code', () {
      final cdmx = InegStates.getByCode('DF');
      expect(cdmx, isNotNull);
      expect(cdmx!['name'], equals('CIUDAD DE MEXICO'));
    });

    test('gets state by INEGI clave', () {
      final cdmx = InegStates.getByClaveInegi('09');
      expect(cdmx, isNotNull);
      expect(cdmx!['name'], equals('CIUDAD DE MEXICO'));
    });

    test('gets state by name', () {
      final jalisco = InegStates.getByName('Jalisco');
      expect(jalisco, isNotNull);
      expect(jalisco!['code'], equals('JC'));
    });

    test('validates state codes', () {
      expect(InegStates.isValid('DF'), isTrue);
      expect(InegStates.isValid('JC'), isTrue);
      expect(InegStates.isValid('XX'), isFalse);
    });

    test('searches states by partial name', () {
      final results = InegStates.search('mexico');
      expect(results.length, greaterThan(0));
    });
  });
}
