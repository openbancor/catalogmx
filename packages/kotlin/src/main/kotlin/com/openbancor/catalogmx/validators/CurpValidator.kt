package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.utils.DateUtils
import com.openbancor.catalogmx.utils.TextUtils
import java.time.LocalDate

/**
 * CURP (Clave Única de Registro de Población) Exception
 */
class CurpException(message: String) : Exception(message)

/**
 * CURP (Clave Única de Registro de Población) Validator
 *
 * CURP is Mexico's unique population registry code, issued by RENAPO.
 *
 * Structure (18 characters):
 * - 4 letters from name (like RFC)
 * - 6 digits for birth date (YYMMDD)
 * - 1 letter for gender (H=Male, M=Female)
 * - 2 letters for birth state code
 * - 3 consonants from paterno, materno, nombre
 * - 1 alphanumeric differentiator (assigned by RENAPO)
 * - 1 numeric check digit
 *
 * Example: OEAF771012HMCRGR09
 */
class CurpValidator(curp: String) {
    val curp: String = curp.uppercase().trim()

    companion object {
        private val generalRegex = Regex(
            "^[A-Z][AEIOUX][A-Z]{2}[0-9]{2}[0-1][0-9][0-3][0-9][MH][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z]{2}$"
        )

        const val LENGTH = 18

        val stateCodes = mapOf(
            "AGUASCALIENTES" to "AS", "BAJA CALIFORNIA" to "BC",
            "BAJA CALIFORNIA SUR" to "BS", "CAMPECHE" to "CC",
            "COAHUILA" to "CL", "COLIMA" to "CM", "CHIAPAS" to "CS",
            "CHIHUAHUA" to "CH", "CIUDAD DE MEXICO" to "DF",
            "DISTRITO FEDERAL" to "DF", "CDMX" to "DF", "DURANGO" to "DG",
            "GUANAJUATO" to "GT", "GUERRERO" to "GR", "HIDALGO" to "HG",
            "JALISCO" to "JC", "ESTADO DE MEXICO" to "MC", "MEXICO" to "MC",
            "MICHOACAN" to "MN", "MORELOS" to "MS", "NAYARIT" to "NT",
            "NUEVO LEON" to "NL", "OAXACA" to "OC", "PUEBLA" to "PL",
            "QUERETARO" to "QT", "QUINTANA ROO" to "QR",
            "SAN LUIS POTOSI" to "SP", "SINALOA" to "SL", "SONORA" to "SR",
            "TABASCO" to "TC", "TAMAULIPAS" to "TS", "TLAXCALA" to "TL",
            "VERACRUZ" to "VZ", "YUCATAN" to "YN", "ZACATECAS" to "ZS",
            "NACIDO EN EL EXTRANJERO" to "NE", "EXTRANJERO" to "NE"
        )

        val cacophonic = listOf(
            "BACA", "BAKA", "BUEI", "BUEY", "CACA", "CACO", "CAGA", "CAGO",
            "CAKA", "KAKO", "COGE", "COGI", "COJA", "COJE", "COJI", "COJO",
            "COLA", "CULO", "FALO", "FETO", "GETA", "GUEI", "GUEY", "JETA",
            "JOTO", "KACA", "KACO", "KAGA", "KAGO", "KOGE", "KOGI", "KOJA",
            "KOJE", "KOJI", "KOJO", "KOLA", "KULO", "LILO", "LOCA", "LOCO",
            "LOKA", "LOKO", "MAME", "MAMO", "MEAR", "MEAS", "MEON", "MIAR",
            "MION", "MOCO", "MOKO", "MULA", "MULO", "NACA", "NACO", "PEDA",
            "PEDO", "PENE", "PIPI", "PITO", "POPO", "PUTA", "PUTO", "QULO",
            "RATA", "ROBA", "ROBE", "ROBO", "RUIN", "SENO", "TETA", "VACA",
            "VAGA", "VAGO", "VAKA", "VUEI", "VUEY", "WUEI", "WUEY"
        )
    }

    /**
     * Validates if the CURP is structurally valid (throws exception on failure)
     */
    fun validate(): Boolean {
        if (curp.length != LENGTH) {
            throw CurpException("CURP length must be $LENGTH")
        }
        if (!generalRegex.matches(curp)) {
            throw CurpException("Invalid CURP structure")
        }
        return true
    }

