@file:Suppress("PackageNaming")

package com.openbancor.catalogmx.catalogs.sat.carta_porte

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo Aeropuertos - SAT Carta Porte 3.0
 */
object CartaPorteAeropuertosCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_aeropuertos"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["codigo_iata"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter {
            val name = (it["nombre"] ?: it["descripcion"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }
}

/**
 * Catálogo Carreteras - SAT Carta Porte 3.0
 */
object CartaPorteCarreterasCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_carreteras"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Configuración Autotransporte - SAT Carta Porte 3.0
 */
object CartaPorteConfigAutotransporteCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_config_autotransporte"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Material Peligroso - SAT Carta Porte 3.0
 */
object CartaPorteMaterialPeligrosoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_material_peligroso"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["clave_material"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter {
            val name = (it["descripcion"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }
}

/**
 * Catálogo Puertos Marítimos - SAT Carta Porte 3.0
 */
object CartaPortePuertosMaritimos : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_puertos_maritimos"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Tipo Embalaje - SAT Carta Porte 3.0
 */
object CartaPorteTipoEmbalajeCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_tipo_embalaje"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Tipo Permiso - SAT Carta Porte 3.0
 */
object CartaPorteTipoPermisoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_carta_porte_3_tipo_permiso"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}
