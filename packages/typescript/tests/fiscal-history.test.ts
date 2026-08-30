import { IMSSCalculator } from '../src/calculators/imss-calculator';
import {
  assertFiscalDataVerified,
  fiscalEntry,
  fiscalManifest,
  fiscalSources,
} from '../src/fiscal';

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

  test('preserves the local calendar date for Date inputs at the UMA boundary', () => {
    // Mimics Jan 31 at 20:00 in a UTC-06 locale: the instant is already Feb 1
    // in UTC, but the caller's local calendar date is still Jan 31.
    const january31Evening = new Date('2026-02-01T02:00:00.000Z');
    january31Evening.getFullYear = () => 2026;
    january31Evening.getMonth = () => 0;
    january31Evening.getDate = () => 31;

    expect(january31Evening.toISOString().startsWith('2026-02-01')).toBe(true);
    expect(IMSSCalculator.getUMAForDate(january31Evening).diaria).toBe(113.14);
  });

  test('rejects invalid calendar dates and dates from another exercise', () => {
    expect(() => IMSSCalculator.getUMAForDate('2026-02-31')).toThrow('Fecha inválida');
    expect(() =>
      IMSSCalculator.calcularCuotasObreroPatronales(500, 30, 2026, 2, '2025-12-31')
    ).toThrow('no pertenece al ejercicio 2026');
    expect(() =>
      IMSSCalculator.getCEAVPatronRate(315.04, 2026, 'general', '2025-12-31')
    ).toThrow('no pertenece al ejercicio 2026');
    expect(() => IMSSCalculator.calcularModalidad40(15000, 12000, 2026, '2025-12-31')).toThrow(
      'no pertenece al ejercicio 2026'
    );
    expect(() => IMSSCalculator.calcularModalidad10(10000, 2026, '2025-12-31')).toThrow(
      'no pertenece al ejercicio 2026'
    );
  });

  test('keeps CEAV patronal rates by exercise instead of overwriting history', () => {
    expect(IMSSCalculator.getCEAVPatronRate(500, 2024, 'general')).toBe(0.05331);
    expect(IMSSCalculator.getCEAVPatronRate(500, 2025, 'general')).toBe(0.06422);
    expect(IMSSCalculator.getCEAVPatronRate(500, 2026, 'general')).toBe(0.07513);

    expect(IMSSCalculator.getCEAVPatronRate(315.04, 2026, 'general')).toBe(0.0315);
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
    expect(IMSSCalculator.calcularModalidad40(10000, 8000, 2024).porcentaje_total).toBe(0.11681);
    expect(IMSSCalculator.calcularModalidad40(12000, 10000, 2025).porcentaje_total).toBe(0.12484);
    expect(IMSSCalculator.calcularModalidad40(15000, 12000, 2026).porcentaje_total).toBe(0.14438);
  });

  test('exposes provenance and verification status programmatically', () => {
    const manifest = fiscalManifest();
    expect(manifest.manifest_id).toBe('catalogmx.fiscal');
    expect(manifest.content_sha256).toMatch(/^[0-9a-f]{64}$/);

    const uma2026 = assertFiscalDataVerified('uma', 2026);
    expect(uma2026.valid_from).toBe('2026-02-01');
    expect(uma2026.values).toMatchObject({ daily: 117.31, monthly: 3566.22 });
    expect(uma2026.sha256).toMatch(/^[0-9a-f]{64}$/);
    expect(fiscalSources('uma', 2026)[0]?.source?.authority).toBe('INEGI');

    expect(assertFiscalDataVerified('minimum_wage', 2024).valid_to).toBe('2024-12-31');
    expect(assertFiscalDataVerified('minimum_wage', 2025).valid_to).toBe('2025-12-31');
    expect(assertFiscalDataVerified('minimum_wage', 2026).valid_to).toBeNull();

    expect(fiscalEntry('isr_payroll', 2026)?.status).toBe('pending_review');
    expect(() => assertFiscalDataVerified('isr_payroll', 2026)).toThrow('pending_review');
    expect(fiscalEntry('imss_modalidad_10', 2026)?.status).toBe('pending_review');
  });

  test('does not allow callers to mutate verification status', () => {
    const manifest = fiscalManifest();
    const pending = fiscalEntry('isr_payroll', 2026);
    expect(pending).toBeDefined();
    expect(Object.isFrozen(manifest)).toBe(true);
    expect(Object.isFrozen(manifest.datasets.isr_payroll.entries)).toBe(true);
    expect(Object.isFrozen(pending)).toBe(true);

    expect(Reflect.set(pending as object, 'status', 'verified')).toBe(false);
    expect(fiscalEntry('isr_payroll', 2026)?.status).toBe('pending_review');
    expect(() => assertFiscalDataVerified('isr_payroll', 2026)).toThrow('pending_review');
  });
});
