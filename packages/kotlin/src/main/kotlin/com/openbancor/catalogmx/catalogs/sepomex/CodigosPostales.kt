package com.openbancor.catalogmx.catalogs.sepomex

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo de Códigos Postales SEPOMEX
 *
 * Provides access to Mexican postal codes with settlement information.
 * Data source: SEPOMEX (Servicio Postal Mexicano)
 *
 * Usage:
 * ```kotlin
 * // Get settlements by postal code
 * val settlements = CodigosPostales.getByCP("01000")
 *
 * // Check if postal code exists
 * val valid = CodigosPostales.isValid("06700")
 *
 * // Get by state
 * val cdmxPostalCodes = CodigosPostales.getByEstado("Ciudad de México")
 *
 * // Search by colonia name
 * val results = CodigosPostales.searchByColonia("Roma")
 * ```
 */
object CodigosPostales {

    const val SQLITE_TABLE = "codigos_postales"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null
    private var indexByCP: Map<String, List<Map<String, Any?>>>? = null
    private var indexByEstado: Map<String, List<Map<String, Any?>>>? = null
    private var indexByMunicipio: Map<String, List<Map<String, Any?>>>? = null

    private fun ensureLoaded() {
        if (cachedData != null) return

        // Try SQLite first
        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            // For postal codes, we don't load all 157K records into memory
            // Instead, we query on demand
            dataSource = "sqlite"
            cachedData = emptyList() // Marker that we're using SQLite
            return
        }

