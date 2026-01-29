package com.openbancor.catalogmx.calculators

import com.openbancor.catalogmx.catalogs.base.BaseCatalog
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File

/**
 * Supported tax years
 */
enum class IsrYear(val value: Int) {
    YEAR_2024(2024),
    YEAR_2025(2025),
    YEAR_2026(2026)
}

/**
 * Supported payment periods
 */
enum class IsrPeriod(val periodValue: String, val jsonKey: String, val factor: Double) {
    DIARIA("diaria", "daily", 30.4),
    SEMANAL("semanal", "weekly", 4.33),
    DECENAL("decenal", "monthly", 3.0),
    QUINCENAL("quincenal", "biweekly", 2.0),
    MENSUAL("mensual", "monthly", 1.0),
    ANUAL("anual", "annual", 1.0 / 12.0)
}

/**
 * Tax bracket structure
 */
data class IsrBracket(
    val limiteInferior: Double,
    val limiteSuperior: Double,
    val cuotaFija: Double,
    val tasa: Double
) {
    fun toMap(): Map<String, Any?> = mapOf(
        "limiteInferior" to limiteInferior,
        "limiteSuperior" to if (limiteSuperior == Double.MAX_VALUE) null else limiteSuperior,
        "cuotaFija" to cuotaFija,
        "tasa" to tasa
    )
}

/**
 * Complete ISR calculation result
 */
data class IsrCalculationResult(
    val ingresoGravable: Double,
    val periodo: String,
    val year: Int,
    val ingresoMensualizado: Double,
    val bracket: IsrBracket,
    val excedente: Double,
    val impuestoMarginal: Double,
    val isrAntesSubsidio: Double,
    val subsidio: Double,
    val isrFinal: Double,
    val tasaEfectiva: Double
) {
    fun toMap(): Map<String, Any?> = mapOf(
        "ingresoGravable" to ingresoGravable,
        "periodo" to periodo,
        "year" to year,
        "ingresoMensualizado" to ingresoMensualizado,
        "bracket" to bracket.toMap(),
        "excedente" to excedente,
        "impuestoMarginal" to impuestoMarginal,
        "isrAntesSubsidio" to isrAntesSubsidio,
        "subsidio" to subsidio,
        "isrFinal" to isrFinal,
        "tasaEfectiva" to tasaEfectiva
    )
}

/**
 * ISR (Impuesto Sobre la Renta) Calculator for Mexico
 *
 * Supports multi-year calculations: 2024, 2025, 2026
 * Uses centralized JSON tables from shared-data
 *
 * Official source: Anexo 8 RMF (Resolución Miscelánea Fiscal)
 */
object IsrCalculator {
    private var isrTables: JsonObject? = null
    private val json = Json { ignoreUnknownKeys = true }

    // Embedded ISR tables for standalone usage (mensual 2026)
    private val embeddedBrackets2026Mensual = listOf(
        IsrBracket(0.01, 746.04, 0.00, 1.92),
        IsrBracket(746.05, 6332.05, 14.32, 6.40),
        IsrBracket(6332.06, 11128.01, 371.83, 10.88),
        IsrBracket(11128.02, 12935.82, 893.63, 16.00),
        IsrBracket(12935.83, 15487.71, 1182.88, 17.92),
        IsrBracket(15487.72, 31236.49, 1640.18, 21.36),
        IsrBracket(31236.50, 49233.00, 5004.12, 23.52),
        IsrBracket(49233.01, 93993.90, 9236.89, 30.00),
        IsrBracket(93993.91, 125325.20, 22665.17, 32.00),
        IsrBracket(125325.21, 375975.61, 32691.18, 34.00),
        IsrBracket(375975.62, Double.MAX_VALUE, 117912.32, 35.00)
    )

