package com.openbancor.catalogmx.validators

import com.openbancor.catalogmx.utils.DateUtils
import com.openbancor.catalogmx.utils.TextUtils
import java.time.LocalDate

/**
 * RFC Generator for Persona Física (Individual)
 */
class RfcGeneratorFisica(
    val nombre: String,
    val apellidoPaterno: String,
    val apellidoMaterno: String,
    val fechaNacimiento: LocalDate
) {
    companion object {
        private val excludedWords = listOf(
            "DE", "LA", "LAS", "MC", "VON", "DEL", "LOS", "Y", "MAC", "VAN", "MI"
        )

        private val allowedChars = listOf(
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
            'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '&'
        )
    }

    fun generate(): String {
        val letters = generateLetters()
        val date = generateDate()
        val homoclave = generateHomoclave()
        val partial = letters + date + homoclave
        val checksum = RfcValidator.calculateChecksum(partial)
        return partial + checksum
    }

    private fun cleanName(name: String): String =
        TextUtils.cleanName(name, excludedWords, allowedChars)

    private fun generateLetters(): String {
        val paternoClean = cleanName(apellidoPaterno)
        val maternoClean = cleanName(apellidoMaterno)
        val nombreClean = cleanName(nombre)

        // Get nombre iniciales (skip JOSE/MARIA if compound)
        var nombreIniciales = nombreClean
        val nombreParts = nombreClean.split(Regex("\\s+")).filter { it.isNotEmpty() }
        if (nombreParts.size > 1) {
            if (nombreParts[0] == "MARIA" || nombreParts[0] == "JOSE") {
                nombreIniciales = nombreParts.drop(1).joinToString(" ")
                if (nombreIniciales.isEmpty()) nombreIniciales = nombreParts[0]
            }
        }

        // Get parts of compound surnames
        val paternoParts = paternoClean.split(Regex("\\s+")).filter { it.isNotEmpty() }
        val maternoParts = maternoClean.split(Regex("\\s+")).filter { it.isNotEmpty() }

        val paternoFirst = paternoParts.firstOrNull() ?: ""
        val nombreSafe = if (nombreIniciales.isNotEmpty()) nombreIniciales else "X"

        // Check if materno originally had prepositions
        val originalMaternoUpper = apellidoMaterno.uppercase().trim()
        val maternoHadPrepositions = originalMaternoUpper.startsWith("DE ") ||
            originalMaternoUpper.startsWith("DEL ") ||
            originalMaternoUpper.startsWith("LA ") ||
            originalMaternoUpper.startsWith("LOS ") ||
            originalMaternoUpper.startsWith("LAS ")

        // Determine effective materno
        var effectiveMaternoFirst = maternoParts.firstOrNull() ?: ""
        if (paternoParts.size >= 2 && (maternoHadPrepositions || effectiveMaternoFirst.isEmpty())) {
            effectiveMaternoFirst = if (paternoParts.size >= 2) paternoParts[1] else ""
        }

        var iniciales = ""

        // Regla 4: Apellido paterno de 1-2 letras
        if (paternoFirst.isNotEmpty() && paternoFirst.length <= 2 && effectiveMaternoFirst.isNotEmpty()) {
            iniciales = if (paternoFirst.isNotEmpty()) paternoFirst[0].toString() else "X"
            iniciales += if (effectiveMaternoFirst.isNotEmpty()) effectiveMaternoFirst[0].toString() else "X"
            iniciales += if (nombreSafe.isNotEmpty()) nombreSafe[0].toString() else "X"
            iniciales += if (nombreSafe.length > 1) nombreSafe[1].toString() else "X"
        }
        // Regla 7: Un solo apellido (sin materno)
        else if (effectiveMaternoFirst.isEmpty()) {
            val apellido = if (paternoFirst.isNotEmpty()) paternoFirst else "X"
            iniciales = if (apellido.isNotEmpty()) apellido[0].toString() else "X"
            iniciales += if (apellido.length > 1) apellido[1].toString() else "X"
            iniciales += if (nombreSafe.isNotEmpty()) nombreSafe[0].toString() else "X"
            iniciales += if (nombreSafe.length > 1) nombreSafe[1].toString() else "X"
        }
        // Regla 1: Formación básica
        else {
            iniciales = if (paternoFirst.isNotEmpty()) paternoFirst[0].toString() else "X"
            val vowel = TextUtils.getFirstVowel(paternoFirst, 1)
            iniciales += vowel?.toString() ?: "X"
            iniciales += if (effectiveMaternoFirst.isNotEmpty()) effectiveMaternoFirst[0].toString() else "X"
            iniciales += if (nombreSafe.isNotEmpty()) nombreSafe[0].toString() else "X"
        }

        // Check for cacophonic words
        if (iniciales in RfcValidator.cacophonic) {
            iniciales = iniciales.dropLast(1) + "X"
        }

        return iniciales
    }

    private fun generateDate(): String = DateUtils.dateToYYMMDD(fechaNacimiento)

    private fun generateHomoclave(): String {
        val fullName = listOf(
            cleanName(apellidoPaterno),
            cleanName(apellidoMaterno),
            cleanName(nombre)
        ).filter { it.isNotEmpty() }.joinToString(" ")

        // Build homoclave string
        val calcStr = StringBuilder("0")
        for (char in fullName) {
            calcStr.append(RfcValidator.homoclaveTable[char] ?: "00")
        }

        val cadena = calcStr.toString()
        var suma = 0
        for (n in 0 until cadena.length - 1) {
            val pair = cadena.substring(n, n + 2).toInt()
            val nextDigit = cadena[n + 1].toString().toInt()
            suma += pair * nextDigit
        }
        suma %= 1000

        val resultado1 = suma / 34
        val resultado2 = suma % 34

        return "${RfcValidator.homoclaveAssignTable[resultado1]}${RfcValidator.homoclaveAssignTable[resultado2]}"
    }
}

