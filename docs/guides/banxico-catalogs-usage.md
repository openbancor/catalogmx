# Guía de Uso: Catálogos de Banxico

Esta guía explica cómo usar los catálogos de datos de Banco de México (Banxico) en Python y TypeScript.

## 📊 Catálogos Disponibles

| Catálogo | Descripción | Frecuencia | Registros |
|----------|-------------|------------|-----------|
| **UDI** | Unidades de Inversión | Diaria | 11,230+ |
| **Tipo de Cambio FIX** | Tipo de cambio USD/MXN oficial | Diaria | 8,556+ |
| **Tipo de Cambio Histórico** | Serie histórica desde 1954 | Diaria | 18,187+ |
| **TIIE** | Tasa Interbancaria de Equilibrio | Diaria | 7,516+ |
| **CETES** | Certificados de la Tesorería | Semanal | 5,003+ |
| **Inflación** | INPC e inflación anual/mensual | Mensual | 184+ |
| **Salarios Mínimos** | Salarios mínimos históricos | Mensual | 598+ |

---

## 🐍 Python

### Instalación

```bash
pip install catalogmx
# o con uv (10-100x más rápido)
uv pip install catalogmx
```

### Importar Catálogos

```python
# UDI
from catalogmx.catalogs.banxico import UDICatalog
from catalogmx.catalogs.banxico.udis_sqlite import (
    get_udi_actual,
    get_udi_por_fecha,
    pesos_a_udis,
    udis_a_pesos
)

# Tipo de Cambio
from catalogmx.catalogs.banxico import TipoCambioUSDCatalog
from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
    get_tipo_cambio_actual,
    get_tipo_cambio_por_fecha,
    pesos_a_dolares,
    dolares_a_pesos
)

# TIIE
from catalogmx.catalogs.banxico import TIIECatalog
from catalogmx.catalogs.banxico.tiie_sqlite import (
    get_tiie_actual,
    get_tiie_por_fecha
)

# CETES
from catalogmx.catalogs.banxico import CETESCatalog
from catalogmx.catalogs.banxico.cetes_sqlite import (
    get_cetes_actual,
    get_cetes_por_fecha
)

# Inflación
from catalogmx.catalogs.banxico import InflacionCatalog
from catalogmx.catalogs.banxico.inflacion_sqlite import (
    get_inflacion_actual,
    get_inflacion_por_fecha,
    get_inflacion_anual_actual
)

# Salarios Mínimos
from catalogmx.catalogs.banxico import SalariosMinimos
from catalogmx.catalogs.banxico.salarios_minimos_sqlite import (
    get_salario_minimo_actual,
    get_salario_minimo_por_fecha
)
```

---

## 📘 Ejemplos de Uso en Python

### 1. UDI (Unidades de Inversión)

```python
from catalogmx.catalogs.banxico.udis_sqlite import (
    UDICatalog,
    get_udi_actual,
    pesos_a_udis
)

# Obtener UDI actual
udi_actual = get_udi_actual()
print(f"UDI actual: {udi_actual['valor']} ({udi_actual['fecha']})")
# Output: UDI actual: 8.412345 (2025-12-30)

# Obtener UDI de una fecha específica
udi = UDICatalog.get_por_fecha("2024-01-15")
print(f"UDI del 15 ene 2024: {udi['valor']}")

# Convertir pesos a UDIs
pesos = 100000.0
udis = pesos_a_udis(pesos, "2024-01-15")
print(f"{pesos:,.2f} MXN = {udis:,.2f} UDIs")

# Obtener promedio mensual
udi_mes = UDICatalog.get_por_mes(2024, 1)
print(f"UDI promedio ene 2024: {udi_mes['valor']}")

# Obtener serie anual
udis_2024 = UDICatalog.get_por_anio(2024)
print(f"UDIs en 2024: {len(udis_2024)} registros")

# Calcular variación
variacion = UDICatalog.calcular_variacion("2024-01-01", "2024-12-31")
print(f"Variación anual: {variacion:.2f}%")
```

