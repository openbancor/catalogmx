/**
 * Tests for tax calculators
 */

import {
  ISRCalculator,
  IVACalculator,
  IEPSCalculator,
  RetencionCalculator,
  ImpuestosLocalesCalculator,
} from '../src/calculators';

describe('ISR Calculator', () => {
  test('should calculate ISR for monthly salary', () => {
    const result = ISRCalculator.calcular(15000, 2025, 'mensual', true);
    expect(result).toBeDefined();
    expect(result.ingreso_gravable).toBe(15000);
    expect(result.isr_causado).toBeGreaterThan(0);
    expect(result.tasa_efectiva).toBeGreaterThan(0);
  });

  test('should calculate ISR with subsidio al empleo', () => {
    const result = ISRCalculator.calcular(7000, 2025, 'mensual', true);
    expect(result.subsidio_empleo).toBeGreaterThan(0);
    expect(result.isr_a_retener).toBeLessThan(result.isr_causado);
  });

  test('should calculate net salary', () => {
    const salarioBruto = 20000;
    const salarioNeto = ISRCalculator.calcularSalarioNeto(salarioBruto, 2025, 'mensual');
    expect(salarioNeto).toBeLessThan(salarioBruto);
    expect(salarioNeto).toBeGreaterThan(0);
  });

  test('should get available years', () => {
    const años = ISRCalculator.getAñosDisponibles();
    expect(años.length).toBeGreaterThan(0);
    expect(años).toContain(2025);
    expect(años).toContain(2024);
  });

  test('should calculate marginal tax rate', () => {
    const tasa = ISRCalculator.calcularTasaMarginal(50000, 2025, 'mensual');
    expect(tasa).toBeGreaterThan(0);
    expect(tasa).toBeLessThanOrEqual(35); // Max 35%
  });

  test('should calculate annual ISR from monthly incomes', () => {
    const ingresosMensuales = Array(12).fill(15000);
    const isrAnual = ISRCalculator.calcularISRAnual(ingresosMensuales, 2025);
    expect(isrAnual).toBeGreaterThan(0);
  });
});

describe('IVA Calculator', () => {
  test('should calculate IVA at general rate (16%)', () => {
    const result = IVACalculator.calcular(1000, 'general');
    expect(result.tasa).toBe(16);
    expect(result.iva).toBe(160);
    expect(result.total_con_iva).toBe(1160);
  });

  test('should calculate IVA at frontier rate (8%)', () => {
    const result = IVACalculator.calcular(1000, 'frontera');
    expect(result.tasa).toBe(8);
    expect(result.iva).toBe(80);
    expect(result.total_con_iva).toBe(1080);
  });

  test('should calculate tasa cero (0%)', () => {
    const result = IVACalculator.calcular(1000, 'tasa_cero');
    expect(result.tasa).toBe(0);
    expect(result.iva).toBe(0);
    expect(result.total_con_iva).toBe(1000);
  });

  test('should calculate IVA incluido (breakdown)', () => {
    const result = IVACalculator.calcularIncluido(1160, 'general');
    expect(result.base).toBeCloseTo(1000, 2);
    expect(result.iva).toBeCloseTo(160, 2);
  });

  test('should get all tasas', () => {
    const tasas = IVACalculator.getAllTasas();
    expect(tasas.length).toBeGreaterThan(0);
  });
});