/**
 * Number conversion tables for Persona Moral RFC generation
 */
private val numerosTexto = mapOf(
    "0" to "CERO", "1" to "UNO", "2" to "DOS", "3" to "TRES", "4" to "CUATRO",
    "5" to "CINCO", "6" to "SEIS", "7" to "SIETE", "8" to "OCHO", "9" to "NUEVE",
    "10" to "DIEZ", "11" to "ONCE", "12" to "DOCE", "13" to "TRECE", "14" to "CATORCE",
    "15" to "QUINCE", "16" to "DIECISEIS", "17" to "DIECISIETE", "18" to "DIECIOCHO",
    "19" to "DIECINUEVE", "20" to "VEINTE", "21" to "VEINTIUNO", "22" to "VEINTIDOS",
    "23" to "VEINTITRES", "24" to "VEINTICUATRO", "25" to "VEINTICINCO",
    "26" to "VEINTISEIS", "27" to "VEINTISIETE", "28" to "VEINTIOCHO",
    "29" to "VEINTINUEVE", "30" to "TREINTA", "40" to "CUARENTA", "50" to "CINCUENTA",
    "60" to "SESENTA", "70" to "SETENTA", "80" to "OCHENTA", "90" to "NOVENTA",
    "100" to "CIEN", "200" to "DOSCIENTOS", "300" to "TRESCIENTOS",
    "400" to "CUATROCIENTOS", "500" to "QUINIENTOS", "600" to "SEISCIENTOS",
    "700" to "SETECIENTOS", "800" to "OCHOCIENTOS", "900" to "NOVECIENTOS"
)

private val numerosRomanos = mapOf(
    "I" to 1, "II" to 2, "III" to 3, "IV" to 4, "V" to 5, "VI" to 6, "VII" to 7,
    "VIII" to 8, "IX" to 9, "X" to 10, "XI" to 11, "XII" to 12, "XIII" to 13,
    "XIV" to 14, "XV" to 15, "XVI" to 16, "XVII" to 17, "XVIII" to 18, "XIX" to 19,
    "XX" to 20, "XXI" to 21, "XXII" to 22, "XXIII" to 23, "XXIV" to 24, "XXV" to 25,
    "XXVI" to 26, "XXVII" to 27, "XXVIII" to 28, "XXIX" to 29, "XXX" to 30
)

private val specialCharWords = mapOf(
    '@' to "ARROBA", '%' to "PORCIENTO", '#' to "NUMERO", '(' to "ABRE", '/' to "DIAGONAL"
)

private fun convertArabigoATexto(num: Int): String {
    if (num < 0) return num.toString()
    if (numerosTexto.containsKey(num.toString())) {
        return numerosTexto[num.toString()]!!
    }
    if (num == 100000) return "CIEN MIL"

    val parts = mutableListOf<String>()
    var remaining = num

    if (remaining >= 1000) {
        val thousands = remaining / 1000
        if (thousands == 1) {
            parts.add("MIL")
        } else {
            parts.add(convertArabigoATexto(thousands))
            parts.add("MIL")
        }
        remaining %= 1000
    }

    if (remaining >= 100) {
        val hundreds = (remaining / 100) * 100
        numerosTexto[hundreds.toString()]?.let { parts.add(it) }
        remaining %= 100
    }

    if (remaining > 0) {
        if (numerosTexto.containsKey(remaining.toString())) {
            parts.add(numerosTexto[remaining.toString()]!!)
        } else if (remaining >= 30) {
            val tens = (remaining / 10) * 10
            val units = remaining % 10
            numerosTexto[tens.toString()]?.let { parts.add(it) }
            if (units > 0) numerosTexto[units.toString()]?.let { parts.add(it) }
        }
    }

    return if (parts.isNotEmpty()) parts.joinToString(" ") else num.toString()
}

