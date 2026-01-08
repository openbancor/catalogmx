"""
Tax Calculators: IVA, IEPS, Retenciones, and Impuestos Locales
Provides methods for calculating taxes according to Mexican tax laws

Official sources:
- Ley del IVA (Value Added Tax Law)
- Ley del IEPS (Special Production and Services Tax Law)
- Ley del ISR (Income Tax Law - for withholdings)
- State and Municipal Tax Laws
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal, TypedDict

# Type aliases
IVATipoTasa = Literal["general", "frontera", "tasa_cero"]


class IVATasa(TypedDict):
    """IVA tax rate structure"""

    tipo: str
    tasa: float
    vigencia_inicio: str
    vigencia_fin: str | None
    descripcion: str
    aplica_en: str


class IVACalculationResult(TypedDict):
    """IVA calculation result"""

    base: float
    tasa: float
    iva: float
    total_con_iva: float
    tipo_tasa: str


class IEPSTasa(TypedDict):
    """IEPS tax rate structure"""

    subcategoria: str
    tasa: float
    tipo: str
    vigencia_inicio: str
    vigencia_fin: str | None
    descripcion: str


class IEPSCategoria(TypedDict):
    """IEPS category structure"""

    categoria: str
    descripcion: str
    tasas: list[IEPSTasa]


class IEPSCalculationResult(TypedDict):
    """IEPS calculation result"""

    base: float
    tasa: float
    ieps: float
    tipo_calculo: str
    unidad: str | None
    cantidad: float | None


class RetencionISR(TypedDict):
    """ISR withholding structure"""

    concepto: str
    tasa: float | str
    descripcion: str
    base: str
    articulo: str


class RetencionIVA(TypedDict):
    """IVA withholding structure"""

    concepto: str
    tasa: float
    descripcion: str
    base: str
    articulo: str


class RetencionCalculationResult(TypedDict):
    """Withholding calculation result"""

    concepto: str
    base: float
    tasa: float
    retencion: float
    impuesto_base: float | None


class ImpuestoEstatal(TypedDict):
    """State tax structure"""

    estado: str
    cve_estado: str
    tasa: float
    base: str


class IVAData(TypedDict):
    """IVA data file structure"""

    metadata: dict
    tasas: list[IVATasa]
    exenciones: list
    tasa_cero_productos: list


class RetencionesData(TypedDict):
    """Retenciones data file structure"""

    metadata: dict
    isr_retenciones: list[RetencionISR]
    iva_retenciones: list[RetencionIVA]
    retenciones_definitivas: list


class ImpuestosLocalesData(TypedDict):
    """Impuestos Locales data file structure"""

    metadata: dict
    impuesto_nomina: list[ImpuestoEstatal]
    impuesto_hospedaje: list[ImpuestoEstatal]
    otros_impuestos_estatales: list
    predial: dict


class IVACalculator:
    """
    IVA (Value Added Tax) Calculator

    Calculates IVA according to Mexican tax law with support for:
    - General rate (16%)
    - Border rate (8%)
    - Zero rate (0%)
    - Historical rates
    """

    _data: IVAData | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Lazy load IVA data from JSON file"""
        if cls._data is not None:
            return

        # Path from catalogmx/calculators/impuestos.py -> shared-data/sat/impuestos/iva_tasas.json
        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "sat"
            / "impuestos"
            / "iva_tasas.json"
        )
        with open(json_path, encoding="utf-8") as f:
            cls._data = json.load(f)

    @classmethod
    def get_tasa_vigente(
        cls,
        fecha: str | datetime | None = None,
        tipo_tasa: IVATipoTasa = "general",
    ) -> IVATasa | None:
        """
        Get the current IVA rate for a specific date and type

        Args:
            fecha: Date in ISO format (YYYY-MM-DD) or datetime object (default: today)
            tipo_tasa: Rate type (general, frontera, tasa_cero)

        Returns:
            IVA rate object or None if not found

        Examples:
            >>> tasa = IVACalculator.get_tasa_vigente()
            >>> print(f"Tasa actual: {tasa['tasa']}%")
            Tasa actual: 16.0%

            >>> tasa = IVACalculator.get_tasa_vigente("2024-01-01", "frontera")
            >>> print(f"Tasa frontera: {tasa['tasa']}%")
            Tasa frontera: 8.0%
        """
        cls._load_data()

        # Convert fecha to datetime
        if fecha is None:
            fecha_date = datetime.now()
        elif isinstance(fecha, str):
            fecha_date = datetime.fromisoformat(fecha)
        else:
            fecha_date = fecha

        # Filter by rate type
        tasas_del_tipo = [t for t in cls._data["tasas"] if t["tipo"] == tipo_tasa]

        # Find applicable rate
        for tasa in tasas_del_tipo:
            inicio_date = datetime.fromisoformat(tasa["vigencia_inicio"])
            fin_date = (
                datetime.fromisoformat(tasa["vigencia_fin"]) if tasa["vigencia_fin"] else None
            )

            despues_inicio = fecha_date >= inicio_date
            antes_fin = not fin_date or fecha_date <= fin_date

            if despues_inicio and antes_fin:
                return tasa

        return None

    @classmethod
    def calcular(
        cls,
        base: float,
        tipo_tasa: IVATipoTasa = "general",
        fecha: str | datetime | None = None,
    ) -> IVACalculationResult:
        """
        Calculate IVA for a base amount

        Args:
            base: Base amount without IVA
            tipo_tasa: Rate type (general, frontera, tasa_cero)
            fecha: Date to determine applicable rate (default: today)

        Returns:
            Complete calculation result with breakdown

        Raises:
            ValueError: If no applicable rate is found

        Examples:
            >>> result = IVACalculator.calcular(1000)
            >>> print(f"IVA: ${result['iva']:.2f}")
            IVA: $160.00

            >>> result = IVACalculator.calcular(1000, "frontera")
            >>> print(f"IVA frontera: ${result['iva']:.2f}")
            IVA frontera: $80.00
        """
        tasa_obj = cls.get_tasa_vigente(fecha, tipo_tasa)

        if not tasa_obj:
            raise ValueError(
                f"No se encontró tasa de IVA vigente para tipo {tipo_tasa} y fecha {fecha}"
            )

        tasa = tasa_obj["tasa"]
        iva = base * (tasa / 100)
        total_con_iva = base + iva

        return IVACalculationResult(
            base=base,
            tasa=tasa,
            iva=iva,
            total_con_iva=total_con_iva,
            tipo_tasa=tipo_tasa,
        )

    @classmethod
    def calcular_incluido(
        cls,
        total_con_iva: float,
        tipo_tasa: IVATipoTasa = "general",
        fecha: str | datetime | None = None,
    ) -> IVACalculationResult:
        """
        Calculate IVA already included in a total amount
        (Break down IVA when price includes IVA)

        Args:
            total_con_iva: Total amount that includes IVA
            tipo_tasa: Rate type (general, frontera, tasa_cero)
            fecha: Date to determine applicable rate (default: today)

        Returns:
            Complete calculation result with breakdown

        Raises:
            ValueError: If no applicable rate is found

        Examples:
            >>> result = IVACalculator.calcular_incluido(1160)
            >>> print(f"Base: ${result['base']:.2f}, IVA: ${result['iva']:.2f}")
            Base: $1000.00, IVA: $160.00
        """
        tasa_obj = cls.get_tasa_vigente(fecha, tipo_tasa)

        if not tasa_obj:
            raise ValueError("No se encontró tasa de IVA vigente")

        tasa = tasa_obj["tasa"]
        base = total_con_iva / (1 + tasa / 100)
        iva = total_con_iva - base

        return IVACalculationResult(
            base=base,
            tasa=tasa,
            iva=iva,
            total_con_iva=total_con_iva,
            tipo_tasa=tipo_tasa,
        )

    @classmethod
    def get_all_tasas(cls) -> list[IVATasa]:
        """
        Get all historical IVA rates

        Returns:
            List of all IVA rates (current and historical)

        Examples:
            >>> tasas = IVACalculator.get_all_tasas()
            >>> print(f"Total tasas: {len(tasas)}")
            Total tasas: 7
        """
        cls._load_data()
        return cls._data["tasas"].copy()


