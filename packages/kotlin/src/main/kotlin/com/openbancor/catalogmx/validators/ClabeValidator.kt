package com.openbancor.catalogmx.validators

/**
 * CLABE (Clave Bancaria Estandarizada) Exception
 */
class ClabeException(message: String) : Exception(message)

/**
 * CLABE (Clave Bancaria Estandarizada) Validator
 *
 * CLABE is the standardized 18-digit bank account number used in Mexico for
 * interbank electronic transfers (SPEI).
 *
 * Structure:
 * - 3 digits: Bank code
 * - 3 digits: Branch/Plaza code
 * - 11 digits: Account number
 * - 1 digit: Check digit (modulo 10 algorithm)
 *
 * Example: 002010077777777771
 * - 002: Banamex
 * - 010: Branch code
 * - 07777777777: Account number
 * - 1: Check digit
 */
class ClabeValidator(clabe: String?) {
    val clabe: String = clabe?.trim() ?: ""

    companion object {
        const val LENGTH = 18

        /**
         * Weights for check digit calculation (positions 0-16)
         * Pattern repeats: 3,7,1,3,7,1,...
         */
        val weights = listOf(3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7, 1, 3, 7)

        /**
         * Calculates the check digit for a 17-digit CLABE
         *
         * Algorithm:
         * 1. Multiply each digit by its weight (3,7,1 pattern)
         * 2. Take modulo 10 of each result
         * 3. Sum all results
         * 4. Take modulo 10 of the sum
         * 5. Subtract from 10
         * 6. Take modulo 10 of the result
         */
        @JvmStatic
        fun calculateCheckDigit(clabe17: String): Char {
            if (clabe17.length != 17) {
                throw ClabeException("Need exactly 17 digits to calculate check digit")
            }

            if (!clabe17.all { it.isDigit() }) {
                throw ClabeException("CLABE must contain only digits")
            }

            // Calculate weighted sum
            var weightedSum = 0
            for (i in clabe17.indices) {
                val digit = clabe17[i].toString().toInt()
                val product = digit * weights[i]
                weightedSum += product % 10
            }

            // Calculate check digit
            val checkDigit = (10 - (weightedSum % 10)) % 10

            return checkDigit.toString()[0]
        }

        /**
         * Verifies the check digit of an 18-digit CLABE
         */
        @JvmStatic
        fun verifyCheckDigit(clabe: String): Boolean {
            if (clabe.length != LENGTH) return false

            val calculated = calculateCheckDigit(clabe.substring(0, 17))
            return calculated == clabe[17]
        }

        /**
         * Generates a complete CLABE with check digit
         */
        @JvmStatic
        fun generateCLABE(bankCode: String, branchCode: String, accountNumber: String): String {
            val bank = bankCode.padStart(3, '0')
            val branch = branchCode.padStart(3, '0')
            val account = accountNumber.padStart(11, '0')

            if (bank.length != 3) {
                throw ClabeException("Bank code must be 3 digits")
            }
            if (branch.length != 3) {
                throw ClabeException("Branch code must be 3 digits")
            }
            if (account.length != 11) {
                throw ClabeException("Account number must be 11 digits")
            }

            val clabe17 = bank + branch + account
            val checkDigit = calculateCheckDigit(clabe17)

            return clabe17 + checkDigit
        }
    }

    /**
     * Validates the CLABE structure and check digit (throws exception on failure)
     */
    fun validate(): Boolean {
        // Check length
        if (clabe.length != LENGTH) {
            throw ClabeException("CLABE length must be $LENGTH digits, got ${clabe.length}")
        }

        // Check if all characters are digits
        if (!clabe.all { it.isDigit() }) {
            throw ClabeException("CLABE must contain only digits")
        }

        // Validate check digit
        if (!verifyCheckDigit(clabe)) {
            throw ClabeException("Invalid CLABE check digit")
        }

        return true
    }

    /**
     * Checks if CLABE is valid without raising exceptions
     */
    fun isValid(): Boolean {
        return try {
            validate()
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Extracts the bank code (first 3 digits)
     */
    fun getBankCode(): String? {
        if (clabe.length >= 3) {
            return clabe.substring(0, 3)
        }
        return null
    }

    /**
     * Extracts the branch/plaza code (digits 4-6)
     */
    fun getBranchCode(): String? {
        if (clabe.length >= 6) {
            return clabe.substring(3, 6)
        }
        return null
    }

    /**
     * Extracts the account number (digits 7-17)
     */
    fun getAccountNumber(): String? {
        if (clabe.length >= 17) {
            return clabe.substring(6, 17)
        }
        return null
    }

    /**
     * Extracts the check digit (digit 18)
     */
    fun getCheckDigit(): Char? {
        if (clabe.length == LENGTH) {
            return clabe[17]
        }
        return null
    }

    /**
     * Returns all CLABE parts as a map
     */
    fun getParts(): Map<String, String?>? {
        if (!isValid()) return null

        return mapOf(
            "bank_code" to getBankCode(),
            "branch_code" to getBranchCode(),
            "account_number" to getAccountNumber(),
            "check_digit" to getCheckDigit()?.toString(),
            "clabe" to clabe
        )
    }
}

/**
 * Gets information from a CLABE
 */
fun getCLABEInfo(clabe: String?): Map<String, String?>? {
    return ClabeValidator(clabe).getParts()
}
