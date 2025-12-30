#!/usr/bin/env python3
"""
Demo de uso de catálogos de Banxico en catalogmx

Este script demuestra cómo usar los diferentes catálogos de
Banco de México disponibles en la librería catalogmx.
"""

from datetime import datetime


def demo_udis():
    """Demostración del catálogo de UDIs"""
    print("\n" + "=" * 60)
    print("📊 UDI (Unidades de Inversión)")
    print("=" * 60)

    from catalogmx.catalogs.banxico.udis_sqlite import (
        UDICatalog,
        get_udi_actual,
        pesos_a_udis,
        udis_a_pesos,
    )

    # 1. UDI actual
    udi_actual = get_udi_actual()
    print(f"\n✓ UDI actual:")
    print(f"  Valor: {udi_actual['valor']:.6f}")
    print(f"  Fecha: {udi_actual['fecha']}")
    print(f"  Tipo: {udi_actual['tipo']}")

    # 2. UDI de una fecha específica
    fecha = "2024-01-15"
    udi = UDICatalog.get_por_fecha(fecha)
    if udi:
        print(f"\n✓ UDI del {fecha}:")
        print(f"  Valor: {udi['valor']:.6f}")

    # 3. Conversión pesos → UDIs
    pesos = 100_000.0
    udis = pesos_a_udis(pesos, fecha)
    if udis:
        print(f"\n✓ Conversión:")
        print(f"  ${pesos:,.2f} MXN = {udis:,.4f} UDIs")

    # 4. Conversión UDIs → pesos
    udis_amount = 10_000.0
    pesos_result = udis_a_pesos(udis_amount, fecha)
    if pesos_result:
        print(f"  {udis_amount:,.2f} UDIs = ${pesos_result:,.2f} MXN")

    # 5. Promedio mensual
    udi_mes = UDICatalog.get_por_mes(2024, 1)
    if udi_mes:
        print(f"\n✓ UDI promedio enero 2024: {udi_mes['valor']:.6f}")

    # 6. Variación anual
    var = UDICatalog.calcular_variacion("2024-01-01", "2024-12-31")
    if var:
        print(f"✓ Variación anual 2024: {var:.2f}%")


def demo_tipo_cambio():
    """Demostración del catálogo de tipo de cambio"""
    print("\n" + "=" * 60)
    print("💵 Tipo de Cambio USD/MXN (FIX)")
    print("=" * 60)

    from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
        TipoCambioUSDCatalog,
        get_tipo_cambio_actual,
        usd_a_mxn,
        mxn_a_usd,
    )

    # 1. Tipo de cambio actual
    tc_actual = get_tipo_cambio_actual()
    print(f"\n✓ Tipo de cambio FIX actual:")
    print(f"  {tc_actual['tipo_cambio']:.4f} MXN/USD")
    print(f"  Fecha: {tc_actual['fecha']}")

    # 2. Tipo de cambio de una fecha
    fecha = "2024-06-15"
    tc = TipoCambioUSDCatalog.get_por_fecha(fecha)
    if tc:
        print(f"\n✓ Tipo de cambio del {fecha}:")
        print(f"  {tc['tipo_cambio']:.4f} MXN/USD")

    # 3. Conversión dólares → pesos
    dolares = 1_000.0
    pesos = usd_a_mxn(dolares, fecha)
    if pesos:
        print(f"\n✓ Conversión:")
        print(f"  ${dolares:,.2f} USD = ${pesos:,.2f} MXN")

    # 4. Conversión pesos → dólares
    pesos_amount = 20_000.0
    dolares_result = mxn_a_usd(pesos_amount, fecha)
    if dolares_result:
        print(f"  ${pesos_amount:,.2f} MXN = ${dolares_result:,.2f} USD")

    # 5. Variación anual
    var = TipoCambioUSDCatalog.calcular_variacion("2024-01-02", "2024-12-31")
    if var:
        print(f"\n✓ Variación del peso en 2024: {var:.2f}%")


def demo_tiie():
    """Demostración del catálogo de TIIE"""
    print("\n" + "=" * 60)
    print("📈 TIIE (Tasa de Interés Interbancaria)")
    print("=" * 60)

    from catalogmx.catalogs.banxico.tiie_sqlite import (
        TIIECatalog,
        get_tiie_actual,
    )

    # 1. TIIE actual (28 días)
    tiie = get_tiie_actual(plazo=28)
    print(f"\n✓ TIIE 28 días actual:")
    print(f"  Tasa: {tiie['tasa']:.4f}%")
    print(f"  Fecha: {tiie['fecha']}")

    # 2. TIIE de una fecha
    fecha = "2024-06-15"
    tiie_fecha = TIIECatalog.get_por_fecha(fecha, plazo=28)
    if tiie_fecha:
        print(f"\n✓ TIIE 28 días del {fecha}:")
        print(f"  Tasa: {tiie_fecha['tasa']:.4f}%")

    # 3. Promedio mensual
    promedio = TIIECatalog.get_promedio_mes(2024, 6, plazo=28)
    if promedio:
        print(f"\n✓ TIIE 28 días promedio junio 2024: {promedio:.4f}%")

    # 4. Datos de un año
    tiies_2024 = TIIECatalog.get_por_anio(2024, plazo=28)
    print(f"\n✓ Registros TIIE 28 días en 2024: {len(tiies_2024)}")