class IEPSCalculator:
    """
    IEPS (Special Production and Services Tax) Calculator

    Calculates IEPS for:
    - Alcoholic beverages (ad valorem)
    - Tobacco products (ad valorem + fixed quota)
    - Fuels (fixed quota)
    - Sugary drinks (fixed quota)
    - High-calorie foods (ad valorem)
    """

    _data: list[IEPSCategoria] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Lazy load IEPS data from JSON file"""
        if cls._data is not None:
            return

        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "sat"
            / "impuestos"
            / "ieps_tasas.json"
        )
        with open(json_path, encoding="utf-8") as f:
            cls._data = json.load(f)

    @classmethod
    def get_categoria(cls, categoria: str) -> IEPSCategoria | None:
        """
        Get an IEPS category by name

        Args:
            categoria: Category name (e.g., "bebidas_alcoholicas", "tabacos")

        Returns:
            IEPS category or None if not found

        Examples:
            >>> cat = IEPSCalculator.get_categoria("bebidas_alcoholicas")
            >>> print(cat["descripcion"])
            Bebidas con contenido alcohólico
        """
        cls._load_data()
        return next((c for c in cls._data if c["categoria"] == categoria), None)

    @classmethod
    def calcular_ad_valorem(cls, base: float, tasa: float) -> IEPSCalculationResult:
        """
        Calculate IEPS ad-valorem (percentage on value)

        Args:
            base: Base value
            tasa: IEPS rate as percentage

        Returns:
            Calculation result

        Examples:
            >>> result = IEPSCalculator.calcular_ad_valorem(1000, 26.5)
            >>> print(f"IEPS: ${result['ieps']:.2f}")
            IEPS: $265.00
        """
        ieps = base * (tasa / 100)

        return IEPSCalculationResult(
            base=base,
            tasa=tasa,
            ieps=ieps,
            tipo_calculo="ad_valorem",
            unidad=None,
            cantidad=None,
        )

    @classmethod
    def calcular_cuota_fija(
        cls, cantidad: float, cuota_por_unidad: float, unidad: str = "litro"
    ) -> IEPSCalculationResult:
        """
        Calculate IEPS by fixed quota (quantity * rate)

        Args:
            cantidad: Number of units
            cuota_por_unidad: Fixed quota per unit
            unidad: Unit of measure (default: "litro")

        Returns:
            Calculation result

        Examples:
            >>> result = IEPSCalculator.calcular_cuota_fija(100, 1.0, "litro")
            >>> print(f"IEPS: ${result['ieps']:.2f}")
            IEPS: $100.00
        """
        ieps = cantidad * cuota_por_unidad

        return IEPSCalculationResult(
            base=cantidad,
            tasa=cuota_por_unidad,
            ieps=ieps,
            tipo_calculo="cuota_fija",
            unidad=unidad,
            cantidad=cantidad,
        )

    @classmethod
    def calcular_bebidas_alcoholicas(
        cls, valor: float, grados_alcohol: float
    ) -> IEPSCalculationResult:
        """
        Calculate IEPS for alcoholic beverages based on alcohol content

        Args:
            valor: Product value
            grados_alcohol: Alcohol content in degrees (GL)

        Returns:
            Calculation result

        Examples:
            >>> result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 5)
            >>> print(f"IEPS cerveza: ${result['ieps']:.2f}")
            IEPS cerveza: $265.00

            >>> result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 40)
            >>> print(f"IEPS licor: ${result['ieps']:.2f}")
            IEPS licor: $530.00
        """
        if grados_alcohol <= 14:
            tasa = 26.5  # Beer and drinks up to 14°
        elif grados_alcohol <= 20:
            tasa = 30.0  # Drinks from 14° to 20°
        else:
            tasa = 53.0  # Drinks over 20°

        return cls.calcular_ad_valorem(valor, tasa)

    @classmethod
    def calcular_cigarros(cls, valor: float, numero_cigarros: int) -> IEPSCalculationResult:
        """
        Calculate IEPS for cigarettes (ad valorem + fixed quota)

        Args:
            valor: Sale value
            numero_cigarros: Number of cigarettes

        Returns:
            Calculation result

        Examples:
            >>> result = IEPSCalculator.calcular_cigarros(100, 20)
            >>> print(f"IEPS cigarros: ${result['ieps']:.2f}")
            IEPS cigarros: $170.16
        """
        # IEPS = 160% of value + $0.5080 per cigarette
        ieps_ad_valorem = valor * (160 / 100)
        ieps_cuota_fija = numero_cigarros * 0.508
        ieps_total = ieps_ad_valorem + ieps_cuota_fija

        return IEPSCalculationResult(
            base=valor,
            tasa=160,
            ieps=ieps_total,
            tipo_calculo="ad_valorem",
            unidad=None,
            cantidad=float(numero_cigarros),
        )

    @classmethod
    def get_all_categorias(cls) -> list[IEPSCategoria]:
        """
        Get all IEPS categories

        Returns:
            List of all IEPS categories

        Examples:
            >>> categorias = IEPSCalculator.get_all_categorias()
            >>> print(f"Total categorías: {len(categorias)}")
            Total categorías: 7
        """
        cls._load_data()
        return cls._data.copy()


class RetencionCalculator:
    """
    Tax Withholding Calculator (ISR and IVA)

    Calculates withholdings for:
    - Professional fees (10% ISR, 2/3 IVA)
    - Rent (10% ISR, 2/3 IVA)
    - Freight (4% ISR, 100% IVA)
    - Other concepts
    """

    _data: RetencionesData | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Lazy load retenciones data from JSON file"""
        if cls._data is not None:
            return

        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "sat"
            / "impuestos"
            / "retenciones.json"
        )
        with open(json_path, encoding="utf-8") as f:
            cls._data = json.load(f)

    @classmethod
    def get_retencion_isr(cls, concepto: str) -> RetencionISR | None:
        """
        Get ISR withholding information by concept

        Args:
            concepto: Withholding concept (e.g., "honorarios", "arrendamiento")

        Returns:
            ISR withholding info or None if not found

        Examples:
            >>> ret = RetencionCalculator.get_retencion_isr("honorarios")
            >>> print(f"Tasa: {ret['tasa']}%")
            Tasa: 10.0%
        """
        cls._load_data()
        return next(
            (r for r in cls._data["isr_retenciones"] if r["concepto"] == concepto),
            None,
        )

    @classmethod
    def get_retencion_iva(cls, concepto: str) -> RetencionIVA | None:
        """
        Get IVA withholding information by concept

        Args:
            concepto: Withholding concept

        Returns:
            IVA withholding info or None if not found

        Examples:
            >>> ret = RetencionCalculator.get_retencion_iva("servicios_profesionales")
            >>> print(f"Tasa: {ret['tasa']}%")
            Tasa: 66.67%
        """
        cls._load_data()
        return next(
            (r for r in cls._data["iva_retenciones"] if r["concepto"] == concepto),
            None,
        )

    @classmethod
    def calcular_retencion_isr(cls, base: float, concepto: str) -> RetencionCalculationResult:
        """
        Calculate ISR withholding

        Args:
            base: Base amount for withholding
            concepto: Withholding concept

        Returns:
            Calculation result

        Raises:
            ValueError: If concept not found or rate is variable

        Examples:
            >>> result = RetencionCalculator.calcular_retencion_isr(10000, "honorarios")
            >>> print(f"Retención: ${result['retencion']:.2f}")
            Retención: $1000.00
        """
        retencion = cls.get_retencion_isr(concepto)

        if not retencion:
            raise ValueError(f"No se encontró retención ISR para concepto: {concepto}")

        if isinstance(retencion["tasa"], str):
            raise ValueError(f"La tasa de {concepto} es variable. Use método específico.")

        monto_retencion = base * (retencion["tasa"] / 100)

        return RetencionCalculationResult(
            concepto=retencion["concepto"],
            base=base,
            tasa=retencion["tasa"],
            retencion=monto_retencion,
            impuesto_base=None,
        )

    @classmethod
    def calcular_retencion_iva(
        cls, iva_trasladado: float, concepto: str
    ) -> RetencionCalculationResult:
        """
        Calculate IVA withholding (typically 2/3 parts)

        Args:
            iva_trasladado: IVA amount transferred
            concepto: Withholding concept

        Returns:
            Calculation result

        Raises:
            ValueError: If concept not found

        Examples:
            >>> result = RetencionCalculator.calcular_retencion_iva(160, "servicios_profesionales")
            >>> print(f"Retención IVA: ${result['retencion']:.2f}")
            Retención IVA: $106.67
        """
        retencion = cls.get_retencion_iva(concepto)

        if not retencion:
            raise ValueError(f"No se encontró retención IVA para concepto: {concepto}")

        monto_retencion = iva_trasladado * (retencion["tasa"] / 100)

        return RetencionCalculationResult(
            concepto=retencion["concepto"],
            base=iva_trasladado,
            tasa=retencion["tasa"],
            retencion=monto_retencion,
            impuesto_base=iva_trasladado,
        )

    @classmethod
    def calcular_honorarios(cls, monto_sin_iva: float) -> RetencionCalculationResult:
        """
        Calculate withholding for professional fees (10% ISR)

        Args:
            monto_sin_iva: Fee amount without IVA

        Returns:
            Calculation result

        Examples:
            >>> result = RetencionCalculator.calcular_honorarios(10000)
            >>> print(f"Retención honorarios: ${result['retencion']:.2f}")
            Retención honorarios: $1000.00
        """
        return cls.calcular_retencion_isr(monto_sin_iva, "honorarios")

    @classmethod
    def calcular_arrendamiento(cls, monto_sin_iva: float) -> RetencionCalculationResult:
        """
        Calculate withholding for rent (10% ISR)

        Args:
            monto_sin_iva: Rent amount without IVA

        Returns:
            Calculation result

        Examples:
            >>> result = RetencionCalculator.calcular_arrendamiento(15000)
            >>> print(f"Retención arrendamiento: ${result['retencion']:.2f}")
            Retención arrendamiento: $1500.00
        """
        return cls.calcular_retencion_isr(monto_sin_iva, "arrendamiento")

    @classmethod
    def calcular_fletes(cls, monto_sin_iva: float) -> RetencionCalculationResult:
        """
        Calculate withholding for freight (4% ISR)

        Args:
            monto_sin_iva: Freight amount without IVA

        Returns:
            Calculation result

        Examples:
            >>> result = RetencionCalculator.calcular_fletes(10000)
            >>> print(f"Retención fletes: ${result['retencion']:.2f}")
            Retención fletes: $400.00
        """
        return cls.calcular_retencion_isr(monto_sin_iva, "fletes")

    @classmethod
    def get_all_retenciones_isr(cls) -> list[RetencionISR]:
        """
        Get all ISR withholding concepts

        Returns:
            List of all ISR withholdings

        Examples:
            >>> retenciones = RetencionCalculator.get_all_retenciones_isr()
            >>> print(f"Total retenciones ISR: {len(retenciones)}")
            Total retenciones ISR: 9
        """
        cls._load_data()
        return cls._data["isr_retenciones"].copy()

    @classmethod
    def get_all_retenciones_iva(cls) -> list[RetencionIVA]:
        """
        Get all IVA withholding concepts

        Returns:
            List of all IVA withholdings

        Examples:
            >>> retenciones = RetencionCalculator.get_all_retenciones_iva()
            >>> print(f"Total retenciones IVA: {len(retenciones)}")
            Total retenciones IVA: 4
        """
        cls._load_data()
        return cls._data["iva_retenciones"].copy()


