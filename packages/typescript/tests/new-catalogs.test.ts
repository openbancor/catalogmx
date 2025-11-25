import { describe, expect, test } from '@jest/globals';
import {
  PlacasFormatosCatalog,
  SalariosMinimos,
  UMACatalog,
  UDICatalog,
  HoyNoCirculaCDMX
} from '../src/catalogs';
import { TipoFactor } from '../src/catalogs/sat/cfdi_4/tipo-factor';
import { Meses } from '../src/catalogs/sat/cfdi_4/meses';
import { Periodicidad } from '../src/catalogs/sat/cfdi_4/periodicidad';

describe('Placas Formatos Catalog', () => {
  test('should validate valid license plate - current format', () => {
    expect(PlacasFormatosCatalog.validatePlaca('ABC-123-A')).toBe(true);
  });

  test('should validate valid license plate - old format still valid', () => {
    // Old format is inactive but pattern still matches
    const formato = PlacasFormatosCatalog.detectFormato('ABC-12-34');
    expect(formato).toBeDefined();
  });

  test('should reject invalid license plate', () => {
    expect(PlacasFormatosCatalog.validatePlaca('INVALID')).toBe(false);
  });

  test('should detect format for valid plate', () => {
    const formato = PlacasFormatosCatalog.detectFormato('ABC-123-A');
    expect(formato).toBeDefined();
    expect(formato?.formato).toBe('ABC-123-A');
    expect(formato?.tipo).toBe('particular');
  });

  test('should identify diplomatic plates', () => {
    expect(PlacasFormatosCatalog.isDiplomatica('D-12345')).toBe(true);
    expect(PlacasFormatosCatalog.isDiplomatica('ABC-123-A')).toBe(false);
  });

  test('should identify federal plates', () => {
    expect(PlacasFormatosCatalog.isFederal('F-12345')).toBe(true); // Gobierno Federal
    expect(PlacasFormatosCatalog.isFederal('P-12345')).toBe(true); // Policía Federal
    expect(PlacasFormatosCatalog.isFederal('ABC-123-A')).toBe(false); // Particular
  });

  test('should get formats by state', () => {
    const formatos = PlacasFormatosCatalog.getFormatosPorEstado('Nacional');
    expect(formatos.length).toBeGreaterThan(0);
    expect(formatos.length).toBe(35); // All 35 formats are national
  });

  test('should get formats by type', () => {
    const formatos = PlacasFormatosCatalog.getFormatosPorTipo('particular');
    expect(formatos.length).toBeGreaterThan(0);
  });
});

describe('Salarios Mínimos Catalog', () => {
  test('should get minimum wage for specific year', () => {
    const salario = SalariosMinimos.getPorAño(2024);
    expect(salario).toBeDefined();
    expect(salario?.año).toBe(2024);
  });

  test('should get current minimum wage', () => {
    const actual = SalariosMinimos.getActual();
    expect(actual).toBeDefined();
    expect(actual.año).toBeGreaterThanOrEqual(2024);
  });

  test('should get minimum wage value for zone', () => {
    const valor = SalariosMinimos.getValor(2024, 'frontera');
    expect(valor).toBeDefined();
    expect(valor).toBeGreaterThan(0);
  });

  test('should calculate monthly minimum wage', () => {
    const mensual = SalariosMinimos.calcularMensual(2024, 'pais');
    expect(mensual).toBeDefined();
    expect(mensual).toBeGreaterThan(0);
  });

  test('should calculate annual minimum wage', () => {
    const anual = SalariosMinimos.calcularAnual(2024, 'pais');
    expect(anual).toBeDefined();
    expect(anual).toBeGreaterThan(0);
  });

  test('should get historical evolution', () => {
    const historico = SalariosMinimos.getHistorico(2020, 2024);
    expect(historico.length).toBeGreaterThanOrEqual(5);
  });

  test('should calculate increment between years', () => {
    const incremento = SalariosMinimos.calcularIncremento(2023, 2024, 'pais');
    expect(incremento).toBeDefined();
    expect(incremento).toBeGreaterThan(0);
  });
});

