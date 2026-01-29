package com.openbancor.catalogmx.catalogs.sat.nomina

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup

/**
 * Catálogo c_Banco - Bancos SAT Nómina 1.2
 */
object NominaBancoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_banco"

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
    override fun getByCode(code: String): Map<String, Any?>? = ensureLoaded().find { it["clave"] == code || it["c_banco"] == code }
    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

/**
 * Catálogo c_PeriodicidadPago - Periodicidad de Pago SAT Nómina 1.2
 */
object NominaPeriodicidadPagoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_periodicidad_pago"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "01", "descripcion" to "Diario"),
        mapOf("clave" to "02", "descripcion" to "Semanal"),
        mapOf("clave" to "03", "descripcion" to "Catorcenal"),
        mapOf("clave" to "04", "descripcion" to "Quincenal"),
        mapOf("clave" to "05", "descripcion" to "Mensual"),
        mapOf("clave" to "06", "descripcion" to "Bimestral"),
        mapOf("clave" to "07", "descripcion" to "Unidad obra"),
        mapOf("clave" to "08", "descripcion" to "Comisión"),
        mapOf("clave" to "09", "descripcion" to "Precio alzado"),
        mapOf("clave" to "10", "descripcion" to "Decenal"),
        mapOf("clave" to "99", "descripcion" to "Otra Periodicidad")
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
 * Catálogo c_RiesgoPuesto - Riesgo del Puesto SAT Nómina 1.2
 */
object NominaRiesgoPuestoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_riesgo_puesto"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "1", "descripcion" to "Clase I"),
        mapOf("clave" to "2", "descripcion" to "Clase II"),
        mapOf("clave" to "3", "descripcion" to "Clase III"),
        mapOf("clave" to "4", "descripcion" to "Clase IV"),
        mapOf("clave" to "5", "descripcion" to "Clase V"),
        mapOf("clave" to "99", "descripcion" to "No aplica")
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
 * Catálogo c_TipoContrato - Tipo de Contrato SAT Nómina 1.2
 */
object NominaTipoContratoCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_tipo_contrato"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "01", "descripcion" to "Contrato de trabajo por tiempo indeterminado"),
        mapOf("clave" to "02", "descripcion" to "Contrato de trabajo para obra determinada"),
        mapOf("clave" to "03", "descripcion" to "Contrato de trabajo por tiempo determinado"),
        mapOf("clave" to "04", "descripcion" to "Contrato de trabajo por temporada"),
        mapOf("clave" to "05", "descripcion" to "Contrato de trabajo sujeto a prueba"),
        mapOf("clave" to "06", "descripcion" to "Contrato de trabajo con capacitación inicial"),
        mapOf("clave" to "07", "descripcion" to "Modalidad de contratación por pago de hora laborada"),
        mapOf("clave" to "08", "descripcion" to "Modalidad de trabajo por comisión laboral"),
        mapOf("clave" to "09", "descripcion" to "Modalidades de contratación donde no existe relación de trabajo"),
        mapOf("clave" to "10", "descripcion" to "Jubilación, pensión, retiro"),
        mapOf("clave" to "99", "descripcion" to "Otro contrato")
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
 * Catálogo c_TipoJornada - Tipo de Jornada SAT Nómina 1.2
 */
object NominaTipoJornadaCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_tipo_jornada"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "01", "descripcion" to "Diurna"),
        mapOf("clave" to "02", "descripcion" to "Nocturna"),
        mapOf("clave" to "03", "descripcion" to "Mixta"),
        mapOf("clave" to "04", "descripcion" to "Por hora"),
        mapOf("clave" to "05", "descripcion" to "Reducida"),
        mapOf("clave" to "06", "descripcion" to "Continuada"),
        mapOf("clave" to "07", "descripcion" to "Partida"),
        mapOf("clave" to "08", "descripcion" to "Por turnos"),
        mapOf("clave" to "99", "descripcion" to "Otra Jornada")
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
 * Catálogo c_TipoNomina - Tipo de Nómina SAT Nómina 1.2
 */
object NominaTipoNominaCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_tipo_nomina"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "O", "descripcion" to "Nómina ordinaria"),
        mapOf("clave" to "E", "descripcion" to "Nómina extraordinaria")
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
 * Catálogo c_TipoRegimen - Tipo de Régimen SAT Nómina 1.2
 */
object NominaTipoRegimenCatalog : CodeLookup {
    const val SQLITE_TABLE = "sat_nomina_1_2_tipo_regimen"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("clave" to "02", "descripcion" to "Sueldos"),
        mapOf("clave" to "03", "descripcion" to "Jubilados"),
        mapOf("clave" to "04", "descripcion" to "Pensionados"),
        mapOf("clave" to "05", "descripcion" to "Asimilados Miembros Sociedades Cooperativas Produccion"),
        mapOf("clave" to "06", "descripcion" to "Asimilados Integrantes Sociedades Asociaciones Civiles"),
        mapOf("clave" to "07", "descripcion" to "Asimilados Miembros consejos"),
        mapOf("clave" to "08", "descripcion" to "Asimilados comisionistas"),
        mapOf("clave" to "09", "descripcion" to "Asimilados Honorarios"),
        mapOf("clave" to "10", "descripcion" to "Asimilados acciones"),
        mapOf("clave" to "11", "descripcion" to "Asimilados otros"),
        mapOf("clave" to "12", "descripcion" to "Jubilados o Pensionados"),
        mapOf("clave" to "13", "descripcion" to "Indemnización o Separación"),
        mapOf("clave" to "99", "descripcion" to "Otro Regimen")
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
