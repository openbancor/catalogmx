package com.openbancor.catalogmx.catalogs.inegi

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo de Municipios INEGI
 *
 * Contains all Mexican municipalities with their codes and state associations.
 * Data source: INEGI (Instituto Nacional de Estadística y Geografía)
 *
 * Usage:
 * ```kotlin
 * // Get municipality by code
 * val mun = InegiMunicipios.getByCode("001")
 *
 * // Get all municipalities in a state
 * val jalisco = InegiMunicipios.getByEstado("14")
 *
 * // Search by name
 * val results = InegiMunicipios.search("Guadalajara")
 * ```
 */
object InegiMunicipios : CodeLookup {

    const val SQLITE_TABLE = "inegi_municipios"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

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

        // No embedded data for municipalities (too large)
        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find {
            it["clave_municipio"] == code || it["codigo"] == code || it["code"] == code
        }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    /**
     * Get all municipalities in a state
     *
     * @param codigoEstado State code (e.g., "14" for Jalisco)
     * @return List of municipalities in that state
     */
    fun getByEstado(codigoEstado: String): List<Map<String, Any?>> =
        ensureLoaded().filter {
            it["clave_entidad"] == codigoEstado || it["codigo_estado"] == codigoEstado
        }

    /**
     * Search municipalities by name (accent-insensitive)
     *
     * @param query Search term
     * @return List of matching municipalities
     */
    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter { mun ->
            val name = (mun["nombre"] ?: mun["municipio"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }

    /**
     * Get municipality count
     */
    fun count(): Int = ensureLoaded().size
}
