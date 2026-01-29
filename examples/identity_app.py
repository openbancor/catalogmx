#!/usr/bin/env python3
"""
Identity Generator App - Genera identidades mexicanas de prueba

Una pequeña app que demuestra el generador de identidades mexicanas
para datos de prueba en desarrollo.

Uso:
    python identity_app.py [comando]

Comandos:
    fisica      Genera una persona física
    moral       Genera una persona moral
    lote        Genera múltiples identidades
"""

import json
import sys


def print_header():
    """Imprime el encabezado de la app."""
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║     🪪 Generador de Identidades - catalogmx          ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()


def cmd_fisica():
    """Genera una persona física."""
    from catalogmx.generators import generate_persona_fisica

    print("  Generando persona física...")
    print()

    identity = generate_persona_fisica()

    print(f"  👤 {identity['nombre_completo']}")
    print(f"     Edad: {identity['edad']} años ({identity['sexo_descripcion']})")
    print(f"     Nacimiento: {identity['fecha_nacimiento']}")
    print(f"     Estado: {identity['estado_nacimiento']}")
    print()
    print(f"  📋 Identificadores:")
    print(f"     RFC:  {identity['rfc']}")
    print(f"     CURP: {identity['curp']}")
    print(f"     NSS:  {identity['nss']}")
    print()
    print(f"  🏦 Datos bancarios:")
    print(f"     Banco: {identity['banco'].get('name', 'N/A')}")
    print(f"     CLABE: {identity['clabe']}")
    print(f"     Cuenta: {identity['cuenta']}")
    print()
    print(f"  📍 Dirección:")
    dir_data = identity['direccion']
    print(f"     {dir_data['calle']} {dir_data['numero_exterior']}")
    print(f"     {dir_data['colonia']}")
    print(f"     {dir_data['municipio']}, {dir_data['estado']}")
    print(f"     CP: {dir_data['codigo_postal']}")
    print()
    print(f"  📞 Contacto:")
    print(f"     Tel: {identity['telefono']}")
    print(f"     Email: {identity['email']}")
    print()
    print(f"  💼 Régimen fiscal:")
    print(f"     {identity['regimen_fiscal'].get('code', '')} - {identity['regimen_fiscal'].get('name', 'N/A')}")


def cmd_moral():
    """Genera una persona moral."""
    from catalogmx.generators import generate_persona_moral

    print("  Generando persona moral...")
    print()

    identity = generate_persona_moral()

    print(f"  🏢 {identity['razon_social']}")
    print(f"     Constitución: {identity['fecha_constitucion']}")
    print()
    print(f"  📋 Identificadores:")
    print(f"     RFC: {identity['rfc']}")
    print()
    print(f"  🏦 Datos bancarios:")
    print(f"     Banco: {identity['banco'].get('name', 'N/A')}")
    print(f"     CLABE: {identity['clabe']}")
    print()
    print(f"  📍 Dirección:")
    dir_data = identity['direccion']
    print(f"     {dir_data['calle']} {dir_data['numero_exterior']}")
    print(f"     {dir_data['colonia']}")
    print(f"     {dir_data['municipio']}, {dir_data['estado']}")
    print(f"     CP: {dir_data['codigo_postal']}")
    print()
    print(f"  📞 Contacto:")
    print(f"     Tel: {identity['telefono']}")
    print(f"     Email: {identity['email']}")


def cmd_lote():
    """Genera múltiples identidades."""
    from catalogmx.generators import generate_persona_fisica, generate_persona_moral

    print("  ¿Cuántas identidades deseas generar?")
    cantidad = input("  Cantidad (1-100): ").strip()

    try:
        cantidad = int(cantidad)
        if cantidad < 1 or cantidad > 100:
            print("  ❌ Cantidad debe ser entre 1 y 100")
            return
    except ValueError:
        print("  ❌ Cantidad inválida")
        return

    print()
    print("  ¿Qué tipo de identidades?")
    print("    1. Personas físicas")
    print("    2. Personas morales")
    print("    3. Mixto (50/50)")
    tipo = input("  Opción (1/2/3): ").strip()

    identidades = []

    if tipo == "1":
        for _ in range(cantidad):
            identidades.append(generate_persona_fisica())
    elif tipo == "2":
        for _ in range(cantidad):
            identidades.append(generate_persona_moral())
    elif tipo == "3":
        for i in range(cantidad):
            if i % 2 == 0:
                identidades.append(generate_persona_fisica())
            else:
                identidades.append(generate_persona_moral())
    else:
        print("  ❌ Opción inválida")
        return

    print()
    print(f"  ✅ Se generaron {len(identidades)} identidades")
    print()

    # Mostrar resumen
    fisicas = [i for i in identidades if i['tipo'] == 'persona_fisica']
    morales = [i for i in identidades if i['tipo'] == 'persona_moral']

    print(f"  📊 Resumen:")
    print(f"     Personas físicas: {len(fisicas)}")
    print(f"     Personas morales: {len(morales)}")
    print()

    # Preguntar si exportar
    print("  ¿Exportar a JSON?")
    exportar = input("  (s/n): ").strip().lower()

    if exportar in ('s', 'si', 'yes', 'y'):
        filename = f"identidades_{len(identidades)}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(identidades, f, ensure_ascii=False, indent=2)
        print(f"  ✅ Exportado a: {filename}")


def cmd_validar():
    """Valida RFC y CURP."""
    from catalogmx import validate_rfc, validate_curp

    print("  Ingresa el RFC o CURP a validar:")
    codigo = input("  Código: ").strip().upper()

    if len(codigo) == 13:
        # RFC persona física
        if validate_rfc(codigo):
            print(f"  ✅ RFC válido: {codigo}")
        else:
            print(f"  ❌ RFC inválido: {codigo}")
    elif len(codigo) == 12:
        # RFC persona moral
        if validate_rfc(codigo):
            print(f"  ✅ RFC válido (persona moral): {codigo}")
        else:
            print(f"  ❌ RFC inválido: {codigo}")
    elif len(codigo) == 18:
        # CURP
        if validate_curp(codigo):
            print(f"  ✅ CURP válido: {codigo}")
        else:
            print(f"  ❌ CURP inválido: {codigo}")
    else:
        print(f"  ❓ Código no reconocido (longitud: {len(codigo)})")
        print("     RFC persona física: 13 caracteres")
        print("     RFC persona moral: 12 caracteres")
        print("     CURP: 18 caracteres")


def cmd_help():
    """Muestra ayuda."""
    print("  Comandos disponibles:")
    print()
    print("    fisica   - Genera una persona física")
    print("    moral    - Genera una persona moral")
    print("    lote     - Genera múltiples identidades")
    print("    validar  - Valida RFC o CURP")
    print("    salir    - Salir de la aplicación")
    print()


def main():
    """Función principal."""
    print_header()

    # Si hay argumentos, ejecutar comando directo
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "fisica":
            cmd_fisica()
        elif cmd == "moral":
            cmd_moral()
        elif cmd == "lote":
            cmd_lote()
        elif cmd == "validar":
            cmd_validar()
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
            elif comando == "fisica":
                cmd_fisica()
            elif comando == "moral":
                cmd_moral()
            elif comando == "lote":
                cmd_lote()
            elif comando == "validar":
                cmd_validar()
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