describe('IEPS Calculator', () => {
  test('should calculate IEPS ad-valorem', () => {
    const result = IEPSCalculator.calcularAdValorem(1000, 26.5);
    expect(result.ieps).toBe(265);
    expect(result.tipo_calculo).toBe('ad_valorem');
  });

  test('should calculate IEPS cuota fija', () => {
    const result = IEPSCalculator.calcularCuotaFija(10, 1.0, 'litro'); // 10 litros a $1.00/litro
    expect(result.ieps).toBe(10);
    expect(result.tipo_calculo).toBe('cuota_fija');
    expect(result.unidad).toBe('litro');
  });

  test('should calculate IEPS for beer (26.5%)', () => {
    const result = IEPSCalculator.calcularBebidasAlcoholicas(1000, 5); // Cerveza 5°
    expect(result.tasa).toBe(26.5);
    expect(result.ieps).toBe(265);
  });

  test('should calculate IEPS for spirits (53%)', () => {
    const result = IEPSCalculator.calcularBebidasAlcoholicas(1000, 40); // Tequila 40°
    expect(result.tasa).toBe(53);
    expect(result.ieps).toBe(530);
  });

  test('should calculate IEPS for cigarettes', () => {
    const result = IEPSCalculator.calcularCigarros(100, 20); // Cajetilla 20 cigarros
    const expectedAdValorem = 100 * 1.6; // 160%
    const expectedCuotaFija = 20 * 0.508;
    expect(result.ieps).toBeCloseTo(expectedAdValorem + expectedCuotaFija, 2);
  });

  test('should get all categories', () => {
    const categorias = IEPSCalculator.getAllCategorias();
    expect(categorias.length).toBeGreaterThan(0);
  });
});

describe('Retención Calculator', () => {
  test('should calculate honorarios retention (10%)', () => {
    const result = RetencionCalculator.calcularHonorarios(10000);
    expect(result.tasa).toBe(10);
    expect(result.retencion).toBe(1000);
    expect(result.concepto).toBe('honorarios');
  });

  test('should calculate arrendamiento retention (10%)', () => {
    const result = RetencionCalculator.calcularArrendamiento(20000);
    expect(result.tasa).toBe(10);
    expect(result.retencion).toBe(2000);
  });

  test('should calculate fletes retention (4%)', () => {
    const result = RetencionCalculator.calcularFletes(50000);
    expect(result.tasa).toBe(4);
    expect(result.retencion).toBe(2000);
  });

  test('should calculate IVA retention (66.67%)', () => {
    const result = RetencionCalculator.calcularRetencionIVA(1600, 'servicios_profesionales');
    expect(result.tasa).toBe(66.67);
    expect(result.retencion).toBeCloseTo(1066.72, 2); // 2/3 de 1600
  });

  test('should get all ISR retentions', () => {
    const retenciones = RetencionCalculator.getAllRetencionesISR();
    expect(retenciones.length).toBeGreaterThan(0);
  });

  test('should get all IVA retentions', () => {
    const retenciones = RetencionCalculator.getAllRetencionesIVA();
    expect(retenciones.length).toBeGreaterThan(0);
  });
});

describe('Impuestos Locales Calculator', () => {
  test('should calculate payroll tax for CDMX (3%)', () => {
    const impuesto = ImpuestosLocalesCalculator.calcularImpuestoNomina(100000, '09');
    expect(impuesto).toBe(3000); // 3% de 100,000
  });

  test('should calculate payroll tax for Nuevo León (3%)', () => {
    const impuesto = ImpuestosLocalesCalculator.calcularImpuestoNomina(50000, '19');
    expect(impuesto).toBe(1500); // 3% de 50,000
  });

  test('should calculate hospedaje tax for Quintana Roo (3%)', () => {
    const impuesto = ImpuestosLocalesCalculator.calcularImpuestoHospedaje(5000, '23');
    expect(impuesto).toBe(150); // 3% de 5,000
  });

  test('should get all payroll taxes', () => {
    const impuestos = ImpuestosLocalesCalculator.getAllImpuestosNomina();
    expect(impuestos.length).toBe(32); // 32 estados
  });

  test('should get all hospedaje taxes', () => {
    const impuestos = ImpuestosLocalesCalculator.getAllImpuestosHospedaje();
    expect(impuestos.length).toBe(32); // 32 estados
  });

  test('should get specific state payroll tax', () => {
    const impuesto = ImpuestosLocalesCalculator.getImpuestoNomina('14'); // Jalisco
    expect(impuesto).toBeDefined();
    expect(impuesto?.estado).toBe('Jalisco');
    expect(impuesto?.tasa).toBe(2.0);
  });
});
