"""
Validador completo para CFDI con Complemento de Comercio Exterior 2.0

Integra todos los catálogos para validación completa de un CFDI con
el complemento de comercio exterior.
"""

from .claves_pedimento import ClavePedimentoCatalog
from .estados import EstadoCatalog
from .incoterms import IncotermsValidator
from .monedas import MonedaCatalog
from .motivos_traslado import MotivoTrasladoCatalog
from .paises import PaisCatalog
from .registro_ident_trib import RegistroIdentTribCatalog
from .unidades_aduana import UnidadAduanaCatalog


class ComercioExteriorValidator:
    """Validador completo para CFDI con Complemento Comercio Exterior 2.0"""

    @classmethod
    def validate(cls, cfdi_ce: dict) -> dict:
        """
        Valida un CFDI completo con Complemento de Comercio Exterior

        Args:
            cfdi_ce: Dict con todos los campos del CFDI y complemento

        Returns:
            Dict con 'valid' (bool), 'errors' (list), 'warnings' (list)

        Example:
            >>> cfdi_ce = {
            ...     'tipo_comprobante': 'I',
            ...     'incoterm': 'CIF',
            ...     'clave_pedimento': 'A1',
            ...     'moneda': 'USD',
            ...     'tipo_cambio_usd': 1.0,
            ...     'total_usd': 50000.00,
            ...     'mercancias': [...]
            ... }
            >>> result = ComercioExteriorValidator.validate(cfdi_ce)
            >>> if not result['valid']:
            ...     for error in result['errors']:
            ...         print(f"Error: {error}")
        """
        errors = []
        warnings = []

        # 1. Validar INCOTERM
        incoterm = cfdi_ce.get("incoterm")
        if not incoterm:
            errors.append("INCOTERM es obligatorio")
        elif not IncotermsValidator.is_valid(incoterm):
            errors.append(f"INCOTERM {incoterm} no válido")

        # 2. Validar Clave de Pedimento
        clave_pedimento = cfdi_ce.get("clave_pedimento")
        if not clave_pedimento:
            errors.append("ClavePedimento es obligatoria")
        elif not ClavePedimentoCatalog.is_valid(clave_pedimento):
            errors.append(f"ClavePedimento {clave_pedimento} no válida")

        # 3. Validar Moneda y conversión USD
        moneda_result = MonedaCatalog.validate_conversion_usd(
            {
                "moneda": cfdi_ce.get("moneda"),
                "total": cfdi_ce.get("total"),
                "tipo_cambio_usd": cfdi_ce.get("tipo_cambio_usd"),
                "total_usd": cfdi_ce.get("total_usd"),
            }
        )
        errors.extend(moneda_result["errors"])

        # 4. Validar Mercancías
        mercancias = cfdi_ce.get("mercancias", [])
        if not mercancias:
            errors.append("Debe incluir al menos una mercancía")
        else:
            for i, merc in enumerate(mercancias):
                merc_errors = cls._validate_mercancia(merc, i)
                errors.extend(merc_errors)

        # 5. Validar Receptor (dirección extranjera)
        receptor = cfdi_ce.get("receptor", {})
        if receptor:
            receptor_result = cls._validate_receptor(receptor)
            errors.extend(receptor_result["errors"])

        # 6. Validar Motivo Traslado (solo si tipo comprobante = T)
        tipo_comprobante = cfdi_ce.get("tipo_comprobante")
        if tipo_comprobante == "T":
            motivo_traslado = cfdi_ce.get("motivo_traslado")
            if not motivo_traslado:
                errors.append("MotivoTraslado es obligatorio para CFDI tipo T")
            elif not MotivoTrasladoCatalog.is_valid(motivo_traslado):
                errors.append(f"MotivoTraslado {motivo_traslado} no válido")
            elif MotivoTrasladoCatalog.requires_propietario(motivo_traslado):
                propietarios = cfdi_ce.get("propietarios", [])
                if not propietarios:
                    errors.append("MotivoTraslado 05 requiere al menos un Propietario")

        # 7. Certificado de Origen (opcional pero validar si presente)
        certificado_origen = cfdi_ce.get("certificado_origen")
        if certificado_origen and certificado_origen not in ["0", "1"]:
            errors.append("CertificadoOrigen debe ser 0 o 1")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    @classmethod
    def _validate_mercancia(cls, mercancia: dict, index: int) -> list[str]:
        """Valida una mercancía individual"""
        errors = []
        prefix = f"Mercancía[{index}]"

        # Fracción arancelaria (omitida por ahora, requiere TIGIE/SQLite)
        fraccion = mercancia.get("fraccion_arancelaria")
        if not fraccion:
            errors.append(f"{prefix}: FraccionArancelaria es obligatoria")
        elif len(fraccion) not in [8, 10]:
            errors.append(f"{prefix}: FraccionArancelaria debe tener 8 o 10 dígitos")

        # Unidad de medida aduanera
        unidad_aduana = mercancia.get("unidad_aduana")
        if not unidad_aduana:
            errors.append(f"{prefix}: UnidadAduana es obligatoria")
        elif not UnidadAduanaCatalog.is_valid(unidad_aduana):
            errors.append(f"{prefix}: UnidadAduana {unidad_aduana} no válida")

        # Cantidad
        cantidad = mercancia.get("cantidad_aduana")
        if not cantidad or cantidad <= 0:
            errors.append(f"{prefix}: CantidadAduana debe ser mayor a 0")

        # Valor unitario
        valor_unitario = mercancia.get("valor_unitario_aduana")
        if not valor_unitario or valor_unitario <= 0:
            errors.append(f"{prefix}: ValorUnitarioAduana debe ser mayor a 0")

        # País de origen
        pais_origen = mercancia.get("pais_origen")
        if not pais_origen:
            errors.append(f"{prefix}: PaisOrigen es obligatorio")
        elif not PaisCatalog.is_valid(pais_origen):
            errors.append(f"{prefix}: PaisOrigen {pais_origen} no válido")

        return errors

    @classmethod
    def _validate_receptor(cls, receptor: dict) -> dict:
        """Valida los datos del receptor extranjero"""
        errors = []

        # Validar país
        pais = receptor.get("pais")
        if not pais:
            errors.append("Receptor.Pais es obligatorio")
        elif not PaisCatalog.is_valid(pais):
            errors.append(f"Receptor.Pais {pais} no válido")

        # Validar estado (obligatorio para USA/CAN)
        if pais:
            address_result = EstadoCatalog.validate_foreign_address(
                {"pais": pais, "estado": receptor.get("estado", "")}
            )
            errors.extend(address_result["errors"])

        # Validar tipo y número de identificación tributaria
        tipo_reg = receptor.get("tipo_registro_trib")
        num_reg = receptor.get("num_reg_id_trib")

        if tipo_reg and num_reg:
            tax_id_result = RegistroIdentTribCatalog.validate_tax_id(tipo_reg, num_reg)
            errors.extend(tax_id_result["errors"])

        return {"errors": errors}

    @classmethod
    def validate_quick(cls, field: str, value: str) -> bool:
        """
        Validación rápida de un campo individual

        Args:
            field: Nombre del campo (incoterm, clave_pedimento, etc.)
            value: Valor a validar

        Returns:
            True si el valor es válido

        Example:
            >>> ComercioExteriorValidator.validate_quick('incoterm', 'FOB')
            True
            >>> ComercioExteriorValidator.validate_quick('clave_pedimento', 'A1')
            True
        """
        validators = {
            "incoterm": IncotermsValidator.is_valid,
            "clave_pedimento": ClavePedimentoCatalog.is_valid,
            "unidad_aduana": UnidadAduanaCatalog.is_valid,
            "motivo_traslado": MotivoTrasladoCatalog.is_valid,
            "tipo_registro_trib": RegistroIdentTribCatalog.is_valid,
            "moneda": MonedaCatalog.is_valid,
            "pais": PaisCatalog.is_valid,
            "estado_usa": lambda v: EstadoCatalog.is_valid(v, "USA"),
            "provincia_canada": lambda v: EstadoCatalog.is_valid(v, "CAN"),
        }

        validator = validators.get(field)
        if not validator:
            raise ValueError(f"Campo {field} no soportado para validación")

        return validator(value)
