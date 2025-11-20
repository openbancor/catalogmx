/// Text utilities for catalogmx
///
/// Provides functions for text normalization, accent removal, and string manipulation
/// used throughout the validators and catalogs.
library;

import 'package:diacritic/diacritic.dart';

/// Removes accents and converts text to uppercase
String cleanText(String text) {
  return removeDiacritics(text).toUpperCase();
}

/// Normalizes text for comparison (removes accents, lowercase, trim)
String normalizeText(String text) {
  return removeDiacritics(text.toLowerCase().trim());
}

/// Removes excluded words from a name
String removeExcludedWords(String text, List<String> excludedWords) {
  final words = text.split(' ');
  final filtered = words.where((word) => !excludedWords.contains(word.toUpperCase())).toList();
  return filtered.join(' ');
}

/// Checks if a string contains only allowed characters
bool containsOnlyAllowed(String text, List<String> allowedChars) {
  for (var i = 0; i < text.length; i++) {
    if (!allowedChars.contains(text[i])) {
      return false;
    }
  }
  return true;
}

/// Gets the first vowel in a string
String? getFirstVowel(String text, {int startIndex = 0}) {
  const vowels = 'AEIOU';
  for (var i = startIndex; i < text.length; i++) {
    if (vowels.contains(text[i])) {
      return text[i];
    }
  }
  return null;
}

/// Gets the first consonant in a string
String? getFirstConsonant(String text, {int startIndex = 0}) {
  const consonants = 'BCDFGHJKLMNPQRSTVWXYZ';
  for (var i = startIndex; i < text.length; i++) {
    if (consonants.contains(text[i])) {
      return text[i];
    }
  }
  return null;
}

/// Cleans a name by removing accents and excluded words
String cleanName(String name, List<String> excludedWords, List<String> allowedChars) {
  // Remove excluded words
  final filtered = removeExcludedWords(name, excludedWords);

  // Clean text and remove accents
  final cleaned = cleanText(filtered);

  // Keep only allowed characters
  final result = StringBuffer();
  for (var i = 0; i < cleaned.length; i++) {
    final char = cleaned[i];
    if (allowedChars.contains(char)) {
      result.write(char);
    } else {
      // Try to remove diacritics
      final normalized = removeDiacritics(char);
      if (allowedChars.contains(normalized)) {
        result.write(normalized);
      } else if (char == ' ') {
        result.write(' ');
      }
    }
  }

  return result.toString().trim();
}