    private fun loadIsrTables(): JsonObject {
        isrTables?.let { return it }

        val candidates = listOf(
            "../shared-data/isr-tables.json",
            "../../shared-data/isr-tables.json",
            "../../../shared-data/isr-tables.json",
            "packages/shared-data/isr-tables.json"
        )

        for (path in candidates) {
            try {
                val file = File(path)
                if (file.exists()) {
                    val jsonString = file.readText()
                    isrTables = json.parseToJsonElement(jsonString).jsonObject
                    return isrTables!!
                }
            } catch (e: Exception) {
                continue
            }
        }

        // Return empty object if not found (will use embedded data)
        return JsonObject(emptyMap())
    }

    /**
     * Get ISR tax brackets for a specific year and period
     */
    @JvmStatic
    fun getIsrBrackets(year: IsrYear, period: IsrPeriod): List<IsrBracket> {
        val tables = loadIsrTables()

        if (tables.isEmpty()) {
            // Use embedded data for 2026 mensual
            if (year == IsrYear.YEAR_2026 && period == IsrPeriod.MENSUAL) {
                return embeddedBrackets2026Mensual
            }
            // For other years/periods, return empty and let calculation handle it
            return emptyList()
        }

        return try {
            val brackets = tables["brackets"]!!.jsonObject[year.value.toString()]!!
                .jsonObject[period.jsonKey]!!.jsonArray

            brackets.map { b ->
                val obj = b.jsonObject
                IsrBracket(
                    limiteInferior = obj["limiteInferior"]!!.jsonPrimitive.content.toDouble(),
                    limiteSuperior = obj["limiteSuperior"]?.jsonPrimitive?.content?.toDoubleOrNull()
                        ?: Double.MAX_VALUE,
                    cuotaFija = obj["cuotaFija"]!!.jsonPrimitive.content.toDouble(),
                    tasa = obj["tasa"]!!.jsonPrimitive.content.toDouble()
                )
            }
        } catch (e: Exception) {
            if (year == IsrYear.YEAR_2026 && period == IsrPeriod.MENSUAL) {
                embeddedBrackets2026Mensual
            } else {
                emptyList()
            }
        }
    }

    /**
     * Calculate employment subsidy (subsidio al empleo)
     */
    @JvmStatic
    fun calculateSubsidy(income: Double, year: IsrYear): Double {
        val tables = loadIsrTables()

        if (tables.isEmpty()) {
            // 2026 flat subsidy: $500 monthly for income <= $10,000
            return if (year == IsrYear.YEAR_2026 && income <= 10000.0) 500.0 else 0.0
        }

        return try {
            val subsidyData = tables["subsidies"]!!.jsonObject[year.value.toString()]!!.jsonObject

            if (subsidyData["type"]?.jsonPrimitive?.content == "tiered") {
                // 2024: tiered system
                val monthly = subsidyData["monthly"]!!.jsonArray
                for (s in monthly) {
                    val obj = s.jsonObject
                    val desde = obj["desde"]!!.jsonPrimitive.content.toDouble()
                    val hasta = obj["hasta"]?.jsonPrimitive?.content?.toDoubleOrNull() ?: Double.MAX_VALUE
                    if (income >= desde && income <= hasta) {
                        return obj["subsidio"]!!.jsonPrimitive.content.toDouble()
                    }
                }
                0.0
            } else {
                // 2025/2026: flat system
                val monthly = subsidyData["monthly"]!!.jsonObject
                val maxIncome = monthly["maxIncome"]!!.jsonPrimitive.content.toDouble()
                val amount = monthly["amount"]!!.jsonPrimitive.content.toDouble()
                if (income <= maxIncome) amount else 0.0
            }
        } catch (e: Exception) {
            // Fallback for 2026
            if (year == IsrYear.YEAR_2026 && income <= 10000.0) 500.0 else 0.0
        }
    }

