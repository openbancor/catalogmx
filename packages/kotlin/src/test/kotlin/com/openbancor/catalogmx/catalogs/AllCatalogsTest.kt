package com.openbancor.catalogmx.catalogs

import com.openbancor.catalogmx.catalogs.banxico.*
import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.cnbv.CnbvSectores
import com.openbancor.catalogmx.catalogs.conapo.MunicipiosZM
import com.openbancor.catalogmx.catalogs.conapo.ZonasMetropolitanas
import com.openbancor.catalogmx.catalogs.ift.CodigosLada
import com.openbancor.catalogmx.catalogs.ift.OperadoresMoviles
import com.openbancor.catalogmx.catalogs.ift.OperadoresPNN
import com.openbancor.catalogmx.catalogs.inegi.*
import com.openbancor.catalogmx.catalogs.mexico.*
import com.openbancor.catalogmx.catalogs.sat.cfdi.*
import com.openbancor.catalogmx.catalogs.sat.nomina.*
import com.openbancor.catalogmx.catalogs.sat.carta_porte.*
import com.openbancor.catalogmx.catalogs.sat.comercio_exterior.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.TestInstance
import java.io.File

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class AllCatalogsTest {

    private var sqliteAvailable = false

    @BeforeAll
    fun setup() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (testDb.exists()) {
            BaseCatalog.sqlitePath = testDb.absolutePath
            sqliteAvailable = true
        }
    }

    @AfterAll
    fun cleanup() {
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
    }

    // ==================== BANXICO ====================

    @Test
    fun `BanxicoBanks should load data`() {
        BanxicoBanks.reload()
        val banks = BanxicoBanks.getAll()
        assertTrue(banks.isNotEmpty(), "Should have banks")
        println("BanxicoBanks: ${banks.size} registros (${BanxicoBanks.dataSource})")
    }

    @Test
    fun `BanxicoTIIE should load from SQLite`() {
        if (!sqliteAvailable) return
        BanxicoTIIE.reload()
        val data = BanxicoTIIE.getAll()
        assertTrue(data.isNotEmpty(), "Should have TIIE data")
        println("BanxicoTIIE: ${data.size} registros")
    }

    @Test
    fun `BanxicoTipoCambio should load from SQLite`() {
        if (!sqliteAvailable) return
        BanxicoTipoCambio.reload()
        val data = BanxicoTipoCambio.getAll()
        assertTrue(data.isNotEmpty(), "Should have exchange rate data")
        println("BanxicoTipoCambio: ${data.size} registros")
    }

    @Test
    fun `BanxicoUDIs should load from SQLite`() {
        if (!sqliteAvailable) return
        BanxicoUDIs.reload()
        val data = BanxicoUDIs.getAll()
        assertTrue(data.isNotEmpty(), "Should have UDIs data")
        println("BanxicoUDIs: ${data.size} registros")
    }

    @Test
    fun `BanxicoCodigosPlaza should load from SQLite`() {
        if (!sqliteAvailable) return
        BanxicoCodigosPlaza.reload()
        val data = BanxicoCodigosPlaza.getAll()
        assertTrue(data.isNotEmpty(), "Should have plaza codes")
        println("BanxicoCodigosPlaza: ${data.size} registros")
    }

    @Test
    fun `BanxicoInstitucionesFinancieras should load from SQLite`() {
        if (!sqliteAvailable) return
        BanxicoInstitucionesFinancieras.reload()
        val data = BanxicoInstitucionesFinancieras.getAll()
        assertTrue(data.isNotEmpty(), "Should have financial institutions")
        println("BanxicoInstitucionesFinancieras: ${data.size} registros")
    }

    // ==================== INEGI ====================

    @Test
    fun `InegiStates should load data`() {
        val states = InegiStates.getAll()
        assertTrue(states.isNotEmpty(), "Should have states")
        // 32 states + 1 "NACIDO EN EL EXTRANJERO"
        assertEquals(33, states.size, "Mexico has 32 states + NE")
        println("InegiStates: ${states.size} registros (embedded)")
    }

    @Test
    fun `InegiMunicipios should load from SQLite`() {
        if (!sqliteAvailable) return
        InegiMunicipios.reload()
        val data = InegiMunicipios.getAll()
        assertTrue(data.isNotEmpty(), "Should have municipalities")
        println("InegiMunicipios: ${data.size} registros")
    }

    @Test
    fun `InegiMunicipiosCompleto should load from SQLite`() {
        if (!sqliteAvailable) return
        InegiMunicipiosCompleto.reload()
        val data = InegiMunicipiosCompleto.getAll()
        assertTrue(data.isNotEmpty(), "Should have complete municipalities")
        println("InegiMunicipiosCompleto: ${data.size} registros")
    }

    @Test
    fun `InegiLocalidades should search localities`() {
        if (!sqliteAvailable) return
        val results = InegiLocalidades.search("Guadalajara", limit = 10)
        assertTrue(results.isNotEmpty(), "Should find Guadalajara")
        println("InegiLocalidades search 'Guadalajara': ${results.size} resultados")
    }

    @Test
    fun `InegiSCIAN should load from SQLite`() {
        if (!sqliteAvailable) return
        InegiSCIAN.reload()
        val data = InegiSCIAN.getAll()
        assertTrue(data.isNotEmpty(), "Should have SCIAN sectors")
        println("InegiSCIAN: ${data.size} registros")
    }

    // ==================== IFT ====================

    @Test
    fun `CodigosLada should load data`() {
        CodigosLada.reload()
        val data = CodigosLada.getAll()
        assertTrue(data.isNotEmpty(), "Should have LADA codes")
        println("CodigosLada: ${data.size} registros (${CodigosLada.dataSource})")

        // Test specific LADA
        assertTrue(CodigosLada.isValid("55"), "55 (CDMX) should be valid")
        assertTrue(CodigosLada.isValid("33"), "33 (GDL) should be valid")
    }

    @Test
    fun `OperadoresMoviles should load data`() {
        OperadoresMoviles.reload()
        val data = OperadoresMoviles.getAll()
        assertTrue(data.isNotEmpty(), "Should have mobile operators")
        println("OperadoresMoviles: ${data.size} registros (${OperadoresMoviles.dataSource})")
    }

    // ==================== MEXICO ====================

    @Test
    fun `UMA should load data`() {
        UMA.reload()
        val data = UMA.getAll()
        assertTrue(data.isNotEmpty(), "Should have UMA data")
        println("UMA: ${data.size} registros (${UMA.dataSource})")

        val current = UMA.getCurrent()
        assertNotNull(current, "Should have current UMA")
        println("UMA actual: ${UMA.getValorDiario()} diario, ${UMA.getValorMensual()} mensual")
    }

    @Test
    fun `SalariosMinimos should load data`() {
        SalariosMinimos.reload()
        val data = SalariosMinimos.getAll()
        assertTrue(data.isNotEmpty(), "Should have salary data")
        println("SalariosMinimos: ${data.size} registros (${SalariosMinimos.dataSource})")

        val current = SalariosMinimos.getCurrent()
        assertNotNull(current, "Should have current minimum wage")
        println("Salario mínimo actual: ${SalariosMinimos.getValorDiario()} diario")
    }

    @Test
    fun `GirosMercantiles should load from SQLite`() {
        if (!sqliteAvailable) return
        GirosMercantiles.reload()
        val data = GirosMercantiles.getAll()
        assertTrue(data.isNotEmpty(), "Should have business types")
        println("GirosMercantiles: ${data.size} registros")
    }

    @Test
    fun `HoyNoCircula should load data`() {
        HoyNoCircula.reload()
        val data = HoyNoCircula.getAll()
        assertTrue(data.isNotEmpty(), "Should have Hoy No Circula data")
        println("HoyNoCircula: ${data.size} registros (${HoyNoCircula.dataSource})")
    }

    @Test
    fun `PalabrasCacofonicas should load data`() {
        PalabrasCacofonicas.reload()
        val words = PalabrasCacofonicas.getWords()
        assertTrue(words.isNotEmpty(), "Should have cacophonic words")
        assertTrue(PalabrasCacofonicas.isCacophonic("BUEY"), "BUEY should be cacophonic")
        assertTrue(PalabrasCacofonicas.isCacophonic("PUTO"), "PUTO should be cacophonic")
        assertFalse(PalabrasCacofonicas.isCacophonic("CASA"), "CASA should not be cacophonic")
        println("PalabrasCacofonicas: ${words.size} palabras")
    }

    // ==================== CONAPO ====================

    @Test
    fun `ZonasMetropolitanas should load from SQLite`() {
        if (!sqliteAvailable) return
        ZonasMetropolitanas.reload()
        val data = ZonasMetropolitanas.getAll()
        assertTrue(data.isNotEmpty(), "Should have metropolitan zones")
        println("ZonasMetropolitanas: ${data.size} registros")
    }

    @Test
    fun `MunicipiosZM should load from SQLite`() {
        if (!sqliteAvailable) return
        MunicipiosZM.reload()
        val data = MunicipiosZM.getAll()
        assertTrue(data.isNotEmpty(), "Should have ZM municipalities")
        println("MunicipiosZM: ${data.size} registros")
    }

    // ==================== CNBV ====================

    @Test
    fun `CnbvSectores should load from SQLite`() {
        if (!sqliteAvailable) return
        CnbvSectores.reload()
        val data = CnbvSectores.getAll()
        assertTrue(data.isNotEmpty(), "Should have CNBV sectors")
        println("CnbvSectores: ${data.size} registros")
    }

    // ==================== SAT CFDI 4.0 ====================

    @Test
    fun `RegimenFiscalCatalog should load data`() {
        val data = RegimenFiscalCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have fiscal regimes")
        println("RegimenFiscalCatalog: ${data.size} registros")

        val pf = RegimenFiscalCatalog.getParaPersonasFisicas()
        val pm = RegimenFiscalCatalog.getParaPersonasMorales()
        println("  - Persona Física: ${pf.size}, Persona Moral: ${pm.size}")
    }

    @Test
    fun `FormaPagoCatalog should load data`() {
        FormaPagoCatalog.reload()
        val data = FormaPagoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have payment forms")
        assertTrue(FormaPagoCatalog.isValidCode("03"), "03 (Transferencia) should be valid")
        println("FormaPagoCatalog: ${data.size} registros (${FormaPagoCatalog.dataSource})")
    }

    @Test
    fun `MetodoPagoCatalog should load data`() {
        MetodoPagoCatalog.reload()
        val data = MetodoPagoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have payment methods")
        assertTrue(MetodoPagoCatalog.isValidCode("PUE"), "PUE should be valid")
        assertTrue(MetodoPagoCatalog.isValidCode("PPD"), "PPD should be valid")
        println("MetodoPagoCatalog: ${data.size} registros (${MetodoPagoCatalog.dataSource})")
    }

    @Test
    fun `UsoCfdiCatalog should load data`() {
        UsoCfdiCatalog.reload()
        val data = UsoCfdiCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have CFDI uses")
        assertTrue(UsoCfdiCatalog.isValidCode("G03"), "G03 (Gastos en general) should be valid")
        println("UsoCfdiCatalog: ${data.size} registros (${UsoCfdiCatalog.dataSource})")
    }

    @Test
    fun `TipoComprobanteCatalog should load data`() {
        TipoComprobanteCatalog.reload()
        val data = TipoComprobanteCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have voucher types")
        assertTrue(TipoComprobanteCatalog.isValidCode("I"), "I (Ingreso) should be valid")
        assertTrue(TipoComprobanteCatalog.isValidCode("E"), "E (Egreso) should be valid")
        println("TipoComprobanteCatalog: ${data.size} registros (${TipoComprobanteCatalog.dataSource})")
    }

    @Test
    fun `MonedaCatalog should load data`() {
        MonedaCatalog.reload()
        val data = MonedaCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have currencies")
        assertTrue(MonedaCatalog.isValidCode("MXN"), "MXN should be valid")
        assertTrue(MonedaCatalog.isValidCode("USD"), "USD should be valid")
        println("MonedaCatalog: ${data.size} registros (${MonedaCatalog.dataSource})")
    }

    @Test
    fun `ImpuestoCatalog should load data`() {
        ImpuestoCatalog.reload()
        val data = ImpuestoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have taxes")
        assertTrue(ImpuestoCatalog.isValidCode("002"), "002 (IVA) should be valid")
        println("ImpuestoCatalog: ${data.size} registros (${ImpuestoCatalog.dataSource})")
    }

    // ==================== SAT NOMINA ====================

    @Test
    fun `NominaPeriodicidadPagoCatalog should load data`() {
        NominaPeriodicidadPagoCatalog.reload()
        val data = NominaPeriodicidadPagoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have payment periodicities")
        assertTrue(NominaPeriodicidadPagoCatalog.isValidCode("04"), "04 (Quincenal) should be valid")
        println("NominaPeriodicidadPagoCatalog: ${data.size} registros")
    }

    @Test
    fun `NominaTipoContratoCatalog should load data`() {
        NominaTipoContratoCatalog.reload()
        val data = NominaTipoContratoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have contract types")
        assertTrue(NominaTipoContratoCatalog.isValidCode("01"), "01 should be valid")
        println("NominaTipoContratoCatalog: ${data.size} registros")
    }

    @Test
    fun `NominaTipoNominaCatalog should load data`() {
        NominaTipoNominaCatalog.reload()
        val data = NominaTipoNominaCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have payroll types")
        assertTrue(NominaTipoNominaCatalog.isValidCode("O"), "O (Ordinaria) should be valid")
        assertTrue(NominaTipoNominaCatalog.isValidCode("E"), "E (Extraordinaria) should be valid")
        println("NominaTipoNominaCatalog: ${data.size} registros")
    }

    @Test
    fun `NominaBancoCatalog should load from SQLite`() {
        if (!sqliteAvailable) return
        NominaBancoCatalog.reload()
        val data = NominaBancoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have banks")
        println("NominaBancoCatalog: ${data.size} registros")
    }

    // ==================== SAT CARTA PORTE ====================

    @Test
    fun `CartaPorteAeropuertosCatalog should load from SQLite`() {
        if (!sqliteAvailable) return
        CartaPorteAeropuertosCatalog.reload()
        val data = CartaPorteAeropuertosCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have airports")
        println("CartaPorteAeropuertosCatalog: ${data.size} registros")
    }

    @Test
    fun `CartaPorteMaterialPeligrosoCatalog should load from SQLite`() {
        if (!sqliteAvailable) return
        CartaPorteMaterialPeligrosoCatalog.reload()
        val data = CartaPorteMaterialPeligrosoCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have hazardous materials")
        println("CartaPorteMaterialPeligrosoCatalog: ${data.size} registros")
    }

    // ==================== SAT COMERCIO EXTERIOR ====================

    @Test
    fun `ComercioExteriorIncotermsCatalog should load data`() {
        ComercioExteriorIncotermsCatalog.reload()
        val data = ComercioExteriorIncotermsCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have incoterms")
        assertTrue(ComercioExteriorIncotermsCatalog.isValidCode("FOB"), "FOB should be valid")
        assertTrue(ComercioExteriorIncotermsCatalog.isValidCode("CIF"), "CIF should be valid")
        println("ComercioExteriorIncotermsCatalog: ${data.size} registros")
    }

    @Test
    fun `ComercioExteriorPaisesCatalog should load from SQLite`() {
        if (!sqliteAvailable) return
        ComercioExteriorPaisesCatalog.reload()
        val data = ComercioExteriorPaisesCatalog.getAll()
        assertTrue(data.isNotEmpty(), "Should have countries")
        println("ComercioExteriorPaisesCatalog: ${data.size} registros")
    }
}
