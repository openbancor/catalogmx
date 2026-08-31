# catalogmx for Kotlin/JVM

Mexican financial and government catalog data library for Kotlin/JVM.

## Installation

### Gradle (Kotlin DSL)

```kotlin
dependencies {
    implementation("com.openbancor:catalogmx:0.7.0")
}
```

### Gradle (Groovy)

```groovy
dependencies {
    implementation 'com.openbancor:catalogmx:0.7.0'
}
```

### Maven

```xml
<dependency>
    <groupId>com.openbancor</groupId>
    <artifactId>catalogmx</artifactId>
    <version>0.7.0</version>
</dependency>
```

## Features

- **Validators**: RFC, CURP, CLABE, NSS validation
- **Generators**: RFC, CURP, NSS, CLABE generation
- **Catalogs**: Banks (Banxico), States (INEGI), Fiscal Regimes (SAT)
- **Calculators**: ISR (Income Tax)
- **Identity Generator**: Generate complete test identities with valid Mexican documents

## Quick Start

### Validation

```kotlin
import com.openbancor.catalogmx.*

// Validate RFC
val isValidRfc = validateRFC("XAXX010101000")  // true

// Validate CURP
val isValidCurp = validateCURP("OEAF771012HMCRGR09")  // true

// Validate CLABE
val isValidClabe = validateCLABE("002010077777777771")  // true

// Validate NSS
val isValidNss = validateNSS("12345678903")  // depends on check digit
```

### Generation

```kotlin
import com.openbancor.catalogmx.*
import java.time.LocalDate

// Generate RFC for Persona Física
val rfcFisica = generateRFC(
    nombre = "Juan",
    apellidoPaterno = "Garcia",
    apellidoMaterno = "Lopez",
    fechaNacimiento = LocalDate.of(1990, 5, 15)
)

// Generate RFC for Persona Moral
val rfcMoral = generateRFCMoral(
    razonSocial = "Comercializadora del Norte SA de CV",
    fechaConstitucion = LocalDate.of(2001, 3, 22)
)

// Generate CURP
val curp = generateCURP(
    nombre = "Juan",
    apellidoPaterno = "Garcia",
    apellidoMaterno = "Lopez",
    fechaNacimiento = LocalDate.of(1990, 5, 15),
    sexo = "H",
    estado = "JALISCO"
)

// Generate CLABE
val clabe = generateCLABE(
    bankCode = "002",
    branchCode = "010",
    accountNumber = "07777777777"
)
```

### Catalogs

```kotlin
import com.openbancor.catalogmx.catalogs.banxico.BanxicoBanks
import com.openbancor.catalogmx.catalogs.inegi.InegiStates
import com.openbancor.catalogmx.catalogs.sat.cfdi.RegimenFiscalCatalog

// Get bank by code
val bank = BanxicoBanks.getByCode("002")  // BANAMEX

// Get all SPEI-enabled banks
val speiBanks = BanxicoBanks.getSPEIBanks()

// Get state by code
val state = InegiStates.getByCode("JC")  // JALISCO

// Get fiscal regimes for Persona Física
val regimenes = RegimenFiscalCatalog.getParaPersonasFisicas()
```

### Tax Calculations

```kotlin
import com.openbancor.catalogmx.calculators.*

// Calculate ISR for monthly income
val result = IsrCalculator.calculateIsr(
    ingresoGravable = 15000.0,
    periodo = IsrPeriod.MENSUAL,
    year = IsrYear.YEAR_2026
)

println("ISR: ${result.isrFinal}")
println("Effective rate: ${result.tasaEfectiva}%")
```

### Identity Generation (for testing)

```kotlin
import com.openbancor.catalogmx.*

// Generate complete Persona Física identity
val identity = generatePersonaFisica()
println(identity["rfc"])      // Valid RFC
println(identity["curp"])     // Valid CURP
println(identity["nss"])      // Valid NSS
println(identity["clabe"])    // Valid CLABE

// Generate Persona Moral identity
val company = generatePersonaMoral()
println(company["rfc"])       // Valid 12-char RFC
println(company["clabe"])     // Valid CLABE
```

### Data Updates (Dynamic Data)

```kotlin
import com.openbancor.catalogmx.*
import com.openbancor.catalogmx.data.DataUpdater
import com.openbancor.catalogmx.data.DataUpdaterConfig

// Download latest economic indicators (TIIE, exchange rates, etc.)
val success = updateDynamicData()

// Or with custom configuration
val config = DataUpdaterConfig(
    cacheDir = ".my-cache",
    maxAgeHours = 48,
    autoUpdate = true
)
val updater = getDataUpdater(config)

// Check cache status
println(updater.getCacheStats())

// Force update
updater.downloadLatest(force = true)
```

### SQLite Catalog Data (Advanced)

```kotlin
import com.openbancor.catalogmx.*
import com.openbancor.catalogmx.catalogs.banxico.BanxicoBanks

// Configure to use local SQLite database for complete catalog data
configureSqlite("/path/to/mexico.sqlite3")

// Now catalogs will use SQLite data (100+ banks instead of 24 embedded)
val banks = BanxicoBanks.getAll()
println("Loaded ${banks.size} banks from ${BanxicoBanks.dataSource}")
```

## Data Sources

The library supports multiple data sources with automatic fallback:

| Priority | Source | Description |
|----------|--------|-------------|
| 1 | SQLite | Complete data from `mexico.sqlite3` (if configured) |
| 2 | JSON | Data from `shared-data/` directory |
| 3 | Embedded | Minimal built-in data (always available) |

## Requirements

- JDK 11 or higher
- Kotlin 1.9+

## License

MIT License - see LICENSE file for details.

## Related Packages

- [catalogmx (Python)](https://pypi.org/project/catalogmx/)
- [catalogmx (TypeScript/Node.js)](https://www.npmjs.com/package/catalogmx)
- [catalogmx (Dart/Flutter)](https://pub.dev/packages/catalogmx)
