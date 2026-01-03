#!/usr/bin/env python3
"""Test ISR calculator"""

from catalogmx.calculators import calculate_isr

# Test 2026 monthly calculation
result = calculate_isr(15000, "mensual", 2026)
isr_final = result["isrFinal"]
tasa = result["tasaEfectiva"]
print(f"ISR 2026 Mensual ($15,000): ${isr_final:.2f}")
print(f"Tasa efectiva: {tasa:.2f}%")

# Test 2024 monthly calculation
result24 = calculate_isr(15000, "mensual", 2024)
isr_final_24 = result24["isrFinal"]
tasa_24 = result24["tasaEfectiva"]
print(f"\nISR 2024 Mensual ($15,000): ${isr_final_24:.2f}")
print(f"Tasa efectiva: {tasa_24:.2f}%")

# Test daily calculation
result_daily = calculate_isr(500, "diaria", 2026)
isr_daily = result_daily["isrFinal"]
print(f"\nISR 2026 Diaria ($500): ${isr_daily:.2f}")

print("\n✅ Python calculator working!")
