package com.openbancor.catalogmx.utils

import com.openbancor.catalogmx.validators.ClabeValidator
import kotlin.random.Random

/**
 * CLABE utility functions
 */
object ClabeUtils {
    /**
     * Generates a random CLABE for a given bank code
     */
    @JvmStatic
    @JvmOverloads
    fun generateCLABERandom(
        bankCode: String? = null,
        random: Random = Random.Default
    ): String {
        val bank = bankCode?.padStart(3, '0') ?: (random.nextInt(900) + 1).toString().padStart(3, '0')
        val branch = random.nextInt(1000).toString().padStart(3, '0')
        val account = (random.nextLong(100000000000) + 1).toString().padStart(11, '0')

        return ClabeValidator.generateCLABE(bank, branch, account)
    }
}

/**
 * Generates a random CLABE for a given bank code
 */
fun generateCLABERandom(bankCode: String? = null): String = ClabeUtils.generateCLABERandom(bankCode)