### 2. Tipo de Cambio USD/MXN

```python
from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
    TipoCambioUSDCatalog,
    get_tipo_cambio_actual,
    dolares_a_pesos
)

# Tipo de cambio actual
tc_actual = get_tipo_cambio_actual()
print(f"Tipo de cambio FIX: {tc_actual['tipo_cambio']} MXN/USD")
# Output: Tipo de cambio FIX: 20.5123 MXN/USD

# Tipo de cambio de una fecha
tc = TipoCambioUSDCatalog.get_por_fecha("2024-06-15")
print(f"TC 15 jun 2024: {tc['tipo_cambio']}")

# Convertir dólares a pesos
dolares = 1000.0
pesos = dolares_a_pesos(dolares, "2024-06-15")
print(f"${dolares:,.2f} USD = ${pesos:,.2f} MXN")

# Serie histórica de un año
tc_2024 = TipoCambioUSDCatalog.get_por_anio(2024)
print(f"TCs en 2024: {len(tc_2024)} días")

# Calcular variación
var = TipoCambioUSDCatalog.calcular_variacion("2024-01-02", "2024-12-31")
print(f"Variación del peso: {var:.2f}%")
```

### 3. TIIE (Tasa de Interés Interbancaria)

```python
from catalogmx.catalogs.banxico.tiie_sqlite import (
    TIIECatalog,
    get_tiie_actual
)

# TIIE actual (28 días por defecto)
tiie = get_tiie_actual(plazo=28)
print(f"TIIE 28 días: {tiie['tasa']:.4f}%")
# Output: TIIE 28 días: 10.8500%

# TIIE de una fecha específica
tiie = TIIECatalog.get_por_fecha("2024-06-15", plazo=28)
print(f"TIIE 28 días (15 jun 2024): {tiie['tasa']}%")

# Todas las tasas de un mes
tiies = TIIECatalog.get_por_mes(2024, 6, plazo=28)
print(f"TIIE 28 días en jun 2024: {len(tiies)} registros")

# Promedio mensual
promedio = TIIECatalog.get_promedio_mes(2024, 6, plazo=28)
print(f"TIIE promedio jun 2024: {promedio:.4f}%")

# Serie anual
tiies_2024 = TIIECatalog.get_por_anio(2024, plazo=28)
print(f"TIIE 28 días en 2024: {len(tiies_2024)} registros")
```

### 4. CETES (Certificados de la Tesorería)

```python
from catalogmx.catalogs.banxico.cetes_sqlite import (
    CETESCatalog,
    get_cetes_actual
)

# CETES actual (28 días)
cetes = get_cetes_actual(plazo=28)
print(f"CETES 28 días: {cetes['tasa']:.4f}%")

# CETES de una fecha
cetes = CETESCatalog.get_por_fecha("2024-06-20", plazo=28)
print(f"CETES 28 días (20 jun 2024): {cetes['tasa']}%")

# CETES de un mes
cetes_mes = CETESCatalog.get_por_mes(2024, 6, plazo=28)
print(f"CETES en jun 2024: {len(cetes_mes)} registros")

# Promedio mensual
promedio = CETESCatalog.get_promedio_mes(2024, 6, plazo=28)
print(f"CETES promedio jun 2024: {promedio:.4f}%")

# Plazos disponibles: 28, 91, 182, 364 días
cetes_364 = CETESCatalog.get_actual(plazo=364)
print(f"CETES 364 días: {cetes_364['tasa']}%")
```

### 5. Inflación (INPC)