    /**
     * Checks if CURP is valid without raising exceptions
     */
    fun isValid(): Boolean {
        return try {
            validate()
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Validates the check digit
     */
    fun validateCheckDigit(): Boolean {
        if (curp.length != 18) return false

        val curp17 = curp.substring(0, 17)
        val expectedDigit = CurpGenerator.calculateCheckDigit(curp17)
        val actualDigit = curp[17]

        return expectedDigit == actualDigit
    }

    /**
     * Extracts birth date from CURP
     */
    fun getBirthDate(): LocalDate? {
        if (!isValid()) return null
        return DateUtils.parseDateYYMMDD(curp.substring(4, 10))
    }

    /**
     * Extracts gender from CURP
     */
    fun getGender(): String? {
        if (!isValid()) return null
        return if (curp[10] == 'H') "Hombre" else "Mujer"
    }

    /**
     * Extracts state code from CURP
     */
    fun getStateCode(): String? {
        if (!isValid()) return null
        return curp.substring(11, 13)
    }
}

/**
 * CURP Generator
 */
class CurpGenerator(
    val nombre: String,
    val apellidoPaterno: String,
    val apellidoMaterno: String? = null,
    val fechaNacimiento: LocalDate,
    val sexo: String,
    val estado: String? = null
) {
    init {
        require(apellidoPaterno.trim().isNotEmpty()) { "Apellido paterno is required" }
        require(nombre.trim().isNotEmpty()) { "Nombre is required" }
        require(sexo.uppercase() == "H" || sexo.uppercase() == "M") { "Sexo must be H or M" }
    }

    companion object {
        private const val VOWELS = "AEIOU"
        private const val CONSONANTS = "BCDFGHJKLMNPQRSTVWXYZ"

        private val excludedWords = listOf(
            "DE", "LA", "LAS", "MC", "VON", "DEL", "LOS", "Y", "MAC", "VAN", "MI",
            "DA", "DAS", "DER", "DI", "DIE", "DD", "EL", "LE", "LES"
        )

        private val allowedChars = listOf(
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
            'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
        )

        /**
         * Calculates the check digit for a 17-character CURP
         */
        @JvmStatic
        fun calculateCheckDigit(curp17: String): Char {
            if (curp17.length != 17) {
                throw CurpException("CURP must have exactly 17 characters for check digit calculation")
            }

            val dictionary = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

            var suma = 0
            for (i in curp17.indices) {
                val char = curp17[i]
                val charValue = dictionary.indexOf(char).coerceAtLeast(0)
                suma += charValue * (18 - i)
            }

            var digito = 10 - (suma % 10)
            if (digito == 10) {
                digito = 0
            }

            return digito.toString()[0]
        }
    }

    fun generate(): String {
        val letters = generateLetters()
        val date = generateDate()
        val gender = sexo.uppercase()
        val stateCode = getStateCode(estado)
        val consonants = generateConsonants()
        val homoclave = generateHomoclave()

        return letters + date + gender + stateCode + consonants + homoclave
    }

    private fun cleanName(name: String): String {
        if (name.isEmpty()) return ""
        return TextUtils.cleanName(name, excludedWords, allowedChars)
    }

    private val paternoCalculo: String get() = cleanName(apellidoPaterno)
    private val maternoCalculo: String get() = apellidoMaterno?.let { cleanName(it) } ?: ""
    private val nombreCalculo: String get() = cleanName(nombre)

    private val nombreIniciales: String
        get() {
            if (nombreCalculo.isEmpty()) return nombreCalculo

            val words = nombreCalculo.split(' ')
            if (words.size > 1) {
                if (words[0] in listOf("MARIA", "JOSE", "MA", "MA.", "J", "J.")) {
                    return words.drop(1).joinToString(" ")
                }
            }
            return nombreCalculo
        }

    private fun generateLetters(): String {
        val clave = StringBuilder()
        val paterno = paternoCalculo

        if (paterno.isEmpty()) {
            throw CurpException("Apellido paterno cannot be empty")
        }

        // First letter of paterno
        clave.append(paterno[0])

        // First vowel of paterno (after first letter)
        var vowelFound = false
        for (i in 1 until paterno.length) {
            if (paterno[i] in VOWELS) {
                clave.append(paterno[i])
                vowelFound = true
                break
            }
        }
        if (!vowelFound) {
            clave.append('X')
        }

        // First letter of materno (or X if none)
        val materno = maternoCalculo
        if (materno.isNotEmpty()) {
            clave.append(materno[0])
        } else {
            clave.append('X')
        }

        // First letter of nombre
        val nombreInit = nombreIniciales
        if (nombreInit.isEmpty()) {
            throw CurpException("Nombre cannot be empty")
        }
        clave.append(nombreInit[0])

        var result = clave.toString()

        // Check for cacophonic words - replace second character with 'X'
        if (result in CurpValidator.cacophonic) {
            result = "${result[0]}X${result.substring(2)}"
        }

        return result
    }

    private fun generateDate(): String = DateUtils.dateToYYMMDD(fechaNacimiento)

    private fun getStateCode(state: String?): String {
        if (state.isNullOrEmpty()) return "NE"

        val stateUpper = state.uppercase().trim()

        // Try exact match
        if (stateUpper in CurpValidator.stateCodes) {
            return CurpValidator.stateCodes[stateUpper]!!
        }

        // Try partial match
        for ((key, value) in CurpValidator.stateCodes) {
            if (key.contains(stateUpper) || stateUpper.contains(key)) {
                return value
            }
        }

        // If it's already a 2-letter code, return it
        if (stateUpper.length == 2) {
            return stateUpper
        }

        return "NE" // Default to born abroad
    }

    private fun getFirstInternalConsonant(word: String): Char {
        if (word.length <= 1) return 'X'

        for (i in 1 until word.length) {
            if (word[i] in CONSONANTS) {
                return word[i]
            }
        }
        return 'X'
    }

    private fun generateConsonants(): String {
        val consonants = StringBuilder()

        // First internal consonant of paterno
        consonants.append(getFirstInternalConsonant(paternoCalculo))

        // First internal consonant of materno
        val materno = maternoCalculo
        if (materno.isNotEmpty()) {
            consonants.append(getFirstInternalConsonant(materno))
        } else {
            consonants.append('X')
        }

        // First internal consonant of nombre
        consonants.append(getFirstInternalConsonant(nombreIniciales))

        return consonants.toString()
    }

    private fun generateHomoclave(): String {
        // Position 17: Differentiator (assigned by RENAPO, we use default)
        val differentiator = if (fechaNacimiento.year < 2000) '0' else 'A'

        // Position 18: Check digit (calculable)
        val tempCurp = generateLetters() +
            generateDate() +
            sexo.uppercase() +
            getStateCode(estado) +
            generateConsonants() +
            differentiator

        val checkDigit = calculateCheckDigit(tempCurp)

        return "$differentiator$checkDigit"
    }
}
