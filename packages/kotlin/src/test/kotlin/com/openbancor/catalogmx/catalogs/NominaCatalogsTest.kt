package com.openbancor.catalogmx.catalogs

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.sat.nomina.*
import kotlin.test.AfterTest
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class NominaCatalogsTest {
    private val originalSharedDataPath = BaseCatalog.sharedDataPath
    private val originalSqlitePath = BaseCatalog.sqlitePath

    @AfterTest
    fun restorePaths() {
        BaseCatalog.sharedDataPath = originalSharedDataPath
        BaseCatalog.sqlitePath = originalSqlitePath
        BaseCatalog.clearCache()
        BaseCatalog.clearSqliteCache()
        BaseCatalog.closeSqliteConnection()
    }

    @Test
    fun `all thirteen Nomina catalogs load from shared JSON without embedded regulatory data`() {
        BaseCatalog.sharedDataPath = "../shared-data"
        BaseCatalog.sqlitePath = null

        val samples = listOf(
            NominaBancoCatalog to "002",
            NominaOrigenRecursoCatalog to "IP",
            NominaPeriodicidadPagoCatalog to "04",
            NominaRiesgoPuestoCatalog to "99",
            NominaTipoContratoCatalog to "10",
            NominaTipoDeduccionCatalog to "115",
            NominaTipoHorasCatalog to "01",
            NominaTipoIncapacidadCatalog to "04",
            NominaTipoJornadaCatalog to "08",
            NominaTipoNominaCatalog to "O",
            NominaTipoOtroPagoCatalog to "999",
            NominaTipoPercepcionCatalog to "057",
            NominaTipoRegimenCatalog to "13"
        )
        assertEquals(13, samples.size)
        for ((catalog, code) in samples) {
            catalog.reload()
            assertTrue(catalog.getAll().isNotEmpty())
            assertTrue(catalog.isValidCode(code), "expected $code in ${catalog::class.simpleName}")
            assertEquals("json", catalog.dataSource)
            assertEquals(code, catalog.getByCode(code)?.get("clave"))
        }
    }

    @Test
    fun `canonical sqlite table names match the release artifact`() {
        assertEquals("nomina_bancos", NominaBancoCatalog.SQLITE_TABLE)
        assertEquals("nomina_origenes_recursos", NominaOrigenRecursoCatalog.SQLITE_TABLE)
        assertEquals("nomina_periodicidades_pagos", NominaPeriodicidadPagoCatalog.SQLITE_TABLE)
        assertEquals("nomina_riesgos_puestos", NominaRiesgoPuestoCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_contratos", NominaTipoContratoCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_deducciones", NominaTipoDeduccionCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_horas", NominaTipoHorasCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_incapacidades", NominaTipoIncapacidadCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_jornadas", NominaTipoJornadaCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_nominas", NominaTipoNominaCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_otros_pagos", NominaTipoOtroPagoCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_percepciones", NominaTipoPercepcionCatalog.SQLITE_TABLE)
        assertEquals("nomina_tipos_regimenes", NominaTipoRegimenCatalog.SQLITE_TABLE)
    }

    @Test
    fun `bank compatibility aliases are normalized`() {
        BaseCatalog.sharedDataPath = "../shared-data"
        BaseCatalog.sqlitePath = null
        NominaBancoCatalog.reload()
        val bank = assertNotNull(NominaBancoCatalog.getByCode("002"))
        assertEquals(bank["full_name"], bank["razon_social"])
        assertEquals(bank["code"], bank["clave"])
    }
}
