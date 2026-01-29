package com.openbancor.catalogmx.utils

import com.ibm.icu.text.Normalizer2

/**
 * Text utility functions for Mexican document processing
 */
object TextUtils {
    private val normalizer = Normalizer2.getNFDInstance()

    /**
     * Removes diacritics from text (e.g., á -> a, ñ -> n)
     * Preserves Ñ when specified
     */
    @JvmStatic
    @JvmOverloads
    fun removeDiacritics(text: String, preserveN: Boolean = false): String {
        val normalized = normalizer.normalize(text)
        val result = StringBuilder()
        for (char in normalized) {
            when {
                char == 'Ñ' || char == 'ñ' -> {
                    if (preserveN) result.append(char)
                    else result.append(if (char == 'Ñ') 'N' else 'n')
                }
                Character.getType(char) != Character.NON_SPACING_MARK.toInt() -> {
                    result.append(char)
                }
            }
        }
        return result.toString()
    }

    /**
     * Normalizes text for comparison (uppercase, no accents, trim)
     */
    @JvmStatic
    fun normalizeText(text: String): String =
        removeDiacritics(text.uppercase().trim())

    /**
     * Normalizes text for search (lowercase, no accents, trim)
     * Alias for search operations that need case-insensitive matching
     */
    @JvmStatic
    fun normalize(text: String): String =
        removeDiacritics(text.lowercase().trim())

    /**
     * Cleans a name by removing excluded words and keeping only allowed characters
     */
    @JvmStatic
    fun cleanName(
        name: String,
        excludedWords: List<String>,
        allowedChars: List<Char>
    ): String {
        var cleanedName = removeDiacritics(name.uppercase().trim(), preserveN = true)

        // Split into words
        val words = cleanedName.split(Regex("\\s+")).filter { it.isNotEmpty() }

        // Filter out excluded words
        val filteredWords = words.filter { word ->
            word !in excludedWords
        }

        // Rejoin words
        cleanedName = if (filteredWords.isEmpty()) words.joinToString(" ") else filteredWords.joinToString(" ")

        // Keep only allowed characters
        val result = StringBuilder()
        for (char in cleanedName) {
            if (char in allowedChars || char == ' ') {
                result.append(char)
            }
        }

        return result.toString().trim()
    }

    /**
     * Gets the first vowel from a string starting at a given index
     */
    @JvmStatic
    @JvmOverloads
    fun getFirstVowel(text: String, startIndex: Int = 0): Char? {
        val vowels = "AEIOU"
        for (i in startIndex until text.length) {
            if (text[i].uppercaseChar() in vowels) {
                return text[i].uppercaseChar()
            }
        }
        return null
    }

    /**
     * Gets the first consonant from a string starting at a given index
     */
    @JvmStatic
    @JvmOverloads
    fun getFirstConsonant(text: String, startIndex: Int = 0): Char? {
        val consonants = "BCDFGHJKLMNPQRSTVWXYZ"
        for (i in startIndex until text.length) {
            if (text[i].uppercaseChar() in consonants) {
                return text[i].uppercaseChar()
            }
        }
        return null
    }
}
