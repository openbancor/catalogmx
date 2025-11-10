"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mrfcmx` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``rfcmx.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``rfcmx.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import datetime

import click

from catalogmx.validators.curp import CURPGenerator, CURPValidator
from catalogmx.validators.rfc import RFCGenerator, RFCValidator


@click.group()
@click.version_option(version="0.2.0")
def main():
    """
    Mexican RFC and CURP calculator and validator.

    This tool helps you generate and validate:
    - RFC (Registro Federal de Contribuyentes) for individuals and companies
    - CURP (Clave Única de Registro de Población) for individuals
    """
    pass


@main.group()
def rfc():
    """RFC (Registro Federal de Contribuyentes) commands"""
    pass


@main.group()
def curp():
    """CURP (Clave Única de Registro de Población) commands"""
    pass


@rfc.command("validate")
@click.argument("rfc_code")
def rfc_validate(rfc_code):
    """Validate an RFC code"""
    validator = RFCValidator(rfc_code)

    if validator.validate():
        click.echo(click.style(f"✓ RFC {rfc_code} is valid", fg="green"))
        tipo = validator.detect_fisica_moral()
        click.echo(f"  Type: {tipo}")

        # Show validation details
        validations = validator.validators()
        click.echo("\n  Validation details:")
        for name, result in validations.items():
            status = "✓" if result else "✗"
            color = "green" if result else "red"
            click.echo(f"    {click.style(status, fg=color)} {name}")
    else:
        click.echo(click.style(f"✗ RFC {rfc_code} is invalid", fg="red"))


@rfc.command("generate-fisica")
@click.option("--nombre", "-n", required=True, help="First name(s)")
@click.option("--paterno", "-p", required=True, help="First surname (apellido paterno)")
@click.option("--materno", "-m", default="", help="Second surname (apellido materno)")
@click.option("--fecha", "-f", required=True, help="Birth date (YYYY-MM-DD)")
def rfc_generate_fisica(nombre, paterno, materno, fecha):
    """Generate RFC for Persona Física (individual)"""
    try:
        # Parse date
        fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()

        # Generate RFC
        rfc_code = RFCGenerator.generate_fisica(
            nombre=nombre, paterno=paterno, materno=materno, fecha=fecha_obj
        )

        click.echo(click.style(f"\nGenerated RFC: {rfc_code}", fg="green", bold=True))
        click.echo(f"\nName: {nombre} {paterno} {materno}")
        click.echo(f"Birth date: {fecha}")

    except ValueError as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {str(e)}", fg="red"))


@rfc.command("generate-moral")
@click.option("--razon-social", "-r", required=True, help="Company name (razón social)")
@click.option("--fecha", "-f", required=True, help="Incorporation date (YYYY-MM-DD)")
def rfc_generate_moral(razon_social, fecha):
    """Generate RFC for Persona Moral (company/legal entity)"""
    try:
        # Parse date
        fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()

        # Generate RFC
        rfc_code = RFCGenerator.generate_moral(razon_social=razon_social, fecha=fecha_obj)

        click.echo(click.style(f"\nGenerated RFC: {rfc_code}", fg="green", bold=True))
        click.echo(f"\nCompany: {razon_social}")
        click.echo(f"Incorporation date: {fecha}")

    except ValueError as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {str(e)}", fg="red"))


@curp.command("validate")
@click.argument("curp_code")
def curp_validate(curp_code):
    """Validate a CURP code"""
    validator = CURPValidator(curp_code)

    if validator.is_valid():
        click.echo(click.style(f"✓ CURP {curp_code} is valid", fg="green"))
    else:
        click.echo(click.style(f"✗ CURP {curp_code} is invalid", fg="red"))


@curp.command("generate")
@click.option("--nombre", "-n", required=True, help="First name(s)")
@click.option("--paterno", "-p", required=True, help="First surname (apellido paterno)")
@click.option("--materno", "-m", default="", help="Second surname (apellido materno)")
@click.option("--fecha", "-f", required=True, help="Birth date (YYYY-MM-DD)")
@click.option(
    "--sexo",
    "-s",
    required=True,
    type=click.Choice(["H", "M"], case_sensitive=False),
    help="Gender: H (Hombre/Male) or M (Mujer/Female)",
)
@click.option("--estado", "-e", required=True, help="Birth state (e.g., Jalisco, CDMX, etc.)")
def curp_generate(nombre, paterno, materno, fecha, sexo, estado):
    """Generate CURP for an individual"""
    try:
        # Parse date
        fecha_obj = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()

        # Generate CURP
        generator = CURPGenerator(
            nombre=nombre,
            paterno=paterno,
            materno=materno,
            fecha_nacimiento=fecha_obj,
            sexo=sexo.upper(),
            estado=estado,
        )

        curp_code = generator.curp

        click.echo(click.style(f"\nGenerated CURP: {curp_code}", fg="green", bold=True))
        click.echo(f"\nName: {nombre} {paterno} {materno}")
        click.echo(f"Birth date: {fecha}")
        click.echo(f"Gender: {sexo.upper()}")
        click.echo(f"Birth state: {estado}")

        # Show a note about homoclave
        click.echo(
            click.style(
                '\nNote: The homoclave (last 2 characters) is a placeholder ("00").', fg="yellow"
            )
        )
        click.echo(click.style("The official homoclave is assigned by RENAPO.", fg="yellow"))

    except ValueError as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Unexpected error: {str(e)}", fg="red"))


if __name__ == "__main__":
    main()
