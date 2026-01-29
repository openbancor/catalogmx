package com.openbancor.catalogmx.data

import io.ktor.client.*
import io.ktor.client.engine.cio.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.http.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.io.File
import java.nio.file.Files
import java.nio.file.StandardCopyOption
import java.sql.Connection
import java.sql.DriverManager
import java.time.Instant
import java.time.temporal.ChronoUnit

/**
 * Version information for cached data
 */
@Serializable
data class VersionInfo(
    val version: String,
    val updatedAt: String,
    val source: String,
    val url: String? = null
) {
    companion object {
        private val json = Json { ignoreUnknownKeys = true }

        fun fromJson(jsonString: String): VersionInfo = json.decodeFromString(jsonString)
    }

    fun toJson(): String = json.encodeToString(this)
}

/**
 * Configuration for DataUpdater
 */
data class DataUpdaterConfig(
    val cacheDir: String = ".catalogmx",
    val maxAgeHours: Int = 24,
    val dataUrl: String = "https://github.com/openbancor/catalogmx/releases/download/latest/mexico_dynamic.sqlite3",
    val autoUpdate: Boolean = true,
    val verbose: Boolean = false
)

/**
 * Data Updater for Kotlin/JVM
 *
 * Downloads and caches SQLite database from GitHub releases.
 * Provides automatic updates when cache expires.
 *
 * Usage:
 * ```kotlin
 * val updater = DataUpdater()
 *
 * // Check if update is needed
 * if (updater.isUpdateNeeded()) {
 *     updater.downloadLatest()
 * }
 *
 * // Get database connection
 * val conn = updater.getConnection()
 * ```
 */
class DataUpdater(private val config: DataUpdaterConfig = DataUpdaterConfig()) {

    private val cacheDir: File by lazy {
        val home = System.getProperty("user.home") ?: System.getenv("HOME") ?: "."
        File(home, config.cacheDir).also { it.mkdirs() }
    }

    private val databaseFile: File get() = File(cacheDir, "mexico_dynamic.sqlite3")
    private val versionFile: File get() = File(cacheDir, "version.json")
    private val tempFile: File get() = File(cacheDir, "mexico_dynamic.sqlite3.tmp")

    private var cachedConnection: Connection? = null

