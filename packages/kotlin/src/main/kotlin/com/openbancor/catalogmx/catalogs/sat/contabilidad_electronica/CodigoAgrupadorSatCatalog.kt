@file:Suppress("PackageNaming", "FunctionNaming")

package com.openbancor.catalogmx.catalogs.sat.contabilidad_electronica

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import java.io.File

/**
 * SAT Anexo 24 - Código agrupador de cuentas
 */
object CodigoAgrupadorSatCatalog {
    private const val VERSION_2024 = "2024-01-22"
    private const val VERSION_2026 = "2026-01-13"
    private const val DEFAULT_VERSION = VERSION_2026

    private val versionFiles = mapOf(
        VERSION_2024 to "sat/contabilidad_electronica/codigo_agrupador_2024.json",
        VERSION_2026 to "sat/contabilidad_electronica/codigo_agrupador_2026.json"
    )

    private val versionAliases = mapOf(
        "2024" to VERSION_2024,
        "2026" to VERSION_2026,
        "latest" to DEFAULT_VERSION
    )

    private val sqliteTables = mapOf(
        VERSION_2024 to "sat_contabilidad_electronica_codigo_agrupador_2024",
        VERSION_2026 to "sat_contabilidad_electronica_codigo_agrupador_2026"
    )

    private val json = Json { ignoreUnknownKeys = true }

    private val cache = mutableMapOf<String, List<Map<String, Any?>>>()
    private val byCodigo = mutableMapOf<String, Map<String, Map<String, Any?>>>()

    var dataSource: String = "none"
        private set

    private fun resolveVersion(version: String?): String {
        if (version.isNullOrBlank()) return DEFAULT_VERSION
        val normalized = version.trim().lowercase()
        versionAliases[normalized]?.let { return it }
        if (versionFiles.containsKey(version)) return version
        throw IllegalArgumentException("Versión no soportada: $version")
    }

    private fun loadData(version: String): List<Map<String, Any?>> {
        cache[version]?.let { return it }

        val sqliteTable = sqliteTables[version]
        if (sqliteTable != null && BaseCatalog.tableExists(sqliteTable)) {
            val sqliteData = BaseCatalog.loadFromSqlite(sqliteTable)
            if (sqliteData.isNotEmpty()) {
                dataSource = "sqlite"
                cache[version] = sqliteData
                byCodigo[version] = sqliteData.associateBy { it["codigo"] as String }
                return sqliteData
            }
        }

        val jsonPath = versionFiles[version]!!
        val jsonData = BaseCatalog.loadJsonData(jsonPath)
        if (jsonData.isNotEmpty()) {
            dataSource = "json"
            cache[version] = jsonData
            byCodigo[version] = jsonData.associateBy { it["codigo"] as String }
            return jsonData
        }

        dataSource = "none"
        cache[version] = emptyList()
        byCodigo[version] = emptyMap()
        return emptyList()
    }

    @JvmStatic
    fun reload() {
        cache.clear()
        byCodigo.clear()
        dataSource = "none"
    }

    @JvmStatic
    fun getVersions(): List<String> = versionFiles.keys.toList()

    @JvmStatic
    fun getDefaultVersion(): String = DEFAULT_VERSION

    @JvmStatic
    fun getAll(version: String? = null): List<Map<String, Any?>> {
        val resolved = resolveVersion(version)
        return loadData(resolved)
    }

    @JvmStatic
    fun getByCodigo(codigo: String, version: String? = null): Map<String, Any?>? {
        val resolved = resolveVersion(version)
        loadData(resolved)
        return byCodigo[resolved]?.get(codigo)
    }

    @JvmStatic
    fun isValid(codigo: String, version: String? = null): Boolean =
        getByCodigo(codigo, version) != null

    @JvmStatic
    fun search(query: String, version: String? = null): List<Map<String, Any?>> {
        if (query.isBlank()) return emptyList()
        val resolved = resolveVersion(version)
        val data = loadData(resolved)
        val normalized = query.lowercase()
        return data.filter { (it["nombre"] as? String)?.lowercase()?.contains(normalized) == true }
    }

    @JvmStatic
    fun count(version: String? = null): Int = getAll(version).size

    @JvmStatic
    fun getDiff2024_2026(): Map<String, Any?> {
        val path = "${BaseCatalog.sharedDataPath}/sat/contabilidad_electronica/codigo_agrupador_diff_2024_2026.json"
        val file = File(path)
        val contents = file.readText()
        val element = json.parseToJsonElement(contents)
        return element.toKotlinValue() as? Map<String, Any?> ?: emptyMap()
    }

    private fun JsonElement.toKotlinValue(): Any? {
        return when (this) {
            is JsonObject -> this.jsonObject.entries.associate { (k, v) -> k to v.toKotlinValue() }
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
