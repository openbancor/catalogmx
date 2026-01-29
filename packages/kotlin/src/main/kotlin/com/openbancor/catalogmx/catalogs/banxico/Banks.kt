package com.openbancor.catalogmx.catalogs.banxico

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.base.CodeLookup
import com.openbancor.catalogmx.catalogs.base.NameSearch
import com.openbancor.catalogmx.catalogs.base.normalizeForSearch

/**
 * Bank data class
 */
data class Bank(
    val code: String,
    val name: String,
    val fullName: String? = null,
    val rfc: String? = null,
    val spei: Boolean = false
) {
    companion object {
        @JvmStatic
        fun fromMap(map: Map<String, Any?>): Bank = Bank(
            code = map["code"] as? String ?: "",
            name = map["name"] as? String ?: "",
            fullName = map["full_name"] as? String,
            rfc = map["rfc"] as? String,
            spei = map["spei"] as? Boolean ?: false
        )
    }

    fun toMap(): Map<String, Any?> = buildMap {
        put("code", code)
        put("name", name)
        fullName?.let { put("full_name", it) }
        rfc?.let { put("rfc", it) }
        put("spei", spei)
    }
}

/**
 * Banxico Banks Catalog
 *
 * Catalog of Mexican banks from Banco de México
 */
object BanxicoBanks : CodeLookup, NameSearch {
    private var data: List<Map<String, Any?>>? = null
    private var byCode: Map<String, Map<String, Any?>>? = null
    private var byName: Map<String, Map<String, Any?>>? = null

    // Embedded common banks for standalone usage
    private val embeddedBanks = listOf(
        mapOf("code" to "002", "name" to "BANAMEX", "full_name" to "Banco Nacional de México", "spei" to true),
        mapOf("code" to "012", "name" to "BBVA MEXICO", "full_name" to "BBVA México", "spei" to true),
        mapOf("code" to "014", "name" to "SANTANDER", "full_name" to "Banco Santander", "spei" to true),
        mapOf("code" to "021", "name" to "HSBC", "full_name" to "HSBC México", "spei" to true),
        mapOf("code" to "036", "name" to "INBURSA", "full_name" to "Banco Inbursa", "spei" to true),
        mapOf("code" to "044", "name" to "SCOTIABANK", "full_name" to "Scotiabank", "spei" to true),
        mapOf("code" to "058", "name" to "BANREGIO", "full_name" to "Banco Regional de Monterrey", "spei" to true),
        mapOf("code" to "072", "name" to "BANORTE", "full_name" to "Banco Mercantil del Norte", "spei" to true),
        mapOf("code" to "127", "name" to "AZTECA", "full_name" to "Banco Azteca", "spei" to true),
        mapOf("code" to "128", "name" to "AUTOFIN", "full_name" to "Banco Autofin México", "spei" to true),
        mapOf("code" to "129", "name" to "BARCLAYS", "full_name" to "Barclays Bank México", "spei" to true),
        mapOf("code" to "130", "name" to "COMPARTAMOS", "full_name" to "Banco Compartamos", "spei" to true),
        mapOf("code" to "131", "name" to "BANCO FAMSA", "full_name" to "Banco Ahorro Famsa", "spei" to true),
        mapOf("code" to "132", "name" to "BMULTIVA", "full_name" to "Banco Multiva", "spei" to true),
        mapOf("code" to "133", "name" to "ACTINVER", "full_name" to "Banco Actinver", "spei" to true),
        mapOf("code" to "134", "name" to "MIFEL", "full_name" to "Banca Mifel", "spei" to true),
        mapOf("code" to "135", "name" to "NAFIN", "full_name" to "Nacional Financiera", "spei" to true),
        mapOf("code" to "136", "name" to "INTERCAM BANCO", "full_name" to "Intercam Banco", "spei" to true),
        mapOf("code" to "137", "name" to "BANCOPPEL", "full_name" to "BanCoppel", "spei" to true),
        mapOf("code" to "138", "name" to "ABC CAPITAL", "full_name" to "ABC Capital", "spei" to true),
        mapOf("code" to "646", "name" to "STP", "full_name" to "Sistema de Transferencias y Pagos STP", "spei" to true),
        mapOf("code" to "659", "name" to "UNAGRA", "full_name" to "Unagra", "spei" to true),
        mapOf("code" to "901", "name" to "CLS", "full_name" to "CLS Bank International", "spei" to false),
        mapOf("code" to "902", "name" to "INDEVAL", "full_name" to "SD Indeval", "spei" to false)
    )

