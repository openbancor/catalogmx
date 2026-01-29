package com.openbancor.catalogmx.catalogs.base

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import java.io.File

/**
 * Base class for all catalogs with lazy loading support
 *
 * Provides common functionality for loading JSON data from shared-data directory.
 */
object BaseCatalog {
    private val cache = mutableMapOf<String, List<Map<String, Any?>>>()

    /**
     * Path to shared-data directory (relative to package root)
     */
    var sharedDataPath: String = "../../shared-data"

    private val json = Json { ignoreUnknownKeys = true }

    /**
     * Loads JSON data from file path with caching
     */
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

    /**
     * Loads JSON data synchronously with caching (same as loadJsonData in Kotlin)
     */
    @JvmStatic
    fun loadJsonDataSync(relativePath: String): List<Map<String, Any?>> = loadJsonData(relativePath)

    /**
     * Clears all cached data
     */
    @JvmStatic
    fun clearCache() {
        cache.clear()
    }

    /**
     * Clears cache for specific path
     */
    @JvmStatic
    fun clearCacheFor(relativePath: String) {
        cache.remove(relativePath)
    }

    /**
     * Converts a JsonElement to a Kotlin Map
     */
    private fun JsonElement.toMap(): Map<String, Any?> {
        return when (this) {
            is JsonObject -> this.jsonObject.entries.associate { (k, v) -> k to v.toKotlinValue() }
            else -> emptyMap()
        }
    }

    /**
     * Converts a JsonElement to a Kotlin value
     */
    private fun JsonElement.toKotlinValue(): Any? {
        return when (this) {
            is JsonObject -> this.toMap()
            is JsonArray -> this.jsonArray.map { it.toKotlinValue() }
            else -> {
                val str = this.toString().trim('"')
                when {
                    str == "null" -> null
                    str == "true" -> true
                    str == "false" -> false
                    str.toIntOrNull() != null -> str.toInt()
                    str.toDoubleOrNull() != null -> str.toDouble()
                    else -> str
                }
            }
        }
    }
}

/**
 * Interface for catalogs with code-based lookup
 */
interface CodeLookup {
    fun getByCode(code: String): Map<String, Any?>?
    fun isValidCode(code: String): Boolean
}

/**
 * Interface for catalogs with name-based search
 */
interface NameSearch {
    fun searchByName(query: String): List<Map<String, Any?>>
    fun getByName(name: String): Map<String, Any?>?
}

/**
 * Normalizes text for comparison (lowercase, trim)
 */
fun normalizeForSearch(text: String): String = text.lowercase().trim()
