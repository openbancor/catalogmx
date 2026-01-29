package com.openbancor.catalogmx.catalogs.mexico

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.utils.TextUtils

/**
 * Catálogo Giros Mercantiles
 */
object GirosMercantiles : CodeLookup {
    const val SQLITE_TABLE = "mexico_giros_mercantiles"

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

    fun search(query: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(query)
        return ensureLoaded().filter {
            val name = (it["descripcion"] ?: it["nombre"] ?: "").toString()
            TextUtils.normalize(name).contains(normalized)
        }
    }
}

/**
 * Catálogo Hoy No Circula CDMX
 */
object HoyNoCircula {
    const val SQLITE_TABLE = "mexico_hoy_no_circula_cdmx"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        mapOf("holograma" to "00", "dias_restriccion" to "Ninguno", "descripcion" to "Exento"),
        mapOf("holograma" to "0", "dias_restriccion" to "Ninguno", "descripcion" to "Exento"),
        mapOf("holograma" to "1", "dias_restriccion" to "1 sábado al mes", "descripcion" to "Un sábado al mes"),
        mapOf("holograma" to "2", "dias_restriccion" to "1 día + 1 sábado", "descripcion" to "Un día entre semana y un sábado al mes")
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
    fun getByHolograma(holograma: String): Map<String, Any?>? = ensureLoaded().find { it["holograma"] == holograma }
}

/**
 * Catálogo Formatos de Placas por Estado
 */
object PlacasFormatos {
    const val SQLITE_TABLE = "mexico_placas_formatos"

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
    fun getByEstado(estado: String): List<Map<String, Any?>> {
        val normalized = TextUtils.normalize(estado)
        return ensureLoaded().filter {
            val stateName = (it["estado"] ?: "").toString()
            TextUtils.normalize(stateName) == normalized ||
                it["cve_ent"] == estado
        }
    }
}

/**
 * Palabras Cacofónicas (para validación de RFC/CURP)
 */
object PalabrasCacofonicas {
    const val SQLITE_TABLE = "misc_cacophonic_words"

    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null

    private val embeddedData = listOf(
        "BUEI", "BUEY", "CACA", "CACO", "CAGA", "CAGO", "CAKA", "CAKO",
        "COGE", "COGI", "COJA", "COJE", "COJI", "COJO", "COLA", "CULO",
        "FALO", "FETO", "GETA", "GUEI", "GUEY", "JETA", "JOTO", "KACA",
        "KACO", "KAGA", "KAGO", "KAKA", "KAKO", "KOGE", "KOGI", "KOJA",
        "KOJE", "KOJI", "KOJO", "KOLA", "KULO", "LILO", "LOCA", "LOCO",
        "LOKA", "LOKO", "MAME", "MAMO", "MEAR", "MEAS", "MEON", "MIAR",
        "MION", "MOCO", "MOKO", "MULA", "MULO", "NACA", "NACO", "PEDA",
        "PEDO", "PENE", "PIPI", "PITO", "POPO", "PUTA", "PUTO", "QULO",
        "RATA", "ROBA", "ROBE", "ROBO", "RUIN", "SENO", "TETA", "VACA",
        "VAGA", "VAGO", "VAKA", "VUEI", "VUEY", "WUEI", "WUEY"
    ).map { mapOf("palabra" to it) }

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

    fun isCacophonic(word: String): Boolean {
        val upper = word.uppercase()
        return ensureLoaded().any { it["palabra"] == upper }
    }

    fun getWords(): List<String> = ensureLoaded().mapNotNull { it["palabra"] as? String }
}
