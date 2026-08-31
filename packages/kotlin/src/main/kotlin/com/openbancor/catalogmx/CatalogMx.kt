/**
 * CatalogMx - Mexican financial and government catalog data library for Kotlin/JVM
 *
 * This library provides:
 * - Validators for RFC, CURP, CLABE, NSS
 * - Generators for RFC, CURP, and complete Mexican identities
 * - Catalogs from INEGI, SAT, Banxico, SEPOMEX, and more
 * - Tax calculators for ISR, IMSS, RESICO
 *
 * Example usage:
 * ```kotlin
 * import com.openbancor.catalogmx.*
 *
 * // Validate RFC
 * val isValid = validateRFC("XAXX010101000")
 *
 * // Get bank by CLABE code
 * val bank = BanxicoBanks.getByCode("002")
 *
 * // Generate test identity
 * val identity = generatePersonaFisica()
 * ```
 */
package com.openbancor.catalogmx

// Re-export validators
import com.openbancor.catalogmx.validators.*
// Re-export generators
import com.openbancor.catalogmx.generators.*
// Re-export catalogs
import com.openbancor.catalogmx.catalogs.banxico.*
import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import com.openbancor.catalogmx.catalogs.inegi.*
import com.openbancor.catalogmx.catalogs.sat.contabilidad_electronica.*
import com.openbancor.catalogmx.catalogs.sat.cfdi.*
import com.openbancor.catalogmx.cfdi.CfdiBuilder
import com.openbancor.catalogmx.cfdi.CfdiResources
import com.openbancor.catalogmx.cfdi.CfdiValidation
import com.openbancor.catalogmx.cfdi.CfdiSigning
// Re-export calculators
import com.openbancor.catalogmx.calculators.*
// Re-export data updater
import com.openbancor.catalogmx.data.DataUpdater
import com.openbancor.catalogmx.data.DataUpdaterConfig

/**
 * Library version
 */
const val CATALOGMX_VERSION = "0.7.0"

// ============================================================================
// Data Configuration
// ============================================================================

/**
 * Configures the library to use a SQLite database for catalog data
 *
 * @param sqlitePath Path to the SQLite database file (mexico.sqlite3)
 */
fun configureSqlite(sqlitePath: String) {
    BaseCatalog.sqlitePath = sqlitePath
    // Reload catalogs to use new data source
    BanxicoBanks.reload()
}

/**
 * Gets the DataUpdater singleton for managing dynamic data downloads
 *
 * @param config Optional configuration for the updater
 * @return DataUpdater instance
 */
fun getDataUpdater(config: DataUpdaterConfig? = null): DataUpdater = DataUpdater.getInstance(config)

/**
 * Downloads the latest dynamic data (economic indicators)
 *
 * @param force Force download even if cache is valid
 * @return true if download was successful
 */
fun updateDynamicData(force: Boolean = false): Boolean = DataUpdater.update(force)

// ============================================================================
// Validator convenience functions
// ============================================================================

/**
 * Validates an RFC (Registro Federal de Contribuyentes)
 *
 * @param rfc The RFC string to validate
 * @param strict If true, validates checksum digit (default: true)
 * @return true if the RFC is valid
 */
fun validateRFC(rfc: String, strict: Boolean = true): Boolean =
    RfcValidator(rfc).validate(strict)

/**
 * Validates a CURP (Clave Única de Registro de Población)
 *
 * @param curp The CURP string to validate
 * @return true if the CURP is valid
 */
fun validateCURP(curp: String): Boolean =
    CurpValidator(curp).isValid()

/**
 * Validates a CLABE (Clave Bancaria Estandarizada)
 *
 * @param clabe The CLABE string to validate
 * @return true if the CLABE is valid
 */
fun validateCLABE(clabe: String?): Boolean =
    ClabeValidator(clabe).isValid()

/**
 * Validates an NSS (Número de Seguridad Social)
 *
 * @param nss The NSS string to validate
 * @return true if the NSS is valid
 */
fun validateNSS(nss: String?): Boolean =
    NssValidator(nss).isValid()

// ============================================================================
// Generator convenience functions
// ============================================================================

/**
 * Generates an RFC for Persona Física (individual)
 *
 * @param nombre First name
 * @param apellidoPaterno Paternal surname
 * @param apellidoMaterno Maternal surname
 * @param fechaNacimiento Birth date
 * @return Generated RFC string
 */
fun generateRFC(
    nombre: String,
    apellidoPaterno: String,
    apellidoMaterno: String,
    fechaNacimiento: java.time.LocalDate
): String = RfcGeneratorFisica(
    nombre = nombre,
    apellidoPaterno = apellidoPaterno,
    apellidoMaterno = apellidoMaterno,
    fechaNacimiento = fechaNacimiento
).generate()

