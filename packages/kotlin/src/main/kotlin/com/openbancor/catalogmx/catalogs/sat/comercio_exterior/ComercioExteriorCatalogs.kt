package com.openbancor.catalogmx.catalogs.sat.comercio_exterior

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup

/**
 * Catálogo Claves Pedimento - SAT Comercio Exterior
 */
object ComercioExteriorClavesPedimentoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_claves_pedimento"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["code"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Estados USA/Canada - SAT Comercio Exterior
 */
object ComercioExteriorEstadosCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_estados_usa_canada"

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
    fun getByCountry(country: String): List<Map<String, Any?>> = ensureLoaded().filter { it["pais"] == country }
}

/**
 * Catálogo Incoterms - SAT Comercio Exterior
 */
object ComercioExteriorIncotermsCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_incoterms"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "CFR", "descripcion" to "Costo y Flete (puerto de destino convenido)"),
        mapOf("clave" to "CIF", "descripcion" to "Costo, Seguro y Flete (puerto de destino convenido)"),
        mapOf("clave" to "CPT", "descripcion" to "Transporte Pagado Hasta (lugar de destino convenido)"),
        mapOf("clave" to "CIP", "descripcion" to "Transporte y Seguro Pagados hasta (lugar de destino convenido)"),
        mapOf("clave" to "DAP", "descripcion" to "Entregado en Lugar (lugar de destino convenido)"),
        mapOf("clave" to "DPU", "descripcion" to "Entregado en Lugar Descargado"),
        mapOf("clave" to "DDP", "descripcion" to "Entregado Derechos Pagados (lugar de destino convenido)"),
        mapOf("clave" to "EXW", "descripcion" to "En Fábrica (lugar convenido)"),
        mapOf("clave" to "FAS", "descripcion" to "Franco al Costado del Buque (puerto de carga convenido)"),
        mapOf("clave" to "FCA", "descripcion" to "Franco Transportista (lugar convenido)"),
        mapOf("clave" to "FOB", "descripcion" to "Franco a Bordo (puerto de carga convenido)")
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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["code"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Monedas - SAT Comercio Exterior
 */
object ComercioExteriorMonedasCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_monedas"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["code"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Motivos Traslado - SAT Comercio Exterior
 */
object ComercioExteriorMotivosTrasladoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_motivos_traslado"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["code"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Países - SAT Comercio Exterior
 */
object ComercioExteriorPaisesCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_paises"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["c_pais"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Registro Identificación Tributaria - SAT Comercio Exterior
 */
object ComercioExteriorRegistroIdentTribCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_registro_ident_trib"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["code"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Unidades Aduana - SAT Comercio Exterior
 */
object ComercioExteriorUnidadesAduanaCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_comercio_exterior_unidades_aduana"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["clave_unidad_aduana"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}
