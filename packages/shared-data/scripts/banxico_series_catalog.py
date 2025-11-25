#!/usr/bin/env python3
"""
Explore available series in Banxico API

Common Banxico Series Codes:
- SF43718: UDI (already implemented)
- SF43936: USD/MXN Exchange Rate (FIX)
- SF61745: TIIE 28 days
- SF43783: TIIE 91 days
- SF331451: CETES 28 days
- SF43936: Tipo de cambio FIX
- SF46410: Reservas internacionales
- SF17905: Base monetaria
"""

# Series that would be useful for catalogmx
BANXICO_SERIES = {
    # Exchange Rates
    "tipo_cambio_usd": {
        "series": "SF43936",
        "name": "Tipo de Cambio USD/MXN (FIX)",
        "description": "Tipo de cambio oficial peso-dólar publicado por Banxico",
        "frequency": "daily",
        "start": "1991-11-08",
    },
    "tipo_cambio_euro": {
        "series": "SF46410", 
        "name": "Tipo de Cambio EUR/MXN",
        "description": "Tipo de cambio peso-euro",
        "frequency": "daily",
        "start": "1999-01-04",
    },
    
    # Interest Rates
    "tiie_28": {
        "series": "SF61745",
        "name": "TIIE 28 días",
        "description": "Tasa de Interés Interbancaria de Equilibrio a 28 días",
        "frequency": "daily",
        "start": "1995-03-23",
    },
    "tiie_91": {
        "series": "SF43783",
        "name": "TIIE 91 días",
        "description": "Tasa de Interés Interbancaria de Equilibrio a 91 días",
        "frequency": "daily",
        "start": "1995-03-23",
    },
    "cetes_28": {
        "series": "SF331451",
        "name": "CETES 28 días",
        "description": "Tasa de rendimiento de CETES a 28 días",
        "frequency": "weekly",
        "start": "1994-01-06",
    },
    
    # Monetary Aggregates  
    "reservas": {
        "series": "SF46410",
        "name": "Reservas Internacionales",
        "description": "Reservas internacionales de México (millones USD)",
        "frequency": "daily",
        "start": "1995-01-02",
    },
}

def print_catalog():
    """Print available series"""
    print("=" * 80)
    print("SERIES DISPONIBLES EN API DE BANXICO")
    print("=" * 80)
    print()
    
    categories = {
        "Tipos de Cambio": ["tipo_cambio_usd", "tipo_cambio_euro"],
        "Tasas de Interés": ["tiie_28", "tiie_91", "cetes_28"],
        "Indicadores Monetarios": ["reservas"],
    }
    
    for category, series_ids in categories.items():
        print(f"📊 {category}")
        print("-" * 80)
        for sid in series_ids:
            if sid in BANXICO_SERIES:
                s = BANXICO_SERIES[sid]
                print(f"  • {s['name']}")
                print(f"    Serie: {s['series']}")
                print(f"    Desde: {s['start']} | Frecuencia: {s['frequency']}")
                print(f"    {s['description']}")
                print()
        print()
    
    print("=" * 80)
    print("IMPLEMENTACIÓN")
    print("=" * 80)
    print()
    print("Para agregar una serie:")
    print("  1. Copia fetch_udis_banxico.py → fetch_<serie>_banxico.py")
    print("  2. Cambia UDI_SERIES al código correspondiente")
    print("  3. Ajusta el formato de salida según necesites")
    print()
    print("Para consultas ad-hoc:")
    print("  curl -H 'Bmx-Token: TU_TOKEN' \\")
    print("    'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43936/datos/2025-01-01/2025-01-31'")
    print()
    print("Más series en: https://www.banxico.org.mx/SieAPIRest/service/v1/doc/catalogoSeries")
    print()


if __name__ == "__main__":
    print_catalog()