    /**
     * Calculate ISR (Income Tax) for Mexico
     *
     * @param ingresoGravable Taxable income for the period
     * @param periodo Payment period (default: mensual)
     * @param year Tax year (default: 2026)
     * @return Complete calculation result with breakdown
     */
    @JvmStatic
    @JvmOverloads
    fun calculateIsr(
        ingresoGravable: Double,
        periodo: IsrPeriod = IsrPeriod.MENSUAL,
        year: IsrYear = IsrYear.YEAR_2026
    ): IsrCalculationResult {
        // For 2026, use period-specific tables directly
        val usePeriodTables = year == IsrYear.YEAR_2026 &&
            periodo in listOf(
                IsrPeriod.DIARIA, IsrPeriod.SEMANAL, IsrPeriod.QUINCENAL,
                IsrPeriod.MENSUAL, IsrPeriod.ANUAL
            )

        if (usePeriodTables) {
            val brackets = getIsrBrackets(year, periodo).ifEmpty {
                getIsrBrackets(IsrYear.YEAR_2026, IsrPeriod.MENSUAL)
            }

            // Find applicable bracket
            val bracket = brackets.firstOrNull { b ->
                ingresoGravable >= b.limiteInferior && ingresoGravable <= b.limiteSuperior
            } ?: brackets.last()

            // Calculate excess over lower limit
            val excedente = ingresoGravable - bracket.limiteInferior

            // Calculate marginal tax
            val impuestoMarginal = excedente * (bracket.tasa / 100)

            // Add fixed fee
            val isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal

            // Calculate subsidy (convert to monthly equivalent)
            val factor = periodo.factor
            val ingresoMensualEquivalente = ingresoGravable * factor
            val subsidioMensual = calculateSubsidy(ingresoMensualEquivalente, year)
            val subsidioProrrateado = subsidioMensual / factor

            // Final ISR
            val isrFinal = maxOf(0.0, isrAntesSubsidio - subsidioProrrateado)

            val tasaEfectiva = if (ingresoGravable > 0) (isrFinal / ingresoGravable * 100) else 0.0

            return IsrCalculationResult(
                ingresoGravable = ingresoGravable,
                periodo = periodo.periodValue,
                year = year.value,
                ingresoMensualizado = ingresoMensualEquivalente,
                bracket = bracket,
                excedente = excedente,
                impuestoMarginal = impuestoMarginal,
                isrAntesSubsidio = isrAntesSubsidio,
                subsidio = subsidioProrrateado,
                isrFinal = isrFinal,
                tasaEfectiva = tasaEfectiva
            )
        }

        // For 2024/2025 or decenal period, use factor-based conversion
        val brackets = getIsrBrackets(year, IsrPeriod.MENSUAL).ifEmpty {
            embeddedBrackets2026Mensual
        }

        // Convert to monthly
        val factor = periodo.factor
        val ingresoMensualizado = ingresoGravable * factor

        // Find applicable bracket
        val bracket = brackets.firstOrNull { b ->
            ingresoMensualizado >= b.limiteInferior && ingresoMensualizado <= b.limiteSuperior
        } ?: brackets.last()

        // Calculate excess over lower limit
        val excedente = ingresoMensualizado - bracket.limiteInferior

        // Calculate marginal tax
        val impuestoMarginal = excedente * (bracket.tasa / 100)

        // Add fixed fee
        val isrAntesSubsidio = bracket.cuotaFija + impuestoMarginal

        // Calculate subsidy
        val subsidio = calculateSubsidy(ingresoMensualizado, year)

        // Final ISR (monthly)
        val isrFinalMensual = maxOf(0.0, isrAntesSubsidio - subsidio)

        // Convert back to original period
        val isrPeriodo = isrFinalMensual / factor

        val tasaEfectiva = if (ingresoGravable > 0) (isrPeriodo / ingresoGravable * 100) else 0.0

        return IsrCalculationResult(
            ingresoGravable = ingresoGravable,
            periodo = periodo.periodValue,
            year = year.value,
            ingresoMensualizado = ingresoMensualizado,
            bracket = bracket,
            excedente = excedente,
            impuestoMarginal = impuestoMarginal,
            isrAntesSubsidio = isrAntesSubsidio,
            subsidio = subsidio,
            isrFinal = isrPeriodo,
            tasaEfectiva = tasaEfectiva
        )
    }
}
