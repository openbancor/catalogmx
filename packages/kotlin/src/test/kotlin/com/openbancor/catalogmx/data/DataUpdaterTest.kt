package com.openbancor.catalogmx.data

import com.openbancor.catalogmx.catalogs.banxico.BanxicoBanks
import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import java.io.File

class DataUpdaterTest {

    @TempDir
    lateinit var tempDir: File

    @Test
    fun `DataUpdater should have correct default config`() {
        val config = DataUpdaterConfig()
        
        assertEquals(".catalogmx", config.cacheDir)
        assertEquals(24, config.maxAgeHours)
        assertTrue(config.dataUrl.contains("mexico_dynamic.sqlite3"))
        assertTrue(config.autoUpdate)
    }

    @Test
    fun `DataUpdater should allow custom config`() {
        val config = DataUpdaterConfig(
            cacheDir = ".custom-cache",
            maxAgeHours = 48,
            autoUpdate = false
        )
        
        assertEquals(".custom-cache", config.cacheDir)
        assertEquals(48, config.maxAgeHours)
        assertFalse(config.autoUpdate)
    }

    @Test
    fun `DataUpdater should report no cache initially`() {
        val config = DataUpdaterConfig(cacheDir = tempDir.absolutePath)
        val updater = DataUpdater(config)
        
        assertNull(updater.getLocalVersion())
        assertNull(updater.getCacheAgeHours())
        assertTrue(updater.isUpdateNeeded())
        assertNull(updater.getDatabasePath())
    }

    @Test
    fun `DataUpdater getCacheStats should return valid info`() {
        val config = DataUpdaterConfig(cacheDir = tempDir.absolutePath)
        val updater = DataUpdater(config)
        
        val stats = updater.getCacheStats()
        
        assertTrue(stats.containsKey("cacheDir"))
        assertTrue(stats.containsKey("databaseExists"))
        assertTrue(stats.containsKey("isExpired"))
        assertEquals(false, stats["databaseExists"])
        assertEquals(true, stats["isExpired"])
    }

    @Test
    fun `VersionInfo should serialize and deserialize correctly`() {
        val version = VersionInfo(
            version = "1.0.0",
            updatedAt = "2024-01-01T00:00:00Z",
            source = "test",
            url = "https://example.com"
        )
        
        val json = version.toJson()
        val restored = VersionInfo.fromJson(json)
        
        assertEquals(version.version, restored.version)
        assertEquals(version.updatedAt, restored.updatedAt)
        assertEquals(version.source, restored.source)
        assertEquals(version.url, restored.url)
    }
}

class SqliteCatalogTest {

    @Test
    fun `BaseCatalog should start without SQLite configured`() {
        // Reset state
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
        
        assertNull(BaseCatalog.sqlitePath)
        assertNull(BaseCatalog.getSqliteConnection())
    }

    @Test
    fun `BanxicoBanks should use embedded data when SQLite not configured`() {
        // Ensure no SQLite configured
        BaseCatalog.sqlitePath = null
        BaseCatalog.closeSqliteConnection()
        BanxicoBanks.reload()
        
        val banks = BanxicoBanks.getAll()
        assertTrue(banks.isNotEmpty())
        
        // Should be embedded or JSON source
        assertTrue(BanxicoBanks.dataSource in listOf("embedded", "json"))
    }

    @Test
    fun `BanxicoBanks should load from SQLite when configured`() {
        // Configure to use test SQLite database - relative to packages/kotlin
        val testDb = File("../shared-data/mexico.sqlite3")

        if (testDb.exists()) {
            BaseCatalog.sqlitePath = testDb.absolutePath
            BanxicoBanks.reload()
            
            val banks = BanxicoBanks.getAll()
            assertTrue(banks.isNotEmpty())
            
            // Should have many more banks from SQLite than embedded
            if (BanxicoBanks.dataSource == "sqlite") {
                assertTrue(banks.size > 50, "SQLite should have more than 50 banks")
            }
            
            // Cleanup
            BaseCatalog.sqlitePath = null
            BaseCatalog.closeSqliteConnection()
            BanxicoBanks.reload()
        }
    }

    @Test
    fun `BanxicoBanks reload should clear cache and reload`() {
        BanxicoBanks.reload()
        
        // After reload, data should still be available
        val banks = BanxicoBanks.getAll()
        assertTrue(banks.isNotEmpty())
    }
}
