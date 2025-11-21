/// Date utilities for catalogmx
///
/// Provides functions for date validation and formatting used in validators.
library;

/// Validates if a date string in YYMMDD format is valid
bool isValidDateYYMMDD(String dateStr) {
  if (dateStr.length != 6) return false;

  try {
    final year = int.parse(dateStr.substring(0, 2));
    final month = int.parse(dateStr.substring(2, 4));
    final day = int.parse(dateStr.substring(4, 6));

    // Validate month
    if (month < 1 || month > 12) return false;

    // Validate day
    if (day < 1 || day > 31) return false;

    // Assume years < 50 are 2000+, others are 1900+
    final fullYear = year < 50 ? 2000 + year : 1900 + year;

    // Validate day is within the month's valid range
    final date = DateTime(fullYear, month, day);

    // DateTime is lenient and will roll over invalid dates
    // Check that the resulting date matches the input
    if (date.month != month || date.day != day) {
      return false;
    }

    return true;
  } catch (e) {
    return false;
  }
}

/// Converts DateTime to YYMMDD format
String dateToYYMMDD(DateTime date) {
  final year = date.year % 100;
  final month = date.month;
  final day = date.day;
  return '${year.toString().padLeft(2, '0')}${month.toString().padLeft(2, '0')}${day.toString().padLeft(2, '0')}';
}

/// Parses a date from YYMMDD format
DateTime? parseDateYYMMDD(String dateStr) {
  if (!isValidDateYYMMDD(dateStr)) return null;

  final year = int.parse(dateStr.substring(0, 2));
  final month = int.parse(dateStr.substring(2, 4));
  final day = int.parse(dateStr.substring(4, 6));

  // Assume years < 50 are 2000+, others are 1900+
  final fullYear = year < 50 ? 2000 + year : 1900 + year;

  return DateTime(fullYear, month, day);
}