class ImpuestosLocalesCalculator:
    """
    State and Municipal Tax Calculator

    Calculates local taxes:
    - Payroll tax (varies by state, 2-3%)
    - Lodging tax (varies by state, 2-5%)
    """

    _data: ImpuestosLocalesData | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Lazy load impuestos locales data from JSON file"""
        if cls._data is not None:
            return

        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "sat"
            / "impuestos"
            / "impuestos_locales.json"
        )
        with open(json_path, encoding="utf-8") as f:
            cls._data = json.load(f)

    @classmethod
    def get_impuesto_nomina(cls, cve_estado: str) -> ImpuestoEstatal | None:
        """
        Get payroll tax rate for a state

        Args:
            cve_estado: State code (01-32)

        Returns:
            State tax info or None if not found

        Examples:
            >>> impuesto = ImpuestosLocalesCalculator.get_impuesto_nomina("09")
            >>> print(f"{impuesto['estado']}: {impuesto['tasa']}%")
            Ciudad de México: 3.0%
        """
        cls._load_data()
        cve_padded = cve_estado.zfill(2)
        return next(
            (i for i in cls._data["impuesto_nomina"] if i["cve_estado"] == cve_padded),
            None,
        )

    @classmethod
    def calcular_impuesto_nomina(cls, total_percepciones: float, cve_estado: str) -> float:
        """
        Calculate payroll tax

        Args:
            total_percepciones: Total payroll for the period
            cve_estado: State code

        Returns:
            Tax amount

        Raises:
            ValueError: If state code not found

        Examples:
            >>> impuesto = ImpuestosLocalesCalculator.calcular_impuesto_nomina(100000, "09")
            >>> print(f"Impuesto sobre nómina CDMX: ${impuesto:.2f}")
            Impuesto sobre nómina CDMX: $3000.00
        """
        impuesto = cls.get_impuesto_nomina(cve_estado)

        if not impuesto:
            raise ValueError(
                f"No se encontró tasa de impuesto sobre nómina para estado: {cve_estado}"
            )

        return total_percepciones * (impuesto["tasa"] / 100)

    @classmethod
    def get_impuesto_hospedaje(cls, cve_estado: str) -> ImpuestoEstatal | None:
        """
        Get lodging tax rate for a state

        Args:
            cve_estado: State code (01-32)

        Returns:
            State tax info or None if not found

        Examples:
            >>> impuesto = ImpuestosLocalesCalculator.get_impuesto_hospedaje("23")
            >>> print(f"{impuesto['estado']}: {impuesto['tasa']}%")
            Quintana Roo: 3.0%
        """
        cls._load_data()
        cve_padded = cve_estado.zfill(2)
        return next(
            (i for i in cls._data["impuesto_hospedaje"] if i["cve_estado"] == cve_padded),
            None,
        )

    @classmethod
    def calcular_impuesto_hospedaje(cls, monto_hospedaje: float, cve_estado: str) -> float:
        """
        Calculate lodging tax

        Args:
            monto_hospedaje: Lodging service amount
            cve_estado: State code

        Returns:
            Tax amount

        Raises:
            ValueError: If state code not found

        Examples:
            >>> impuesto = ImpuestosLocalesCalculator.calcular_impuesto_hospedaje(5000, "23")
            >>> print(f"Impuesto sobre hospedaje: ${impuesto:.2f}")
            Impuesto sobre hospedaje: $150.00
        """
        impuesto = cls.get_impuesto_hospedaje(cve_estado)

        if not impuesto:
            raise ValueError(
                f"No se encontró tasa de impuesto sobre hospedaje para estado: {cve_estado}"
            )

        return monto_hospedaje * (impuesto["tasa"] / 100)

    @classmethod
    def get_all_impuestos_nomina(cls) -> list[ImpuestoEstatal]:
        """
        Get all payroll tax rates

        Returns:
            List of all state payroll taxes

        Examples:
            >>> impuestos = ImpuestosLocalesCalculator.get_all_impuestos_nomina()
            >>> print(f"Total estados: {len(impuestos)}")
            Total estados: 32
        """
        cls._load_data()
        return cls._data["impuesto_nomina"].copy()

    @classmethod
    def get_all_impuestos_hospedaje(cls) -> list[ImpuestoEstatal]:
        """
        Get all lodging tax rates

        Returns:
            List of all state lodging taxes

        Examples:
            >>> impuestos = ImpuestosLocalesCalculator.get_all_impuestos_hospedaje()
            >>> print(f"Total estados: {len(impuestos)}")
            Total estados: 32
        """
        cls._load_data()
        return cls._data["impuesto_hospedaje"].copy()