        // No embedded data for postal codes (too large)
        // Must use SQLite
        dataSource = "none"
        cachedData = emptyList()
    }

    /**
     * Reload data from source
     */
    fun reload() {
        cachedData = null
        indexByCP = null
        indexByEstado = null
        indexByMunicipio = null
        dataSource = "none"
    }

    /**
     * Get all settlements for a postal code
     *
     * @param cp The 5-digit postal code
     * @return List of settlements (a CP can have multiple colonias)
     */
    fun getByCP(cp: String): List<Map<String, Any?>> {
        ensureLoaded()

        if (dataSource == "sqlite") {
            return BaseCatalog.queryFromSqlite(
                SQLITE_TABLE,
                "cp = ?",
                cp
            )
        }

        return emptyList()
    }

    /**
     * Check if a postal code exists
     *
     * @param cp The postal code to validate
     * @return true if the postal code exists
     */
    fun isValid(cp: String): Boolean {
        return getByCP(cp).isNotEmpty()
    }

    /**
     * Get all postal codes for a state (accent-insensitive)
     *
     * @param estado State name (e.g., "Ciudad de México", "Jalisco")
     * @return List of postal code records
     */
    fun getByEstado(estado: String): List<Map<String, Any?>> {
        ensureLoaded()

        if (dataSource == "sqlite") {
            // Try exact match first
            var results = BaseCatalog.queryFromSqlite(
                SQLITE_TABLE,
                "estado = ?",
                estado
            )

            // If no results, try normalized search
            if (results.isEmpty()) {
                val normalized = TextUtils.normalize(estado)
                results = BaseCatalog.queryFromSqlite(
                    SQLITE_TABLE,
                    "LOWER(estado) LIKE ?",
                    "%${normalized.lowercase()}%"
                )
            }

            return results
        }

        return emptyList()
    }

    /**
     * Get all postal codes for a municipality (accent-insensitive)
     *
     * @param municipio Municipality name
     * @return List of postal code records
     */
    fun getByMunicipio(municipio: String): List<Map<String, Any?>> {
        ensureLoaded()

        if (dataSource == "sqlite") {
            val results = BaseCatalog.queryFromSqlite(
                SQLITE_TABLE,
                "municipio = ?",
                municipio
            )

            if (results.isEmpty()) {
                val normalized = TextUtils.normalize(municipio)
                return BaseCatalog.queryFromSqlite(
                    SQLITE_TABLE,
                    "LOWER(municipio) LIKE ?",
                    "%${normalized.lowercase()}%"
                )
            }

            return results
        }

        return emptyList()
    }

    /**
     * Search postal codes by colonia/settlement name (accent-insensitive)
     *
     * @param colonia The colonia name to search for
     * @return List of matching postal code records
     */
    fun searchByColonia(colonia: String): List<Map<String, Any?>> {
        ensureLoaded()

        if (dataSource == "sqlite") {
            val normalized = TextUtils.normalize(colonia)
            return BaseCatalog.queryFromSqlite(
                SQLITE_TABLE,
                "LOWER(asentamiento) LIKE ?",
                "%${normalized.lowercase()}%"
            )
        }

        return emptyList()
    }

    /**
     * Get the municipality for a postal code
     *
     * @param cp The postal code
     * @return Municipality name or null if not found
     */
    fun getMunicipio(cp: String): String? {
        val settlements = getByCP(cp)
        return settlements.firstOrNull()?.get("municipio") as? String
    }

    /**
     * Get the state for a postal code
     *
     * @param cp The postal code
     * @return State name or null if not found
     */
    fun getEstado(cp: String): String? {
        val settlements = getByCP(cp)
        return settlements.firstOrNull()?.get("estado") as? String
    }

    /**
     * Get total count of postal codes in the database
     *
     * @return Number of postal code records
     */
    fun count(): Int {
        ensureLoaded()

        if (dataSource == "sqlite") {
            val conn = BaseCatalog.getSqliteConnection() ?: return 0
            return try {
                conn.createStatement().use { stmt ->
                    stmt.executeQuery("SELECT COUNT(*) FROM $SQLITE_TABLE").use { rs ->
                        if (rs.next()) rs.getInt(1) else 0
                    }
                }
            } catch (e: Exception) {
                0
            }
        }

        return 0
    }

    /**
     * Full-text search across all fields (uses FTS if available)
     *
     * @param query Search query
     * @param limit Maximum results to return (default 100)
     * @return List of matching records
     */
    @Suppress("NestedBlockDepth")
    fun search(query: String, limit: Int = 100): List<Map<String, Any?>> {
        ensureLoaded()

        if (dataSource == "sqlite") {
            val conn = BaseCatalog.getSqliteConnection() ?: return emptyList()

            // Try FTS table first
            try {
                val ftsSql = """
                    SELECT cp.* FROM codigos_postales_fts fts
                    JOIN $SQLITE_TABLE cp ON cp.rowid = fts.rowid
                    WHERE codigos_postales_fts MATCH ?
                    LIMIT ?
                """.trimIndent()

                conn.prepareStatement(ftsSql).use { stmt ->
                    stmt.setString(1, query)
                    stmt.setInt(2, limit)
                    stmt.executeQuery().use { rs ->
                        val results = mutableListOf<Map<String, Any?>>()
                        val meta = rs.metaData
                        while (rs.next()) {
                            val row = mutableMapOf<String, Any?>()
                            for (i in 1..meta.columnCount) {
                                row[meta.getColumnName(i)] = rs.getObject(i)
                            }
                            results.add(row)
                        }
                        if (results.isNotEmpty()) return results
                    }
                }
            } catch (_: Exception) {
                // FTS not available, fall back to LIKE
            }

            // Fallback to LIKE search
            val normalized = TextUtils.normalize(query).lowercase()
            val likeSql = """
                SELECT * FROM $SQLITE_TABLE
                WHERE LOWER(asentamiento) LIKE ?
                   OR LOWER(municipio) LIKE ?
                   OR LOWER(ciudad) LIKE ?
                   OR cp LIKE ?
                LIMIT ?
            """.trimIndent()

            return try {
                conn.prepareStatement(likeSql).use { stmt ->
                    val pattern = "%$normalized%"
                    stmt.setString(1, pattern)
                    stmt.setString(2, pattern)
                    stmt.setString(3, pattern)
                    stmt.setString(4, pattern)
                    stmt.setInt(5, limit)
                    stmt.executeQuery().use { rs ->
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
                }
            } catch (_: Exception) {
                emptyList()
            }
        }

        return emptyList()
    }
}
