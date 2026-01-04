/**
 * ISR 2026 Official Tax Tables
 * Source: Anexo 8 de la RMF 2026, DOF 28/12/2025
 * Adjustment factor: 1.1321 (13.21% accumulated inflation)
 */

export interface ISRBracket {
  limiteInferior: number;
  limiteSuperior: number;
  cuotaFija: number;
  tasa: number;
}

// Daily Rate Table (Tarifa Diaria)
export const ISR_2026_DAILY: ISRBracket[] = [
  { limiteInferior: 0.01, limiteSuperior: 27.78, cuotaFija: 0.00, tasa: 1.92 },
  { limiteInferior: 27.79, limiteSuperior: 235.81, cuotaFija: 0.53, tasa: 6.40 },
  { limiteInferior: 235.82, limiteSuperior: 414.41, cuotaFija: 13.85, tasa: 10.88 },
  { limiteInferior: 414.42, limiteSuperior: 481.73, cuotaFija: 33.28, tasa: 16.00 },
  { limiteInferior: 481.74, limiteSuperior: 576.76, cuotaFija: 44.05, tasa: 17.92 },
  { limiteInferior: 576.77, limiteSuperior: 1163.25, cuotaFija: 61.08, tasa: 21.36 },
  { limiteInferior: 1163.26, limiteSuperior: 1833.44, cuotaFija: 186.35, tasa: 23.52 },
  { limiteInferior: 1833.45, limiteSuperior: 3500.35, cuotaFija: 343.98, tasa: 30.00 },
  { limiteInferior: 3500.36, limiteSuperior: 4667.13, cuotaFija: 844.05, tasa: 32.00 },
  { limiteInferior: 4667.14, limiteSuperior: 14001.38, cuotaFija: 1217.42, tasa: 34.00 },
  { limiteInferior: 14001.39, limiteSuperior: Infinity, cuotaFija: 4391.07, tasa: 35.00 }
];

// Weekly (7-Day) Rate Table
export const ISR_2026_WEEKLY: ISRBracket[] = [
  { limiteInferior: 0.01, limiteSuperior: 194.46, cuotaFija: 0.00, tasa: 1.92 },
  { limiteInferior: 194.47, limiteSuperior: 1650.67, cuotaFija: 3.71, tasa: 6.40 },
  { limiteInferior: 1650.68, limiteSuperior: 2900.87, cuotaFija: 96.95, tasa: 10.88 },
  { limiteInferior: 2900.88, limiteSuperior: 3372.11, cuotaFija: 232.96, tasa: 16.00 },
  { limiteInferior: 3372.12, limiteSuperior: 4037.32, cuotaFija: 308.35, tasa: 17.92 },
  { limiteInferior: 4037.33, limiteSuperior: 8142.75, cuotaFija: 427.56, tasa: 21.36 },
  { limiteInferior: 8142.76, limiteSuperior: 12834.08, cuotaFija: 1304.45, tasa: 23.52 },
  { limiteInferior: 12834.09, limiteSuperior: 24502.45, cuotaFija: 2407.86, tasa: 30.00 },
  { limiteInferior: 24502.46, limiteSuperior: 32669.91, cuotaFija: 5908.35, tasa: 32.00 },
  { limiteInferior: 32669.92, limiteSuperior: 98009.66, cuotaFija: 8521.94, tasa: 34.00 },
  { limiteInferior: 98009.67, limiteSuperior: Infinity, cuotaFija: 30737.49, tasa: 35.00 }
];

// 10-Day Period Rate Table (Decenal)
export const ISR_2026_DECEN: ISRBracket[] = [
  { limiteInferior: 0.01, limiteSuperior: 277.80, cuotaFija: 0.00, tasa: 1.92 },
  { limiteInferior: 277.81, limiteSuperior: 2358.10, cuotaFija: 5.30, tasa: 6.40 },
  { limiteInferior: 2358.11, limiteSuperior: 4144.10, cuotaFija: 138.50, tasa: 10.88 },
  { limiteInferior: 4144.11, limiteSuperior: 4817.30, cuotaFija: 332.80, tasa: 16.00 },
  { limiteInferior: 4817.31, limiteSuperior: 5767.60, cuotaFija: 440.50, tasa: 17.92 },
  { limiteInferior: 5767.61, limiteSuperior: 11632.50, cuotaFija: 610.80, tasa: 21.36 },
  { limiteInferior: 11632.51, limiteSuperior: 18334.40, cuotaFija: 1863.50, tasa: 23.52 },
  { limiteInferior: 18334.41, limiteSuperior: 35003.50, cuotaFija: 3439.80, tasa: 30.00 },
  { limiteInferior: 35003.51, limiteSuperior: 46671.30, cuotaFija: 8440.50, tasa: 32.00 },
  { limiteInferior: 46671.31, limiteSuperior: 140013.80, cuotaFija: 12174.20, tasa: 34.00 },
  { limiteInferior: 140013.81, limiteSuperior: Infinity, cuotaFija: 43910.70, tasa: 35.00 }
];

