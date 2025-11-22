/**
 * Catalog data for demo - organized by category
 */

export interface CatalogItem {
  id: string;
  name: string;
  description: string;
  category: string;
  source: string;
  recordCount: string;
  columns: string[];
  data: Record<string, unknown>[];
}

export const CATALOG_CATEGORIES = [
  { id: 'banxico', name: 'Banxico', description: 'Banco de México - Financial data' },
  { id: 'inegi', name: 'INEGI', description: 'Instituto Nacional de Estadística - Geographic data' },
  { id: 'sepomex', name: 'SEPOMEX', description: 'Servicio Postal Mexicano - Postal codes' },
  { id: 'sat-cfdi', name: 'SAT CFDI 4.0', description: 'Electronic invoicing catalogs' },
  { id: 'sat-nomina', name: 'SAT Nómina', description: 'Payroll catalogs' },
  { id: 'sat-comext', name: 'SAT Comercio Exterior', description: 'International trade' },
  { id: 'ift', name: 'IFT', description: 'Instituto Federal de Telecomunicaciones' },
  { id: 'mexico', name: 'México', description: 'National regulations and data' }
];

export const CATALOGS: CatalogItem[] = [
  // BANXICO
  {
    id: 'banks',
    name: 'Bancos',
    description: 'Mexican banks with SPEI support',
    category: 'banxico',
    source: 'Banco de México',
    recordCount: '150+',
    columns: ['Código', 'Nombre', 'Nombre Completo', 'SPEI'],
    data: [
      { codigo: '002', nombre: 'BANAMEX', nombre_completo: 'Banco Nacional de México, S.A.', spei: true },
      { codigo: '012', nombre: 'BBVA MEXICO', nombre_completo: 'BBVA México, S.A.', spei: true },
      { codigo: '014', nombre: 'SANTANDER', nombre_completo: 'Banco Santander México, S.A.', spei: true },
      { codigo: '021', nombre: 'HSBC', nombre_completo: 'HSBC México, S.A.', spei: true },
      { codigo: '030', nombre: 'BAJIO', nombre_completo: 'Banco del Bajío, S.A.', spei: true },
      { codigo: '036', nombre: 'INBURSA', nombre_completo: 'Banco Inbursa, S.A.', spei: true },
      { codigo: '042', nombre: 'MIFEL', nombre_completo: 'Banca Mifel, S.A.', spei: true },
      { codigo: '044', nombre: 'SCOTIABANK', nombre_completo: 'Scotiabank Inverlat, S.A.', spei: true },
      { codigo: '058', nombre: 'BANREGIO', nombre_completo: 'Banco Regional de Monterrey, S.A.', spei: true },
      { codigo: '072', nombre: 'BANORTE', nombre_completo: 'Banco Mercantil del Norte, S.A.', spei: true },
      { codigo: '127', nombre: 'AZTECA', nombre_completo: 'Banco Azteca, S.A.', spei: true },
      { codigo: '137', nombre: 'BANCOPPEL', nombre_completo: 'BanCoppel, S.A.', spei: true }
    ]
  },
  {
    id: 'currencies',
    name: 'Monedas',
    description: 'World currencies with ISO codes',
    category: 'banxico',
    source: 'Banco de México / ISO 4217',
    recordCount: '150+',
    columns: ['Código', 'Nombre', 'Decimales'],
    data: [
      { codigo: 'MXN', nombre: 'Peso Mexicano', decimales: 2 },
      { codigo: 'USD', nombre: 'Dólar Estadounidense', decimales: 2 },
      { codigo: 'EUR', nombre: 'Euro', decimales: 2 },
      { codigo: 'GBP', nombre: 'Libra Esterlina', decimales: 2 },
      { codigo: 'JPY', nombre: 'Yen Japonés', decimales: 0 },
      { codigo: 'CAD', nombre: 'Dólar Canadiense', decimales: 2 },
      { codigo: 'CHF', nombre: 'Franco Suizo', decimales: 2 },
      { codigo: 'CNY', nombre: 'Yuan Chino', decimales: 2 },
      { codigo: 'BRL', nombre: 'Real Brasileño', decimales: 2 },
      { codigo: 'ARS', nombre: 'Peso Argentino', decimales: 2 }
    ]
  },
  // INEGI
  {
    id: 'states',
    name: 'Estados',
    description: 'Mexican states with CURP and INEGI codes',
    category: 'inegi',
    source: 'INEGI',
    recordCount: '32',
    columns: ['Código CURP', 'Nombre', 'Clave INEGI'],
    data: [
      { codigo_curp: 'AS', nombre: 'Aguascalientes', clave_inegi: '01' },
      { codigo_curp: 'BC', nombre: 'Baja California', clave_inegi: '02' },
      { codigo_curp: 'BS', nombre: 'Baja California Sur', clave_inegi: '03' },
      { codigo_curp: 'CC', nombre: 'Campeche', clave_inegi: '04' },
      { codigo_curp: 'CL', nombre: 'Coahuila de Zaragoza', clave_inegi: '05' },
      { codigo_curp: 'CM', nombre: 'Colima', clave_inegi: '06' },
      { codigo_curp: 'CS', nombre: 'Chiapas', clave_inegi: '07' },
      { codigo_curp: 'CH', nombre: 'Chihuahua', clave_inegi: '08' },
      { codigo_curp: 'DF', nombre: 'Ciudad de México', clave_inegi: '09' },
      { codigo_curp: 'DG', nombre: 'Durango', clave_inegi: '10' },
      { codigo_curp: 'GT', nombre: 'Guanajuato', clave_inegi: '11' },
      { codigo_curp: 'GR', nombre: 'Guerrero', clave_inegi: '12' },
      { codigo_curp: 'HG', nombre: 'Hidalgo', clave_inegi: '13' },
      { codigo_curp: 'JC', nombre: 'Jalisco', clave_inegi: '14' },
      { codigo_curp: 'MC', nombre: 'Estado de México', clave_inegi: '15' },
      { codigo_curp: 'MN', nombre: 'Michoacán de Ocampo', clave_inegi: '16' },
      { codigo_curp: 'MS', nombre: 'Morelos', clave_inegi: '17' },
      { codigo_curp: 'NT', nombre: 'Nayarit', clave_inegi: '18' },
      { codigo_curp: 'NL', nombre: 'Nuevo León', clave_inegi: '19' },
      { codigo_curp: 'OC', nombre: 'Oaxaca', clave_inegi: '20' },
      { codigo_curp: 'PL', nombre: 'Puebla', clave_inegi: '21' },
      { codigo_curp: 'QT', nombre: 'Querétaro', clave_inegi: '22' },
      { codigo_curp: 'QR', nombre: 'Quintana Roo', clave_inegi: '23' },
      { codigo_curp: 'SP', nombre: 'San Luis Potosí', clave_inegi: '24' },
      { codigo_curp: 'SL', nombre: 'Sinaloa', clave_inegi: '25' },
      { codigo_curp: 'SR', nombre: 'Sonora', clave_inegi: '26' },
      { codigo_curp: 'TC', nombre: 'Tabasco', clave_inegi: '27' },
      { codigo_curp: 'TS', nombre: 'Tamaulipas', clave_inegi: '28' },
      { codigo_curp: 'TL', nombre: 'Tlaxcala', clave_inegi: '29' },
      { codigo_curp: 'VZ', nombre: 'Veracruz de Ignacio de la Llave', clave_inegi: '30' },
      { codigo_curp: 'YN', nombre: 'Yucatán', clave_inegi: '31' },
      { codigo_curp: 'ZS', nombre: 'Zacatecas', clave_inegi: '32' }
    ]
  },
  // SEPOMEX
  {
    id: 'postal-codes',
    name: 'Códigos Postales',
    description: 'Mexican postal codes with localities',
    category: 'sepomex',
    source: 'SEPOMEX',
    recordCount: '157,000+',
    columns: ['CP', 'Colonia', 'Tipo', 'Municipio', 'Estado'],
    data: [
      { cp: '06600', colonia: 'Roma Norte', tipo: 'Colonia', municipio: 'Cuauhtémoc', estado: 'Ciudad de México' },
      { cp: '06700', colonia: 'Roma Sur', tipo: 'Colonia', municipio: 'Cuauhtémoc', estado: 'Ciudad de México' },
      { cp: '06100', colonia: 'Centro (Área 1)', tipo: 'Colonia', municipio: 'Cuauhtémoc', estado: 'Ciudad de México' },
      { cp: '11560', colonia: 'Polanco V Sección', tipo: 'Colonia', municipio: 'Miguel Hidalgo', estado: 'Ciudad de México' },
      { cp: '03100', colonia: 'Del Valle Centro', tipo: 'Colonia', municipio: 'Benito Juárez', estado: 'Ciudad de México' },
      { cp: '01000', colonia: 'San Ángel', tipo: 'Colonia', municipio: 'Álvaro Obregón', estado: 'Ciudad de México' },
      { cp: '64000', colonia: 'Centro', tipo: 'Colonia', municipio: 'Monterrey', estado: 'Nuevo León' },
      { cp: '44100', colonia: 'Centro', tipo: 'Colonia', municipio: 'Guadalajara', estado: 'Jalisco' }
    ]
  },
  // SAT CFDI
  {
    id: 'regimen-fiscal',
    name: 'Régimen Fiscal',
    description: 'Tax regime codes for CFDI',
    category: 'sat-cfdi',
    source: 'SAT',
    recordCount: '15',
    columns: ['Código', 'Descripción', 'Persona Física', 'Persona Moral'],
    data: [
      { codigo: '601', descripcion: 'General de Ley Personas Morales', fisica: false, moral: true },
      { codigo: '603', descripcion: 'Personas Morales con Fines no Lucrativos', fisica: false, moral: true },
      { codigo: '605', descripcion: 'Sueldos y Salarios e Ingresos Asimilados a Salarios', fisica: true, moral: false },
      { codigo: '606', descripcion: 'Arrendamiento', fisica: true, moral: false },
      { codigo: '607', descripcion: 'Régimen de Enajenación o Adquisición de Bienes', fisica: true, moral: false },
      { codigo: '608', descripcion: 'Demás ingresos', fisica: true, moral: false },
      { codigo: '610', descripcion: 'Residentes en el Extranjero sin Establecimiento Permanente en México', fisica: true, moral: true },
      { codigo: '612', descripcion: 'Personas Físicas con Actividades Empresariales y Profesionales', fisica: true, moral: false },
      { codigo: '620', descripcion: 'Sociedades Cooperativas de Producción que optan por diferir sus ingresos', fisica: false, moral: true },
      { codigo: '621', descripcion: 'Incorporación Fiscal', fisica: true, moral: false },
      { codigo: '625', descripcion: 'Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas', fisica: true, moral: false },
      { codigo: '626', descripcion: 'Régimen Simplificado de Confianza', fisica: true, moral: true }
    ]
  },
  {
    id: 'uso-cfdi',
    name: 'Uso CFDI',
    description: 'Invoice usage codes',
    category: 'sat-cfdi',
    source: 'SAT',
    recordCount: '25',
    columns: ['Código', 'Descripción'],
    data: [
      { codigo: 'G01', descripcion: 'Adquisición de mercancías' },
      { codigo: 'G02', descripcion: 'Devoluciones, descuentos o bonificaciones' },
      { codigo: 'G03', descripcion: 'Gastos en general' },
      { codigo: 'I01', descripcion: 'Construcciones' },
      { codigo: 'I02', descripcion: 'Mobiliario y equipo de oficina por inversiones' },
      { codigo: 'I03', descripcion: 'Equipo de transporte' },
      { codigo: 'I04', descripcion: 'Equipo de computo y accesorios' },
      { codigo: 'I05', descripcion: 'Dados, troqueles, moldes, matrices y herramental' },
      { codigo: 'I08', descripcion: 'Otra maquinaria y equipo' },
      { codigo: 'D01', descripcion: 'Honorarios médicos, dentales y gastos hospitalarios' },
      { codigo: 'D02', descripcion: 'Gastos médicos por incapacidad o discapacidad' },
      { codigo: 'D03', descripcion: 'Gastos funerales' },
      { codigo: 'D04', descripcion: 'Donativos' },
      { codigo: 'P01', descripcion: 'Por definir' },
      { codigo: 'S01', descripcion: 'Sin efectos fiscales' },
      { codigo: 'CP01', descripcion: 'Pagos' }
    ]
  },
  {
    id: 'forma-pago',
    name: 'Forma de Pago',
    description: 'Payment method codes',
    category: 'sat-cfdi',
    source: 'SAT',
    recordCount: '29',
    columns: ['Código', 'Descripción'],
    data: [
      { codigo: '01', descripcion: 'Efectivo' },
      { codigo: '02', descripcion: 'Cheque nominativo' },
      { codigo: '03', descripcion: 'Transferencia electrónica de fondos' },
      { codigo: '04', descripcion: 'Tarjeta de crédito' },
      { codigo: '05', descripcion: 'Monedero electrónico' },
      { codigo: '06', descripcion: 'Dinero electrónico' },
      { codigo: '08', descripcion: 'Vales de despensa' },
      { codigo: '12', descripcion: 'Dación en pago' },
      { codigo: '13', descripcion: 'Pago por subrogación' },
      { codigo: '14', descripcion: 'Pago por consignación' },
      { codigo: '15', descripcion: 'Condonación' },
      { codigo: '17', descripcion: 'Compensación' },
      { codigo: '23', descripcion: 'Novación' },
      { codigo: '24', descripcion: 'Confusión' },
      { codigo: '25', descripcion: 'Remisión de deuda' },
      { codigo: '26', descripcion: 'Prescripción o caducidad' },
      { codigo: '27', descripcion: 'A satisfacción del acreedor' },
      { codigo: '28', descripcion: 'Tarjeta de débito' },
      { codigo: '29', descripcion: 'Tarjeta de servicios' },
      { codigo: '30', descripcion: 'Aplicación de anticipos' },
      { codigo: '31', descripcion: 'Intermediario pagos' },
      { codigo: '99', descripcion: 'Por definir' }
    ]
  },
  // SAT NOMINA
  {
    id: 'tipo-contrato',
    name: 'Tipo de Contrato',
    description: 'Employment contract types',
    category: 'sat-nomina',
    source: 'SAT',
    recordCount: '10',
    columns: ['Código', 'Descripción'],
    data: [
      { codigo: '01', descripcion: 'Contrato de trabajo por tiempo indeterminado' },
      { codigo: '02', descripcion: 'Contrato de trabajo para obra determinada' },
      { codigo: '03', descripcion: 'Contrato de trabajo por tiempo determinado' },
      { codigo: '04', descripcion: 'Contrato de trabajo por temporada' },
      { codigo: '05', descripcion: 'Contrato de trabajo sujeto a prueba' },
      { codigo: '06', descripcion: 'Contrato de trabajo con capacitación inicial' },
      { codigo: '07', descripcion: 'Modalidad de contratación por pago de hora laborada' },
      { codigo: '08', descripcion: 'Modalidad de trabajo por comisión laboral' },
      { codigo: '09', descripcion: 'Modalidades de contratación donde no existe relación de trabajo' },
      { codigo: '10', descripcion: 'Jubilación, pensión, retiro' },
      { codigo: '99', descripcion: 'Otro contrato' }
    ]
  },
  {
    id: 'tipo-jornada',
    name: 'Tipo de Jornada',
    description: 'Working shift types',
    category: 'sat-nomina',
    source: 'SAT',
    recordCount: '8',
    columns: ['Código', 'Descripción'],
    data: [
      { codigo: '01', descripcion: 'Diurna' },
      { codigo: '02', descripcion: 'Nocturna' },
      { codigo: '03', descripcion: 'Mixta' },
      { codigo: '04', descripcion: 'Por hora' },
      { codigo: '05', descripcion: 'Reducida' },
      { codigo: '06', descripcion: 'Continuada' },
      { codigo: '07', descripcion: 'Partida' },
      { codigo: '08', descripcion: 'Por turnos' },
      { codigo: '99', descripcion: 'Otra Jornada' }
    ]
  },
  {
    id: 'riesgo-puesto',
    name: 'Riesgo del Puesto',
    description: 'IMSS job risk classifications',
    category: 'sat-nomina',
    source: 'SAT / IMSS',
    recordCount: '5',
    columns: ['Clase', 'Descripción', 'Prima (%)'],
    data: [
      { clase: '1', descripcion: 'Clase I - Riesgo ordinario de vida', prima: 0.54355 },
      { clase: '2', descripcion: 'Clase II - Riesgo bajo', prima: 1.13065 },
      { clase: '3', descripcion: 'Clase III - Riesgo medio', prima: 2.59840 },
      { clase: '4', descripcion: 'Clase IV - Riesgo alto', prima: 4.65325 },
      { clase: '5', descripcion: 'Clase V - Riesgo máximo', prima: 7.58875 }
    ]
  },
  // SAT COMERCIO EXTERIOR
  {
    id: 'incoterms',
    name: 'Incoterms',
    description: 'International trade terms',
    category: 'sat-comext',
    source: 'ICC / SAT',
    recordCount: '11',
    columns: ['Código', 'Nombre', 'Descripción'],
    data: [
      { codigo: 'EXW', nombre: 'Ex Works', descripcion: 'En fábrica (lugar convenido)' },
      { codigo: 'FCA', nombre: 'Free Carrier', descripcion: 'Franco transportista (lugar convenido)' },
      { codigo: 'CPT', nombre: 'Carriage Paid To', descripcion: 'Transporte pagado hasta (lugar de destino convenido)' },
      { codigo: 'CIP', nombre: 'Carriage and Insurance Paid To', descripcion: 'Transporte y seguro pagados hasta (lugar de destino convenido)' },
      { codigo: 'DAP', nombre: 'Delivered At Place', descripcion: 'Entregado en lugar (lugar de destino convenido)' },
      { codigo: 'DPU', nombre: 'Delivered at Place Unloaded', descripcion: 'Entregado en lugar descargado' },
      { codigo: 'DDP', nombre: 'Delivered Duty Paid', descripcion: 'Entregado con derechos pagados (lugar de destino convenido)' },
      { codigo: 'FAS', nombre: 'Free Alongside Ship', descripcion: 'Franco al costado del buque (puerto de carga convenido)' },
      { codigo: 'FOB', nombre: 'Free On Board', descripcion: 'Franco a bordo (puerto de carga convenido)' },
      { codigo: 'CFR', nombre: 'Cost and Freight', descripcion: 'Costo y flete (puerto de destino convenido)' },
      { codigo: 'CIF', nombre: 'Cost, Insurance and Freight', descripcion: 'Costo, seguro y flete (puerto de destino convenido)' }
    ]
  },
  // IFT
  {
    id: 'lada',
    name: 'Códigos LADA',
    description: 'Mexican area codes',
    category: 'ift',
    source: 'IFT',
    recordCount: '1,000+',
    columns: ['LADA', 'Ciudad', 'Estado'],
    data: [
      { lada: '55', ciudad: 'Ciudad de México', estado: 'CDMX' },
      { lada: '33', ciudad: 'Guadalajara', estado: 'Jalisco' },
      { lada: '81', ciudad: 'Monterrey', estado: 'Nuevo León' },
      { lada: '222', ciudad: 'Puebla', estado: 'Puebla' },
      { lada: '664', ciudad: 'Tijuana', estado: 'Baja California' },
      { lada: '442', ciudad: 'Querétaro', estado: 'Querétaro' },
      { lada: '449', ciudad: 'Aguascalientes', estado: 'Aguascalientes' },
      { lada: '614', ciudad: 'Chihuahua', estado: 'Chihuahua' },
      { lada: '656', ciudad: 'Ciudad Juárez', estado: 'Chihuahua' },
      { lada: '998', ciudad: 'Cancún', estado: 'Quintana Roo' }
    ]
  },
  // MEXICO
  {
    id: 'salarios-minimos',
    name: 'Salarios Mínimos',
    description: 'Minimum wage history',
    category: 'mexico',
    source: 'CONASAMI',
    recordCount: 'Historical',
    columns: ['Año', 'General (MXN)', 'Zona Libre (MXN)'],
    data: [
      { año: 2024, general: 248.93, zona_libre: 374.89 },
      { año: 2023, general: 207.44, zona_libre: 312.41 },
      { año: 2022, general: 172.87, zona_libre: 260.34 },
      { año: 2021, general: 141.70, zona_libre: 213.39 },
      { año: 2020, general: 123.22, zona_libre: 185.56 },
      { año: 2019, general: 102.68, zona_libre: 176.72 }
    ]
  },
  {
    id: 'uma',
    name: 'UMA',
    description: 'Unidad de Medida y Actualización',
    category: 'mexico',
    source: 'INEGI',
    recordCount: 'Annual',
    columns: ['Año', 'Diario', 'Mensual', 'Anual'],
    data: [
      { año: 2024, diario: 108.57, mensual: 3300.53, anual: 39606.36 },
      { año: 2023, diario: 103.74, mensual: 3153.70, anual: 37844.40 },
      { año: 2022, diario: 96.22, mensual: 2925.09, anual: 35101.08 },
      { año: 2021, diario: 89.62, mensual: 2724.45, anual: 32693.40 },
      { año: 2020, diario: 86.88, mensual: 2641.15, anual: 31693.80 }
    ]
  }
];

export function getCatalogsByCategory(categoryId: string): CatalogItem[] {
  return CATALOGS.filter(c => c.category === categoryId);
}

export function searchCatalogs(query: string): CatalogItem[] {
  const q = query.toLowerCase();
  return CATALOGS.filter(c =>
    c.name.toLowerCase().includes(q) ||
    c.description.toLowerCase().includes(q) ||
    c.category.toLowerCase().includes(q)
  );
}

export function searchInCatalog(catalog: CatalogItem, query: string): Record<string, unknown>[] {
  const q = query.toLowerCase();
  return catalog.data.filter(row =>
    Object.values(row).some(v =>
      String(v).toLowerCase().includes(q)
    )
  );
}