    private fun loadData() {
        if (data != null) return

        // Try to load from shared-data first
        val loadedData = BaseCatalog.loadJsonData("banxico/banks.json")
        data = if (loadedData.isNotEmpty()) loadedData else embeddedBanks

        // Build indices
        byCode = mutableMapOf<String, Map<String, Any?>>().apply {
            data!!.forEach { bank ->
                val code = bank["code"] as? String ?: return@forEach
                put(code, bank)
            }
        }

        byName = mutableMapOf<String, Map<String, Any?>>().apply {
            data!!.forEach { bank ->
                val name = (bank["name"] as? String ?: "").uppercase()
                put(name, bank)
            }
        }
    }

    /**
     * Gets all banks
     */
    @JvmStatic
    fun getAll(): List<Map<String, Any?>> {
        loadData()
        return data!!.toList()
    }

    /**
     * Gets all banks as Bank objects
     */
    @JvmStatic
    fun getAllBanks(): List<Bank> {
        loadData()
        return data!!.map { Bank.fromMap(it) }
    }

    /**
     * Gets a bank by code (CLABE bank code)
     */
    override fun getByCode(code: String): Map<String, Any?>? {
        loadData()
        val paddedCode = code.padStart(3, '0')
        return byCode!![paddedCode]
    }

    /**
     * Gets a Bank object by code
     */
    @JvmStatic
    fun getBankByCode(code: String): Bank? {
        val data = getByCode(code) ?: return null
        return Bank.fromMap(data)
    }

    /**
     * Gets a bank by name (case-insensitive)
     */
    override fun getByName(name: String): Map<String, Any?>? {
        loadData()
        val normalized = name.uppercase()
        return byName!![normalized]
    }

    /**
     * Gets a Bank object by name
     */
    @JvmStatic
    fun getBankByName(name: String): Bank? {
        val data = getByName(name) ?: return null
        return Bank.fromMap(data)
    }

    /**
     * Searches banks by keyword (name or code)
     */
    override fun searchByName(query: String): List<Map<String, Any?>> {
        loadData()
        val q = query.uppercase()
        return data!!.filter { b ->
            val name = (b["name"] as? String ?: "").uppercase()
            val fullName = (b["full_name"] as? String ?: "").uppercase()
            val code = b["code"] as? String ?: ""
            name.contains(q) || fullName.contains(q) || code.contains(q)
        }
    }

    /**
     * Alias for searchByName
     */
    @JvmStatic
    fun search(query: String) = searchByName(query)

    /**
     * Validates if a bank code exists
     */
    override fun isValidCode(code: String): Boolean = getByCode(code) != null

    /**
     * Alias for isValidCode
     */
    @JvmStatic
    fun isValid(code: String) = isValidCode(code)

    /**
     * Gets all SPEI banks
     */
    @JvmStatic
    fun getSPEIBanks(): List<Map<String, Any?>> {
        loadData()
        return data!!.filter { it["spei"] == true }
    }

    /**
     * Gets all SPEI banks as Bank objects
     */
    @JvmStatic
    fun getAllSPEIBanks(): List<Bank> = getSPEIBanks().map { Bank.fromMap(it) }

    /**
     * Checks if a bank supports SPEI
     */
    @JvmStatic
    fun supportsSPEI(code: String): Boolean {
        val bank = getByCode(code)
        return bank?.get("spei") == true
    }
}
