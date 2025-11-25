# 📊 Series Útiles de Banxico para catalogmx

## 🏦 Tasas de Interés

| Serie | Nombre | Inicio | Periodicidad | Uso |
|-------|--------|--------|--------------|-----|
| **SF43783** | TIIE 28 días | 1995-03-23 | Diaria | ✅ Tasa interbancaria, créditos |
| **SF43784** | TIIE 91 días | 1995-03-23 | Diaria | Tasa interbancaria mediano plazo |
| **SF43878** | TIIE 182 días | 1995-03-23 | Diaria | Tasa interbancaria largo plazo |
| **SF43936** | CETES 28 días | 1978-01-05 | Semanal | ✅ Tasa libre de riesgo |
| **SF43939** | CETES 182 días | 1978-01-05 | Semanal | Inversión mediano plazo |
| **SF43942** | CETES 364 días | 1978-01-05 | Semanal | Inversión anual |

## 💱 Tipos de Cambio

| Serie | Nombre | Inicio | Uso |
|-------|--------|--------|-----|
| **SF63528** | USD/MXN Serie Histórica | 1954-01-01 | ✅ Tipo de cambio peso dólar desde 1954 |
| **SF43718** | USD/MXN FIX | 1991-11-08 | ✅ Fecha de determinación (FIX) |
| **SF60653** | USD/MXN Liquidación | 1991-11-08 | ✅ Fecha de liquidación |
| **SF46410** | EUR/MXN | 1999-01-04 | Euro/Peso |
| **SF46406** | GBP/MXN | 1992-11-16 | Libra/Peso |
| **SF46407** | JPY/MXN (100) | 1992-11-16 | Yen/Peso |
| **SF46405** | CAD/MXN | 1992-11-16 | Dólar canadiense |

## 📈 Inflación

| Serie | Nombre | Inicio | Uso |
|-------|--------|--------|-----|
| **SP30577** | INPC General | 2010-07 | Índice de precios |
| **SP1** | Inflación mensual | 1969-01 | Variación % mensual |
| **SP30579** | Inflación anual | 2010-07 | Variación % anual |

## 💰 Indicadores Monetarios

| Serie | Nombre | Inicio | Uso |
|-------|--------|--------|-----|
| **SF110168** | Reservas internacionales | 1995-01-03 | Reservas en USD |
| **SF17905** | Base monetaria | 2001-01-01 | M0 |
| **SP68257** | UDI | 1995-04-04 | ✅ Ya implementado |

## 💼 Salarios Mínimos

| Serie | Nombre | Período | Uso |
|-------|--------|---------|-----|
| **SL2538** | Salarios Mínimos General | Hasta nov-2012 | Pesos por día |
| **SL2542** | Índices Reales (1994=100) | Hasta nov-2012 | Inflación ajustada |
| **SL11126** | Salarios Mínimos General | dic-2012 a dic-2018 | Pesos por día |
| **SL11127** | Índices Reales (Dic2012=100) | dic-2012 a dic-2018 | Inflación ajustada |
| **SL11298** | Salarios Mínimos General | Desde dic-2018 | Pesos por día |
| **SL11295** | Zona Libre Frontera Norte | Desde dic-2018 | Pesos por día |
| **SL11297** | Índices Reales General (Dic2018=100) | Desde dic-2018 | Inflación ajustada |
| **SL11296** | Índices Reales Zona Libre | Desde dic-2018 | Inflación ajustada |

## 🎯 Recomendaciones para Implementar

### Alta Prioridad (muy útiles):
1. ✅ **UDI** (SP68257) - Ya implementado
2. **Tipo de Cambio USD FIX** (SF43718) - Crítico para facturación
3. **Tipo de Cambio Histórico** (SF63528) - Serie completa desde 1954
4. **TIIE 28 días** (SF43783) - Tasa de referencia para créditos
5. **CETES 28 días** (SF43936) - Tasa libre de riesgo
6. **Inflación anual** (SP30579) - Indicador económico clave

### Media Prioridad:
7. **Fecha de Liquidación** (SF60653) - Para operaciones financieras
8. **EUR/MXN** (SF46410) - Comercio internacional
9. **Reservas internacionales** (SF110168) - Indicador macroeconómico
10. **Salarios Mínimos** (SL11298, SL11295) - Datos laborales vigentes

### Baja Prioridad:
- Otras tasas TIIE (91, 182 días)
- CETES otros plazos
- Otras divisas

## 🔍 Cómo Encontrar Más Series

Banxico publica el catálogo completo en:
- **Portal Web**: https://www.banxico.org.mx/SieInternet/
- **App móvil**: "Estadísticas Banxico" (190,000+ series)
- **Documentación**: https://www.banxico.org.mx/SieAPIRest/service/v1/doc/index.html

## 💡 Scripts a Crear

Basándome en la prioridad, creemos:

```bash
# Ya tenemos:
fetch_udis_banxico.py (SP68257) ✅

# A crear:
fetch_tipo_cambio_fix.py (SF43718)     # FIX - Fecha determinación
fetch_tipo_cambio_hist.py (SF63528)    # Histórico completo
fetch_tipo_cambio_liq.py (SF60653)     # Liquidación
fetch_tiie_28.py (SF43783)             # Tasa interbancaria
fetch_cetes_28.py (SF43936)            # Tasa libre riesgo
fetch_inflacion.py (SP30579)           # Inflación anual
fetch_salarios_minimos.py (SL11298)    # Salarios vigentes
```

¿Cuáles de estas quieres que implemente primero?

