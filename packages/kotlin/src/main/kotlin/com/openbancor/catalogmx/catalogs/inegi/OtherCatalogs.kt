package com.openbancor.catalogmx.catalogs.inegi

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo Localidades INEGI
 *
 * Contains all Mexican localities (cities, towns, villages).
 * Note: This is a large dataset (~300K records), queries should be targeted.
 */
object InegiLocalidades {
    const val SQLITE_TABLE = "localidades"

    var dataSource: String = "none"
        private set

    fun reload() { dataSource = "none" }

    private fun checkSqlite(): Boolean {
        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            dataSource = "sqlite"
            return true
        }
        return false
    }

    /**
     * Get localities by state and municipality
     */
    fun getByMunicipio(cveEntidad: String, cveMunicipio: String): List<Map<String, Any?>> {
        if (!checkSqlite()) return emptyList()
        return BaseCatalog.queryFromSqlite(
            SQLITE_TABLE,
            "cve_ent = ? AND cve_mun = ?",
            cveEntidad, cveMunicipio
        )
    }

    /**
     * Get locality by full code
     */
    fun getByCode(cveEntidad: String, cveMunicipio: String, cveLocalidad: String): Map<String, Any?>? {
        if (!checkSqlite()) return null
        return BaseCatalog.queryFromSqlite(
            SQLITE_TABLE,
            "cve_ent = ? AND cve_mun = ? AND cve_loc = ?",
            cveEntidad, cveMunicipio, cveLocalidad
        ).firstOrNull()
    }

    /**
     * Search localities by name
     */
    fun search(query: String, limit: Int = 100): List<Map<String, Any?>> {
        if (!checkSqlite()) return emptyList()
        val conn = BaseCatalog.getSqliteConnection() ?: return emptyList()
        return try {
            val normalized = TextUtils.normalize(query).lowercase()
            val sql = "SELECT * FROM $SQLITE_TABLE WHERE LOWER(nom_loc) LIKE ? LIMIT ?"
            conn.prepareStatement(sql).use { stmt ->
                stmt.setString(1, "%$normalized%")
                stmt.setInt(2, limit)
                val rs = stmt.executeQuery()
                val results = mutableListOf<Map<String, Any?>>()
                val meta = rs.metaData
                while (rs.next()) {
                    val row = mutableMapOf<String, Any?>()
                    for (i in 1..meta.columnCount) {
                        row[meta.getColumnName(i)] = rs.getObject(i)
                    }
                    results.add(row)
                }
                results
            }
        } catch (_: Exception) {
            emptyList()
        }
    }

    /**
     * Get count of localities
     */
    fun count(): Int {
        if (!checkSqlite()) return 0
        val conn = BaseCatalog.getSqliteConnection() ?: return 0
        return try {
            conn.createStatement().use { stmt ->
                stmt.executeQuery("SELECT COUNT(*) FROM $SQLITE_TABLE").use { rs ->
                    if (rs.next()) rs.getInt(1) else 0
                }
            }
        } catch (_: Exception) {
            0
        }
    }
}

/**
 * Catálogo SCIAN (Sistema de Clasificación Industrial de América del Norte)
 */
object InegiSCIAN : CodeLookup {
    const val SQLITE_TABLE = "inegi_scian_sectores"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["codigo"] == code || it["clave"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter {
            val name = (it["descripcion"] ?: it["nombre"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }

    /**
     * Get sectors (2-digit codes)
     */
    fun getSectores(): List<Map<String, Any?>> =
        ensureLoaded().filter {
            val code = (it["codigo"] ?: it["clave"] ?: "").toString()
            code.length == 2
        }

    /**
     * Get subsectors (3-digit codes)
     */
    fun getSubsectores(): List<Map<String, Any?>> =
        ensureLoaded().filter {
            val code = (it["codigo"] ?: it["clave"] ?: "").toString()
            code.length == 3
        }
}

/**
 * Catálogo Municipios Completo INEGI (con más detalles)
 */
object InegiMunicipiosCompleto {
    const val SQLITE_TABLE = "inegi_municipios_completo"

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
    fun getByEstado(cveEntidad: String): List<Map<String, Any?>> =
        ensureLoaded().filter { it["cve_ent"] == cveEntidad }
}
