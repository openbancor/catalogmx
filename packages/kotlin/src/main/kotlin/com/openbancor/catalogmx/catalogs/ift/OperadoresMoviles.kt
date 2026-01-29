package com.openbancor.catalogmx.catalogs.ift

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo Operadores Móviles IFT
 *
 * Contains mobile network operators in Mexico.
 */
object OperadoresMoviles : CodeLookup {
    const val SQLITE_TABLE = "ift_operadores_moviles"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "ATT", "nombre" to "AT&T México"),
        mapOf("clave" to "TELCEL", "nombre" to "Telcel"),
        mapOf("clave" to "MOVISTAR", "nombre" to "Movistar"),
        mapOf("clave" to "ALTAN", "nombre" to "Altán Redes")
    )

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }
        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) { dataSource = "sqlite"; cachedData = data; return data }
        }
        dataSource = "embedded"; cachedData = embeddedData; return embeddedData
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["codigo"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter {
            val name = (it["nombre"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }
}

/**
 * Catálogo Operadores PNN (Plan Nacional de Numeración)
 */
object OperadoresPNN {
    const val SQLITE_TABLE = "ift_operadores_pnn"

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
    fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["codigo"] == code }
}
