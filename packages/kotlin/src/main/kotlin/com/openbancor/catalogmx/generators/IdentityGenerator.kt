package com.openbancor.catalogmx.generators

import com.openbancor.catalogmx.catalogs.banxico.BanxicoBanks
import com.openbancor.catalogmx.catalogs.inegi.InegiStates
import com.openbancor.catalogmx.catalogs.sat.cfdi.RegimenFiscalCatalog
import com.openbancor.catalogmx.utils.ClabeUtils
import com.openbancor.catalogmx.utils.DateUtils
import com.openbancor.catalogmx.validators.CurpGenerator
import com.openbancor.catalogmx.validators.NssValidator
import com.openbancor.catalogmx.validators.RfcGeneratorFisica
import com.openbancor.catalogmx.validators.RfcGeneratorMoral
import java.time.LocalDate
import kotlin.random.Random

/**
 * Persona Fisica identity data
 */
data class PersonaFisica(
    val tipo: String = "persona_fisica",
    val nombre: String,
    val apellidoPaterno: String,
    val apellidoMaterno: String,
    val nombreCompleto: String,
    val fechaNacimiento: LocalDate,
    val edad: Int,
    val sexo: String,
    val sexoDescripcion: String,
    val estadoNacimiento: String,
    val estadoNacimientoCode: String,
    val rfc: String,
    val curp: String,
    val nss: String,
    val banco: Map<String, String>,
    val clabe: String,
    val cuenta: String,
    val tarjetaDebito: String,
    val direccion: Map<String, String>,
    val telefono: String,
    val email: String,
    val regimenFiscal: Map<String, String>
) {
    fun toMap(): Map<String, Any?> = mapOf(
        "tipo" to tipo,
        "nombre" to nombre,
        "apellido_paterno" to apellidoPaterno,
        "apellido_materno" to apellidoMaterno,
        "nombre_completo" to nombreCompleto,
        "fecha_nacimiento" to "${fechaNacimiento.year}-${fechaNacimiento.monthValue.toString().padStart(2, '0')}-${fechaNacimiento.dayOfMonth.toString().padStart(2, '0')}",
        "edad" to edad,
        "sexo" to sexo,
        "sexo_descripcion" to sexoDescripcion,
        "estado_nacimiento" to estadoNacimiento,
        "estado_nacimiento_code" to estadoNacimientoCode,
        "rfc" to rfc,
        "curp" to curp,
        "nss" to nss,
        "banco" to banco,
        "clabe" to clabe,
        "cuenta" to cuenta,
        "tarjeta_debito" to tarjetaDebito,
        "direccion" to direccion,
        "telefono" to telefono,
        "email" to email,
        "regimen_fiscal" to regimenFiscal
    )
}

/**
 * Persona Moral identity data
 */
data class PersonaMoral(
    val tipo: String = "persona_moral",
    val razonSocial: String,
    val nombreComercial: String,
    val fechaConstitucion: LocalDate,
    val antiguedad: Int,
    val rfc: String,
    val banco: Map<String, String>,
    val clabe: String,
    val cuenta: String,
    val direccion: Map<String, String>,
    val telefono: String,
    val email: String,
    val regimenFiscal: Map<String, String>
) {
    fun toMap(): Map<String, Any?> = mapOf(
        "tipo" to tipo,
        "razon_social" to razonSocial,
        "nombre_comercial" to nombreComercial,
        "fecha_constitucion" to "${fechaConstitucion.year}-${fechaConstitucion.monthValue.toString().padStart(2, '0')}-${fechaConstitucion.dayOfMonth.toString().padStart(2, '0')}",
        "antiguedad" to antiguedad,
        "rfc" to rfc,
        "banco" to banco,
        "clabe" to clabe,
        "cuenta" to cuenta,
        "direccion" to direccion,
        "telefono" to telefono,
        "email" to email,
        "regimen_fiscal" to regimenFiscal
    )
}

/**
 * Identity Generator for Mexican test data
 *
 * Generates complete Mexican identities with valid RFC, CURP, NSS, CLABE.
 *
 * Example:
 * ```kotlin
 * val generator = IdentityGenerator()
 * val identity = generator.generatePersonaFisica()
 * println(identity.rfc) // Valid RFC
 * ```
 */