```python
from catalogmx.catalogs.banxico.inflacion_sqlite import (
    InflacionCatalog,
    get_inflacion_actual,
    get_inflacion_anual_actual
)

# Inflación actual
inflacion = get_inflacion_actual()
print(f"Inflación anual: {inflacion['inflacion_anual']:.2f}%")
print(f"Inflación mensual: {inflacion['inflacion_mensual']:.2f}%")
print(f"INPC: {inflacion['inpc']:.4f}")

# Solo inflación anual
inflacion_anual = get_inflacion_anual_actual()
print(f"Inflación anual: {inflacion_anual}%")

# Inflación de un mes específico
inf = InflacionCatalog.get_por_mes(2024, 6)
print(f"Inflación jun 2024: {inf['inflacion_anual']}%")

# Serie de un año
inflaciones_2024 = InflacionCatalog.get_por_anio(2024)
print(f"Inflaciones en 2024: {len(inflaciones_2024)} meses")

# Promedio anual
promedio = InflacionCatalog.get_promedio_anual(2024)
print(f"Inflación promedio 2024: {promedio:.2f}%")

# Calcular inflación acumulada
acumulada = InflacionCatalog.calcular_inflacion_acumulada(2024, 1, 2024, 12)
print(f"Inflación acumulada 2024: {acumulada:.2f}%")
```

### 6. Salarios Mínimos

```python
from catalogmx.catalogs.banxico.salarios_minimos_sqlite import (
    SalariosMinimosCatalog,
    get_salario_minimo_actual
)

# Salario mínimo actual (general)
salario = get_salario_minimo_actual(zona="general")
print(f"Salario mínimo general: ${salario['salario_diario']:.2f} MXN")

# Salario mínimo frontera norte
salario_fn = SalariosMinimosCatalog.get_actual(zona="frontera_norte")
print(f"Salario frontera norte: ${salario_fn['salario_diario']:.2f} MXN")

# Salario de una fecha específica
salario = SalariosMinimosCatalog.get_por_fecha("2024-01-01", zona="general")
print(f"Salario 1 ene 2024: ${salario['salario_diario']:.2f}")

# Serie de un año
salarios_2024 = SalariosMinimosCatalog.get_por_anio(2024, zona="general")
print(f"Cambios en 2024: {len(salarios_2024)}")

# Calcular variación
var = SalariosMinimosCatalog.calcular_variacion(
    "2023-01-01", "2024-01-01", zona="general"
)
print(f"Incremento anual: {var:.2f}%")
```

---

## 🔷 TypeScript

### Instalación

```bash
npm install catalogmx
# o con yarn
yarn add catalogmx
```

### Importar Catálogos

```typescript
// UDI
import { UDICatalog } from 'catalogmx/catalogs/banxico/udis-sqlite';

// Tipo de Cambio
import { TipoCambioUSDCatalog } from 'catalogmx/catalogs/banxico/tipo-cambio-usd-sqlite';

// TIIE
import { TIIECatalog } from 'catalogmx/catalogs/banxico/tiie-28-sqlite';

// CETES
import { CETESCatalog } from 'catalogmx/catalogs/banxico/cetes-28-sqlite';

// Inflación
import { InflacionCatalog } from 'catalogmx/catalogs/banxico/inflacion-anual-sqlite';

// Salarios Mínimos
import { SalariosMinimosCatalog } from 'catalogmx/catalogs/banxico/salarios-minimos-sqlite';
```

---

## 📗 Ejemplos de Uso en TypeScript

### 1. UDI (Unidades de Inversión)

```typescript
import { UDICatalog } from 'catalogmx/catalogs/banxico/udis-sqlite';

// Obtener UDI actual
const udiActual = await UDICatalog.getActual();
console.log(`UDI actual: ${udiActual.valor} (${udiActual.fecha})`);
// Output: UDI actual: 8.412345 (2025-12-30)

// Obtener UDI de una fecha específica
const udi = await UDICatalog.getPorFecha('2024-01-15');
console.log(`UDI del 15 ene 2024: ${udi?.valor}`);

// Convertir pesos a UDIs
const pesos = 100000.0;
const udis = await UDICatalog.pesosAUdis(pesos, '2024-01-15');
console.log(`${pesos} MXN = ${udis?.toFixed(2)} UDIs`);

// Convertir UDIs a pesos
const udisAmount = 1000.0;
const pesosResult = await UDICatalog.udisAPesos(udisAmount, '2024-01-15');
console.log(`${udisAmount} UDIs = ${pesosResult?.toFixed(2)} MXN`);

// Obtener promedio mensual
const udiMes = await UDICatalog.getPorMes(2024, 1);
console.log(`UDI promedio ene 2024: ${udiMes?.valor}`);

// Obtener serie anual
const udis2024 = await UDICatalog.getPorAnio(2024);
console.log(`UDIs en 2024: ${udis2024.length} registros`);

// Calcular variación
const variacion = await UDICatalog.calcularVariacion('2024-01-01', '2024-12-31');
console.log(`Variación anual: ${variacion?.toFixed(2)}%`);
```