private fun convertirNumeroATexto(numero: String): String {
    val upper = numero.trim().uppercase()
    if (numerosRomanos.containsKey(upper)) {
        return convertArabigoATexto(numerosRomanos[upper]!!)
    }
    val num = upper.toIntOrNull()
    if (num != null && num >= 0) {
        return convertArabigoATexto(num)
    }
    return numero
}

/**
 * RFC Generator for Persona Moral (Company)
 */
class RfcGeneratorMoral(
    val razonSocial: String,
    val fechaConstitucion: LocalDate
) {
    companion object {
        private val excludedWords = listOf(
            "EL", "LA", "DE", "LOS", "LAS", "Y", "DEL", "MI",
            "COMPAÑIA", "COMPAÑÍA", "COMPANIA", "CIA", "CIA.",
            "SOCIEDAD", "SOC", "SOC.",
            "S.A.", "SA", "S.A", "S. A.", "S. A",
            "S.A.B.", "SAB", "S.A.B", "S. A. B.", "S. A. B",
            "S. DE R.L.", "S DE RL", "SRL", "S.R.L.", "S. R. L.",
            "S. EN C.", "S EN C", "S.C.", "SC",
            "S. EN C. POR A.", "S EN C POR A", "S. EN N.C.", "S EN NC",
            "A.C.", "AC", "A. C.", "A. EN P.", "A EN P",
            "S.C.L.", "SCL", "S.N.C.", "SNC", "C.V.", "CV", "C. V.",
            "SA DE CV", "S.A. DE C.V.", "SA DE CV MI", "S.A. DE C.V. MI",
            "S.A.B. DE C.V.", "SAB DE CV", "S.A.B DE C.V",
            "SRL DE CV", "S.R.L. DE C.V.", "SRL DE CV MI", "SRL MI",
            "THE", "OF", "COMPANY", "AND", "CO", "CO.",
            "MC", "VON", "MAC", "VAN", "PARA", "POR", "AL", "E", "EN", "CON", "SUS", "A"
        )

        private val allowedChars = listOf(
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
            'Ñ', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '&'
        )
    }

    fun generate(): String {
        val letters = generateLetters()
        val date = generateDate()
        val homoclave = generateHomoclave()
        val partial = letters + date + homoclave
        val checksum = RfcValidator.calculateChecksum(partial)
        return partial + checksum
    }

    private fun cleanRazonSocial(): String {
        var razon = razonSocial.uppercase().trim()

        // Step 0: Handle special characters
        for ((char, word) in specialCharWords) {
            razon = razon.replace(Regex("(^|\\s)${Regex.escape(char.toString())}(\\s|$)")) { m ->
                "${m.groupValues[1]}$word${m.groupValues[2]}"
            }
        }
        for (char in specialCharWords.keys) {
            razon = razon.replace(char.toString(), "")
        }

        // Step 1: First pass - remove excluded words
        val sortedExcluded = excludedWords.sortedByDescending { it.length }
        for (excluded in sortedExcluded) {
            razon = razon.replace(" $excluded ", " ")
            razon = razon.replace(" $excluded,", " ")
            razon = razon.replace(" $excluded.", " ")
            if (razon.startsWith("$excluded ")) {
                razon = razon.substring(excluded.length + 1)
            }
            if (razon.endsWith(" $excluded")) {
                razon = razon.substring(0, razon.length - excluded.length - 1)
            }
            if (razon.endsWith(",$excluded")) {
                razon = razon.substring(0, razon.length - excluded.length - 1)
            }
        }

        // Step 2: Remove special characters except allowed ones
        val allowedForProcessing = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .ÑÁÉÍÓÚÜñáéíóúü&"
        val sanitized = StringBuilder()
        for (char in razon) {
            if (char in allowedForProcessing) {
                sanitized.append(char)
            } else {
                sanitized.append(' ')
            }
        }
        razon = sanitized.toString()

        // Step 3: Substitute Ñ with X
        razon = razon.replace("Ñ", "X").replace("ñ", "X")

        // Step 4: Handle initials and convert numbers
        val wordsTemp = mutableListOf<String>()
        val isInitial = mutableListOf<Boolean>()

        for (word in razon.split(Regex("\\s+"))) {
            val trimmed = word.trim()
            if (trimmed.isEmpty()) continue

            // Detect initials pattern
            if ('.' in trimmed && trimmed.length <= 15) {
                val parts = trimmed.split('.').filter { it.trim().isNotEmpty() }
                if (parts.isNotEmpty() && parts.all { p ->
                        p.length <= 2 && p.matches(Regex("^[A-Z]+$", RegexOption.IGNORE_CASE))
                    }) {
                    for (part in parts) {
                        wordsTemp.add(part.uppercase())
                        isInitial.add(true)
                    }
                    continue
                }
            }
            // Remove trailing dots from normal words
            val cleanWord = trimmed.replace(Regex("\\.+$"), "")
            if (cleanWord.isNotEmpty()) {
                wordsTemp.add(cleanWord)
                isInitial.add(false)
            }
        }

        // Step 5: Convert numbers to text
        val wordsConverted = mutableListOf<String>()
        val isInitialConverted = mutableListOf<Boolean>()

        for (i in wordsTemp.indices) {
            val word = wordsTemp[i]
            val isInit = isInitial[i]
            if (word.matches(Regex("^\\d+$")) || numerosRomanos.containsKey(word)) {
                wordsConverted.add(convertirNumeroATexto(word))
            } else {
                wordsConverted.add(word)
            }
            isInitialConverted.add(isInit)
        }

        // Step 6: Second pass - Remove excluded words (but keep initials)
        val filteredWords = mutableListOf<String>()
        for (i in wordsConverted.indices) {
            val word = wordsConverted[i].trim().uppercase()
            if (word.isEmpty()) continue
            if (isInitialConverted[i]) {
                filteredWords.add(word)
            } else if (word !in excludedWords) {
                filteredWords.add(word)
            }
        }

        val wordsToUse = if (filteredWords.isEmpty()) {
            wordsConverted.map { it.uppercase() }
        } else {
            filteredWords
        }

        // Step 7: Clean remaining special characters and accents
        val result = StringBuilder()
        for (char in wordsToUse.joinToString(" ")) {
            when {
                char in allowedChars -> result.append(char)
                char == ' ' -> result.append(' ')
                else -> {
                    val decoded = TextUtils.removeDiacritics(char.toString())
                    if (decoded.uppercase()[0] in allowedChars) {
                        result.append(decoded.uppercase())
                    }
                }
            }
        }
        val resultStr = result.toString().trim().uppercase()

        // Step 8: Handle consonant compounds (CH → C, LL → L)
        val wordsFinal = mutableListOf<String>()
        for (word in resultStr.split(Regex("\\s+"))) {
            var processedWord = word
            if (word.startsWith("CH")) {
                processedWord = "C${word.substring(2)}"
            } else if (word.startsWith("LL")) {
                processedWord = "L${word.substring(2)}"
            }
            wordsFinal.add(processedWord)
        }

        return wordsFinal.joinToString(" ")
    }

    private fun generateLetters(): String {
        val cleaned = cleanRazonSocial()
        if (cleaned.isEmpty()) {
            throw RfcException("Company name is empty after cleaning")
        }

        val words = cleaned.split(' ').filter { it.isNotEmpty() }
        if (words.isEmpty()) {
            throw RfcException("No valid words in company name")
        }

        val clave = StringBuilder()

        when {
            words.size == 1 -> {
                // Single word: First 3 letters
                val word = words[0]
                clave.append(if (word.isNotEmpty()) word[0] else 'X')
                clave.append(if (word.length > 1) word[1] else 'X')
                clave.append(if (word.length > 2) word[2] else 'X')
            }
            words.size == 2 -> {
                // Two words: First letter of first word + first two letters of second word
                clave.append(words[0][0])
                val second = words[1]
                clave.append(if (second.isNotEmpty()) second[0] else 'X')
                clave.append(if (second.length > 1) second[1] else 'X')
            }
            else -> {
                // Three or more words: First letter of each of first three words
                clave.append(words[0][0])
                clave.append(words[1][0])
                clave.append(words[2][0])
            }
        }

        var result = clave.toString()

        // Check for cacophonic words
        if (result in RfcValidator.cacophonic) {
            result = "${result.dropLast(1)}X"
        }

        return result
    }

    private fun generateDate(): String = DateUtils.dateToYYMMDD(fechaConstitucion)

    private fun generateHomoclave(): String {
        val fullName = cleanRazonSocial()

        // Build homoclave string
        val calcStr = StringBuilder("0")
        for (char in fullName) {
            calcStr.append(RfcValidator.homoclaveTable[char] ?: "00")
        }

        val cadena = calcStr.toString()
        var suma = 0
        for (n in 0 until cadena.length - 1) {
            val pair = cadena.substring(n, n + 2).toInt()
            val nextDigit = cadena[n + 1].toString().toInt()
            suma += pair * nextDigit
        }
        suma %= 1000

        val resultado1 = suma / 34
        val resultado2 = suma % 34

        return "${RfcValidator.homoclaveAssignTable[resultado1]}${RfcValidator.homoclaveAssignTable[resultado2]}"
    }
}