class IdentityGenerator(
    private val random: Random = Random.Default
) {
    companion object {
        private val maleNames = listOf(
            "Juan", "José", "Luis", "Carlos", "Miguel", "Francisco", "Antonio",
            "Pedro", "Manuel", "Rafael", "Ricardo", "Fernando", "Jorge", "Roberto",
            "Eduardo", "Alejandro", "Sergio", "Daniel", "Mario", "Arturo"
        )

        private val femaleNames = listOf(
            "María", "Ana", "Rosa", "Guadalupe", "Carmen", "Patricia", "Laura",
            "Elena", "Teresa", "Mónica", "Adriana", "Claudia", "Verónica", "Sandra",
            "Gabriela", "Leticia", "Silvia", "Martha", "Isabel", "Beatriz"
        )

        private val lastNames = listOf(
            "García", "Hernández", "López", "Martínez", "González", "Rodríguez",
            "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez",
            "Díaz", "Cruz", "Morales", "Reyes", "Jiménez", "Ruiz", "Ortiz"
        )

        private val streetTypes = listOf(
            "Calle", "Avenida", "Boulevard", "Calzada", "Paseo",
            "Privada", "Cerrada", "Circuito", "Peatonal"
        )

        private val colonias = listOf(
            "Centro", "Roma Norte", "Condesa", "Polanco", "Del Valle",
            "Narvarte", "Coyoacán", "Santa Fe", "Anzures", "Juárez"
        )

        private val companySuffixes = listOf(
            "S.A. de C.V.", "S. de R.L. de C.V.", "S.C.", "A.C.", "S.A.P.I. de C.V."
        )

        private val companyTypes = listOf(
            "Comercializadora", "Distribuidora", "Grupo", "Servicios", "Consultores",
            "Industrial", "Tecnología", "Inmobiliaria", "Constructora", "Transportes"
        )
    }

    private fun <T> randomElement(list: List<T>): T = list[random.nextInt(list.size)]

    private fun firstName(sexo: String?): String {
        val isMale = sexo == "H" || (sexo == null && random.nextBoolean())
        return randomElement(if (isMale) maleNames else femaleNames)
    }

    private fun lastName(): String = randomElement(lastNames)

    private fun randomDate(minAge: Int, maxAge: Int): LocalDate {
        val now = LocalDate.now()
        for (attempts in 0 until 100) {
            val minYear = now.year - maxAge - 1
            val maxYear = now.year - minAge
            val year = minYear + random.nextInt(maxYear - minYear + 1)
            val month = 1 + random.nextInt(12)
            val day = 1 + random.nextInt(28)
            val date = LocalDate.of(year, month, day)
            val age = DateUtils.calculateAge(date)
            if (age in minAge..maxAge) {
                return date
            }
        }
        // Fallback: return a date that guarantees age is within bounds
        val safeYear = now.year - minAge - 1
        return LocalDate.of(safeYear, now.monthValue, now.dayOfMonth)
    }

    private fun generateAddress(): Map<String, String> {
        val streetType = randomElement(streetTypes)
        val streetName = randomElement(lastNames)
        val numero = (random.nextInt(9000) + 100).toString()
        val colonia = randomElement(colonias)
        val cp = (10000 + random.nextInt(89999)).toString().padStart(5, '0')

        return mapOf(
            "calle" to "$streetType $streetName",
            "numero_exterior" to numero,
            "numero_interior" to "",
            "colonia" to colonia,
            "codigo_postal" to cp,
            "municipio" to "Ciudad de México",
            "estado" to "Ciudad de México"
        )
    }

    private fun generatePhone(): String {
        val areaCode = (55 + random.nextInt(44)).toString().padStart(2, '0')
        val number = (random.nextInt(90000000) + 10000000).toString()
        return areaCode + number
    }

    private fun generateEmail(firstName: String, lastName: String): String {
        val domains = listOf("gmail.com", "hotmail.com", "outlook.com", "yahoo.com")
        val fn = firstName.lowercase().replace(Regex("[^a-z]"), "")
        val ln = lastName.lowercase().replace(Regex("[^a-z]"), "")
        val num = random.nextInt(100)
        return "$fn$ln$num@${randomElement(domains)}"
    }

    private fun generateDebitCard(): String {
        val prefix = listOf("4", "5")[random.nextInt(2)]
        var card = prefix
        for (i in 1 until 16) {
            card += random.nextInt(10).toString()
        }
        return card
    }

    private fun generateBank(): Map<String, String> {
        val speiBanks = BanxicoBanks.getSPEIBanks()
        if (speiBanks.isEmpty()) {
            return mapOf("code" to "002", "name" to "BANAMEX")
        }
        val bank = speiBanks[random.nextInt(speiBanks.size)]
        return mapOf(
            "code" to (bank["code"] as? String ?: "002"),
            "name" to (bank["name"] as? String ?: "BANAMEX")
        )
    }

    private fun generateRegimenFiscal(personaMoral: Boolean = false): Map<String, String> {
        val regimenes = if (personaMoral) {
            RegimenFiscalCatalog.getParaPersonasMorales()
        } else {
            RegimenFiscalCatalog.getParaPersonasFisicas()
        }

        if (regimenes.isEmpty()) {
            return if (personaMoral) {
                mapOf("code" to "601", "name" to "General de Ley Personas Morales")
            } else {
                mapOf("code" to "612", "name" to "Personas Físicas con Actividades Empresariales y Profesionales")
            }
        }

        val regimen = regimenes[random.nextInt(regimenes.size)]
        return mapOf(
            "code" to (regimen["clave"] as? String ?: "612"),
            "name" to (regimen["descripcion"] as? String ?: "No especificado")
        )
    }

    /**
     * Generate a Persona Fisica identity
     *
     * @param sexo 'H' for male, 'M' for female, null for random
     * @param estado State code (e.g., 'DF', 'JC'), null for random
     * @param minAge Minimum age (default 18)
     * @param maxAge Maximum age (default 65)
     */
    @JvmOverloads
    fun generatePersonaFisica(
        sexo: String? = null,
        estado: String? = null,
        minAge: Int = 18,
        maxAge: Int = 65
    ): PersonaFisica {
        // Generate or assign sex
        val sex = sexo ?: if (random.nextBoolean()) "H" else "M"
        val sexDesc = if (sex == "H") "Masculino" else "Femenino"

        // Generate names
        val nombre = firstName(sex)
        val apellidoPaterno = lastName()
        val apellidoMaterno = lastName()
        val nombreCompleto = "$nombre $apellidoPaterno $apellidoMaterno"

        // Generate birth date
        val fechaNacimiento = randomDate(minAge, maxAge)
        val edad = DateUtils.calculateAge(fechaNacimiento)

        // Get state
        val states = InegiStates.getAll().filter { it["code"] != "NE" }
        val stateData = if (estado != null) {
            InegiStates.getByCode(estado)
        } else {
            states[random.nextInt(states.size)]
        }
        val estadoNacimiento = stateData?.get("name") as? String ?: "CIUDAD DE MEXICO"
        val estadoCode = stateData?.get("code") as? String ?: "DF"

        // Generate RFC
        val rfc = RfcGeneratorFisica(
            nombre = nombre,
            apellidoPaterno = apellidoPaterno,
            apellidoMaterno = apellidoMaterno,
            fechaNacimiento = fechaNacimiento
        ).generate()

        // Generate CURP
        val curp = CurpGenerator(
            nombre = nombre,
            apellidoPaterno = apellidoPaterno,
            apellidoMaterno = apellidoMaterno,
            fechaNacimiento = fechaNacimiento,
            sexo = sex,
            estado = estadoNacimiento
        ).generate()

        // Generate NSS
        val subdelegation = (random.nextInt(97) + 1).toString().padStart(2, '0')
        val regYear = (fechaNacimiento.year + 18).toString().takeLast(2)
        val birthYear = fechaNacimiento.year.toString().takeLast(2)
        val sequential = random.nextInt(10000).toString().padStart(4, '0')
        val nss = NssValidator.generateNSS(subdelegation, regYear, birthYear, sequential)

        // Generate banking data
        val banco = generateBank()
        val clabe = ClabeUtils.generateCLABERandom(banco["code"], random)
        val cuenta = clabe.substring(6, 17)
        val tarjeta = generateDebitCard()

        // Generate contact info
        val direccion = generateAddress()
        val telefono = generatePhone()
        val email = generateEmail(nombre, apellidoPaterno)

        // Generate fiscal regime
        val regimenFiscal = generateRegimenFiscal()

        return PersonaFisica(
            nombre = nombre,
            apellidoPaterno = apellidoPaterno,
            apellidoMaterno = apellidoMaterno,
            nombreCompleto = nombreCompleto,
            fechaNacimiento = fechaNacimiento,
            edad = edad,
            sexo = sex,
            sexoDescripcion = sexDesc,
            estadoNacimiento = estadoNacimiento,
            estadoNacimientoCode = estadoCode,
            rfc = rfc,
            curp = curp,
            nss = nss,
            banco = banco,
            clabe = clabe,
            cuenta = cuenta,
            tarjetaDebito = tarjeta,
            direccion = direccion,
            telefono = telefono,
            email = email,
            regimenFiscal = regimenFiscal
        )
    }

    /**
     * Generate a Persona Moral identity
     *
     * @param minYears Minimum years since constitution (default 1)
     * @param maxYears Maximum years since constitution (default 30)
     */
    @JvmOverloads
    fun generatePersonaMoral(
        minYears: Int = 1,
        maxYears: Int = 30
    ): PersonaMoral {
        // Generate company name
        val companyType = randomElement(companyTypes)
        val lastName = lastName()
        val suffix = randomElement(companySuffixes)
        val razonSocial = "$companyType $lastName $suffix"
        val nombreComercial = "$companyType $lastName"

        // Generate constitution date
        val fechaConstitucion = randomDate(minYears, maxYears)
        val antiguedad = DateUtils.calculateAge(fechaConstitucion)

        // Generate RFC
        val rfc = RfcGeneratorMoral(
            razonSocial = razonSocial,
            fechaConstitucion = fechaConstitucion
        ).generate()

        // Generate banking data
        val banco = generateBank()
        val clabe = ClabeUtils.generateCLABERandom(banco["code"], random)
        val cuenta = clabe.substring(6, 17)

        // Generate contact info
        val direccion = generateAddress()
        val telefono = generatePhone()
        val email = generateEmail(companyType.lowercase(), lastName)

        // Generate fiscal regime
        val regimenFiscal = generateRegimenFiscal(personaMoral = true)

        return PersonaMoral(
            razonSocial = razonSocial,
            nombreComercial = nombreComercial,
            fechaConstitucion = fechaConstitucion,
            antiguedad = antiguedad,
            rfc = rfc,
            banco = banco,
            clabe = clabe,
            cuenta = cuenta,
            direccion = direccion,
            telefono = telefono,
            email = email,
            regimenFiscal = regimenFiscal
        )
    }
}
