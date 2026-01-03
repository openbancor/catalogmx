# Guía de Publicación de Librerías CatalogMX

Esta guía explica cómo publicar las librerías de CatalogMX en los repositorios oficiales de **Python (PyPI)**, **TypeScript (npm)**, y **Dart (pub.dev)**.

---

## 📦 Python (PyPI)

### Pre-requisitos

```bash
# Instalar herramientas de publicación
pip install build twine

# Configurar credenciales PyPI (crea ~/.pypirc)
cat > ~/.pypirc <<EOF
[distutils]
index-servers =
    pypi

[pypi]
username = __token__
password = <tu-token-de-pypi>
EOF
```

### Obtener token de PyPI

1. Ve a https://pypi.org/manage/account/token/
2. Crea un nuevo token con scope "Entire account" o específico para `catalogmx`
3. Copia el token (empieza con `pypi-`)
4. Guárdalo en `~/.pypirc` como se muestra arriba

### Proceso de publicación

```bash
cd packages/python

# 1. Actualizar versión en pyproject.toml
# Edita la línea: version = "X.Y.Z"
nano pyproject.toml

# 2. Limpiar builds anteriores
rm -rf dist/ build/ *.egg-info

# 3. Ejecutar tests (obligatorio - coverage >= 90%)
pytest tests/ --cov=catalogmx --cov-branch
# Debe mostrar coverage >= 90%

# 4. Lint y format (obligatorio)
black catalogmx/
ruff check catalogmx/

# 5. Build del paquete
python -m build

# 6. Verificar el paquete
python -m twine check dist/*
# Debe mostrar: PASSED

# 7. Publicar a PyPI (PRODUCCIÓN)
python -m twine upload dist/*

# 7-alt. Publicar a TestPyPI (PRUEBAS)
python -m twine upload --repository testpypi dist/*
```

### Verificar instalación

```bash
# Desde PyPI
pip install catalogmx

# Desde TestPyPI
pip install --index-url https://test.pypi.org/simple/ catalogmx

# Verificar versión
python -c "import catalogmx; print(catalogmx.__version__)"
```

### Checklist pre-publicación Python

- [ ] Coverage >= 90%
- [ ] Todos los tests pasando
- [ ] Código formateado con Black
- [ ] Sin errores de Ruff
- [ ] Versión actualizada en `pyproject.toml`
- [ ] CHANGELOG.rst actualizado
- [ ] Build verificado con `twine check`

---

## 📦 TypeScript/JavaScript (npm)

### Pre-requisitos

```bash
# Login a npm
npm login

# Verificar usuario logueado
npm whoami
```

### Obtener token de npm

1. Ve a https://www.npmjs.com/settings/[tu-usuario]/tokens
2. Crea un nuevo token tipo "Automation" o "Publish"
3. O usa `npm login` interactivo

### Proceso de publicación

```bash
cd packages/typescript

# 1. Actualizar versión en package.json
# Puedes hacerlo manualmente o con npm version
npm version patch  # Para X.Y.Z -> X.Y.(Z+1)
npm version minor  # Para X.Y.Z -> X.(Y+1).0
npm version major  # Para X.Y.Z -> (X+1).0.0

# 2. Ejecutar tests (si existen)
npm test

# 3. Lint y format
npm run lint
npm run format:check

# 4. Build del paquete
npm run build

# 5. Verificar contenido del paquete
npm pack --dry-run
# Revisa que solo incluya archivos necesarios

# 6. Publicar a npm (PRODUCCIÓN)
npm publish

# 6-alt. Publicar como beta/alpha
npm publish --tag beta
npm publish --tag next
```

### Configurar .npmignore

Crea `.npmignore` para excluir archivos innecesarios:

```
# .npmignore
*.md
!README.md
tests/
examples/
docs/
.github/
tsconfig.json
.eslintrc.js
.prettierrc
```

### Verificar instalación

```bash
npm install @tuorg/catalogmx-ts
# o
npm install catalogmx-ts

# Verificar versión
npm list catalogmx-ts
```

### Checklist pre-publicación npm

- [ ] Tests pasando (si existen)
- [ ] Lint sin errores
- [ ] Build exitoso
- [ ] Versión actualizada
- [ ] README.md actualizado
- [ ] .npmignore configurado
- [ ] package.json con campos correctos (main, types, exports)

---

## 📦 Dart/Flutter (pub.dev)

### Pre-requisitos

```bash
# Verificar que Dart SDK esté instalado
dart --version

# No necesitas login previo para publicar
# pub.dev usa OAuth con tu cuenta de Google
```

### Proceso de publicación

```bash
cd packages/dart

# 1. Actualizar versión en pubspec.yaml
# Edita la línea: version: X.Y.Z
nano pubspec.yaml

# 2. Ejecutar tests
dart test

# 3. Analizar código (debe pasar sin errores)
dart analyze

# 4. Formatear código
dart format .

# 5. Dry-run de publicación (IMPORTANTE)
dart pub publish --dry-run
# Revisa warnings y errores
# Verifica que puntaje sea >= 130/160

# 6. Publicar a pub.dev (PRODUCCIÓN)
dart pub publish
# Te pedirá autorización via navegador la primera vez
```

### Configurar pubspec.yaml correctamente

