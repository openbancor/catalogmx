package com.openbancor.catalogmx.catalogs.base

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.booleanOrNull
import kotlinx.serialization.json.doubleOrNull
import kotlinx.serialization.json.intOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import java.io.File
import java.sql.Connection
import java.sql.DriverManager
import java.sql.ResultSet

/**
 * Base class for all catalogs with lazy loading support.
 *
 * Provides common functionality for loading data from SQLite and JSON files.
 */
object BaseCatalog {
    private val cache = mutableMapOf<String, List<Map<String, Any?>>>()
    private val sqliteCache = mutableMapOf<String, List<Map<String, Any?>>>()

    /** Path to packages/shared-data when running from packages/kotlin. */
    var sharedDataPath: String = "../shared-data"

    /** Path to SQLite database file (optional). */
    var sqlitePath: String? = null

    private var sqliteConnection: Connection? = null
    private val json = Json { ignoreUnknownKeys = true }

    @JvmStatic
    fun getSqliteConnection(): Connection? {
        val path = sqlitePath ?: return null
        sqliteConnection?.let { if (!it.isClosed) return it }
        return try {
            val file = File(path)
            if (!file.exists()) return null
            DriverManager.getConnection("jdbc:sqlite:$path").also { sqliteConnection = it }
        } catch (e: Exception) {
            null
        }
    }

    @JvmStatic
    fun loadFromSqlite(tableName: String): List<Map<String, Any?>> {
        sqliteCache[tableName]?.let { return it }
        val conn = getSqliteConnection() ?: return emptyList()
        return try {
            val stmt = conn.createStatement()
            val rs = stmt.executeQuery("SELECT * FROM $tableName")
            val results = resultSetToList(rs)
            rs.close()
            stmt.close()
            sqliteCache[tableName] = results
            results
        } catch (e: Exception) {
            emptyList()
        }
    }

    @JvmStatic
    fun queryFromSqlite(
        tableName: String,
        whereClause: String,
        vararg params: Any
    ): List<Map<String, Any?>> {
        val conn = getSqliteConnection() ?: return emptyList()
        return try {
            val sql = "SELECT * FROM $tableName WHERE $whereClause"
            val stmt = conn.prepareStatement(sql)
            params.forEachIndexed { index, param -> stmt.setObject(index + 1, param) }
            val rs = stmt.executeQuery()
            val results = resultSetToList(rs)
            rs.close()
            stmt.close()
            results
        } catch (e: Exception) {
            emptyList()
        }
    }

    @JvmStatic
    fun tableExists(tableName: String): Boolean {
        val conn = getSqliteConnection() ?: return false
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

    private fun resultSetToList(rs: ResultSet): List<Map<String, Any?>> {
        val results = mutableListOf<Map<String, Any?>>()
        val metaData = rs.metaData
        val columnCount = metaData.columnCount
        while (rs.next()) {
            val row = mutableMapOf<String, Any?>()
            for (i in 1..columnCount) {
                row[metaData.getColumnName(i)] = rs.getObject(i)
            }
            results.add(row)
        }
        return results
    }

    @JvmStatic
    fun closeSqliteConnection() {
        sqliteConnection?.close()
        sqliteConnection = null
    }

    @JvmStatic
    fun clearSqliteCache() {
        sqliteCache.clear()
    }

    @JvmStatic
    fun loadJsonData(relativePath: String): List<Map<String, Any?>> {
        cache[relativePath]?.let { return it }
        return try {
            val file = File("$sharedDataPath/$relativePath")
            val contents = file.readText()
            val data = json.parseToJsonElement(contents)
            val items = when {
                data is JsonArray -> data.jsonArray.map { it.toMap() }
                data is JsonObject -> {
                    val obj = data.jsonObject
                    if (obj.containsKey("items")) {
                        val itemsData = obj["items"]
                        if (itemsData is JsonArray) {
                            itemsData.jsonArray.map { it.toMap() }
                        } else {
                            listOf(obj.toMap())
                        }
                    } else {
                        listOf(obj.toMap())
                    }
                }
                else -> emptyList()
            }
            cache[relativePath] = items
            items
        } catch (e: Exception) {
            cache[relativePath] = emptyList()
            emptyList()
        }
    }

    @JvmStatic
    fun loadJsonDataSync(relativePath: String): List<Map<String, Any?>> = loadJsonData(relativePath)

    @JvmStatic
    fun clearCache() {
        cache.clear()
    }

    @JvmStatic
    fun clearCacheFor(relativePath: String) {
        cache.remove(relativePath)
    }

    private fun JsonElement.toMap(): Map<String, Any?> = when (this) {
        is JsonObject -> this.jsonObject.entries.associate { (k, v) -> k to v.toKotlinValue() }
        else -> emptyMap()
    }

    /** Preserve JSON's declared primitive type; catalog codes such as "002" are strings. */
    private fun JsonElement.toKotlinValue(): Any? = when (this) {
        is JsonObject -> this.toMap()
        is JsonArray -> this.jsonArray.map { it.toKotlinValue() }
        is JsonNull -> null
        is JsonPrimitive -> when {
            this.isString -> this.content
            this.booleanOrNull != null -> this.booleanOrNull
            this.intOrNull != null -> this.intOrNull
            this.doubleOrNull != null -> this.doubleOrNull
            else -> this.content
        }
        else -> null
    }
}

interface CodeLookup {
    fun getByCode(code: String): Map<String, Any?>?
    fun isValidCode(code: String): Boolean
}

interface NameSearch {
    fun searchByName(query: String): List<Map<String, Any?>>
    fun getByName(name: String): Map<String, Any?>?
}

fun normalizeForSearch(text: String): String = text.lowercase().trim()