### 2. Tipo de Cambio USD/MXN

```typescript
import { TipoCambioUSDCatalog } from 'catalogmx/catalogs/banxico/tipo-cambio-usd-sqlite';

// Tipo de cambio actual
const tcActual = await TipoCambioUSDCatalog.getActual();
console.log(`Tipo de cambio FIX: ${tcActual.tipo_cambio} MXN/USD`);

// Tipo de cambio de una fecha
const tc = await TipoCambioUSDCatalog.getPorFecha('2024-06-15');
console.log(`TC 15 jun 2024: ${tc?.tipo_cambio}`);

// Convertir dólares a pesos
const dolares = 1000.0;
const pesos = await TipoCambioUSDCatalog.dolaresAPesos(dolares, '2024-06-15');
console.log(`$${dolares} USD = $${pesos?.toFixed(2)} MXN`);

// Convertir pesos a dólares
const pesosAmount = 20000.0;
const dolaresResult = await TipoCambioUSDCatalog.pesosADolares(pesosAmount, '2024-06-15');
console.log(`$${pesosAmount} MXN = $${dolaresResult?.toFixed(2)} USD`);

// Serie de un año
const tc2024 = await TipoCambioUSDCatalog.getPorAnio(2024);
console.log(`TCs en 2024: ${tc2024.length} días`);

// Calcular variación
const variacion = await TipoCambioUSDCatalog.calcularVariacion('2024-01-02', '2024-12-31');
console.log(`Variación del peso: ${variacion?.toFixed(2)}%`);
```

### 3. TIIE (Tasa de Interés Interbancaria)

```typescript
import { TIIECatalog } from 'catalogmx/catalogs/banxico/tiie-28-sqlite';

// TIIE actual (28 días por defecto)
const tiie = await TIIECatalog.getActual(28);
console.log(`TIIE 28 días: ${tiie.tasa.toFixed(4)}%`);

// TIIE de una fecha específica
const tiieDate = await TIIECatalog.getPorFecha('2024-06-15', 28);
console.log(`TIIE 28 días (15 jun 2024): ${tiieDate?.tasa}%`);

// Todas las tasas de un mes
const tiiesMes = await TIIECatalog.getPorMes(2024, 6, 28);
console.log(`TIIE 28 días en jun 2024: ${tiiesMes.length} registros`);

// Promedio mensual
const promedio = await TIIECatalog.getPromedioMes(2024, 6, 28);
console.log(`TIIE promedio jun 2024: ${promedio?.toFixed(4)}%`);

// Serie anual
const tiies2024 = await TIIECatalog.getPorAnio(2024, 28);
console.log(`TIIE 28 días en 2024: ${tiies2024.length} registros`);
```

### 4. CETES (Certificados de la Tesorería)

