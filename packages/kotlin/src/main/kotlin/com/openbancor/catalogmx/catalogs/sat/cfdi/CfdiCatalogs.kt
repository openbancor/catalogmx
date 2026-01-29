package com.openbancor.catalogmx.catalogs.sat.cfdi

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup

/**
 * Catálogo c_FormaPago - Formas de pago SAT CFDI 4.0
 */
object FormaPagoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_formapago"

    private val embeddedData = listOf(
        mapOf("clave" to "01", "descripcion" to "Efectivo"),
        mapOf("clave" to "02", "descripcion" to "Cheque nominativo"),
        mapOf("clave" to "03", "descripcion" to "Transferencia electrónica de fondos"),
        mapOf("clave" to "04", "descripcion" to "Tarjeta de crédito"),
        mapOf("clave" to "28", "descripcion" to "Tarjeta de débito"),
        mapOf("clave" to "99", "descripcion" to "Por definir")
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_MetodoPago - Métodos de pago SAT CFDI 4.0
 */
object MetodoPagoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_metodopago"

    private val embeddedData = listOf(
        mapOf("clave" to "PUE", "descripcion" to "Pago en una sola exhibición"),
        mapOf("clave" to "PPD", "descripcion" to "Pago en parcialidades o diferido")
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_UsoCFDI - Uso del CFDI SAT CFDI 4.0
 */
object UsoCfdiCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_usocfdi"

    private val embeddedData = listOf(
        mapOf("clave" to "G01", "descripcion" to "Adquisición de mercancías", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "G02", "descripcion" to "Devoluciones, descuentos o bonificaciones", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "G03", "descripcion" to "Gastos en general", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "I01", "descripcion" to "Construcciones", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "I02", "descripcion" to "Mobiliario y equipo de oficina por inversiones", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "I03", "descripcion" to "Equipo de transporte", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "I04", "descripcion" to "Equipo de cómputo y accesorios", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "P01", "descripcion" to "Por definir", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "S01", "descripcion" to "Sin efectos fiscales", "persona_fisica" to true, "persona_moral" to true),
        mapOf("clave" to "CP01", "descripcion" to "Pagos", "persona_fisica" to true, "persona_moral" to true)
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    fun getParaPersonasFisicas(): List<Map<String, Any?>> =
        ensureLoaded().filter { it["persona_fisica"] == true || it["persona_fisica"] == 1 }

    fun getParaPersonasMorales(): List<Map<String, Any?>> =
        ensureLoaded().filter { it["persona_moral"] == true || it["persona_moral"] == 1 }
}

/**
 * Catálogo c_TipoDeComprobante - Tipos de comprobante SAT CFDI 4.0
 */
object TipoComprobanteCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_tipodecomprobante"

    private val embeddedData = listOf(
        mapOf("clave" to "I", "descripcion" to "Ingreso"),
        mapOf("clave" to "E", "descripcion" to "Egreso"),
        mapOf("clave" to "T", "descripcion" to "Traslado"),
        mapOf("clave" to "N", "descripcion" to "Nómina"),
        mapOf("clave" to "P", "descripcion" to "Pago")
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_Moneda - Monedas SAT CFDI 4.0
 */
object MonedaCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_moneda"

    private val embeddedData = listOf(
        mapOf("clave" to "MXN", "descripcion" to "Peso Mexicano", "decimales" to 2),
        mapOf("clave" to "USD", "descripcion" to "Dólar americano", "decimales" to 2),
        mapOf("clave" to "EUR", "descripcion" to "Euro", "decimales" to 2),
        mapOf("clave" to "XXX", "descripcion" to "Los códigos asignados para las transacciones en que intervenga ninguna moneda", "decimales" to 0)
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_Impuesto - Impuestos SAT CFDI 4.0
 */
object ImpuestoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_impuesto"

    private val embeddedData = listOf(
        mapOf("clave" to "001", "descripcion" to "ISR"),
        mapOf("clave" to "002", "descripcion" to "IVA"),
        mapOf("clave" to "003", "descripcion" to "IEPS")
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_ObjetoImp - Objeto del Impuesto SAT CFDI 4.0
 */
object ObjetoImpCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_objetoimp"

    private val embeddedData = listOf(
        mapOf("clave" to "01", "descripcion" to "No objeto de impuesto"),
        mapOf("clave" to "02", "descripcion" to "Sí objeto de impuesto"),
        mapOf("clave" to "03", "descripcion" to "Sí objeto del impuesto y no obligado al desglose"),
        mapOf("clave" to "04", "descripcion" to "Sí objeto del impuesto y no causa impuesto")
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_Exportacion - Exportación SAT CFDI 4.0
 */
object ExportacionCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_cfdi_4_0_c_exportacion"

    private val embeddedData = listOf(
        mapOf("clave" to "01", "descripcion" to "No aplica"),
        mapOf("clave" to "02", "descripcion" to "Definitiva con clave A1"),
        mapOf("clave" to "03", "descripcion" to "Temporal"),
        mapOf("clave" to "04", "descripcion" to "Definitiva con clave distinta a A1 o cuando no existe enajenación en términos del CFF")
    )

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

        dataSource = "embedded"
        cachedData = embeddedData
        return embeddedData
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["clave"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}
