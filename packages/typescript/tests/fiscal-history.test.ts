import { IMSSCalculator } from '../src/calculators/imss-calculator';

describe('historical fiscal parameters', () => {
  test('keeps official UMA history and the January/February 2026 boundary', () => {
    expect(IMSSCalculator.getUMA(2024)).toMatchObject({
      diaria: 108.57,
      mensual: 3300.53,
      anual: 39606.36,
    });
    expect(IMSSCalculator.getUMA(2025)).toMatchObject({
      diaria: 113.14,
      mensual: 3439.46,
      anual: 41273.52,
    });
    expect(IMSSCalculator.getUMA(2026)).toMatchObject({
      diaria: 117.31,
      mensual: 3566.22,
      anual: 42794.64,
    });

    expect(IMSSCalculator.getUMAForDate('2026-01-15').diaria).toBe(113.14);
    expect(IMSSCalculator.getUMAForDate('2026-02-01').diaria).toBe(117.31);
  });

  test('keeps CEAV patronal rates by exercise instead of overwriting history', () => {
    expect(IMSSCalculator.getCEAVPatronRate(500, 2024)).toBe(0.05331);
    expect(IMSSCalculator.getCEAVPatronRate(500, 2025)).toBe(0.06422);
    expect(IMSSCalculator.getCEAVPatronRate(500, 2026)).toBe(0.07513);

    expect(IMSSCalculator.getCEAVPatronRate(315.04, 2026)).toBe(0.0315);
  });

  test('uses 2026 CEAV in January while keeping the still-valid 2025 UMA', () => {
    const january = IMSSCalculator.calcularCuotasObreroPatronales(500, 30, 2026, 2, '2026-01-15');
    const february = IMSSCalculator.calcularCuotasObreroPatronales(500, 30, 2026, 2, '2026-02-15');

    expect(january.uma_diaria).toBe(113.14);
    expect(february.uma_diaria).toBe(117.31);
    expect(january.ceav_patron_rate).toBe(0.07513);
    expect(february.ceav_patron_rate).toBe(0.07513);
  });

  test('uses one UMA, not three UMAs, for the fixed sickness/maternity quota', () => {
    const result = IMSSCalculator.calcularCuotasObreroPatronales(500, 30, 2026, 2);
    expect(result.cuotas_patron.enfermedad_mat_cuota_fija).toBeCloseTo(717.9372, 6);
  });

  test('keeps historical Modalidad 40 rates', () => {
    expect(IMSSCalculator.calcularModalidad40(10000, 2024).porcentaje_total).toBe(0.11681);
    expect(IMSSCalculator.calcularModalidad40(12000, 2025).porcentaje_total).toBe(0.12484);
    expect(IMSSCalculator.calcularModalidad40(15000, 2026).porcentaje_total).toBe(0.14438);
  });
});
