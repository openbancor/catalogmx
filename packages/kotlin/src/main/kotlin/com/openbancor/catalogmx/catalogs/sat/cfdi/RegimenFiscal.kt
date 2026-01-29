package com.openbancor.catalogmx.catalogs.sat.cfdi

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup

/**
 * SAT Regimen Fiscal Catalog (CFDI 4.0)
 *
 * Catalogs for fiscal regime codes used in Mexican tax documents
 */
object RegimenFiscalCatalog : CodeLookup {
    private var data: List<Map<String, Any?>>? = null
    private var byCode: Map<String, Map<String, Any?>>? = null

    // Embedded regimen fiscal data for standalone usage
    private val embeddedData = listOf(
        mapOf("clave" to "601", "descripcion" to "General de Ley Personas Morales", "fisica" to false, "moral" to true),
        mapOf("clave" to "603", "descripcion" to "Personas Morales con Fines no Lucrativos", "fisica" to false, "moral" to true),
        mapOf("clave" to "605", "descripcion" to "Sueldos y Salarios e Ingresos Asimilados a Salarios", "fisica" to true, "moral" to false),
        mapOf("clave" to "606", "descripcion" to "Arrendamiento", "fisica" to true, "moral" to false),
        mapOf("clave" to "607", "descripcion" to "Régimen de Enajenación o Adquisición de Bienes", "fisica" to true, "moral" to false),
        mapOf("clave" to "608", "descripcion" to "Demás ingresos", "fisica" to true, "moral" to false),
        mapOf("clave" to "609", "descripcion" to "Consolidación", "fisica" to false, "moral" to true),
        mapOf("clave" to "610", "descripcion" to "Residentes en el Extranjero sin Establecimiento Permanente en México", "fisica" to true, "moral" to true),
        mapOf("clave" to "611", "descripcion" to "Ingresos por Dividendos (socios y accionistas)", "fisica" to true, "moral" to false),
        mapOf("clave" to "612", "descripcion" to "Personas Físicas con Actividades Empresariales y Profesionales", "fisica" to true, "moral" to false),
        mapOf("clave" to "614", "descripcion" to "Ingresos por intereses", "fisica" to true, "moral" to false),
        mapOf("clave" to "615", "descripcion" to "Régimen de los ingresos por obtención de premios", "fisica" to true, "moral" to false),
        mapOf("clave" to "616", "descripcion" to "Sin obligaciones fiscales", "fisica" to true, "moral" to true),
        mapOf("clave" to "620", "descripcion" to "Sociedades Cooperativas de Producción que optan por diferir sus ingresos", "fisica" to false, "moral" to true),
        mapOf("clave" to "621", "descripcion" to "Incorporación Fiscal", "fisica" to true, "moral" to false),
        mapOf("clave" to "622", "descripcion" to "Actividades Agrícolas, Ganaderas, Silvícolas y Pesqueras", "fisica" to true, "moral" to true),
        mapOf("clave" to "623", "descripcion" to "Opcional para Grupos de Sociedades", "fisica" to false, "moral" to true),
        mapOf("clave" to "624", "descripcion" to "Coordinados", "fisica" to false, "moral" to true),
        mapOf("clave" to "625", "descripcion" to "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas", "fisica" to true, "moral" to false),
        mapOf("clave" to "626", "descripcion" to "Régimen Simplificado de Confianza", "fisica" to true, "moral" to true)
    )

    private fun loadData() {
        if (data != null) return

        // Try to load from shared-data first
        val loadedData = BaseCatalog.loadJsonData("sat/cfdi/regimen_fiscal.json")
        data = if (loadedData.isNotEmpty()) loadedData else embeddedData

        // Build index
        byCode = mutableMapOf<String, Map<String, Any?>>().apply {
            data!!.forEach { regimen ->
                val clave = regimen["clave"] as? String ?: return@forEach
                put(clave, regimen)
            }
        }
    }

    /**
     * Gets all fiscal regimes
     */
    @JvmStatic
    fun getAll(): List<Map<String, Any?>> {
        loadData()
        return data!!.toList()
    }

    /**
     * Gets a fiscal regime by code
     */
    override fun getByCode(code: String): Map<String, Any?>? {
        loadData()
        return byCode!![code]
    }

    /**
     * Alias using SAT terminology
     */
    @JvmStatic
    fun getByClave(clave: String) = getByCode(clave)

    /**
     * Validates if a code exists
     */
    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    /**
     * Gets all fiscal regimes valid for Personas Físicas
     */
    @JvmStatic
    fun getParaPersonasFisicas(): List<Map<String, Any?>> {
        loadData()
        return data!!.filter { it["fisica"] == true }
    }

    /**
     * Gets all fiscal regimes valid for Personas Morales
     */
    @JvmStatic
    fun getParaPersonasMorales(): List<Map<String, Any?>> {
        loadData()
        return data!!.filter { it["moral"] == true }
    }

    /**
     * Checks if a regime is valid for Persona Física
     */
    @JvmStatic
    fun isValidForFisica(code: String): Boolean {
        val regimen = getByCode(code)
        return regimen?.get("fisica") == true
    }

    /**
     * Checks if a regime is valid for Persona Moral
     */
    @JvmStatic
    fun isValidForMoral(code: String): Boolean {
        val regimen = getByCode(code)
        return regimen?.get("moral") == true
    }
}