```typescript
import { CETESCatalog } from 'catalogmx/catalogs/banxico/cetes-28-sqlite';

// CETES actual (28 días)
const cetes = await CETESCatalog.getActual(28);
console.log(`CETES 28 días: ${cetes.tasa.toFixed(4)}%`);

// CETES de una fecha
const cetesDate = await CETESCatalog.getPorFecha('2024-06-20', 28);
console.log(`CETES 28 días (20 jun 2024): ${cetesDate?.tasa}%`);

// CETES de un mes
const cetesMes = await CETESCatalog.getPorMes(2024, 6, 28);
console.log(`CETES en jun 2024: ${cetesMes.length} registros`);

// Promedio mensual
const promedio = await CETESCatalog.getPromedioMes(2024, 6, 28);
console.log(`CETES promedio jun 2024: ${promedio?.toFixed(4)}%`);

// Plazos disponibles: 28, 91, 182, 364 días
const cetes364 = await CETESCatalog.getActual(364);
console.log(`CETES 364 días: ${cetes364.tasa}%`);
```

### 5. Inflación (INPC)

```typescript
import { InflacionCatalog } from 'catalogmx/catalogs/banxico/inflacion-anual-sqlite';

// Inflación actual
const inflacion = await InflacionCatalog.getActual();
console.log(`Inflación anual: ${inflacion.inflacion_anual.toFixed(2)}%`);
console.log(`Inflación mensual: ${inflacion.inflacion_mensual.toFixed(2)}%`);
console.log(`INPC: ${inflacion.inpc.toFixed(4)}`);

// Solo inflación anual
const inflacionAnual = await InflacionCatalog.getInflacionAnualActual();
console.log(`Inflación anual: ${inflacionAnual}%`);

// Inflación de un mes específico
const inf = await InflacionCatalog.getPorMes(2024, 6);
console.log(`Inflación jun 2024: ${inf?.inflacion_anual}%`);

// Serie de un año
const inflaciones2024 = await InflacionCatalog.getPorAnio(2024);
console.log(`Inflaciones en 2024: ${inflaciones2024.length} meses`);

// Promedio anual
const promedio = await InflacionCatalog.getPromedioAnual(2024);
console.log(`Inflación promedio 2024: ${promedio?.toFixed(2)}%`);

// Calcular inflación acumulada
const acumulada = await InflacionCatalog.calcularInflacionAcumulada(2024, 1, 2024, 12);
console.log(`Inflación acumulada 2024: ${acumulada?.toFixed(2)}%`);
```

### 6. Salarios Mínimos

```typescript
import { SalariosMinimosCatalog } from 'catalogmx/catalogs/banxico/salarios-minimos-sqlite';

// Salario mínimo actual (general)
const salario = await SalariosMinimosCatalog.getActual('general');
console.log(`Salario mínimo general: $${salario.salario_diario.toFixed(2)} MXN`);

// Salario mínimo frontera norte
const salarioFN = await SalariosMinimosCatalog.getActual('frontera_norte');
console.log(`Salario frontera norte: $${salarioFN.salario_diario.toFixed(2)} MXN`);

// Salario de una fecha específica
const salarioDate = await SalariosMinimosCatalog.getPorFecha('2024-01-01', 'general');
console.log(`Salario 1 ene 2024: $${salarioDate?.salario_diario.toFixed(2)}`);

// Serie de un año
const salarios2024 = await SalariosMinimosCatalog.getPorAnio(2024, 'general');
console.log(`Cambios en 2024: ${salarios2024.length}`);

// Calcular variación
const variacion = await SalariosMinimosCatalog.calcularVariacion(
  '2023-01-01',
  '2024-01-01',
  'general'
);
console.log(`Incremento anual: ${variacion?.toFixed(2)}%`);
```

---

## 🔄 Actualización Automática

### Python

Los catálogos SQLite se actualizan automáticamente:

```python
from catalogmx.data.updater import get_database_path

# Actualización manual
db_path = get_database_path(
    auto_update=True,      # Activar auto-actualización
    max_age_hours=24       # Actualizar si tiene más de 24 horas
)

# Los catálogos ya incluyen auto-actualización por defecto
from catalogmx.catalogs.banxico.udis_sqlite import UDICatalog
udi = UDICatalog.get_actual()  # Se actualiza automáticamente si es necesario
```

### TypeScript