/**
 * Generates an RFC for Persona Moral (company)
 *
 * @param razonSocial Company name
 * @param fechaConstitucion Incorporation date
 * @return Generated RFC string
 */
fun generateRFCMoral(
    razonSocial: String,
    fechaConstitucion: java.time.LocalDate
): String = RfcGeneratorMoral(
    razonSocial = razonSocial,
    fechaConstitucion = fechaConstitucion
).generate()

/**
 * Generates a CURP
 *
 * @param nombre First name
 * @param apellidoPaterno Paternal surname
 * @param apellidoMaterno Maternal surname (optional)
 * @param fechaNacimiento Birth date
 * @param sexo Gender ('H' for male, 'M' for female)
 * @param estado State name or code (optional, defaults to "NE" for foreign-born)
 * @return Generated CURP string
 */
fun generateCURP(
    nombre: String,
    apellidoPaterno: String,
    apellidoMaterno: String? = null,
    fechaNacimiento: java.time.LocalDate,
    sexo: String,
    estado: String? = null
): String = CurpGenerator(
    nombre = nombre,
    apellidoPaterno = apellidoPaterno,
    apellidoMaterno = apellidoMaterno,
    fechaNacimiento = fechaNacimiento,
    sexo = sexo,
    estado = estado
).generate()

/**
 * Generates a complete CLABE with check digit
 *
 * @param bankCode 3-digit bank code
 * @param branchCode 3-digit branch code
 * @param accountNumber 11-digit account number
 * @return Generated CLABE string
 */
fun generateCLABE(
    bankCode: String,
    branchCode: String,
    accountNumber: String
): String = ClabeValidator.generateCLABE(bankCode, branchCode, accountNumber)

/**
 * Generates an NSS with check digit
 *
 * @param subdelegation 2-digit subdelegation code
 * @param registrationYear 2-digit registration year
 * @param birthYear 2-digit birth year
 * @param sequential 4-digit sequential number
 * @return Generated NSS string
 */
fun generateNSS(
    subdelegation: String,
    registrationYear: String,
    birthYear: String,
    sequential: String
): String = NssValidator.generateNSS(subdelegation, registrationYear, birthYear, sequential)

/**
 * Generates a complete Persona Física identity with valid RFC, CURP, NSS, CLABE
 *
 * @param sexo Gender ('H' or 'M'), null for random
 * @param estado State code, null for random
 * @param minAge Minimum age (default: 18)
 * @param maxAge Maximum age (default: 65)
 * @return Map containing all identity data
 */
fun generatePersonaFisica(
    sexo: String? = null,
    estado: String? = null,
    minAge: Int = 18,
    maxAge: Int = 65
): Map<String, Any?> = IdentityGenerator().generatePersonaFisica(
    sexo = sexo,
    estado = estado,
    minAge = minAge,
    maxAge = maxAge
).toMap()

/**
 * Generates a complete Persona Moral identity with valid RFC, CLABE
 *
 * @param minYears Minimum years since constitution (default: 1)
 * @param maxYears Maximum years since constitution (default: 30)
 * @return Map containing all identity data
 */
fun generatePersonaMoral(
    minYears: Int = 1,
    maxYears: Int = 30
): Map<String, Any?> = IdentityGenerator().generatePersonaMoral(
    minYears = minYears,
    maxYears = maxYears
).toMap()

// ============================================================================
// CFDI helpers
// ============================================================================

fun buildUnsignedCfdiXml(input: com.openbancor.catalogmx.cfdi.CfdiComprobanteInput): String =
    CfdiBuilder.buildUnsignedXml(input)

fun generateCadenaOriginalCfdi(
    xml: String,
    xslt: String
): com.openbancor.catalogmx.cfdi.CadenaOriginalResult =
    CfdiValidation.generateCadenaOriginal(xml, xslt)

fun validateCfdiXsd(
    xml: String,
    xsd: String
): com.openbancor.catalogmx.cfdi.XsdValidationResult =
    CfdiValidation.validateXsd(xml, xsd)

fun getCfdi40XsdPath(): String = CfdiResources.cfdi40Xsd()

fun getCadenaOriginal40XsltPath(): String = CfdiResources.cadenaOriginal40Xslt()

fun signCadenaOriginalCfdi(cadena: String, privateKeyPem: String): String =
    CfdiSigning.signCadenaOriginal(cadena, privateKeyPem)

fun applySelloToCfdiXml(
    xml: String,
    sello: String,
    certificado: String? = null,
    noCertificado: String? = null,
): String = CfdiSigning.applySelloToXml(xml, sello, certificado, noCertificado)
