package com.openbancor.catalogmx.catalogs.ift

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo de Códigos LADA (Area Codes) IFT
 *
 * Contains Mexican telephone area codes with location information.
 * Data source: IFT (Instituto Federal de Telecomunicaciones)
 *
 * Usage:
 * ```kotlin
 * // Get location by LADA code
 * val locations = CodigosLada.getByLada("33")  // Guadalajara
 *
 * // Check if LADA is valid
 * val valid = CodigosLada.isValid("55")
 *
 * // Search by city name
 * val results = CodigosLada.searchByCity("Monterrey")
 * ```
 */
object CodigosLada {

    const val SQLITE_TABLE = "ift_codigos_lada"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    // Minimal embedded data for common area codes
    private val embeddedData = listOf(
        mapOf("lada" to "55", "ciudad" to "Ciudad de México", "estado" to "Ciudad de México", "tipo" to "metropolitana"),
        mapOf("lada" to "33", "ciudad" to "Guadalajara", "estado" to "Jalisco", "tipo" to "metropolitana"),
        mapOf("lada" to "81", "ciudad" to "Monterrey", "estado" to "Nuevo León", "tipo" to "metropolitana"),
        mapOf("lada" to "222", "ciudad" to "Puebla", "estado" to "Puebla", "tipo" to "metropolitana"),
        mapOf("lada" to "664", "ciudad" to "Tijuana", "estado" to "Baja California", "tipo" to "metropolitana")
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

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    /**
     * Get locations by LADA code
     *
     * @param lada The area code (e.g., "33", "55", "81")
     * @return List of locations with that area code
     */
    fun getByLada(lada: String): List<Map<String, Any?>> =
        ensureLoaded().filter { it["lada"] == lada }

    /**
     * Check if a LADA code exists
     *
     * @param lada The area code to validate
     * @return true if the LADA exists
     */
    fun isValid(lada: String): Boolean = getByLada(lada).isNotEmpty()

    /**
     * Get the primary city for a LADA code
     *
     * @param lada The area code
     * @return City name or null if not found
     */
    fun getCity(lada: String): String? {
        val locations = getByLada(lada)
        return locations.firstOrNull()?.get("ciudad") as? String
    }

    /**
     * Get the state for a LADA code
     *
     * @param lada The area code
     * @return State name or null if not found
     */
    fun getState(lada: String): String? {
        val locations = getByLada(lada)
        return locations.firstOrNull()?.get("estado") as? String
    }

    /**
     * Search LADA codes by city name (accent-insensitive)
     *
     * @param city The city name to search
     * @return List of matching records
     */
    fun searchByCity(city: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(city)
        return ensureLoaded().filter { record ->
            val cityName = (record["ciudad"] ?: "").toString()
            TextUtils.normalize(cityName).contains(normalized)
        }
    }

    /**
     * Get all LADA codes for a state
     *
     * @param estado State name
     * @return List of LADA records for that state
     */
    fun getByEstado(estado: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(estado)
        return ensureLoaded().filter { record ->
            val stateName = (record["estado"] ?: "").toString()
            TextUtils.normalize(stateName) == normalized ||
                TextUtils.normalize(stateName).contains(normalized)
        }
    }

    /**
     * Get unique LADA codes
     *
     * @return Set of all unique LADA codes
     */
    fun getUniqueLadas(): Set<String> =
        ensureLoaded().mapNotNull { it["lada"] as? String }.toSet()

    /**
     * Get count of LADA records
     */
    fun count(): Int = ensureLoaded().size
}