```typescript
import { HttpVfsUpdater } from 'catalogmx/data/http-vfs-updater';

// Configurar actualización
const updater = new HttpVfsUpdater({
  dbUrl: 'https://openbancor.github.io/catalogmx/data/mexico.sqlite3',
  maxAgeDays: 1  // Actualizar cada día
});

// Los catálogos usan HttpVfsUpdater internamente
```

---

## 📝 Notas Importantes

### Python
- ⚠️ **Todos los métodos son síncronos**
- ✅ Auto-actualización habilitada por defecto (cada 24 horas)
- ✅ Base de datos: `mexico_dynamic.sqlite3`
- ✅ Tablas sin prefijo: `udis`, `tipo_cambio`, `tiie`, etc.

### TypeScript
- ⚠️ **Todos los métodos son asíncronos** (usar `await`)
- ✅ Auto-actualización habilitada por defecto (cada 1 día)
- ✅ Base de datos: `mexico.sqlite3`
- ✅ Tablas con prefijo: `banxico_udis`, `banxico_tipo_cambio`, etc.

### Diferencias Clave

| Aspecto | Python | TypeScript |
|---------|--------|------------|
| **Async/Await** | ❌ No | ✅ Sí (obligatorio) |
| **Base de datos** | `mexico_dynamic.sqlite3` | `mexico.sqlite3` |
| **Prefijo tablas** | Sin prefijo | Con prefijo `banxico_` |
| **Auto-update** | 24 horas | 1 día |
| **Entorno** | Backend / Scripts | Frontend / Backend |

---

## 🚀 Casos de Uso Comunes

### 1. Calcular crédito hipotecario en UDIs

```python
from catalogmx.catalogs.banxico.udis_sqlite import UDICatalog

# Crédito de 1,000,000 MXN
monto_pesos = 1_000_000
fecha = "2024-01-01"

# Convertir a UDIs
monto_udis = UDICatalog.pesos_a_udis(monto_pesos, fecha)
print(f"Crédito: {monto_udis:,.2f} UDIs")

# Pago mensual en UDIs (ejemplo simplificado)
tasa_mensual = 0.08 / 12  # 8% anual
plazo_meses = 240  # 20 años
pago_udi = monto_udis * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)

# Convertir pago a pesos
udi_actual = UDICatalog.get_actual()
pago_pesos = pago_udi * udi_actual['valor']
print(f"Pago mensual: {pago_pesos:,.2f} MXN ({pago_udi:,.2f} UDIs)")
```

### 2. Convertir factura en dólares

```python
from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import TipoCambioUSDCatalog

# Factura de $5,000 USD
dolares = 5000
fecha = "2024-06-15"

# Convertir a pesos
pesos = TipoCambioUSDCatalog.dolares_a_pesos(dolares, fecha)
print(f"${dolares:,.2f} USD = ${pesos:,.2f} MXN")
```

### 3. Calcular rendimiento CETES

```python
from catalogmx.catalogs.banxico.cetes_sqlite import CETESCatalog

# Invertir en CETES 28 días
monto = 100_000
plazo = 28

# Tasa actual
cetes = CETESCatalog.get_actual(plazo=plazo)
tasa = cetes['tasa'] / 100

# Rendimiento
rendimiento = monto * tasa * (plazo / 360)
print(f"Inversión: ${monto:,.2f}")
print(f"Tasa CETES {plazo} días: {cetes['tasa']}%")
print(f"Rendimiento estimado: ${rendimiento:,.2f}")
```

---

## 🔗 Referencias

- **Documentación completa**: [https://github.com/openbancor/catalogmx](https://github.com/openbancor/catalogmx)
- **API Reference Python**: [docs/api/python/](../api/python/)
- **API Reference TypeScript**: [docs/api/typescript/](../api/typescript/)
- **Fuente de datos**: [Banco de México (Banxico)](https://www.banxico.org.mx/)

---

## 📄 Licencia

BSD-2-Clause © 2024 Luis Fernando Barrera