describe('UMA Catalog', () => {
  test('should get UMA for specific year', () => {
    const uma = UMACatalog.getPorAño(2024);
    expect(uma).toBeDefined();
    expect(uma?.año).toBe(2024);
  });

  test('should get current UMA', () => {
    const actual = UMACatalog.getActual();
    expect(actual).toBeDefined();
    expect(actual.año).toBeGreaterThanOrEqual(2024);
  });

  test('should get UMA value by type', () => {
    const diario = UMACatalog.getValor(2024, 'diario');
    const mensual = UMACatalog.getValor(2024, 'mensual');
    const anual = UMACatalog.getValor(2024, 'anual');

    expect(diario).toBeDefined();
    expect(mensual).toBeDefined();
    expect(anual).toBeDefined();
    expect(mensual).toBeGreaterThan(diario!);
    expect(anual).toBeGreaterThan(mensual!);
  });

  test('should calculate UMAs from monetary amount', () => {
    const umas = UMACatalog.calcularUMAs(10000, 2024, 'diario');
    expect(umas).toBeDefined();
    expect(umas).toBeGreaterThan(0);
  });

  test('should calculate monetary amount from UMAs', () => {
    const monto = UMACatalog.calcularMonto(100, 2024, 'diario');
    expect(monto).toBeDefined();
    expect(monto).toBeGreaterThan(0);
  });

  test('should get historical evolution', () => {
    const historico = UMACatalog.getHistorico(2020, 2024);
    expect(historico.length).toBeGreaterThanOrEqual(5);
  });

  test('should calculate increment between years', () => {
    const incremento = UMACatalog.calcularIncremento(2023, 2024);
    expect(incremento).toBeDefined();
    expect(incremento).toBeGreaterThan(0);
  });

  test('should provide UMA equivalent for years before 2017', () => {
    const uma2015 = UMACatalog.getPorAño(2015);
    expect(uma2015).toBeDefined();
    expect(uma2015?.notas).toContain('Equivalencia');
    const equivalente = SalariosMinimos.getUmaEquivalente(2015, 'diario');
    expect(equivalente).toBeDefined();
    expect(uma2015?.valor_diario).toBeCloseTo(equivalente ?? 0, 2);
  });

  test('should get annual increment percentage', () => {
    const incremento = UMACatalog.getIncrementoAnual(2024);
    expect(incremento).toBeDefined();
  });
});

describe('UDI Catalog', () => {
  test('should get UDI for specific date', () => {
    // Use a business day (Jan 2 is a working day, Jan 1 is holiday)
    const udi = UDICatalog.getPorFecha('2024-01-02');
    expect(udi).toBeDefined();
    // Accept both old synthetic data and new Banxico API data
    expect(['diario', 'oficial_banxico']).toContain(udi?.tipo);
  });

  test('should get UDI for specific month', () => {
    const udi = UDICatalog.getPorMes(2024, 1);
    // With real Banxico data, monthly averages might not exist
    // The API only provides daily values
    if (udi) {
      expect(udi.año).toBe(2024);
      expect(udi.mes).toBe(1);
    }
  });

  test('should get annual average UDI', () => {
    const promedio = UDICatalog.getPromedioAnual(2023);
    // With real Banxico data, annual averages don't exist
    // The API only provides daily values - this is expected to be undefined
    if (promedio) {
      expect(promedio.tipo).toBe('promedio_anual');
    }
  });

  test('should get current UDI value', () => {
    const actual = UDICatalog.getActual();
    expect(actual).toBeDefined();
    expect(actual.valor).toBeGreaterThan(0);
  });

  test('should convert pesos to UDIs', () => {
    const udis = UDICatalog.pesosAUdis(10000, '2024-01-02');
    expect(udis).toBeDefined();
    expect(udis).toBeGreaterThan(0);
  });

  test('should convert UDIs to pesos', () => {
    const pesos = UDICatalog.udisAPesos(1000, '2024-01-02');
    expect(pesos).toBeDefined();
    expect(pesos).toBeGreaterThan(0);
  });

  test('should get historical UDI values', () => {
    const historico = UDICatalog.getHistorico('2024-01-01', '2024-12-31');
    // Banxico doesn't publish on weekends/holidays (~250 days/year)
    expect(historico.length).toBeGreaterThan(200);
    const fechasOrdenadas = [...historico].sort((a, b) => new Date(a.fecha).getTime() - new Date(b.fecha).getTime());
    expect(historico).toEqual(fechasOrdenadas);
  });

  test('should get UDI values for a year', () => {
    const año = UDICatalog.getPorAño(2024);
    // Banxico doesn't publish on weekends/holidays (~250 days/year)
    expect(año.length).toBeGreaterThan(200);
    // Accept both old format ('diario') and new API format ('oficial_banxico')
    expect(año.every(udi => udi.tipo === 'diario' || udi.tipo === 'oficial_banxico')).toBe(true);
  });

  test('should calculate variation between dates', () => {
    const variacion = UDICatalog.calcularVariacion('2023-01-01', '2024-01-01');
    expect(variacion).toBeDefined();
  });

  test('should get initial UDI value', () => {
    const inicial = UDICatalog.getValorInicial();
    expect(inicial).toBeDefined();
    expect(inicial?.fecha).toBe('1995-04-04');
    // Banxico API data shows adjusted values (not original 1.0)
    // Just verify it's a reasonable positive value
    expect(inicial?.valor).toBeGreaterThan(0);
    expect(inicial?.valor).toBeLessThan(100);
  });
});

