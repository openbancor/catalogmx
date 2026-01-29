#!/usr/bin/env python3
"""
Tipo de Cambio App - Consulta y convierte USD/MXN

Una pequeña app que demuestra el uso del catálogo de tipo de cambio
de Banxico con actualizaciones automáticas.

Uso:
    python tipo_cambio_app.py [comando]

Comandos:
    actual      Muestra el tipo de cambio actual
    convertir   Convierte entre USD y MXN
    historico   Muestra tipo de cambio de una fecha
    rango       Muestra variación en un rango de fechas
"""

import sys
from datetime import date, timedelta


def print_header():
    """Imprime el encabezado de la app."""
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║     💵 Tipo de Cambio USD/MXN - catalogmx            ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


def cmd_actual():
    """Muestra el tipo de cambio actual."""
    from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
        get_tipo_cambio_actual,
    )

    tc = get_tipo_cambio_actual()

    print(f"  📅 Fecha:        {tc['fecha']}")
    print(f"  💱 Tipo cambio:  ${tc['tipo_cambio']:.4f} MXN por 1 USD")
    print()
    print(f"  Ejemplos de conversión:")
    print(f"    $1 USD    = ${tc['tipo_cambio']:.2f} MXN")
    print(f"    $100 USD  = ${tc['tipo_cambio'] * 100:,.2f} MXN")
    print(f"    $1000 USD = ${tc['tipo_cambio'] * 1000:,.2f} MXN")
    print()
    print(f"    $100 MXN  = ${100 / tc['tipo_cambio']:.2f} USD")
    print(f"    $1000 MXN = ${1000 / tc['tipo_cambio']:.2f} USD")


def cmd_convertir():
    """Convierte entre USD y MXN."""
    from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
        get_tipo_cambio_actual,
        usd_a_mxn,
        mxn_a_usd,
    )

    print("  Ingresa la cantidad a convertir:")
    cantidad = input("  Cantidad: ").strip()

    try:
        cantidad = float(cantidad.replace(",", "").replace("$", ""))
    except ValueError:
        print("  ❌ Cantidad inválida")
        return

    print()
    print("  ¿De qué moneda a cuál?")
    print("    1. USD → MXN")
    print("    2. MXN → USD")
    opcion = input("  Opción (1/2): ").strip()

    tc = get_tipo_cambio_actual()

    if opcion == "1":
        resultado = usd_a_mxn(cantidad)
        print()
        print(f"  💵 ${cantidad:,.2f} USD = ${resultado:,.2f} MXN")
        print(f"     (Tipo de cambio: {tc['tipo_cambio']:.4f})")
    elif opcion == "2":
        resultado = mxn_a_usd(cantidad)
        print()
        print(f"  🇲🇽 ${cantidad:,.2f} MXN = ${resultado:,.2f} USD")
        print(f"     (Tipo de cambio: {tc['tipo_cambio']:.4f})")
    else:
        print("  ❌ Opción inválida")


def cmd_historico():
    """Muestra tipo de cambio de una fecha específica."""
    from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
        TipoCambioUSDCatalog,
    )

    print("  Ingresa la fecha (YYYY-MM-DD):")
    fecha = input("  Fecha: ").strip()

    tc = TipoCambioUSDCatalog.get_por_fecha(fecha)

    if tc:
        print()
        print(f"  📅 Fecha:       {tc['fecha']}")
        print(f"  💱 Tipo cambio: ${tc['tipo_cambio']:.4f} MXN/USD")
    else:
        print(f"  ❌ No hay datos para la fecha {fecha}")
        print("     (Solo días hábiles tienen tipo de cambio)")


def cmd_rango():
    """Muestra variación en un rango de fechas."""
    from catalogmx.catalogs.banxico.tipo_cambio_usd_sqlite import (
        TipoCambioUSDCatalog,
    )

    # Por defecto: últimos 30 días
    hoy = date.today()
    hace_30 = hoy - timedelta(days=30)

    fecha_inicio = hace_30.isoformat()
    fecha_fin = hoy.isoformat()

    print(f"  Rango por defecto: {fecha_inicio} a {fecha_fin}")
    print("  (Presiona Enter para usar el rango por defecto)")

    nueva_inicio = input("  Fecha inicio (YYYY-MM-DD): ").strip()
    if nueva_inicio:
        fecha_inicio = nueva_inicio

    nueva_fin = input("  Fecha fin (YYYY-MM-DD): ").strip()
    if nueva_fin:
        fecha_fin = nueva_fin

    datos = TipoCambioUSDCatalog.get_rango(fecha_inicio, fecha_fin)

    if not datos:
        print("  ❌ No hay datos para el rango especificado")
        return

    # Calcular estadísticas
    valores = [d["tipo_cambio"] for d in datos]
    minimo = min(valores)
    maximo = max(valores)
    promedio = sum(valores) / len(valores)
    primero = valores[0]
    ultimo = valores[-1]
    variacion = ((ultimo - primero) / primero) * 100

    print()
    print(f"  📊 Estadísticas del período:")
    print(f"     Registros:  {len(datos)}")
    print(f"     Mínimo:     ${minimo:.4f}")
    print(f"     Máximo:     ${maximo:.4f}")
    print(f"     Promedio:   ${promedio:.4f}")
    print(f"     Inicial:    ${primero:.4f}")
    print(f"     Final:      ${ultimo:.4f}")
    print(f"     Variación:  {variacion:+.2f}%")


def cmd_help():
    """Muestra ayuda."""
    print("  Comandos disponibles:")
    print()
    print("    actual     - Muestra el tipo de cambio actual")
    print("    convertir  - Convierte entre USD y MXN")
    print("    historico  - Consulta tipo de cambio de una fecha")
    print("    rango      - Muestra estadísticas de un período")
    print("    salir      - Salir de la aplicación")
    print()


def main():
    """Función principal."""
    print_header()

    # Si hay argumentos, ejecutar comando directo
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "actual":
            cmd_actual()
        elif cmd == "convertir":
            cmd_convertir()
        elif cmd == "historico":
            cmd_historico()
        elif cmd == "rango":
            cmd_rango()
        else:
            cmd_help()
        return

    # Modo interactivo
    print("  Escribe 'ayuda' para ver los comandos disponibles")
    print()

    while True:
        try:
            comando = input("  > ").strip().lower()

            if comando in ("salir", "exit", "quit", "q"):
                print("  👋 ¡Hasta luego!")
                break
            elif comando in ("ayuda", "help", "?"):
                cmd_help()
            elif comando == "actual":
                cmd_actual()
            elif comando == "convertir":
                cmd_convertir()
            elif comando == "historico":
                cmd_historico()
            elif comando == "rango":
                cmd_rango()
            elif comando == "":
                continue
            else:
                print(f"  ❓ Comando desconocido: {comando}")
                print("     Escribe 'ayuda' para ver los comandos")

            print()

        except KeyboardInterrupt:
            print("\n  👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"  ❌ Error: {e}")
            print()


if __name__ == "__main__":
    main()
