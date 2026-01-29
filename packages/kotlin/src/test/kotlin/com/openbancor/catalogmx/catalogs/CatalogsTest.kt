package com.openbancor.catalogmx.catalogs

import com.openbancor.catalogmx.catalogs.banxico.BanxicoBanks
import com.openbancor.catalogmx.catalogs.inegi.InegiStates
import com.openbancor.catalogmx.catalogs.sat.cfdi.RegimenFiscalCatalog
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class CatalogsTest {

    @Test
    fun `InegiStates should return all states`() {
        val states = InegiStates.getAll()
        assertTrue(states.isNotEmpty())
        assertEquals(33, states.size) // 32 states + NE (foreign born)
    }

    @Test
    fun `InegiStates should find state by code`() {
        val cdmx = InegiStates.getByCode("DF")
        assertNotNull(cdmx)
        assertEquals("CIUDAD DE MEXICO", cdmx!!["name"])

        val jalisco = InegiStates.getByCode("JC")
        assertNotNull(jalisco)
        assertEquals("JALISCO", jalisco!!["name"])
    }

    @Test
    fun `InegiStates should handle case insensitive code lookup`() {
        val state = InegiStates.getByCode("df")
        assertNotNull(state)
        assertEquals("DF", state!!["code"])
    }

    @Test
    fun `InegiStates should find state by INEGI clave`() {
        val cdmx = InegiStates.getByClaveInegi("09")
        assertNotNull(cdmx)
        assertEquals("CIUDAD DE MEXICO", cdmx!!["name"])
    }

    @Test
    fun `InegiStates should find state by name`() {
        val state = InegiStates.getByName("jalisco")
        assertNotNull(state)
        assertEquals("JC", state!!["code"])
    }

    @Test
    fun `InegiStates should validate codes`() {
        assertTrue(InegiStates.isValidCode("DF"))
        assertTrue(InegiStates.isValidCode("JC"))
        assertFalse(InegiStates.isValidCode("XX"))
    }

    @Test
    fun `InegiStates should search states`() {
        val results = InegiStates.searchByName("BAJA")
        assertEquals(2, results.size) // Baja California and Baja California Sur
    }

    @Test
    fun `BanxicoBanks should return all banks`() {
        val banks = BanxicoBanks.getAll()
        assertTrue(banks.isNotEmpty())
    }

    @Test
    fun `BanxicoBanks should find bank by code`() {
        val banamex = BanxicoBanks.getByCode("002")
        assertNotNull(banamex)
        assertEquals("BANAMEX", banamex!!["name"])

        // Also test without padding
        val banamex2 = BanxicoBanks.getByCode("2")
        assertNotNull(banamex2)
        assertEquals("BANAMEX", banamex2!!["name"])
    }

    @Test
    fun `BanxicoBanks should find bank by name`() {
        val bank = BanxicoBanks.getByName("BANAMEX")
        assertNotNull(bank)
        assertEquals("002", bank!!["code"])
    }

    @Test
    fun `BanxicoBanks should validate codes`() {
        assertTrue(BanxicoBanks.isValid("002"))
        assertTrue(BanxicoBanks.isValid("072"))
    }

    @Test
    fun `BanxicoBanks should return SPEI banks`() {
        val speiBanks = BanxicoBanks.getSPEIBanks()
        assertTrue(speiBanks.isNotEmpty())
        assertTrue(speiBanks.all { it["spei"] == true })
    }

    @Test
    fun `BanxicoBanks should check SPEI support`() {
        assertTrue(BanxicoBanks.supportsSPEI("002")) // BANAMEX
        assertTrue(BanxicoBanks.supportsSPEI("072")) // BANORTE
    }

    @Test
    fun `BanxicoBanks should search banks`() {
        val results = BanxicoBanks.search("BAN")
        assertTrue(results.isNotEmpty())
        assertTrue(results.any { (it["name"] as? String)?.contains("BAN") == true })
    }

    @Test
    fun `BanxicoBanks should return Bank objects`() {
        val banks = BanxicoBanks.getAllBanks()
        assertTrue(banks.isNotEmpty())

        val banamex = BanxicoBanks.getBankByCode("002")
        assertNotNull(banamex)
        assertEquals("002", banamex!!.code)
        assertEquals("BANAMEX", banamex.name)
    }

    @Test
    fun `RegimenFiscalCatalog should return all regimes`() {
        val regimenes = RegimenFiscalCatalog.getAll()
        assertTrue(regimenes.isNotEmpty())
    }

    @Test
    fun `RegimenFiscalCatalog should find by code`() {
        val regimen = RegimenFiscalCatalog.getByCode("601")
        assertNotNull(regimen)
        assertEquals("General de Ley Personas Morales", regimen!!["descripcion"])
    }

    @Test
    fun `RegimenFiscalCatalog should validate codes`() {
        assertTrue(RegimenFiscalCatalog.isValidCode("601"))
        assertTrue(RegimenFiscalCatalog.isValidCode("612"))
        assertFalse(RegimenFiscalCatalog.isValidCode("999"))
    }

    @Test
    fun `RegimenFiscalCatalog should filter for persona fisica`() {
        val regimenes = RegimenFiscalCatalog.getParaPersonasFisicas()
        assertTrue(regimenes.isNotEmpty())
        assertTrue(regimenes.all { it["fisica"] == true })
    }

    @Test
    fun `RegimenFiscalCatalog should filter for persona moral`() {
        val regimenes = RegimenFiscalCatalog.getParaPersonasMorales()
        assertTrue(regimenes.isNotEmpty())
        assertTrue(regimenes.all { it["moral"] == true })
    }

    @Test
    fun `RegimenFiscalCatalog should validate for entity type`() {
        // 601 is only for persona moral
        assertTrue(RegimenFiscalCatalog.isValidForMoral("601"))
        assertFalse(RegimenFiscalCatalog.isValidForFisica("601"))

        // 612 is only for persona fisica
        assertTrue(RegimenFiscalCatalog.isValidForFisica("612"))
        assertFalse(RegimenFiscalCatalog.isValidForMoral("612"))

        // 626 (RESICO) is for both
        assertTrue(RegimenFiscalCatalog.isValidForFisica("626"))
        assertTrue(RegimenFiscalCatalog.isValidForMoral("626"))
    }
}
