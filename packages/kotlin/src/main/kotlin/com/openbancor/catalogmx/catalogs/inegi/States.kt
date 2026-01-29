package com.openbancor.catalogmx.catalogs.inegi

import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.catalogs.base.NameSearch
import com.openbancor.catalogmx.catalogs.base.normalizeForSearch
import com.openbancor.catalogmx.utils.TextUtils

/**
 * INEGI States Catalog
 *
 * Provides access to Mexican states (entidades federativas) data from INEGI.
 */
object InegiStates : CodeLookup, NameSearch {
    private var data: List<Map<String, Any?>>? = null
    private var byCode: Map<String, Map<String, Any?>>? = null
    private var byClaveInegi: Map<String, Map<String, Any?>>? = null

    // Embedded states data for standalone usage
    private val embeddedStates = listOf(
        mapOf("code" to "AS", "name" to "AGUASCALIENTES", "abbreviation" to "AGS", "clave_inegi" to "01"),
        mapOf("code" to "BC", "name" to "BAJA CALIFORNIA", "abbreviation" to "BC", "clave_inegi" to "02"),
        mapOf("code" to "BS", "name" to "BAJA CALIFORNIA SUR", "abbreviation" to "BCS", "clave_inegi" to "03"),
        mapOf("code" to "CC", "name" to "CAMPECHE", "abbreviation" to "CAMP", "clave_inegi" to "04"),
        mapOf("code" to "CL", "name" to "COAHUILA", "abbreviation" to "COAH", "clave_inegi" to "05"),
        mapOf("code" to "CM", "name" to "COLIMA", "abbreviation" to "COL", "clave_inegi" to "06"),
        mapOf("code" to "CS", "name" to "CHIAPAS", "abbreviation" to "CHIS", "clave_inegi" to "07"),
        mapOf("code" to "CH", "name" to "CHIHUAHUA", "abbreviation" to "CHIH", "clave_inegi" to "08"),
        mapOf("code" to "DF", "name" to "CIUDAD DE MEXICO", "abbreviation" to "CDMX", "clave_inegi" to "09"),
        mapOf("code" to "DG", "name" to "DURANGO", "abbreviation" to "DGO", "clave_inegi" to "10"),
        mapOf("code" to "GT", "name" to "GUANAJUATO", "abbreviation" to "GTO", "clave_inegi" to "11"),
        mapOf("code" to "GR", "name" to "GUERRERO", "abbreviation" to "GRO", "clave_inegi" to "12"),
        mapOf("code" to "HG", "name" to "HIDALGO", "abbreviation" to "HGO", "clave_inegi" to "13"),
        mapOf("code" to "JC", "name" to "JALISCO", "abbreviation" to "JAL", "clave_inegi" to "14"),
        mapOf("code" to "MC", "name" to "ESTADO DE MEXICO", "abbreviation" to "MEX", "clave_inegi" to "15"),
        mapOf("code" to "MN", "name" to "MICHOACAN", "abbreviation" to "MICH", "clave_inegi" to "16"),
        mapOf("code" to "MS", "name" to "MORELOS", "abbreviation" to "MOR", "clave_inegi" to "17"),
        mapOf("code" to "NT", "name" to "NAYARIT", "abbreviation" to "NAY", "clave_inegi" to "18"),
        mapOf("code" to "NL", "name" to "NUEVO LEON", "abbreviation" to "NL", "clave_inegi" to "19"),
        mapOf("code" to "OC", "name" to "OAXACA", "abbreviation" to "OAX", "clave_inegi" to "20"),
        mapOf("code" to "PL", "name" to "PUEBLA", "abbreviation" to "PUE", "clave_inegi" to "21"),
        mapOf("code" to "QT", "name" to "QUERETARO", "abbreviation" to "QRO", "clave_inegi" to "22"),
        mapOf("code" to "QR", "name" to "QUINTANA ROO", "abbreviation" to "QROO", "clave_inegi" to "23"),
        mapOf("code" to "SP", "name" to "SAN LUIS POTOSI", "abbreviation" to "SLP", "clave_inegi" to "24"),
        mapOf("code" to "SL", "name" to "SINALOA", "abbreviation" to "SIN", "clave_inegi" to "25"),
        mapOf("code" to "SR", "name" to "SONORA", "abbreviation" to "SON", "clave_inegi" to "26"),
        mapOf("code" to "TC", "name" to "TABASCO", "abbreviation" to "TAB", "clave_inegi" to "27"),
        mapOf("code" to "TS", "name" to "TAMAULIPAS", "abbreviation" to "TAMPS", "clave_inegi" to "28"),
        mapOf("code" to "TL", "name" to "TLAXCALA", "abbreviation" to "TLAX", "clave_inegi" to "29"),
        mapOf("code" to "VZ", "name" to "VERACRUZ", "abbreviation" to "VER", "clave_inegi" to "30"),
        mapOf("code" to "YN", "name" to "YUCATAN", "abbreviation" to "YUC", "clave_inegi" to "31"),
        mapOf("code" to "ZS", "name" to "ZACATECAS", "abbreviation" to "ZAC", "clave_inegi" to "32"),
        mapOf("code" to "NE", "name" to "NACIDO EN EL EXTRANJERO", "abbreviation" to "EXT", "clave_inegi" to "99")
    )

    private fun loadData() {
        if (data != null) return

        // Use embedded data for standalone usage
        data = embeddedStates

        // Build lookup maps
        byCode = mutableMapOf<String, Map<String, Any?>>().apply {
            data!!.forEach { state ->
                val code = state["code"] as? String ?: return@forEach
                put(code, state)
            }
        }

        byClaveInegi = mutableMapOf<String, Map<String, Any?>>().apply {
            data!!.forEach { state ->
                val clave = state["clave_inegi"] as? String ?: return@forEach
                put(clave, state)
            }
        }
    }

    /**
     * Gets all states
     */
    @JvmStatic
    fun getAll(): List<Map<String, Any?>> {
        loadData()
        return data!!.toList()
    }

    /**
     * Gets a state by CURP/RFC code (2 letters)
     */
    override fun getByCode(code: String): Map<String, Any?>? {
        loadData()
        return byCode!![code.uppercase()]
    }

    /**
     * Gets a state by INEGI clave (2 digits)
     */
    @JvmStatic
    fun getByClaveInegi(clave: String): Map<String, Any?>? {
        loadData()
        return byClaveInegi!![clave]
    }

    /**
     * Gets a state by name (case insensitive)
     */
    override fun getByName(name: String): Map<String, Any?>? {
        loadData()
        val normalized = TextUtils.normalizeText(name)
        return data!!.firstOrNull {
            TextUtils.normalizeText(it["name"] as? String ?: "") == normalized
        }
    }

    /**
     * Validates if a code exists
     */
    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    /**
     * Searches states by partial name match
     */
    override fun searchByName(query: String): List<Map<String, Any?>> {
        loadData()
        val normalized = normalizeForSearch(query)
        return data!!.filter {
            normalizeForSearch(it["name"] as? String ?: "").contains(normalized)
        }
    }

    /**
     * Alias for getAll()
     */
    @JvmStatic
    fun getAllStates() = getAll()
}
