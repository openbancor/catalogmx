package com.openbancor.catalogmx.data

import com.openbancor.catalogmx.catalogs.banxico.BanxicoBanks
import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.configureSqlite
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.AfterEach
import java.io.File

/**
 * Integration test for SQLite catalog loading
 * 
 * Run with: ./gradlew test --tests "*SqliteIntegrationTest*" -i
 */
class SqliteIntegrationTest {

    @BeforeEach
    fun setup() {
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
        BanxicoBanks.reload()
    }

    @AfterEach
    fun cleanup() {
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
        BanxicoBanks.reload()
    }

    @Test
    fun `full SQLite integration test`() {
        println("\n=== SQLite Integration Test ===\n")
        
        // 1. Test embedded data
        println("1. SIN SQLite (datos embebidos):")
        val embeddedBanks = BanxicoBanks.getAll()
        println("   Fuente: ${BanxicoBanks.dataSource}")
        println("   Bancos: ${embeddedBanks.size}")
        println("   Banco 002: ${BanxicoBanks.getByCode("002")?.get("name")}")
        
        // 2. Check if SQLite file exists - resolve from project directory
        val userDir = File(System.getProperty("user.dir"))
        val possiblePaths = listOf(
            File(userDir, "../shared-data/mexico.sqlite3"),
            File(userDir.parentFile, "shared-data/mexico.sqlite3"),
            File("/Users/luisfernando/Code/openbancor/catalogmx/packages/shared-data/mexico.sqlite3")
        )
        val sqlitePath = possiblePaths.firstOrNull { it.exists() }
        println("\n2. SQLite file search:")
        println("   user.dir: $userDir")
        possiblePaths.forEach { p -> println("   - ${p.absolutePath}: exists=${p.exists()}") }
        println("   Selected: ${sqlitePath?.absolutePath ?: "NONE"}")
        
        if (sqlitePath == null) {
            println("   SKIP: SQLite file not found at any location")
            return
        }

        // 3. Configure SQLite
        println("\n3. CON SQLite:")
        println("   Using: ${sqlitePath.absolutePath}")
        configureSqlite(sqlitePath.absolutePath)
        
        val sqliteBanks = BanxicoBanks.getAll()
        println("   Fuente: ${BanxicoBanks.dataSource}")
        println("   Bancos: ${sqliteBanks.size}")
        
        // 4. Verify bank details
        val bank002 = BanxicoBanks.getByCode("002")
        println("\n4. Banco 002 detalles:")
        bank002?.forEach { (key, value) ->
            println("   $key: $value")
        }
        
        // 5. SPEI banks
        val speiBanks = BanxicoBanks.getSPEIBanks()
        println("\n5. Bancos SPEI: ${speiBanks.size}")
        speiBanks.take(5).forEach { bank ->
            println("   - ${bank["code"]}: ${bank["name"]}")
        }
        
        // 6. Search test
        println("\n6. Busqueda 'BBVA':")
        BanxicoBanks.search("BBVA").forEach { bank ->
            println("   - ${bank["code"]}: ${bank["name"]}")
        }
        
        // Assertions
        assert(sqliteBanks.size > embeddedBanks.size) { 
            "SQLite should have more banks (${sqliteBanks.size}) than embedded (${embeddedBanks.size})" 
        }
        assert(BanxicoBanks.dataSource == "sqlite") { "Data source should be sqlite" }
        assert(bank002 != null) { "Bank 002 should exist" }
        
        println("\n=== Test PASSED ===")
    }
}
