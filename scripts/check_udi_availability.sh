#!/bin/bash
# Script para verificar qué valores de UDI están disponibles en Banxico

if [ -z "$BANXICO_TOKEN" ]; then
  echo "Error: BANXICO_TOKEN no está configurado"
  exit 1
fi

echo "🔍 Verificando disponibilidad de UDI en Banxico..."
echo ""

# Ver último valor local
LAST_LOCAL=$(jq -r '.[-1].fecha' packages/shared-data/banxico/udis.json 2>/dev/null || echo "sin datos")
echo "📅 Última fecha local: $LAST_LOCAL"
echo ""

# Probar fin de mes actual
YEAR=$(date +%Y)
MONTH=$(date +%m)
# Calcular último día del mes
LAST_DAY=$(date -v1d -v+1m -v-1d +%Y-%m-%d 2>/dev/null || date -d "$(date +%Y-%m-01) +1 month -1 day" +%Y-%m-%d)

echo "🌐 Consultando Banxico para fin de mes: $LAST_DAY"
echo ""

RESPONSE=$(curl -s -H "Bmx-Token: $BANXICO_TOKEN" \
  "https://www.banxico.org.mx/SieAPIRest/service/v1/series/SP68257/datos/$LAST_DAY/$LAST_DAY")

if echo "$RESPONSE" | jq -e '.bmx.series[0].datos[0]' > /dev/null 2>&1; then
  VALOR=$(echo "$RESPONSE" | jq -r '.bmx.series[0].datos[0].dato')
  echo "✅ Banxico tiene UDI para $LAST_DAY: $VALOR MXN"
  echo ""
  echo "💡 Puedes descargar hasta el fin de mes ejecutando:"
  echo "   python3 packages/shared-data/scripts/fetch_udis_banxico.py"
else
  echo "⚠️  UDI para $LAST_DAY aún no disponible"
  echo ""
  echo "Banxico publica valores de UDI para todo el mes, usualmente:"
  echo "  • Al inicio del mes (día 1-5)"
  echo "  • Los valores están disponibles por adelantado"
fi

echo ""
echo "📊 Para actualizar: ./scripts/full_check.sh"

