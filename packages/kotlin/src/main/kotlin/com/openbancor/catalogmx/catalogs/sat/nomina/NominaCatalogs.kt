package com.openbancor.catalogmx.catalogs.sat.nomina

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup

/** Shared loader for the 13 SAT Nómina 1.2 catalog families. */
abstract class NominaCatalogBase(
    private val sqliteTable: String,
    private val jsonFile: String,
    private val bankShape: Boolean = false
) : CodeLookup {
    var dataSource: String = "none"
        private set

    private var cachedData: List<Map<String, Any?>>? = null
    private val jsonPath: String = "sat/nomina_1.2/$jsonFile"

    private fun normalize(source: Map<String, Any?>): Map<String, Any?> {
        val item = source.toMutableMap()
        val code = (item["code"] ?: item["clave"] ?: item["id"] ?: item["c_banco"])?.toString()
            ?: error("$sqliteTable row has no code")
        item["code"] = code
        item.putIfAbsent("clave", code)

        val text = item["description"] ?: item["descripcion"] ?: item["texto"]
        if (bankShape) {
            val name = item["name"] ?: item["nombre"] ?: text
            if (name != null) {
                item["name"] = name.toString()
                item.putIfAbsent("nombre", name.toString())
            }
            val legal = item["razon_social"] ?: item["full_name"]
            if (legal != null) {
                item["razon_social"] = legal.toString()
                item.putIfAbsent("full_name", legal.toString())
            }
        } else if (text != null) {
            item["description"] = text.toString()
            item.putIfAbsent("descripcion", text.toString())
        }

        if (item.containsKey("vigencia_desde")) {
            val validFrom = item["vigencia_desde"]?.toString()?.takeIf { it.isNotBlank() }
            item.putIfAbsent("valid_from", validFrom)
        }
        if (item.containsKey("vigencia_hasta")) {
            val validTo = item["vigencia_hasta"]?.toString()?.takeIf { it.isNotBlank() }
            item.putIfAbsent("valid_to", validTo)
        }
        return item
    }

    private fun ensureLoaded(): List<Map<String, Any?>> {
        cachedData?.let { return it }

        if (BaseCatalog.sqlitePath != null && BaseCatalog.tableExists(sqliteTable)) {
            val rows = BaseCatalog.loadFromSqlite(sqliteTable).map(::normalize)
            if (rows.isNotEmpty()) {
                dataSource = "sqlite"
                cachedData = rows
                return rows
            }
        }

        val rows = BaseCatalog.loadJsonData(jsonPath).map(::normalize)
        dataSource = if (rows.isNotEmpty()) "json" else "none"
        cachedData = rows
        return rows
    }

    fun reload() {
        cachedData = null
        dataSource = "none"
        BaseCatalog.clearCacheFor(jsonPath)
    }

    fun getAll(): List<Map<String, Any?>> = ensureLoaded()

    override fun getByCode(code: String): Map<String, Any?>? =
        ensureLoaded().find { it["code"] == code }

    override fun isValidCode(code: String): Boolean = getByCode(code) != null
}

object NominaBancoCatalog : NominaCatalogBase("nomina_bancos", "banco.json", bankShape = true) {
    const val SQLITE_TABLE = "nomina_bancos"
}

object NominaOrigenRecursoCatalog : NominaCatalogBase("nomina_origenes_recursos", "origen_recurso.json") {
    const val SQLITE_TABLE = "nomina_origenes_recursos"
}

object NominaPeriodicidadPagoCatalog : NominaCatalogBase("nomina_periodicidades_pagos", "periodicidad_pago.json") {
    const val SQLITE_TABLE = "nomina_periodicidades_pagos"
}

object NominaRiesgoPuestoCatalog : NominaCatalogBase("nomina_riesgos_puestos", "riesgo_puesto.json") {
    const val SQLITE_TABLE = "nomina_riesgos_puestos"
}

object NominaTipoContratoCatalog : NominaCatalogBase("nomina_tipos_contratos", "tipo_contrato.json") {
    const val SQLITE_TABLE = "nomina_tipos_contratos"
}

object NominaTipoDeduccionCatalog : NominaCatalogBase("nomina_tipos_deducciones", "tipo_deduccion.json") {
    const val SQLITE_TABLE = "nomina_tipos_deducciones"
}

object NominaTipoHorasCatalog : NominaCatalogBase("nomina_tipos_horas", "tipo_horas.json") {
    const val SQLITE_TABLE = "nomina_tipos_horas"
}

object NominaTipoIncapacidadCatalog : NominaCatalogBase("nomina_tipos_incapacidades", "tipo_incapacidad.json") {
    const val SQLITE_TABLE = "nomina_tipos_incapacidades"
}

object NominaTipoJornadaCatalog : NominaCatalogBase("nomina_tipos_jornadas", "tipo_jornada.json") {
    const val SQLITE_TABLE = "nomina_tipos_jornadas"
}

object NominaTipoNominaCatalog : NominaCatalogBase("nomina_tipos_nominas", "tipo_nomina.json") {
    const val SQLITE_TABLE = "nomina_tipos_nominas"
}

object NominaTipoOtroPagoCatalog : NominaCatalogBase("nomina_tipos_otros_pagos", "tipo_otro_pago.json") {
    const val SQLITE_TABLE = "nomina_tipos_otros_pagos"
}

object NominaTipoPercepcionCatalog : NominaCatalogBase("nomina_tipos_percepciones", "tipo_percepcion.json") {
    const val SQLITE_TABLE = "nomina_tipos_percepciones"
}

object NominaTipoRegimenCatalog : NominaCatalogBase("nomina_tipos_regimenes", "tipo_regimen.json") {
    const val SQLITE_TABLE = "nomina_tipos_regimenes"
}
