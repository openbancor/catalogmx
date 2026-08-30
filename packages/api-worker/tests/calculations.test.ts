import { calculateImss, calculateIsr } from '../src/calculations';

describe('ISR calculation adapter', () => {
  test.each(['diario', 'semanal', 'quincenal', 'mensual', 'anual'] as const)(
    'delegates the %s period to the loaded fiscal table',
    (periodo) => {
      const result = calculateIsr({ base_gravable: 15000, periodo, ejercicio: 2026 });

      expect(result.periodo).toBe(periodo);
      expect(result.ejercicio).toBe(2026);
      expect(result.retencion_mensual).toBeGreaterThanOrEqual(0);
      expect(result.tabla_aplicada).toMatchObject({ ejercicio: 2026, periodicidad: periodo });
      expect(result.regla_aplicada.formulas).toMatchObject({
        excedente: 'ingreso_tabla - limite_inferior',
        impuesto_marginal: 'excedente * tasa_marginal',
      });
    }
  );

  test('exposes exact calculator values separately from rounded API values', () => {
    const result = calculateIsr({ base_gravable: 15000, periodo: 'mensual', ejercicio: 2026 });

    expect(result.resultado.isr_a_retener).toBe(
      Number(result.auditoria.interno.isr_a_retener.toFixed(2))
    );
    expect(result.auditoria.redondeo_decimales).toBe(2);
    expect(result.tabla_aplicada).toMatchObject({
      limite_inferior: expect.any(Number),
      limite_superior: expect.any(Number),
      cuota_fija: expect.any(Number),
      tasa_marginal: expect.any(Number),
      subsidio: expect.any(Number),
    });
  });

  test.each([
    [{ base_gravable: 15000, periodo: 'mensual', ejercicio: 1900 }, 'unsupported_fiscal_data'],
    [{ base_gravable: 15000, periodo: 'trimestral', ejercicio: 2026 }, 'unsupported_fiscal_data'],
    [{ base_gravable: '15000', periodo: 'mensual', ejercicio: 2026 }, 'invalid_request'],
    [{ base_gravable: -1, periodo: 'mensual', ejercicio: 2026 }, 'invalid_request'],
    [
      { base_gravable: 15000, periodo: 'mensual', ejercicio: 2026, rfc: 'BACL891217NJ5' },
      'invalid_request',
    ],
    [{ base_gravable: 15000, periodo: 123, ejercicio: 2026 }, 'invalid_request'],
    [{ base_gravable: 15000, periodo: 'mensual', ejercicio: 1899 }, 'invalid_request'],
    [{ base_gravable: 1_000_000_001, periodo: 'mensual', ejercicio: 2026 }, 'invalid_request'],
  ])('rejects invalid ISR input %j with %s', (body, code) => {
    expect(() => calculateIsr(body)).toThrow(
      expect.objectContaining({ status: code === 'invalid_request' ? 400 : 422, code })
    );
  });

  test('uses the monthly table path for a supported pre-2026 exercise', () => {
    const result = calculateIsr({ base_gravable: 15000, periodo: 'semanal', ejercicio: 2025 });

    expect(result.ejercicio).toBe(2025);
    expect(result.tabla_aplicada.ingreso_tabla).toBeGreaterThan(result.resultado.ingreso_gravable);
  });

  test('reports an open-ended upper limit for the top fiscal bracket', () => {
    const result = calculateIsr({ base_gravable: 1_000_000, periodo: 'mensual', ejercicio: 2026 });

    expect(result.tabla_aplicada.limite_superior).toBeNull();
  });

  test('serializes deterministic output for identical requests', () => {
    const body = { base_gravable: 15000, periodo: 'mensual' as const, ejercicio: 2026 };
    expect(JSON.stringify(calculateIsr(body))).toBe(JSON.stringify(calculateIsr(body)));
  });
});

describe('IMSS calculation adapter', () => {
  test('delegates with risk class 1 and returns complete component maps', () => {
    const result = calculateImss({ sdi: 500, dias_cotizados: 30, ejercicio: 2026 });

    expect(result.cuotas_obrera).toBeGreaterThanOrEqual(0);
    expect(result.cuotas_patronal).toBeGreaterThan(result.cuotas_obrera);
    expect(result.desglose.cuotas_obrera).toEqual(
      expect.objectContaining({ enfermedad_mat_dinero: expect.any(Number) })
    );
    expect(result.desglose.cuotas_patronal).toEqual(
      expect.objectContaining({ riesgo_trabajo: expect.any(Number) })
    );
    expect(result.regla_aplicada).toMatchObject({
      ejercicio: 2026,
      clase_riesgo: 1,
      uma: expect.objectContaining({ diaria: expect.any(Number) }),
      formula_identificadores: expect.arrayContaining(['cuotas_imss', 'riesgo_trabajo']),
    });
  });

  test('rounds only the public projection and keeps the internal result', () => {
    const result = calculateImss({ sdi: 500, dias_cotizados: 30, ejercicio: 2026 });

    expect(result.auditoria.interno.total_imss).toBeGreaterThan(0);
    expect(result.auditoria.redondeo_decimales).toBe(2);
    expect(result.resultado.total_imss).toBe(
      Number(result.auditoria.interno.total_imss.toFixed(2))
    );
  });

  test('retains rounded UMA and source-precision CEAV rate in the public result', () => {
    const result = calculateImss({ sdi: 500, dias_cotizados: 30, ejercicio: 2026 });

    expect(result.resultado.uma_diaria).toBe(
      Number(result.auditoria.interno.uma_diaria.toFixed(2))
    );
    expect(result.resultado.ceav_patron_rate).toBe(0.07513);
    expect(result.resultado.ceav_patron_rate).toBe(result.auditoria.interno.ceav_patron_rate);
  });

  test('rejects an IMSS daily salary below the 2026 general minimum as invalid input', () => {
    expect(() => calculateImss({ sdi: 315.03, dias_cotizados: 30, ejercicio: 2026 })).toThrow(
      expect.objectContaining({ status: 400, code: 'invalid_request' })
    );
  });

  test('accepts the exact 2026 general minimum daily salary', () => {
    const result = calculateImss({ sdi: 315.04, dias_cotizados: 30, ejercicio: 2026 });

    expect(result.resultado.salario_diario).toBe(315.04);
  });

  test.each([
    [{ sdi: 500, dias_cotizados: 30, ejercicio: 1900 }, 422],
    [{ sdi: 500, dias_cotizados: 0.5, ejercicio: 2026 }, 400],
    [{ sdi: 500, dias_cotizados: 30, ejercicio: 2026, nombre: 'Empleado' }, 400],
    [{ sdi: Number.POSITIVE_INFINITY, dias_cotizados: 30, ejercicio: 2026 }, 400],
    [{ sdi: 500, dias_cotizados: 0, ejercicio: 2026 }, 400],
    [{ sdi: 1_000_000_001, dias_cotizados: 30, ejercicio: 2026 }, 400],
  ])('rejects invalid IMSS input %j with status %s', (body, status) => {
    expect(() => calculateImss(body)).toThrow(expect.objectContaining({ status }));
  });
});