// Biweekly (15-Day) Rate Table (Quincenal)
export const ISR_2026_BIWEEKLY: ISRBracket[] = [
  { limiteInferior: 0.01, limiteSuperior: 416.70, cuotaFija: 0.00, tasa: 1.92 },
  { limiteInferior: 416.71, limiteSuperior: 3537.15, cuotaFija: 7.95, tasa: 6.40 },
  { limiteInferior: 3537.16, limiteSuperior: 6216.15, cuotaFija: 207.75, tasa: 10.88 },
  { limiteInferior: 6216.16, limiteSuperior: 7225.95, cuotaFija: 499.20, tasa: 16.00 },
  { limiteInferior: 7225.96, limiteSuperior: 8651.40, cuotaFija: 660.75, tasa: 17.92 },
  { limiteInferior: 8651.41, limiteSuperior: 17448.75, cuotaFija: 916.20, tasa: 21.36 },
  { limiteInferior: 17448.76, limiteSuperior: 27501.60, cuotaFija: 2795.25, tasa: 23.52 },
  { limiteInferior: 27501.61, limiteSuperior: 52505.25, cuotaFija: 5159.70, tasa: 30.00 },
  { limiteInferior: 52505.26, limiteSuperior: 70006.95, cuotaFija: 12660.75, tasa: 32.00 },
  { limiteInferior: 70006.96, limiteSuperior: 210020.70, cuotaFija: 18261.30, tasa: 34.00 },
  { limiteInferior: 210020.71, limiteSuperior: Infinity, cuotaFija: 65866.05, tasa: 35.00 }
];

// Monthly Rate Table (Mensual)
export const ISR_2026_MONTHLY: ISRBracket[] = [
  { limiteInferior: 0.01, limiteSuperior: 844.59, cuotaFija: 0.00, tasa: 1.92 },
  { limiteInferior: 844.60, limiteSuperior: 7168.51, cuotaFija: 16.22, tasa: 6.40 },
  { limiteInferior: 7168.52, limiteSuperior: 12598.02, cuotaFija: 420.95, tasa: 10.88 },
  { limiteInferior: 12598.03, limiteSuperior: 14644.64, cuotaFija: 1011.68, tasa: 16.00 },
  { limiteInferior: 14644.65, limiteSuperior: 17533.64, cuotaFija: 1339.14, tasa: 17.92 },
  { limiteInferior: 17533.65, limiteSuperior: 35362.83, cuotaFija: 1856.84, tasa: 21.36 },
  { limiteInferior: 35362.84, limiteSuperior: 55736.68, cuotaFija: 5665.16, tasa: 23.52 },
  { limiteInferior: 55736.69, limiteSuperior: 106410.50, cuotaFija: 10457.09, tasa: 30.00 },
  { limiteInferior: 106410.51, limiteSuperior: 141880.66, cuotaFija: 25659.23, tasa: 32.00 },
  { limiteInferior: 141880.67, limiteSuperior: 425641.99, cuotaFija: 37009.69, tasa: 34.00 },
  { limiteInferior: 425642.00, limiteSuperior: Infinity, cuotaFija: 133488.54, tasa: 35.00 }
];

// Annual Rate Table (Anual) - For reference
export const ISR_2026_ANNUAL: ISRBracket[] = [
  { limiteInferior: 0.01, limiteSuperior: 10135.11, cuotaFija: 0.00, tasa: 1.92 },
  { limiteInferior: 10135.12, limiteSuperior: 86022.12, cuotaFija: 194.59, tasa: 6.40 },
  { limiteInferior: 86022.13, limiteSuperior: 151176.24, cuotaFija: 5051.37, tasa: 10.88 },
  { limiteInferior: 151176.25, limiteSuperior: 175735.68, cuotaFija: 12140.13, tasa: 16.00 },
  { limiteInferior: 175735.69, limiteSuperior: 210403.68, cuotaFija: 16069.64, tasa: 17.92 },
  { limiteInferior: 210403.69, limiteSuperior: 424353.96, cuotaFija: 22282.10, tasa: 21.36 },
  { limiteInferior: 424353.97, limiteSuperior: 668840.16, cuotaFija: 67981.98, tasa: 23.52 },
  { limiteInferior: 668840.17, limiteSuperior: 1276926.00, cuotaFija: 125485.08, tasa: 30.00 },
  { limiteInferior: 1276926.01, limiteSuperior: 1702567.92, cuotaFija: 307910.82, tasa: 32.00 },
  { limiteInferior: 1702567.93, limiteSuperior: 5107703.88, cuotaFija: 444116.23, tasa: 34.00 },
  { limiteInferior: 5107703.89, limiteSuperior: Infinity, cuotaFija: 1601862.48, tasa: 35.00 }
];
