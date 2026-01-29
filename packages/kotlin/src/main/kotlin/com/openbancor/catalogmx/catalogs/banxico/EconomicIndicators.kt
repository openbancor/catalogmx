package com.openbancor.catalogmx.catalogs.banxico

import com.openbancor.catalogmx.catalogs.base.BaseCatalog

/**
 * Catálogo TIIE (Tasa de Interés Interbancaria de Equilibrio)
 */
object BanxicoTIIE {
    const val SQLITE_TABLE = "banxico_tiie"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getCurrent(): Map<String, Any?>? = ensureLoaded().maxByOrNull { it["fecha"]?.toString() ?: "" }
    fun getByDate(fecha: String): Map<String, Any?>? = ensureLoaded().find { it["fecha"] == fecha }
}

/**
 * Catálogo Tipo de Cambio USD/MXN
 */
object BanxicoTipoCambio {
    const val SQLITE_TABLE = "banxico_tipo_cambio"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getCurrent(): Map<String, Any?>? = ensureLoaded().maxByOrNull { it["fecha"]?.toString() ?: "" }
    fun getByDate(fecha: String): Map<String, Any?>? = ensureLoaded().find { it["fecha"] == fecha }
}

/**
 * Catálogo UDIs (Unidades de Inversión)
 */
object BanxicoUDIs {
    const val SQLITE_TABLE = "banxico_udis"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getCurrent(): Map<String, Any?>? = ensureLoaded().maxByOrNull { it["fecha"]?.toString() ?: "" }
    fun getByDate(fecha: String): Map<String, Any?>? = ensureLoaded().find { it["fecha"] == fecha }
}

/**
 * Catálogo CETES
 */
object BanxicoCETES {
    const val SQLITE_TABLE = "banxico_cetes"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getCurrent(): Map<String, Any?>? = ensureLoaded().maxByOrNull { it["fecha"]?.toString() ?: "" }
}

/**
 * Catálogo Inflación
 */
object BanxicoInflacion {
    const val SQLITE_TABLE = "banxico_inflacion"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getCurrent(): Map<String, Any?>? = ensureLoaded().maxByOrNull { it["fecha"]?.toString() ?: it["periodo"]?.toString() ?: "" }
}

/**
 * Catálogo Códigos Plaza Banxico
 */
object BanxicoCodigosPlaza {
    const val SQLITE_TABLE = "banxico_codigos_plaza"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["codigo"] == code || it["clave"] == code }
    fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo Instituciones Financieras
 */
object BanxicoInstitucionesFinancieras {
    const val SQLITE_TABLE = "banxico_instituciones_financieras"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["codigo"] == code || it["clave"] == code }
}

/**
 * Catálogo Monedas y Divisas
 */
object BanxicoMonedasDivisas {
    const val SQLITE_TABLE = "banxico_monedas_divisas"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["codigo"] == code || it["clave"] == code }
}

/**
 * Catálogo Salarios Mínimos Banxico (histórico)
 */
object BanxicoSalariosMinimos {
    const val SQLITE_TABLE = "banxico_salarios_minimos"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(SQLITE_TABLE)) {
            val data = BaseCatalog.loadFromSqlite(SQLITE_TABLE)
            if (data.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = data
                return data
            }
        }

        dataSource = "none"
        cachedData = emptyList()
        return emptyList()
    }

    fun reload() { cachedData = null; dataSource = "none" }
    fun getAll(): List<Map<String, Any?>> = ensureLoaded()
    fun getCurrent(): Map<String, Any?>? = ensureLoaded().maxByOrNull { it["fecha"]?.toString() ?: it["vigencia"]?.toString() ?: "" }
}
