package com.openbancor.catalogmx.catalogs.cnbv

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup

/**
 * Catálogo Sectores CNBV
 *
 * Contains financial sector classifications from CNBV
 * (Comisión Nacional Bancaria y de Valores)
 */
object CnbvSectores : CodeLookup {
    const val SQLITE_TABLE = "cnbv_sectores"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["codigo"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}
