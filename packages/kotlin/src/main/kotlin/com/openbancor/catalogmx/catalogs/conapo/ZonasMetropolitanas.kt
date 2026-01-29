package com.openbancor.catalogmx.catalogs.conapo

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo Zonas Metropolitanas CONAPO
 *
 * Contains metropolitan zones defined by CONAPO
 * (Consejo Nacional de Población)
 */
object ZonasMetropolitanas : CodeLookup {
    const val SQLITE_TABLE = "geo_zonas_metropolitanas"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }
        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) { dataSource = "sqlite"; cachedData = data; return data }
        }
        dataSource = "none"; cachedData = emptyList(); return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["cve_zm"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter {
            val name = (it["nombre"] ?: it["nom_zm"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }
}

/**
 * Catálogo Municipios por Zona Metropolitana
 */
object MunicipiosZM {
    const val SQLITE_TABLE = "geo_municipio_zm"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }
        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) { dataSource = "sqlite"; cachedData = data; return data }
        }
        dataSource = "none"; cachedData = emptyList(); return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    fun getByZonaMetropolitana(cveZm: String): List<Map<String, Any?>> =
        ensureLoaded().filter { it["cve_zm"] == cveZm }
}
