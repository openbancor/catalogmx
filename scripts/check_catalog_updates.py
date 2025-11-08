#!/usr/bin/env python3
"""
Script de verificación de actualizaciones de catálogos oficiales

Monitorea catálogos de SAT, Banxico, INEGI, SEPOMEX, IFT y otros para
detectar actualizaciones disponibles.

Uso:
    python scripts/check_catalog_updates.py --check-all
    python scripts/check_catalog_updates.py --source sat
    python scripts/check_catalog_updates.py --auto-update
    python scripts/check_catalog_updates.py --report
"""

import argparse
import hashlib
import json
import requests
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse


# Colores para terminal
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text: str, color: str = Colors.RESET):
    """Imprime texto con color"""
    print(f"{color}{text}{Colors.RESET}")


def load_catalog_versions() -> Dict:
    """Carga el archivo .catalog-versions.json"""
    versions_file = Path(__file__).parent.parent / '.catalog-versions.json'

    if not versions_file.exists():
        print_colored("❌ Error: .catalog-versions.json no encontrado", Colors.RED)
        return {}

    with open(versions_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_catalog_versions(data: Dict):
    """Guarda actualizaciones a .catalog-versions.json"""
    versions_file = Path(__file__).parent.parent / '.catalog-versions.json'

    # Actualizar timestamp
    data['last_check'] = datetime.utcnow().isoformat() + 'Z'

    with open(versions_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print_colored(f"✅ Actualizado .catalog-versions.json", Colors.GREEN)


def check_url_exists(url: str, timeout: int = 10) -> tuple[bool, Optional[str]]:
    """
    Verifica si una URL existe y retorna su hash

    Returns:
        (exists, checksum) tuple
    """
    try:
        headers = {
            'User-Agent': 'CatalogMX/0.1 (Catalog Update Checker)'
        }
        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)

        if response.status_code == 200:
            # Intentar obtener ETag o Last-Modified
            etag = response.headers.get('ETag')
            last_modified = response.headers.get('Last-Modified')

            checksum = etag or last_modified or None
            return True, checksum

        return False, None

    except requests.exceptions.RequestException as e:
        print_colored(f"⚠️  Error verificando URL {url}: {e}", Colors.YELLOW)
        return False, None


def download_file(url: str, destination: Path, timeout: int = 60) -> bool:
    """Descarga un archivo desde URL"""
    try:
        headers = {
            'User-Agent': 'CatalogMX/0.1 (Catalog Update Checker)'
        }
        response = requests.get(url, timeout=timeout, headers=headers, stream=True)
        response.raise_for_status()

        destination.parent.mkdir(parents=True, exist_ok=True)

        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return True

    except requests.exceptions.RequestException as e:
        print_colored(f"❌ Error descargando {url}: {e}", Colors.RED)
        return False


def calculate_file_checksum(file_path: Path) -> str:
    """Calcula SHA256 de un archivo"""
    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)

    return sha256.hexdigest()


def check_sat_cfdi_updates(versions: Dict, auto_update: bool = False) -> Dict:
    """Verifica actualizaciones de catálogos SAT CFDI 4.0"""
    print_colored("\n📋 Verificando SAT CFDI 4.0...", Colors.BOLD)

    cfdi_data = versions['catalogs']['sat']['cfdi_4.0']
    url = cfdi_data['url']

    exists, checksum = check_url_exists(url)

    if not exists:
        print_colored(f"  ❌ No se puede acceder a {url}", Colors.RED)
        return {'status': 'error', 'message': 'URL no accesible'}

    # Comparar checksum
    current_checksum = cfdi_data.get('checksum')

    if current_checksum is None:
        print_colored(f"  🆕 Primera verificación - sin checksum previo", Colors.YELLOW)
        has_updates = True
    elif checksum != current_checksum:
        print_colored(f"  🔄 ACTUALIZACIÓN DISPONIBLE", Colors.YELLOW)
        print_colored(f"     Anterior: {current_checksum}", Colors.RESET)
        print_colored(f"     Nueva:    {checksum}", Colors.RESET)
        has_updates = True
    else:
        print_colored(f"  ✅ Sin cambios detectados", Colors.GREEN)
        has_updates = False

    if has_updates and auto_update:
        print_colored(f"  📥 Descargando actualización...", Colors.BLUE)

        downloads_dir = Path(__file__).parent.parent / 'downloads' / 'sat'
        downloads_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination = downloads_dir / f'catCFDI_{timestamp}.xls'

        if download_file(url, destination):
            print_colored(f"  ✅ Descargado: {destination}", Colors.GREEN)

            # Actualizar checksum en versions
            cfdi_data['checksum'] = checksum
            cfdi_data['last_updated'] = datetime.utcnow().isoformat() + 'Z'

            return {
                'status': 'downloaded',
                'file': str(destination),
                'checksum': checksum
            }
        else:
            return {'status': 'download_failed'}

    return {
        'status': 'checked',
        'has_updates': has_updates,
        'checksum': checksum
    }