    /**
     * Gets the local version info, or null if no cache exists
     */
    fun getLocalVersion(): VersionInfo? {
        return try {
            if (versionFile.exists()) {
                VersionInfo.fromJson(versionFile.readText())
            } else null
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Gets the age of the cache in hours, or null if no cache exists
     */
    fun getCacheAgeHours(): Double? {
        return try {
            val version = getLocalVersion() ?: return null
            val updatedAt = Instant.parse(version.updatedAt)
            val now = Instant.now()
            ChronoUnit.MINUTES.between(updatedAt, now) / 60.0
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Checks if an update is needed (no cache or cache expired)
     */
    fun isUpdateNeeded(): Boolean {
        if (!databaseFile.exists()) return true
        val age = getCacheAgeHours() ?: return true
        return age > config.maxAgeHours
    }

    /**
     * Downloads the latest database from GitHub releases
     *
     * @param force Force download even if cache is valid
     * @return true if download was successful
     */
    fun downloadLatest(force: Boolean = false): Boolean {
        if (!force && !isUpdateNeeded()) {
            if (config.verbose) println("Cache is valid, skipping download")
            return true
        }

        if (config.verbose) println("Downloading data from ${config.dataUrl}...")

        return runBlocking {
            try {
                val client = HttpClient(CIO) {
                    followRedirects = true
                }

                val response: HttpResponse = client.get(config.dataUrl)

                if (response.status != HttpStatusCode.OK) {
                    if (config.verbose) println("HTTP ${response.status}")
                    client.close()
                    return@runBlocking false
                }

                // Download to temp file first
                withContext(Dispatchers.IO) {
                    val bytes = response.readBytes()
                    tempFile.writeBytes(bytes)

                    // Verify it's a valid SQLite database
                    if (!verifySqliteDatabase(tempFile)) {
                        if (config.verbose) println("Downloaded file is not a valid SQLite database")
                        tempFile.delete()
                        client.close()
                        return@withContext false
                    }

                    // Move temp file to final location
                    Files.move(
                        tempFile.toPath(),
                        databaseFile.toPath(),
                        StandardCopyOption.REPLACE_EXISTING
                    )

                    // Save version info
                    val versionInfo = VersionInfo(
                        version = "latest",
                        updatedAt = Instant.now().toString(),
                        source = "github-releases",
                        url = config.dataUrl
                    )
                    versionFile.writeText(versionInfo.toJson())
                }

                client.close()

                if (config.verbose) println("Data updated successfully")
                true
            } catch (e: Exception) {
                if (config.verbose) println("Error downloading data: ${e.message}")
                tempFile.delete()
                false
            }
        }
    }

    /**
     * Verifies that a file is a valid SQLite database
     */
    private fun verifySqliteDatabase(file: File): Boolean {
        return try {
            val conn = DriverManager.getConnection("jdbc:sqlite:${file.absolutePath}")
            val stmt = conn.createStatement()
            val rs = stmt.executeQuery("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
            val valid = rs.next() // At least one table exists
            rs.close()
            stmt.close()
            conn.close()
            valid
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Gets a connection to the SQLite database
     *
     * @param autoUpdate If true, will download latest if cache is expired
     * @return JDBC Connection to the SQLite database, or null if not available
     */
    fun getConnection(autoUpdate: Boolean = config.autoUpdate): Connection? {
        // Check if we need to update
        if (autoUpdate && isUpdateNeeded()) {
            downloadLatest()
        }

        // If still no database file, return null
        if (!databaseFile.exists()) {
            return null
        }

        // Reuse existing connection if valid
        cachedConnection?.let {
            if (!it.isClosed) return it
        }

        return try {
            DriverManager.getConnection("jdbc:sqlite:${databaseFile.absolutePath}").also {
                cachedConnection = it
            }
        } catch (e: Exception) {
            if (config.verbose) println("Error connecting to database: ${e.message}")
            null
        }
    }

    /**
     * Gets the path to the database file
     */
    fun getDatabasePath(): String? {
        return if (databaseFile.exists()) databaseFile.absolutePath else null
    }

    /**
     * Clears the cache (deletes database and version files)
     */
    fun clearCache(): Boolean {
        return try {
            cachedConnection?.close()
            cachedConnection = null
            databaseFile.delete()
            versionFile.delete()
            tempFile.delete()
            true
        } catch (e: Exception) {
            false
        }
    }

    /**
     * Gets cache statistics
     */
    fun getCacheStats(): Map<String, Any?> {
        return mapOf(
            "cacheDir" to cacheDir.absolutePath,
            "databaseExists" to databaseFile.exists(),
            "databaseSize" to if (databaseFile.exists()) databaseFile.length() else 0,
            "version" to getLocalVersion()?.version,
            "ageHours" to getCacheAgeHours(),
            "isExpired" to isUpdateNeeded()
        )
    }

    companion object {
        @Volatile
        private var instance: DataUpdater? = null

        /**
         * Gets or creates the singleton instance
         */
        @JvmStatic
        fun getInstance(config: DataUpdaterConfig? = null): DataUpdater {
            return instance ?: synchronized(this) {
                instance ?: DataUpdater(config ?: DataUpdaterConfig()).also { instance = it }
            }
        }

        /**
         * Convenience method to get a database connection
         */
        @JvmStatic
        fun getConnection(): Connection? = getInstance().getConnection()

        /**
         * Convenience method to update data
         */
        @JvmStatic
        fun update(force: Boolean = false): Boolean = getInstance().downloadLatest(force)
    }
}
