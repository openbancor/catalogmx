#!/usr/bin/env python3
"""Test RESICO calculator"""

from catalogmx.calculators import calculate_resico

print("=" * 80)
print("TEST RESICO CALCULATOR - PYTHON")
print("=" * 80)

# Test case 1: Monthly $50,000 → bracket 1.5% → ISR = $750
result1 = calculate_resico(50000, "mensual", 2026)
print(f"\nTest 1: Ingreso mensual $50,000")
print(
    f"  Bracket: ${result1['bracket']['limiteInferior']:.2f} - ${result1['bracket']['limiteSuperior']:.2f}"
)
print(f"  Tasa: {result1['bracket']['tasa']}%")
print(f"  RESICO: ${result1['resicoCalculado']:.2f}")
print(f"  Tasa efectiva: {result1['tasaEfectiva']:.2f}%")
print(f"  Dentro del límite: {'Sí' if result1['dentroDeLimite'] else 'No'}")

# Test case 2: Monthly $25,000 → bracket 1.1% → ISR = $275
result2 = calculate_resico(25000, "mensual", 2026)
print(f"\nTest 2: Ingreso mensual $25,000")
print(f"  RESICO: ${result2['resicoCalculado']:.2f} (esperado: $275.00)")

# Test case 3: Annual $500,000 → bracket 1.1% → ISR = $5,500
result3 = calculate_resico(500000, "anual", 2026)
print(f"\nTest 3: Ingreso anual $500,000")
print(f"  RESICO: ${result3['resicoCalculado']:.2f} (esperado: $5,500.00)")

# Test case 4: Annual $1,000,000 → bracket 1.5% → ISR = $15,000
result4 = calculate_resico(1000000, "anual", 2024)
print(f"\nTest 4: Ingreso anual $1,000,000 (2024)")
print(f"  RESICO: ${result4['resicoCalculado']:.2f} (esperado: $15,000.00)")

# Test case 5: Over limit
result5 = calculate_resico(400000, "mensual", 2026)
print(f"\nTest 5: Ingreso mensual $400,000 (excede límite)")
print(f"  RESICO: ${result5['resicoCalculado']:.2f}")
print(f"  Dentro del límite: {'Sí' if result5['dentroDeLimite'] else 'No'}")
print(f"  Límite máximo mensual: ${result5['limiteMaximo']:.2f}")

print("\n" + "=" * 80)
print("✅ RESICO Python calculator working!")
print("=" * 80)
