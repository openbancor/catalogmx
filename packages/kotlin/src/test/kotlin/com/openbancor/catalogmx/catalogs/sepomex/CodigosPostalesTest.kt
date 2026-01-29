package com.openbancor.catalogmx.catalogs.sepomex

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import java.io.File

class CodigosPostalesTest {

    @BeforeEach
    fun setup() {
        // Configure SQLite path
        val testDb = File("../shared-data/mexico.sqlite3")
        if (testDb.exists()) {
            BaseCatalog.sqlitePath = testDb.absolutePath
        }
        CodigosPostales.reload()
    }

    @AfterEach
    fun cleanup() {
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
        CodigosPostales.reload()
    }

    @Test
    fun `getByCP should return settlements for valid postal code`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) {
            println("SKIP: SQLite not available")
            return
        }

        val settlements = CodigosPostales.getByCP("01000")

        println("CP 01000 settlements: ${settlements.size}")
        settlements.forEach { s ->
            println("  - ${s["asentamiento"]}, ${s["municipio"]}, ${s["estado"]}")
        }

        assertTrue(settlements.isNotEmpty(), "01000 should have settlements")
        assertEquals("sqlite", CodigosPostales.dataSource)
    }

    @Test
    fun `isValid should return true for existing postal code`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        assertTrue(CodigosPostales.isValid("01000"))
        assertTrue(CodigosPostales.isValid("06700"))
        assertFalse(CodigosPostales.isValid("99999"))
    }

    @Test
    fun `getMunicipio should return municipality for postal code`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val municipio = CodigosPostales.getMunicipio("01000")
        println("Municipio for 01000: $municipio")
        assertNotNull(municipio)
    }

    @Test
    fun `getEstado should return state for postal code`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val estado = CodigosPostales.getEstado("01000")
        println("Estado for 01000: $estado")
        assertNotNull(estado)
    }

    @Test
    fun `searchByColonia should find colonias by name`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val results = CodigosPostales.searchByColonia("Roma")
        println("Colonias with 'Roma': ${results.size}")
        results.take(5).forEach { r ->
            println("  - ${r["cp"]}: ${r["asentamiento"]}, ${r["municipio"]}")
        }

        assertTrue(results.isNotEmpty(), "Should find colonias named Roma")
    }

    @Test
    fun `count should return total postal codes`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val total = CodigosPostales.count()
        println("Total postal codes: $total")

        assertTrue(total > 100000, "Should have more than 100K postal codes")
    }

    @Test
    fun `search should find results with FTS or LIKE`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val results = CodigosPostales.search("Polanco", limit = 10)
        println("Search 'Polanco': ${results.size} results")
        results.forEach { r ->
            println("  - ${r["cp"]}: ${r["asentamiento"]}, ${r["municipio"]}")
        }

        assertTrue(results.isNotEmpty(), "Should find Polanco")
    }

    @Test
    fun `getByEstado should return postal codes for state`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val results = CodigosPostales.getByEstado("Jalisco")
        println("Postal codes in Jalisco: ${results.size}")

        assertTrue(results.isNotEmpty(), "Should find postal codes in Jalisco")
    }

    @Test
    fun `getByMunicipio should return postal codes for municipality`() {
        val testDb = File("../shared-data/mexico.sqlite3")
        if (!testDb.exists()) return

        val results = CodigosPostales.getByMunicipio("Guadalajara")
        println("Postal codes in Guadalajara: ${results.size}")

        assertTrue(results.isNotEmpty(), "Should find postal codes in Guadalajara")
    }

    @Test
    fun `should return empty list when SQLite not configured`() {
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
        CodigosPostales.reload()

        val settlements = CodigosPostales.getByCP("01000")
        assertTrue(settlements.isEmpty())
        assertEquals("none", CodigosPostales.dataSource)
    }
}
