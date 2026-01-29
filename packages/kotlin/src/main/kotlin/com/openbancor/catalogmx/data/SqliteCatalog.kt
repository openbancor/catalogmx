package com.openbancor.catalogmx.data

import java.sql.Connection
import java.sql.ResultSet

/**
 * Base class for catalogs that can read from SQLite database
 *
 * Provides common functionality for loading and querying catalog data
 * from the dynamic SQLite database.
 */
abstract class SqliteCatalog {

    /**
     * The table name in the SQLite database
     */
    abstract val tableName: String

    /**
     * Column mappings from SQLite to the catalog's internal format
     * Maps SQLite column names to output key names
     */
    open val columnMappings: Map<String, String> = emptyMap()

    /**
     * Gets a connection to the SQLite database
     */
    protected fun getConnection(): Connection? = DataUpdater.getConnection()

    /**
     * Loads all records from the table
     */
    protected fun loadAll(): List<Map<String, Any?>> {
        val conn = getConnection() ?: return emptyList()

        return try {
            val stmt = conn.createStatement()
            val rs = stmt.executeQuery("SELECT * FROM $tableName")
            val results = resultSetToList(rs)
            rs.close()
            stmt.close()
            results
        } catch (e: Exception) {
            emptyList()
        }
    }

    /**
     * Loads records matching a WHERE clause
     */
    protected fun loadWhere(whereClause: String, vararg params: Any): List<Map<String, Any?>> {
        val conn = getConnection() ?: return emptyList()

        return try {
            val sql = "SELECT * FROM $tableName WHERE $whereClause"
            val stmt = conn.prepareStatement(sql)

            params.forEachIndexed { index, param ->
                when (param) {
                    is String -> stmt.setString(index + 1, param)
                    is Int -> stmt.setInt(index + 1, param)
                    is Long -> stmt.setLong(index + 1, param)
                    is Double -> stmt.setDouble(index + 1, param)
                    is Boolean -> stmt.setBoolean(index + 1, param)
                    else -> stmt.setObject(index + 1, param)
                }
            }

            val rs = stmt.executeQuery()
            val results = resultSetToList(rs)
            rs.close()
            stmt.close()
            results
        } catch (e: Exception) {
            emptyList()
        }
    }

    /**
     * Loads a single record by primary key
     */
    protected fun loadByKey(keyColumn: String, keyValue: Any): Map<String, Any?>? {
        return loadWhere("$keyColumn = ?", keyValue).firstOrNull()
    }

    /**
     * Searches records using LIKE
     */
    protected fun searchLike(column: String, pattern: String): List<Map<String, Any?>> {
        return loadWhere("$column LIKE ?", "%$pattern%")
    }

    /**
     * Counts records in the table
     */
    protected fun count(): Int {
        val conn = getConnection() ?: return 0

        return try {
            val stmt = conn.createStatement()
            val rs = stmt.executeQuery("SELECT COUNT(*) FROM $tableName")
            val count = if (rs.next()) rs.getInt(1) else 0
            rs.close()
            stmt.close()
            count
        } catch (e: Exception) {
            0
        }
    }

    /**
     * Checks if the table exists in the database
     */
    fun tableExists(): Boolean {
        val conn = getConnection() ?: return false

        return try {
            val stmt = conn.createStatement()
            val rs = stmt.executeQuery(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='$tableName'"
            )
            val exists = rs.next()
            rs.close()
            stmt.close()
            exists
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Gets table schema information
     */
    fun getTableSchema(): List<Map<String, Any?>> {
        val conn = getConnection() ?: return emptyList()

        return try {
            val stmt = conn.createStatement()
            val rs = stmt.executeQuery("PRAGMA table_info($tableName)")
            val schema = mutableListOf<Map<String, Any?>>()

            while (rs.next()) {
                schema.add(
                    mapOf(
                        "cid" to rs.getInt("cid"),
                        "name" to rs.getString("name"),
                        "type" to rs.getString("type"),
                        "notnull" to rs.getBoolean("notnull"),
                        "dflt_value" to rs.getObject("dflt_value"),
                        "pk" to rs.getBoolean("pk")
                    )
                )
            }

            rs.close()
            stmt.close()
            schema
        } catch (e: Exception) {
            emptyList()
        }
    }

    /**
     * Converts a ResultSet to a list of maps
     */
    private fun resultSetToList(rs: ResultSet): List<Map<String, Any?>> {
        val results = mutableListOf<Map<String, Any?>>()
        val metaData = rs.metaData
        val columnCount = metaData.columnCount

        while (rs.next()) {
            val row = mutableMapOf<String, Any?>()

            for (i in 1..columnCount) {
                val columnName = metaData.getColumnName(i)
                val outputKey = columnMappings[columnName] ?: columnName
                row[outputKey] = rs.getObject(i)
            }

            results.add(row)
        }

        return results
    }
}

/**
 * Catalog that combines embedded data with SQLite data
 *
 * Falls back to embedded data if SQLite is not available
 */
abstract class HybridCatalog : SqliteCatalog() {

    /**
     * Embedded data to use as fallback
     */
    abstract val embeddedData: List<Map<String, Any?>>

    /**
     * Cached data (from SQLite or embedded)
     */
    private var cachedData: List<Map<String, Any?>>? = null

    /**
     * Whether data has been loaded from SQLite
     */
    var isFromSqlite: Boolean = false
        private set

    /**
     * Gets all data (from SQLite if available, otherwise embedded)
     */
    fun getData(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        // Try SQLite first
        if (tableExists()) {
            val sqliteData = loadAll()
            if (sqliteData.isNotEmpty()) {
                cachedData = sqliteData
                isFromSqlite = true
                return sqliteData
            }
        }

        // Fall back to embedded
        cachedData = embeddedData
        isFromSqlite = false
        return embeddedData
    }

    /**
     * Refreshes data from SQLite (clears cache)
     */
    fun refresh() {
        cachedData = null
        isFromSqlite = false
    }

    /**
     * Gets data source info
     */
    fun getDataSourceInfo(): Map<String, Any?> {
        getData() // Ensure data is loaded
        return mapOf(
            "source" to if (isFromSqlite) "sqlite" else "embedded",
            "tableName" to tableName,
            "recordCount" to (cachedData?.size ?: 0)
        )
    }
}