def check_tigie_updates(versions: Dict, auto_update: bool = False) -> Dict:
    """Verifica actualizaciones de TIGIE (Fracciones Arancelarias)"""
    print_colored("\n📦 Verificando TIGIE/NICO (Fracciones Arancelarias)...", Colors.BOLD)

    tigie_data = versions['catalogs']['sat']['comercio_exterior']['subcatalogs']['c_FraccionArancelaria']

    # SNICE requiere autenticación - por ahora solo verificamos si está pendiente
    if not tigie_data['implemented']:
        print_colored(f"  ⏳ Implementación pendiente", Colors.YELLOW)
        print_colored(f"     URL: {tigie_data['url']}", Colors.RESET)
        print_colored(f"     Próxima verificación: {tigie_data['next_check']}", Colors.RESET)
        print_colored(f"     Frecuencia: {tigie_data['frequency']}", Colors.RESET)
        print_colored(f"     ⚠️  Requiere autenticación en SNICE", Colors.YELLOW)

        return {
            'status': 'pending_implementation',
            'message': 'TIGIE requiere implementación manual con credenciales SNICE'
        }

    return {'status': 'checked', 'has_updates': False}


def check_banxico_updates(versions: Dict, auto_update: bool = False) -> Dict:
    """Verifica actualizaciones de catálogo Banxico"""
    print_colored("\n🏦 Verificando Banxico (Instituciones Financieras)...", Colors.BOLD)

    banks_data = versions['catalogs']['banxico']['banks']
    url = banks_data['url']

    print_colored(f"  ℹ️  URL: {url}", Colors.BLUE)
    print_colored(f"  ℹ️  Versión actual: {banks_data['version']}", Colors.RESET)
    print_colored(f"  ℹ️  Registros: {banks_data['records']}", Colors.RESET)
    print_colored(f"  ℹ️  Última actualización: {banks_data['last_updated']}", Colors.RESET)

    # Banxico publica en PDF - requiere procesamiento manual
    print_colored(f"  ⚠️  Verificación manual requerida (PDF)", Colors.YELLOW)
    print_colored(f"     Descargar PDF mensual y comparar con catálogo actual", Colors.RESET)

    return {
        'status': 'manual_check_required',
        'message': 'Banxico publica en PDF - requiere verificación manual'
    }


def check_iso_standards(versions: Dict) -> Dict:
    """Verifica estándares ISO (4217, 3166)"""
    print_colored("\n🌍 Verificando estándares ISO...", Colors.BOLD)

    iso_catalogs = versions['catalogs']['iso']
    results = []

    for catalog_name, catalog_data in iso_catalogs.items():
        next_check = datetime.fromisoformat(catalog_data['next_check'].replace('Z', '+00:00'))
        today = datetime.now(next_check.tzinfo)

        if today < next_check:
            days_until = (next_check - today).days
            print_colored(f"  ✅ {catalog_name}: Próxima verificación en {days_until} días", Colors.GREEN)
        else:
            print_colored(f"  ⚠️  {catalog_name}: Verificación vencida", Colors.YELLOW)
            print_colored(f"     URL: {catalog_data['url']}", Colors.RESET)

        results.append({
            'catalog': catalog_name,
            'next_check': catalog_data['next_check'],
            'needs_check': today >= next_check
        })

    return {'status': 'checked', 'results': results}


