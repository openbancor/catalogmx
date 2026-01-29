package com.openbancor.catalogmx.calculators

import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class IsrCalculatorTest {

    @Test
    fun `should calculate ISR for monthly income`() {
        val result = IsrCalculator.calculateIsr(15000.0)

        assertEquals(15000.0, result.ingresoGravable)
        assertEquals("mensual", result.periodo)
        assertEquals(2026, result.year)
        assertTrue(result.isrFinal > 0)
        assertTrue(result.tasaEfectiva > 0)
    }

    @Test
    fun `should calculate zero ISR for zero income`() {
        val result = IsrCalculator.calculateIsr(0.0)

        assertEquals(0.0, result.ingresoGravable)
        assertEquals(0.0, result.isrFinal)
        assertEquals(0.0, result.tasaEfectiva)
    }

    @Test
    fun `should apply employment subsidy for low income`() {
        // Income that qualifies for subsidy (less than 10000)
        val result = IsrCalculator.calculateIsr(8000.0)

        assertTrue(result.subsidio > 0 || result.isrFinal == 0.0,
            "Low income should receive subsidy or zero ISR")
    }

    @Test
    fun `should not apply subsidy for high income`() {
        val result = IsrCalculator.calculateIsr(50000.0)

        assertEquals(0.0, result.subsidio)
        assertTrue(result.isrFinal > 0)
    }

    @Test
    fun `should find correct bracket for various income levels`() {
        // Test lower bracket
        val lowIncome = IsrCalculator.calculateIsr(500.0)
        assertEquals(1.92, lowIncome.bracket.tasa)

        // Test middle bracket
        val midIncome = IsrCalculator.calculateIsr(15000.0)
        assertTrue(midIncome.bracket.tasa > 1.92)

        // Test higher bracket
        val highIncome = IsrCalculator.calculateIsr(100000.0)
        assertTrue(highIncome.bracket.tasa >= 30.0)
    }

    @Test
    fun `should calculate excedente correctly`() {
        val result = IsrCalculator.calculateIsr(10000.0)

        // Excedente = income - lower limit of bracket
        assertTrue(result.excedente >= 0)
        assertTrue(result.excedente <= result.ingresoGravable)
    }

    @Test
    fun `should calculate marginal tax correctly`() {
        val result = IsrCalculator.calculateIsr(15000.0)

        // Marginal tax = excedente * (tasa / 100)
        val expectedMarginal = result.excedente * (result.bracket.tasa / 100)
        assertEquals(expectedMarginal, result.impuestoMarginal, 0.01)
    }

    @Test
    fun `should calculate ISR antes subsidio correctly`() {
        val result = IsrCalculator.calculateIsr(20000.0)

        // ISR antes subsidio = cuota fija + impuesto marginal
        val expectedIsrAntes = result.bracket.cuotaFija + result.impuestoMarginal
        assertEquals(expectedIsrAntes, result.isrAntesSubsidio, 0.01)
    }

    @Test
    fun `should calculate effective rate correctly`() {
        val result = IsrCalculator.calculateIsr(25000.0)

        // Effective rate = (ISR final / income) * 100
        val expectedRate = (result.isrFinal / result.ingresoGravable) * 100
        assertEquals(expectedRate, result.tasaEfectiva, 0.01)
    }

    @Test
    fun `should handle weekly period`() {
        val result = IsrCalculator.calculateIsr(3000.0, periodo = IsrPeriod.SEMANAL)

        assertEquals("semanal", result.periodo)
        // Monthly equivalent should be approximately 3000 * 4.33
        assertTrue(result.ingresoMensualizado > result.ingresoGravable)
    }

    @Test
    fun `should handle biweekly period`() {
        val result = IsrCalculator.calculateIsr(7500.0, periodo = IsrPeriod.QUINCENAL)

        assertEquals("quincenal", result.periodo)
        // Monthly equivalent should be approximately 7500 * 2
        assertEquals(7500.0 * 2, result.ingresoMensualizado, 100.0)
    }

    @Test
    fun `should handle annual period`() {
        val result = IsrCalculator.calculateIsr(180000.0, periodo = IsrPeriod.ANUAL)

        assertEquals("anual", result.periodo)
        // Monthly equivalent should be 180000 / 12
        assertEquals(180000.0 / 12, result.ingresoMensualizado, 100.0)
    }

    @Test
    fun `should return ISR brackets for 2026 mensual`() {
        val brackets = IsrCalculator.getIsrBrackets(IsrYear.YEAR_2026, IsrPeriod.MENSUAL)

        assertTrue(brackets.isNotEmpty())
        // First bracket should start at 0.01
        assertEquals(0.01, brackets.first().limiteInferior, 0.01)
        // Last bracket should have high upper limit
        assertEquals(Double.MAX_VALUE, brackets.last().limiteSuperior)
    }

    @Test
    fun `brackets should be sorted by lower limit`() {
        val brackets = IsrCalculator.getIsrBrackets(IsrYear.YEAR_2026, IsrPeriod.MENSUAL)

        for (i in 0 until brackets.size - 1) {
            assertTrue(brackets[i].limiteInferior < brackets[i + 1].limiteInferior)
        }
    }

    @Test
    fun `ISR result should be convertible to map`() {
        val result = IsrCalculator.calculateIsr(15000.0)
        val map = result.toMap()

        assertEquals(15000.0, map["ingresoGravable"])
        assertEquals("mensual", map["periodo"])
        assertEquals(2026, map["year"])
        assertTrue(map.containsKey("bracket"))
        assertTrue(map.containsKey("isrFinal"))
    }

    @Test
    fun `should calculate subsidy for various income levels`() {
        // Below subsidy threshold
        val lowSubsidy = IsrCalculator.calculateSubsidy(5000.0, IsrYear.YEAR_2026)
        assertTrue(lowSubsidy >= 0)

        // At threshold
        val atThreshold = IsrCalculator.calculateSubsidy(10000.0, IsrYear.YEAR_2026)
        assertTrue(atThreshold >= 0)

        // Above threshold
        val noSubsidy = IsrCalculator.calculateSubsidy(15000.0, IsrYear.YEAR_2026)
        assertEquals(0.0, noSubsidy)
    }

    @Test
    fun `progressive tax rates should increase with income`() {
        val incomes = listOf(1000.0, 10000.0, 30000.0, 50000.0, 100000.0)
        var previousRate = 0.0

        for (income in incomes) {
            val result = IsrCalculator.calculateIsr(income)
            if (income > 1000.0) {
                assertTrue(result.bracket.tasa >= previousRate,
                    "Tax rate should increase or stay same with income")
            }
            previousRate = result.bracket.tasa
        }
    }
}
