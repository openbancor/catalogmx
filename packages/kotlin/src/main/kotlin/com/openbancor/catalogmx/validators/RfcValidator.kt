package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.utils.DateUtils
import com.openbancor.catalogmx.utils.TextUtils

/**
 * RFC (Registro Federal de Contribuyentes) Exception
 */
class RfcException(message: String) : Exception(message)

/**
 * RFC (Registro Federal de Contribuyentes) Validator and utilities
 *
 * RFC is Mexico's tax identification number, issued by SAT.
 *
 * Structure:
 * - Persona Física (Individual): 13 characters (AAAA-YYMMDD-XXX)
 *   - 4 letters from name
 *   - 6 digits for birth date (YYMMDD)
 *   - 3 alphanumeric characters (homoclave + checksum)
 *
 * - Persona Moral (Company): 12 characters (AAA-YYMMDD-XXX)
 *   - 3 letters from company name
 *   - 6 digits for incorporation date (YYMMDD)
 *   - 3 alphanumeric characters (homoclave + checksum)
 *
 * Example: XAXX010101000 (Generic RFC)
 */
class RfcValidator(rfc: String) {
    val rfc: String = rfc.uppercase().trim()

    companion object {
        private val generalRegex = Regex("^[A-ZÑ&]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]$")
        private const val HOMOCLAVE_CHARS = "ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789"

        val checksumTable = mapOf(
            '0' to "00", '1' to "01", '2' to "02", '3' to "03", '4' to "04",
            '5' to "05", '6' to "06", '7' to "07", '8' to "08", '9' to "09",
            'A' to "10", 'B' to "11", 'C' to "12", 'D' to "13", 'E' to "14",
            'F' to "15", 'G' to "16", 'H' to "17", 'I' to "18", 'J' to "19",
            'K' to "20", 'L' to "21", 'M' to "22", 'N' to "23", '&' to "24",
            'O' to "25", 'P' to "26", 'Q' to "27", 'R' to "28", 'S' to "29",
            'T' to "30", 'U' to "31", 'V' to "32", 'W' to "33", 'X' to "34",
            'Y' to "35", 'Z' to "36", ' ' to "37", 'Ñ' to "38"
        )

        val homoclaveTable = mapOf(
            ' ' to "00", '0' to "00", '1' to "01", '2' to "02", '3' to "03",
            '4' to "04", '5' to "05", '6' to "06", '7' to "07", '8' to "08",
            '9' to "09", '&' to "10", 'A' to "11", 'B' to "12", 'C' to "13",
            'D' to "14", 'E' to "15", 'F' to "16", 'G' to "17", 'H' to "18",
            'I' to "19", 'J' to "21", 'K' to "22", 'L' to "23", 'M' to "24",
            'N' to "25", 'O' to "26", 'P' to "27", 'Q' to "28", 'R' to "29",
            'S' to "32", 'T' to "33", 'U' to "34", 'V' to "35", 'W' to "36",
            'X' to "37", 'Y' to "38", 'Z' to "39", 'Ñ' to "40"
        )

        val homoclaveAssignTable = listOf(
            '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D',
            'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R',
            'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        )

        val cacophonic = listOf(
            "BUEI", "BUEY", "CACA", "CACO", "CAGA", "CAGO", "CAKA", "COGE",
            "COJA", "COJE", "COJI", "COJO", "CULO", "FETO", "GUEY", "JOTO",
            "KACA", "KACO", "KAGA", "KAGO", "KOGE", "KOJO", "KAKA", "KULO",
            "MAME", "MAMO", "MEAR", "MEON", "MION", "MOCO", "MULA", "PEDA",
            "PEDO", "PENE", "PUTA", "PUTO", "QULO", "RATA", "RUIN"
        )

        /**
         * Calculates the checksum digit for an RFC without checksum
         */
        @JvmStatic
        fun calculateChecksum(rfcWithoutChecksum: String): Char {
            var rfcStr = rfcWithoutChecksum.uppercase().trim()
            if (rfcStr.length == 11) {
                rfcStr = " $rfcStr"
            }
            if (rfcStr.length != 12) {
                throw RfcException("RFC must be 11 or 12 characters for checksum calculation")
            }

            var sum = 0
            var position = 13

            for (char in rfcStr) {
                val value = checksumTable[char]?.toInt() ?: 0
                sum += value * position
                position--
            }

            val residual = sum % 11

            return when {
                residual == 0 -> '0'
                (11 - residual) == 10 -> 'A'
                else -> (11 - residual).toString()[0]
            }
        }
    }

    /**
     * Validates the RFC with optional strict checksum validation
     */
    @JvmOverloads
    fun validate(strict: Boolean = true): Boolean {
        if (!validateGeneralRegex()) return false
        if (!validateDate()) return false
        if (!validateHomoclave()) return false
        if (strict && !validateChecksum()) return false
        return true
    }

    /**
     * Alias for validate()
     */
    @JvmOverloads
    fun isValid(strict: Boolean = true): Boolean = validate(strict)

    /**
     * Validates the general structure using regex
     */
    fun validateGeneralRegex(): Boolean {
        if (rfc.length != 12 && rfc.length != 13) return false
        return generalRegex.matches(rfc)
    }

    /**
     * Validates the date portion
     */
    fun validateDate(): Boolean {
        if (!validateGeneralRegex()) return false
        val dateStr = if (rfc.length == 13) rfc.substring(4, 10) else rfc.substring(3, 9)
        return DateUtils.isValidDateYYMMDD(dateStr)
    }

    /**
     * Validates the homoclave characters
     */
    fun validateHomoclave(): Boolean {
        if (!validateGeneralRegex()) return false
        val homoclave = rfc.substring(rfc.length - 3, rfc.length - 1)
        return homoclave.all { it in HOMOCLAVE_CHARS }
    }

    /**
     * Validates the checksum digit
     */
    fun validateChecksum(): Boolean {
        if (!validateGeneralRegex()) return false
        if (isGeneric()) return true // Generic RFCs have incorrect checksums
        val calculated = calculateChecksum(rfc.substring(0, rfc.length - 1))
        return calculated == rfc.last()
    }

    /**
     * Checks if RFC is generic (XAXX010101000 or XEXX010101000)
     */
    fun isGeneric(): Boolean = rfc == "XAXX010101000" || rfc == "XEXX010101000"

    /**
     * Checks if RFC belongs to a Persona Física (individual)
     */
    fun isFisica(): Boolean {
        if (!validateGeneralRegex()) throw RfcException("Invalid RFC")
        if (isGeneric()) return false
        return rfc[3].isLetter()
    }

    /**
     * Checks if RFC belongs to a Persona Moral (company)
     */
    fun isMoral(): Boolean {
        if (!validateGeneralRegex()) throw RfcException("Invalid RFC")
        return rfc[3].isDigit()
    }

    /**
     * Detects the type of RFC
     */
    fun detectType(): String {
        if (!validateGeneralRegex()) return "Invalid"
        if (isGeneric()) return "Generic"
        if (isFisica()) return "Persona Física"
        if (isMoral()) return "Persona Moral"
        return "Unknown"
    }
}
