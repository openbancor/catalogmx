package com.openbancor.catalogmx.validators

/**
 * NSS (Número de Seguridad Social) Exception
 */
class NssException(message: String) : Exception(message)

/**
 * NSS (Número de Seguridad Social) Validator
 *
 * NSS is the 11-digit social security number issued by IMSS
 * (Instituto Mexicano del Seguro Social).
 *
 * Structure:
 * - 2 digits: Subdelegation code (IMSS office)
 * - 2 digits: Registration year (last 2 digits)
 * - 2 digits: Birth year (last 2 digits)
 * - 4 digits: Sequential number
 * - 1 digit: Check digit (modified Luhn algorithm)
 *
 * Example: 12345678903
 * - 12: Subdelegation
 * - 34: Registration year (2034 or 1934)
 * - 56: Birth year (2056 or 1956)
 * - 7890: Sequential
 * - 3: Check digit
 */
class NssValidator(nss: String?) {
    val nss: String = nss?.trim() ?: ""

    companion object {
        const val LENGTH = 11

        /**
         * Calculates the check digit for a 10-digit NSS using modified Luhn algorithm
         *
         * Algorithm (modified Luhn):
         * 1. Starting from the right, multiply alternating digits by 2 and 1
         * 2. If the product is > 9, sum its digits
         * 3. Sum all results
         * 4. The check digit is (10 - (sum % 10)) % 10
         */
        @JvmStatic
        fun calculateCheckDigit(nss10: String): Char {
            if (nss10.length != 10) {
                throw NssException("Need exactly 10 digits to calculate check digit")
            }

            if (!nss10.all { it.isDigit() }) {
                throw NssException("NSS must contain only digits")
            }

            // Process digits from right to left
            var total = 0
            val reversed = nss10.reversed()

            for (i in reversed.indices) {
                var n = reversed[i].toString().toInt()

                // Alternate between multiplying by 2 and 1 (starting with 2 for rightmost)
                if (i % 2 == 0) {
                    n *= 2
                    // If result is > 9, sum its digits (e.g., 12 -> 1+2 = 3)
                    if (n > 9) {
                        n = n / 10 + n % 10
                    }
                }

                total += n
            }

            // Calculate check digit
            val checkDigit = (10 - (total % 10)) % 10

            return checkDigit.toString()[0]
        }

        /**
         * Verifies the check digit of an 11-digit NSS
         */
        @JvmStatic
        fun verifyCheckDigit(nss: String): Boolean {
            if (nss.length != LENGTH) return false

            val calculated = calculateCheckDigit(nss.substring(0, 10))
            return calculated == nss[10]
        }

        /**
         * Generates a complete NSS with check digit
         */
        @JvmStatic
        fun generateNSS(
            subdelegation: String,
            registrationYear: String,
            birthYear: String,
            sequential: String
        ): String {
            val sub = subdelegation.padStart(2, '0')
            val regYr = registrationYear.padStart(2, '0')
            val birthYr = birthYear.padStart(2, '0')
            val seq = sequential.padStart(4, '0')

            if (sub.length != 2) {
                throw NssException("Subdelegation must be 2 digits")
            }
            if (regYr.length != 2) {
                throw NssException("Registration year must be 2 digits")
            }
            if (birthYr.length != 2) {
                throw NssException("Birth year must be 2 digits")
            }
            if (seq.length != 4) {
                throw NssException("Sequential must be 4 digits")
            }

            val nss10 = sub + regYr + birthYr + seq
            val checkDigit = calculateCheckDigit(nss10)

            return nss10 + checkDigit
        }
    }

    /**
     * Validates the NSS structure and check digit (throws exception on failure)
     */
    fun validate(): Boolean {
        // Check length
        if (nss.length != LENGTH) {
            throw NssException("NSS length must be $LENGTH digits, got ${nss.length}")
        }

        // Check if all characters are digits
        if (!nss.all { it.isDigit() }) {
            throw NssException("NSS must contain only digits")
        }

        // Validate check digit
        if (!verifyCheckDigit(nss)) {
            throw NssException("Invalid NSS check digit")
        }

        return true
    }

    /**
     * Checks if NSS is valid without raising exceptions
     */
    fun isValid(): Boolean {
        return try {
            validate()
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Extracts the subdelegation code (first 2 digits)
     */
    fun getSubdelegation(): String? {
        if (nss.length >= 2) {
            return nss.substring(0, 2)
        }
        return null
    }

    /**
     * Extracts the registration year (digits 3-4, last 2 digits of year)
     * Note: This is ambiguous - could be 19XX or 20XX
     */
    fun getRegistrationYear(): String? {
        if (nss.length >= 4) {
            return nss.substring(2, 4)
        }
        return null
    }

    /**
     * Extracts the birth year (digits 5-6, last 2 digits of year)
     */
    fun getBirthYear(): String? {
        if (nss.length >= 6) {
            return nss.substring(4, 6)
        }
        return null
    }

    /**
     * Extracts the sequential number (digits 7-10)
     */
    fun getSequential(): String? {
        if (nss.length >= 10) {
            return nss.substring(6, 10)
        }
        return null
    }

    /**
     * Extracts the check digit (digit 11)
     */
    fun getCheckDigit(): Char? {
        if (nss.length == LENGTH) {
            return nss[10]
        }
        return null
    }

    /**
     * Returns all NSS parts as a map
     */
    fun getParts(): Map<String, String?>? {
        if (!isValid()) return null

        return mapOf(
            "subdelegation" to getSubdelegation(),
            "registration_year" to getRegistrationYear(),
            "birth_year" to getBirthYear(),
            "sequential" to getSequential(),
            "check_digit" to getCheckDigit()?.toString(),
            "nss" to nss
        )
    }
}

/**
 * Gets information from an NSS
 */
fun getNSSInfo(nss: String?): Map<String, String?>? {
    return NssValidator(nss).getParts()
}
