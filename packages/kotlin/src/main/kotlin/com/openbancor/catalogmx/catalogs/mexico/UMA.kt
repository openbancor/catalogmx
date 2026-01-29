package com.openbancor.catalogmx.catalogs.mexico

import com.openbancor.catalogmx.catalogs.base.BaseCatalog

/**
 * Catálogo UMA (Unidad de Medida y Actualización)
 *
 * The UMA is a reference unit for calculating payment obligations
 * and legal provisions, replacing the minimum wage for these purposes.
 *
 * Usage:
 * ```kotlin
 * // Get current UMA value
 * val uma = UMA.getCurrent()
 * println("UMA diario: ${uma?.get("valor_diario")}")
 *
 * // Get UMA for specific year
 * val uma2024 = UMA.getByYear(2024)
 *
 * // Get historical UMA values
 * val history = UMA.getAll()
 * ```
 */
object UMA {

    const val SQLITE_TABLE = "mexico_uma"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    // Embedded UMA values for recent years
    private val embeddedData = listOf(
        mapOf(
            "año" to 2025,
            "valor_diario" to 113.14,
            "valor_mensual" to 3441.90,
            "valor_anual" to 41302.80,
            "vigencia_inicio" to "2025-02-01",
            "vigencia_fin" to "2026-01-31"
        ),
        mapOf(
            "año" to 2024,
            "valor_diario" to 108.57,
            "valor_mensual" to 3300.53,
            "valor_anual" to 39606.36,
            "vigencia_inicio" to "2024-02-01",
            "vigencia_fin" to "2025-01-31"
        ),
        mapOf(
            "año" to 2023,
            "valor_diario" to 103.74,
            "valor_mensual" to 3153.70,
            "valor_anual" to 37844.40,
            "vigencia_inicio" to "2023-02-01",
            "vigencia_fin" to "2024-01-31"
        )
    )

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    /**
     * Get all UMA records
     */
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    /**
     * Get UMA for a specific year
     *
     * @param year The year (e.g., 2024)
     * @return UMA record or null if not found
     */
    fun getByYear(year: Int): Map<String, Any?>? =
        ensureLoaded().find {
            val recordYear = (it["año"] ?: it["anio"])
            when (recordYear) {
                is Int -> recordYear == year
                is Long -> recordYear.toInt() == year
                is String -> recordYear.toIntOrNull() == year
                else -> false
            }
        }

    /**
     * Get the most recent UMA value
     *
     * @return Most recent UMA record
     */
    fun getCurrent(): Map<String, Any?>? {
        return ensureLoaded()
            .sortedByDescending {
                val year = it["año"] ?: it["anio"]
                when (year) {
                    is Int -> year
                    is Long -> year.toInt()
                    is String -> year.toIntOrNull() ?: 0
                    else -> 0
                }
            }
            .firstOrNull()
    }

    /**
     * Get current daily UMA value
     */
    fun getValorDiario(): Double? {
        val current = getCurrent() ?: return null
        val valor = current["valor_diario"]
        return when (valor) {
            is Double -> valor
            is Float -> valor.toDouble()
            is Int -> valor.toDouble()
            is Long -> valor.toDouble()
            is String -> valor.toDoubleOrNull()
            else -> null
        }
    }

    /**
     * Get current monthly UMA value
     */
    fun getValorMensual(): Double? {
        val current = getCurrent() ?: return null
        val valor = current["valor_mensual"]
        return when (valor) {
            is Double -> valor
            is Float -> valor.toDouble()
            is Int -> valor.toDouble()
            is Long -> valor.toDouble()
            is String -> valor.toDoubleOrNull()
            else -> null
        }
    }

    /**
     * Get current annual UMA value
     */
    fun getValorAnual(): Double? {
        val current = getCurrent() ?: return null
        val valor = current["valor_anual"]
        return when (valor) {
            is Double -> valor
            is Float -> valor.toDouble()
            is Int -> valor.toDouble()
            is Long -> valor.toDouble()
            is String -> valor.toDoubleOrNull()
            else -> null
        }
    }
}

/**
 * Catálogo Salarios Mínimos México
 *
 * Contains Mexican minimum wage values by zone and year.
 *
 * Usage:
 * ```kotlin
 * // Get current minimum wage
 * val sm = SalariosMinimos.getCurrent()
 *
 * // Get for specific year
 * val sm2024 = SalariosMinimos.getByYear(2024)
 * ```
 */
object SalariosMinimos {

    const val SQLITE_TABLE = "mexico_salarios_minimos"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    // Embedded recent minimum wages
    private val embeddedData = listOf(
        mapOf(
            "año" to 2025,
            "zona" to "general",
            "valor_diario" to 278.80,
            "valor_mensual" to 8479.84,
            "vigencia_inicio" to "2025-01-01"
        ),
        mapOf(
            "año" to 2025,
            "zona" to "zlfn",
            "valor_diario" to 419.88,
            "valor_mensual" to 12772.71,
            "vigencia_inicio" to "2025-01-01"
        ),
        mapOf(
            "año" to 2024,
            "zona" to "general",
            "valor_diario" to 248.93,
            "valor_mensual" to 7571.14,
            "vigencia_inicio" to "2024-01-01"
        ),
        mapOf(
            "año" to 2024,
            "zona" to "zlfn",
            "valor_diario" to 374.89,
            "valor_mensual" to 11403.77,
            "vigencia_inicio" to "2024-01-01"
        )
    )

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    /**
     * Get all salary records
     */
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    /**
     * Get salaries for a specific year
     *
     * @param year The year
     * @return List of salary records for that year (may include multiple zones)
     */
    fun getByYear(year: Int): List<Map<String, Any?>> =
        ensureLoaded().filter {
            val recordYear = it["año"] ?: it["anio"]
            when (recordYear) {
                is Int -> recordYear == year
                is Long -> recordYear.toInt() == year
                is String -> recordYear.toIntOrNull() == year
                else -> false
            }
        }

    /**
     * Get current general minimum wage
     *
     * @return Most recent general zone salary record
     */
    fun getCurrent(): Map<String, Any?>? {
        return ensureLoaded()
            .filter { (it["zona"] ?: "general") == "general" }
            .sortedByDescending {
                val year = it["año"] ?: it["anio"]
                when (year) {
                    is Int -> year
                    is Long -> year.toInt()
                    is String -> year.toIntOrNull() ?: 0
                    else -> 0
                }
            }
            .firstOrNull()
    }

    /**
     * Get current ZLFN (Zona Libre de la Frontera Norte) minimum wage
     */
    fun getCurrentZLFN(): Map<String, Any?>? {
        return ensureLoaded()
            .filter { (it["zona"] ?: "") == "zlfn" }
            .sortedByDescending {
                val year = it["año"] ?: it["anio"]
                when (year) {
                    is Int -> year
                    is Long -> year.toInt()
                    is String -> year.toIntOrNull() ?: 0
                    else -> 0
                }
            }
            .firstOrNull()
    }

    /**
     * Get current daily general minimum wage value
     */
    fun getValorDiario(): Double? {
        val current = getCurrent() ?: return null
        val valor = current["valor_diario"]
        return when (valor) {
            is Double -> valor
            is Float -> valor.toDouble()
            is Int -> valor.toDouble()
            is Long -> valor.toDouble()
            is String -> valor.toDoubleOrNull()
            else -> null
        }
    }
}