```yaml
name: catalogmx
description: Enterprise-grade Mexican data validation and official catalog library
version: 1.0.0+1  # version+build

environment:
  sdk: '>=3.0.0 <4.0.0'

# Campos obligatorios para pub.dev
homepage: https://github.com/tuorg/catalogmx
repository: https://github.com/tuorg/catalogmx
issue_tracker: https://github.com/tuorg/catalogmx/issues
documentation: https://catalogmx.readthedocs.io

# Ejemplo de dependencias
dependencies:
  http: ^1.1.0

dev_dependencies:
  test: ^1.24.0
  lints: ^3.0.0
```

### Mejorar puntaje pub.dev

pub.dev califica paquetes en 4 áreas (máx 160 puntos):

1. **Follow Dart file conventions** (30 pts)
   - Estructura de carpetas correcta
   - Archivos en lugares esperados

2. **Provide documentation** (50 pts)
   - README.md completo
   - CHANGELOG.md actualizado
   - Ejemplos de uso
   - Documentación de API

3. **Support multiple platforms** (30 pts)
   - Especificar plataformas en pubspec.yaml
   - Evitar dependencias específicas de plataforma

4. **Pass static analysis** (50 pts)
   - `dart analyze` sin errores
   - Código formateado
   - No advertencias

### Verificar instalación

```bash
# Agregar a un proyecto
dart pub add catalogmx

# O en pubspec.yaml
dependencies:
  catalogmx: ^1.0.0

# Instalar
dart pub get
```

### Checklist pre-publicación Dart

- [ ] Tests pasando (`dart test`)
- [ ] Análisis sin errores (`dart analyze`)
- [ ] Código formateado (`dart format`)
- [ ] Versión actualizada en `pubspec.yaml`
- [ ] README.md completo
- [ ] CHANGELOG.md actualizado
- [ ] Dry-run exitoso
- [ ] Puntaje >= 130/160

---

## 🔄 Workflow Recomendado (Todas las Plataformas)

### 1. Preparación

```bash
# Crear branch de release
git checkout -b release/vX.Y.Z

# Actualizar versiones en:
# - packages/python/pyproject.toml
# - packages/typescript/package.json
# - packages/dart/pubspec.yaml

# Actualizar CHANGELOG en cada paquete
```

### 2. Testing exhaustivo

```bash
# Python
cd packages/python && pytest tests/ --cov=catalogmx --cov-branch

# TypeScript
cd packages/typescript && npm test

# Dart
cd packages/dart && dart test
```

### 3. Publicación secuencial

```bash
# 1. Python (más rápido)
cd packages/python
python -m build
python -m twine upload dist/*

# 2. TypeScript
cd packages/typescript
npm run build
npm publish

# 3. Dart (tarda más en aprobar)
cd packages/dart
dart pub publish
```

### 4. Post-publicación

```bash
# Merge a main
git checkout main
git merge release/vX.Y.Z

# Tag de versión
git tag vX.Y.Z
git push origin vX.Y.Z

# Crear GitHub Release
gh release create vX.Y.Z --notes "Release vX.Y.Z"
```

---

## ⚠️ Troubleshooting

### Python

**Error: "File already exists"**
```bash
# No puedes re-subir la misma versión
# Incrementa la versión en pyproject.toml
```

**Error: "Invalid credentials"**
```bash
# Verifica ~/.pypirc
# Regenera token en pypi.org
```

### TypeScript

**Error: "You do not have permission to publish"**
```bash
# Verifica que seas owner/maintainer del paquete
npm owner ls catalogmx-ts
```

**Error: "Version X.Y.Z already published"**
```bash
# Incrementa versión
npm version patch
```

### Dart

**Error: "Package validation failed"**
```bash
# Revisa el output de:
dart pub publish --dry-run
# Corrige los errores mencionados
```

**Error: "pubspec.yaml is missing required fields"**
```bash
# Asegúrate de tener:
# - homepage o repository
# - description
```

---

## 📊 Verificación Post-Publicación

### Python (PyPI)

- Página del paquete: https://pypi.org/project/catalogmx/
- Stats de descarga: https://pypistats.org/packages/catalogmx
- Badge: `[![PyPI version](https://badge.fury.io/py/catalogmx.svg)](https://pypi.org/project/catalogmx/)`

### TypeScript (npm)

- Página del paquete: https://www.npmjs.com/package/catalogmx-ts
- Stats: Visible en la página del paquete
- Badge: `[![npm version](https://badge.fury.io/js/catalogmx-ts.svg)](https://www.npmjs.com/package/catalogmx-ts)`

### Dart (pub.dev)

- Página del paquete: https://pub.dev/packages/catalogmx
- Puntaje: Visible en la página (debe ser >= 130/160)
- Badge: `[![pub package](https://img.shields.io/pub/v/catalogmx.svg)](https://pub.dev/packages/catalogmx)`

---

## 📝 Notas Importantes

1. **Nunca publiques secretos**: Revisa que no haya API keys, tokens, o credenciales en el código
2. **Versioning semántico**: Usa [SemVer](https://semver.org/)
   - MAJOR: Cambios incompatibles
   - MINOR: Nueva funcionalidad compatible
   - PATCH: Bugfixes compatibles
3. **Testing es crítico**: Especialmente para Python (90% coverage requerido)
4. **Documentación**: README.md claro con ejemplos es fundamental
5. **Changelog**: Mantén un registro de cambios detallado

---

## 🎯 Contacto y Soporte

- **Issues**: GitHub Issues
- **Documentación**: README.md de cada paquete
- **Email**: [tu-email]

---

**Última actualización**: Enero 2026