def demo_cetes():
    """Demostración del catálogo de CETES"""
    print("\n" + "=" * 60)
    print("📉 CETES (Certificados de la Tesorería)")
    print("=" * 60)

    from catalogmx.catalogs.banxico.cetes_sqlite import (
        CETESCatalog,
        get_cetes_actual,
    )

    # 1. CETES actual (28 días)
    cetes = get_cetes_actual(plazo=28)
    print(f"\n✓ CETES 28 días actual:")
    print(f"  Tasa: {cetes['tasa']:.4f}%")
    print(f"  Fecha: {cetes['fecha']}")

    # 2. Diferentes plazos
    for plazo in [28, 91, 182, 364]:
        cetes_p = CETESCatalog.get_actual(plazo=plazo)
        if cetes_p:
            print(f"  CETES {plazo} días: {cetes_p['tasa']:.4f}%")

    # 3. Calcular rendimiento
    monto = 100_000
    plazo = 28
    tasa = cetes['tasa'] / 100
    rendimiento = monto * tasa * (plazo / 360)
    print(f"\n✓ Inversión simulada:")
    print(f"  Monto: ${monto:,.2f}")
    print(f"  Plazo: {plazo} días")
    print(f"  Tasa: {cetes['tasa']:.4f}%")
    print(f"  Rendimiento estimado: ${rendimiento:,.2f}")


def demo_inflacion():
    """Demostración del catálogo de inflación"""
    print("\n" + "=" * 60)
    print("📊 Inflación (INPC)")
    print("=" * 60)

    from catalogmx.catalogs.banxico.inflacion_sqlite import (
        InflacionCatalog,
        get_inflacion_actual,
        get_inflacion_anual_actual,
    )

    # 1. Inflación actual
    inflacion = get_inflacion_actual()
    print(f"\n✓ Inflación actual:")
    print(f"  Anual: {inflacion['inflacion_anual']:.2f}%")
    print(f"  Mensual: {inflacion['inflacion_mensual']:.2f}%")
    print(f"  INPC: {inflacion['inpc']:.4f}")
    print(f"  Fecha: {inflacion['fecha']}")

    # 2. Solo inflación anual
    inf_anual = get_inflacion_anual_actual()
    print(f"\n✓ Inflación anual: {inf_anual:.2f}%")

    # 3. Inflación de un mes específico
    inf_mes = InflacionCatalog.get_por_mes(2024, 6)
    if inf_mes:
        print(f"\n✓ Inflación junio 2024:")
        print(f"  Anual: {inf_mes['inflacion_anual']:.2f}%")
        print(f"  Mensual: {inf_mes['inflacion_mensual']:.2f}%")

    # 4. Promedio anual
    promedio = InflacionCatalog.get_promedio_anual(2024)
    if promedio:
        print(f"\n✓ Inflación promedio 2024: {promedio:.2f}%")

    # 5. Inflación acumulada
    acumulada = InflacionCatalog.calcular_inflacion_acumulada(2024, 1, 2024, 12)
    if acumulada:
        print(f"✓ Inflación acumulada 2024: {acumulada:.2f}%")


def demo_salarios():
    """Demostración del catálogo de salarios mínimos"""
    print("\n" + "=" * 60)
    print("💰 Salarios Mínimos")
    print("=" * 60)

    from catalogmx.catalogs.banxico.salarios_minimos_sqlite import (
        SalariosMinimosCatalog,
        get_salario_minimo_actual,
    )

    # 1. Salario mínimo actual (general)
    salario = get_salario_minimo_actual(zona="general")
    print(f"\n✓ Salario mínimo general:")
    print(f"  Diario: ${salario['salario_diario']:.2f} MXN")
    print(f"  Fecha: {salario['fecha']}")

    # 2. Salario frontera norte
    salario_fn = SalariosMinimosCatalog.get_actual(zona="frontera_norte")
    print(f"\n✓ Salario mínimo frontera norte:")
    print(f"  Diario: ${salario_fn['salario_diario']:.2f} MXN")

    # 3. Calcular mensual y anual
    diario = salario['salario_diario']
    mensual = diario * 30
    anual = diario * 365
    print(f"\n✓ Equivalencias (zona general):")
    print(f"  Diario: ${diario:,.2f}")
    print(f"  Mensual (30 días): ${mensual:,.2f}")
    print(f"  Anual (365 días): ${anual:,.2f}")

    # 4. Variación anual
    var = SalariosMinimosCatalog.calcular_variacion(
        "2023-01-01", "2024-01-01", zona="general"
    )
    if var:
        print(f"\n✓ Incremento anual 2023-2024: {var:.2f}%")


def main():
    """Ejecutar todos los demos"""
    print("\n" + "=" * 60)
    print("🇲🇽 catalogmx - Demo de Catálogos Banxico")
    print("=" * 60)
    print("\nEste demo muestra cómo usar los catálogos de Banco de México.")
    print("Presiona Ctrl+C para salir en cualquier momento.\n")

    try:
        demo_udis()
        demo_tipo_cambio()
        demo_tiie()
        demo_cetes()
        demo_inflacion()
        demo_salarios()

        print("\n" + "=" * 60)
        print("✅ Demo completado")
        print("=" * 60)
        print("\nPara más información:")
        print("  📖 Documentación: docs/guides/banxico-catalogs-usage.md")
        print("  🔗 GitHub: https://github.com/openbancor/catalogmx")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
