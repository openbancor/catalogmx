import 'package:test/test.dart';
import 'package:catalogmx/src/utils/date_utils.dart';

void main() {
  group('isValidDateYYMMDD', () {
    test('validates correct dates', () {
      expect(isValidDateYYMMDD('900515'), isTrue);
      expect(isValidDateYYMMDD('000101'), isTrue);
      expect(isValidDateYYMMDD('991231'), isTrue);
    });

    test('rejects invalid month', () {
      expect(isValidDateYYMMDD('901301'), isFalse);
      expect(isValidDateYYMMDD('900001'), isFalse);
    });

    test('rejects invalid day', () {
      expect(isValidDateYYMMDD('900132'), isFalse);
      expect(isValidDateYYMMDD('900100'), isFalse);
    });

    test('rejects invalid date for month', () {
      expect(isValidDateYYMMDD('900230'), isFalse); // Feb 30
      expect(isValidDateYYMMDD('900431'), isFalse); // Apr 31
    });

    test('handles leap years', () {
      expect(isValidDateYYMMDD('000229'), isTrue); // 2000 is leap year
      expect(isValidDateYYMMDD('010229'), isFalse); // 2001 is not
    });

    test('rejects wrong length', () {
      expect(isValidDateYYMMDD('90051'), isFalse);
      expect(isValidDateYYMMDD('9005150'), isFalse);
      expect(isValidDateYYMMDD(''), isFalse);
    });

    test('rejects non-numeric strings', () {
      expect(isValidDateYYMMDD('AABBCC'), isFalse);
      expect(isValidDateYYMMDD('90051A'), isFalse);
    });
  });

  group('dateToYYMMDD', () {
    test('converts DateTime to YYMMDD', () {
      expect(dateToYYMMDD(DateTime(1990, 5, 15)), equals('900515'));
      expect(dateToYYMMDD(DateTime(2000, 1, 1)), equals('000101'));
      expect(dateToYYMMDD(DateTime(2023, 12, 31)), equals('231231'));
    });

    test('pads single digit month and day', () {
      expect(dateToYYMMDD(DateTime(2005, 3, 7)), equals('050307'));
    });

    test('handles year 2000', () {
      expect(dateToYYMMDD(DateTime(2000, 6, 15)), equals('000615'));
    });

    test('handles year 1999', () {
      expect(dateToYYMMDD(DateTime(1999, 6, 15)), equals('990615'));
    });
  });

  group('parseDateYYMMDD', () {
    test('parses valid date strings', () {
      final date = parseDateYYMMDD('900515');
      expect(date, isNotNull);
      expect(date!.year, equals(1990));
      expect(date.month, equals(5));
      expect(date.day, equals(15));
    });

    test('handles century threshold (year < 50 = 2000s)', () {
      final date1 = parseDateYYMMDD('490101');
      expect(date1!.year, equals(2049));

      final date2 = parseDateYYMMDD('500101');
      expect(date2!.year, equals(1950));
    });

    test('returns null for invalid dates', () {
      expect(parseDateYYMMDD('991332'), isNull);
      expect(parseDateYYMMDD('invalid'), isNull);
      expect(parseDateYYMMDD(''), isNull);
    });
  });
}