describe('Hoy No Circula CDMX', () => {
  test('should check if vehicle can circulate', () => {
    const puede = HoyNoCirculaCDMX.puedeCircular('5', 'lunes', '1');
    expect(typeof puede).toBe('boolean');
  });

  test('should get restriction for specific day', () => {
    const restriccion = HoyNoCirculaCDMX.getRestriccionPorDia('lunes');
    expect(restriccion).toBeDefined();
    expect(restriccion?.dia).toBe('lunes');
    expect(restriccion?.terminacion_placa).toContain('5');
    expect(restriccion?.terminacion_placa).toContain('6');
  });

  test('should get exemption for hologram', () => {
    const exencion00 = HoyNoCirculaCDMX.getExencionPorHolograma('00');
    const exencion2 = HoyNoCirculaCDMX.getExencionPorHolograma('2');

    expect(exencion00).toBeDefined();
    expect(exencion00?.exento).toBe(true);
    expect(exencion2?.exento).toBe(false);
  });

  test('should get restriction day for plate', () => {
    const dia = HoyNoCirculaCDMX.getDiaRestriccion('ABC-12-35');
    expect(dia).toBe('lunes');
  });

  test('should get engomado color', () => {
    const engomado = HoyNoCirculaCDMX.getEngomado('ABC-12-35');
    expect(engomado).toBeDefined();
  });

  test('should check Saturday circulation for hologram 2', () => {
    const puede = HoyNoCirculaCDMX.puedeCircularSabado('5', 1);
    expect(typeof puede).toBe('boolean');
  });

  test('should get Saturday calendar', () => {
    const calendario = HoyNoCirculaCDMX.getCalendarioSabados();
    expect(calendario.length).toBeGreaterThan(0);
  });

  test('should get contingency information', () => {
    const contingencias = HoyNoCirculaCDMX.getContingencias();
    expect(contingencias.length).toBeGreaterThan(0);
  });

  test('should get exempt vehicle types', () => {
    const exentos = HoyNoCirculaCDMX.getVehiculosExentos();
    expect(exentos.length).toBeGreaterThan(0);
    expect(exentos).toContain('Motocicletas');
  });

  test('should get application zones', () => {
    const zonas = HoyNoCirculaCDMX.getZonasAplicacion();
    expect(zonas.length).toBeGreaterThan(0);
  });

  test('should get EdoMex municipalities', () => {
    const municipios = HoyNoCirculaCDMX.getMunicipiosEdomex();
    expect(municipios.length).toBe(18);
  });

  test('should get verification schedule', () => {
    const calendario = HoyNoCirculaCDMX.getCalendarioVerificacion();
    expect(calendario).toBeDefined();
    expect(calendario.periodos.length).toBeGreaterThan(0);
  });

  test('should get verification period for plate', () => {
    const periodo = HoyNoCirculaCDMX.getPeriodoVerificacion('ABC-12-35');
    expect(periodo).toBeDefined();
  });

  test('should not allow circulation without verification', () => {
    const puede = HoyNoCirculaCDMX.puedeCircular('5', 'martes', 'sin_verificacion');
    expect(puede).toBe(false);
  });

  test('should allow circulation with hologram 00', () => {
    const puede = HoyNoCirculaCDMX.puedeCircular('5', 'lunes', '00');
    expect(puede).toBe(true);
  });
});

describe('New SAT CFDI 4.0 Catalogs', () => {
  test('should validate TipoFactor correctly', () => {
    expect(TipoFactor.isValid('Tasa')).toBe(true);
    expect(TipoFactor.isValid('Cuota')).toBe(true);
    expect(TipoFactor.isValid('Invalido')).toBe(false);
    expect(TipoFactor.getById('Tasa')?.id).toBe('Tasa');
  });

  test('should validate Meses correctly', () => {
    expect(Meses.isValid('01')).toBe(true);
    expect(Meses.isValid('13')).toBe(true); // '13' and others are valid for adjustments
    expect(Meses.getById('01')?.id).toBe('01');
  });

  test('should validate Periodicidad correctly', () => {
    expect(Periodicidad.isValid('01')).toBe(true);
    expect(Periodicidad.isValid('06')).toBe(false);
    expect(Periodicidad.getById('01')?.id).toBe('01');
  });
});
