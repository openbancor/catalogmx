import fs from 'fs';
import path from 'path';

import {
  IEPSCalculator,
  IVACalculator,
  ImpuestosLocalesCalculator,
  RetencionCalculator,
} from '../src/calculators/tax-calculator';

type IvaVectors = {
  calcular: Array<{
    base: number;
    tipo_tasa: 'general' | 'frontera' | 'tasa_cero';
    fecha: string;
    expected: {
      iva: number;
      total_con_iva: number;
      tasa: number;
    };
  }>;
  calcular_incluido: Array<{
    total_con_iva: number;
    tipo_tasa: 'general' | 'frontera' | 'tasa_cero';
    fecha: string;
    expected: {
      iva: number;
      base: number;
      tasa: number;
    };
  }>;
};

type IepsVectors = {
  ad_valorem: Array<{
    base: number;
    tasa: number;
    expected: { ieps: number; tasa: number };
  }>;
  cuota_fija: Array<{
    base: number;
    cuota: number;
    expected: { ieps: number; tasa: number };
  }>;
  bebidas_alcoholicas: Array<{
    valor: number;
    grados_alcohol: number;
    expected: { ieps: number; tasa: number };
  }>;
  cigarros: Array<{
    valor: number;
    numero_cigarros: number;
    expected: { ieps: number; tasa: number };
  }>;
};

type RetencionesVectors = {
  isr: Array<{
    base: number;
    concepto: string;
    expected: { retencion: number; tasa: number };
  }>;
  iva: Array<{
    iva_trasladado: number;
    concepto: string;
    expected: { retencion: number; tasa: number };
  }>;
  honorarios: Array<{
    monto_sin_iva: number;
    expected: { retencion: number; tasa: number };
  }>;
  arrendamiento: Array<{
    monto_sin_iva: number;
    expected: { retencion: number; tasa: number };
  }>;
  fletes: Array<{
    monto_sin_iva: number;
    expected: { retencion: number; tasa: number };
  }>;
};

type LocalesVectors = {
  impuesto_nomina: Array<{
    total_percepciones: number;
    cve_estado: string;
    expected: number;
  }>;
  impuesto_hospedaje: Array<{
    monto_hospedaje: number;
    cve_estado: string;
    expected: number;
  }>;
};

const ivaPath = path.resolve(__dirname, '../../shared-data/tests/iva_vectors.json');
const iepsPath = path.resolve(__dirname, '../../shared-data/tests/ieps_vectors.json');
const retencionesPath = path.resolve(
  __dirname,
  '../../shared-data/tests/retenciones_vectors.json'
);
const localesPath = path.resolve(
  __dirname,
  '../../shared-data/tests/impuestos_locales_vectors.json'
);

const ivaVectors: IvaVectors = JSON.parse(fs.readFileSync(ivaPath, 'utf-8'));
const iepsVectors: IepsVectors = JSON.parse(fs.readFileSync(iepsPath, 'utf-8'));
const retencionesVectors: RetencionesVectors = JSON.parse(
  fs.readFileSync(retencionesPath, 'utf-8')
);
const localesVectors: LocalesVectors = JSON.parse(fs.readFileSync(localesPath, 'utf-8'));

const round = (value: number) => Number(value.toFixed(6));

describe('Impuestos shared vectors', () => {
  test('IVA', () => {
    for (const vector of ivaVectors.calcular) {
      const result = IVACalculator.calcular(vector.base, vector.tipo_tasa, vector.fecha);
      expect(round(result.iva)).toBe(vector.expected.iva);
      expect(round(result.total_con_iva)).toBe(vector.expected.total_con_iva);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of ivaVectors.calcular_incluido) {
      const result = IVACalculator.calcularIncluido(
        vector.total_con_iva,
        vector.tipo_tasa,
        vector.fecha
      );
      expect(round(result.iva)).toBe(vector.expected.iva);
      expect(round(result.base)).toBe(vector.expected.base);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }
  });

  test('IEPS', () => {
    for (const vector of iepsVectors.ad_valorem) {
      const result = IEPSCalculator.calcularAdValorem(vector.base, vector.tasa);
      expect(round(result.ieps)).toBe(vector.expected.ieps);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of iepsVectors.cuota_fija) {
      const result = IEPSCalculator.calcularCuotaFija(vector.base, vector.cuota);
      expect(round(result.ieps)).toBe(vector.expected.ieps);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of iepsVectors.bebidas_alcoholicas) {
      const result = IEPSCalculator.calcularBebidasAlcoholicas(
        vector.valor,
        vector.grados_alcohol
      );
      expect(round(result.ieps)).toBe(vector.expected.ieps);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of iepsVectors.cigarros) {
      const result = IEPSCalculator.calcularCigarros(vector.valor, vector.numero_cigarros);
      expect(round(result.ieps)).toBe(vector.expected.ieps);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }
  });

  test('Retenciones', () => {
    for (const vector of retencionesVectors.isr) {
      const result = RetencionCalculator.calcularRetencionISR(vector.base, vector.concepto);
      expect(round(result.retencion)).toBe(vector.expected.retencion);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of retencionesVectors.iva) {
      const result = RetencionCalculator.calcularRetencionIVA(
        vector.iva_trasladado,
        vector.concepto
      );
      expect(round(result.retencion)).toBe(vector.expected.retencion);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of retencionesVectors.honorarios) {
      const result = RetencionCalculator.calcularHonorarios(vector.monto_sin_iva);
      expect(round(result.retencion)).toBe(vector.expected.retencion);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of retencionesVectors.arrendamiento) {
      const result = RetencionCalculator.calcularArrendamiento(vector.monto_sin_iva);
      expect(round(result.retencion)).toBe(vector.expected.retencion);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }

    for (const vector of retencionesVectors.fletes) {
      const result = RetencionCalculator.calcularFletes(vector.monto_sin_iva);
      expect(round(result.retencion)).toBe(vector.expected.retencion);
      expect(round(result.tasa)).toBe(vector.expected.tasa);
    }
  });

  test('Impuestos locales', () => {
    for (const vector of localesVectors.impuesto_nomina) {
      const result = ImpuestosLocalesCalculator.calcularImpuestoNomina(
        vector.total_percepciones,
        vector.cve_estado
      );
      expect(round(result)).toBe(vector.expected);
    }

    for (const vector of localesVectors.impuesto_hospedaje) {
      const result = ImpuestosLocalesCalculator.calcularImpuestoHospedaje(
        vector.monto_hospedaje,
        vector.cve_estado
      );
      expect(round(result)).toBe(vector.expected);
    }
  });
});
