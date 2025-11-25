# Investigación: Serie correcta de UDI en Banxico

## Problema Detectado

La serie **SF43718** descargó valores incorrectos:
- 1995-04-04: 6.5883 ❌ (debería ser 1.0)
- Esos valores parecen ser tipo de cambio USD/MXN

## Series de UDI en Banxico

Según la documentación de Banxico, las series de UDI son:

### Posibles series correctas:

1. **SP68257** - UDI (Valor en pesos)
2. **SF60632** - UDI 
3. **SF43718** - ❌ Esta parece ser otra cosa (tipo de cambio?)

## Acción Requerida

Necesitas verificar en el catálogo de Banxico cuál es la serie correcta:

https://www.banxico.org.mx/SieAPIRest/service/v1/doc/catalogoSeries

O buscar "UDI" en:
- https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do

## Solución Temporal

Mantener el dato sintético original (1.0 en 1995-04-04) hasta confirmar la serie correcta.

## Cómo Probar Series

```bash
# Probar serie SP68257
curl -H "Bmx-Token: $BANXICO_TOKEN" \
  "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SP68257/datos/1995-04-04/1995-04-10"

# Probar serie SF60632  
curl -H "Bmx-Token: $BANXICO_TOKEN" \
  "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF60632/datos/1995-04-04/1995-04-10"
```

El resultado correcto debe mostrar:
- 1995-04-04: ~1.0
- 1995-04-05: ~1.000X (incremento mínimo)
- 2025-11-24: ~8.4 (no 18.5)

