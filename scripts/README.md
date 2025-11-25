# 🚀 Script de Validación Completa - full_check.sh

## Qué hace

Ejecuta **TODOS** los checks de calidad antes de publicar:

1. ✅ Actualiza datos de UDI desde Banxico (si tienes token)
2. ✅ Genera base de datos SQLite unificada
3. ✅ Cierra WAL para compatibilidad con navegador
4. ✅ Sincroniza a webapp/public/data
5. ✅ Build del webapp
6. ✅ Lint + typecheck TypeScript
7. ✅ Format + lint + tests Python (>90% coverage)
8. ✅ Format + analyze + tests Dart

## 🎯 Uso

### Básico (sin actualizar UDI):
```bash
cd catalogmx
./scripts/full_check.sh
```

### Con actualización de UDI:
```bash
cd catalogmx
export BANXICO_TOKEN="tu_token_aqui"
./scripts/full_check.sh
```

## 🔑 Token de Banxico (Opcional)

Para actualizar automáticamente los valores de UDI:

1. **Obtén token gratis**: https://www.banxico.org.mx/SieAPIRest/service/v1/token
2. **Configura**:
   ```bash
   # Una sola vez en tu .bashrc o .zshrc
   export BANXICO_TOKEN="abc123def456..."
   ```
3. **Usa**: El script automáticamente descargará ~11k registros de UDI

Si NO tienes token:
- ℹ️ El script continúa normalmente
- ℹ️ Usa los datos existentes de UDI
- ✅ Todo lo demás funciona igual

## 📋 Flujo Completo de Publicación

```bash
# 1. Actualizar UDI y validar TODO
export BANXICO_TOKEN="tu_token"  # Opcional
./scripts/full_check.sh

# 2. Si TODO pasa ✅
git add .
git commit -m "feat: descripción"
git push origin main
```

## ✅ Qué Verifica

### Datos
- 📊 UDI actualizada (si hay token)
- 🗄️ mexico.sqlite3 generado sin WAL
- 📁 Archivos copiados a public/data

### Webapp
- 🔨 Build exitoso
- 📦 Assets generados

### TypeScript
- 🎨 ESLint + auto-fix
- 💅 Prettier format
- 🔍 Type check

### Python
- 🎨 Black format
- 🔍 Ruff lint + auto-fix
- 🏷️ mypy type check
- 🧪 Tests con >90% coverage

### Dart
- 🎨 dart format
- 🔍 dart analyze
- 🧪 dart test

## ⏱️ Tiempo Estimado

- Sin UDI: ~2-3 minutos
- Con UDI: ~3-4 minutos (primera vez descarga ~11k registros)

## 🎉 Resultado

Si el script termina con:
```
All checks completed.
```

Entonces TODO está listo para commitear y publicar. 🚀