def generate_report(versions: Dict):
    """Genera reporte de estado de catálogos"""
    print_colored("\n" + "="*80, Colors.BOLD)
    print_colored("📊 REPORTE DE ESTADO DE CATÁLOGOS", Colors.BOLD)
    print_colored("="*80, Colors.BOLD)

    stats = versions['statistics']

    print(f"\n📈 Estadísticas Generales:")
    print(f"   Total de catálogos: {stats['total_catalogs']}")
    print(f"   Implementados:      {stats['implemented']} ({stats['coverage_percentage']}%)")
    print(f"   Pendientes:         {stats['pending']}")
    print(f"   Alta prioridad pendientes: {stats['high_priority_pending']}")

    print_colored(f"\n🔔 Próximas actualizaciones necesarias:", Colors.YELLOW)

    for update in stats['next_updates_due']:
        priority_color = Colors.RED if update['priority'] == 'high' else Colors.YELLOW
        print_colored(f"   • {update['catalog']}", priority_color)
        print(f"     Fecha: {update['date']}")
        print(f"     Prioridad: {update['priority']}")

    # Catálogos por estado
    print(f"\n📋 Catálogos por estado:")

    for source, source_data in versions['catalogs'].items():
        print_colored(f"\n   {source.upper()}:", Colors.BOLD)

        for catalog_name, catalog_data in source_data.items():
            if isinstance(catalog_data, dict) and 'status' in catalog_data:
                status = catalog_data['status']

                if status == 'implemented':
                    icon = "✅"
                    color = Colors.GREEN
                elif status == 'partially_implemented':
                    icon = "🔸"
                    color = Colors.YELLOW
                else:
                    icon = "⏳"
                    color = Colors.RESET

                records = catalog_data.get('records', catalog_data.get('records_expected', 'N/A'))
                print_colored(f"      {icon} {catalog_name}: {status} ({records} registros)", color)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Verifica actualizaciones de catálogos oficiales'
    )
    parser.add_argument(
        '--check-all',
        action='store_true',
        help='Verifica todos los catálogos'
    )
    parser.add_argument(
        '--source',
        choices=['sat', 'banxico', 'inegi', 'sepomex', 'ift', 'iso'],
        help='Verifica solo catálogos de una fuente específica'
    )
    parser.add_argument(
        '--auto-update',
        action='store_true',
        help='Descarga automáticamente si hay actualizaciones'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Genera reporte de estado'
    )

    args = parser.parse_args()

    # Cargar versiones actuales
    versions = load_catalog_versions()

    if not versions:
        print_colored("❌ No se pudo cargar .catalog-versions.json", Colors.RED)
        return 1

    print_colored(f"\n{'='*80}", Colors.BOLD)
    print_colored(f"🔍 VERIFICADOR DE ACTUALIZACIONES DE CATÁLOGOS", Colors.BOLD)
    print_colored(f"{'='*80}\n", Colors.BOLD)

    if args.report:
        generate_report(versions)
        return 0

    # Verificar catálogos según argumentos
    results = {}

    if args.check_all or args.source == 'sat':
        results['sat_cfdi'] = check_sat_cfdi_updates(versions, args.auto_update)
        results['tigie'] = check_tigie_updates(versions, args.auto_update)

    if args.check_all or args.source == 'banxico':
        results['banxico'] = check_banxico_updates(versions, args.auto_update)

    if args.check_all or args.source == 'iso':
        results['iso'] = check_iso_standards(versions)

    # Guardar actualizaciones si hubo cambios
    if args.auto_update:
        save_catalog_versions(versions)

    # Resumen
    print_colored(f"\n{'='*80}", Colors.BOLD)
    print_colored(f"✅ Verificación completada", Colors.GREEN)
    print_colored(f"{'='*80}\n", Colors.BOLD)

    # Mostrar resumen de resultados
    updates_found = any(
        r.get('has_updates', False) for r in results.values() if isinstance(r, dict)
    )

    if updates_found:
        print_colored(f"🔔 Se encontraron actualizaciones disponibles", Colors.YELLOW)
    else:
        print_colored(f"✅ Todos los catálogos están actualizados", Colors.GREEN)

    return 0


if __name__ == '__main__':
    sys.exit(main())
