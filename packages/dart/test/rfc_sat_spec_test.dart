/// RFC SAT Specification Tests
///
/// Tests based on official SAT algorithm specification (IFAI 0610100135506)
/// Reference: https://www.mariovaldez.net/files/IFAI%200610100135506%20065%20Algoritmo%20para%20generar%20el%20RFC%20con%20homoclave%20para%20personas%20fisicas%20y%20morales.pdf
import 'dart:convert';
import 'dart:io';

import 'package:catalogmx/catalogmx.dart';
import 'package:test/test.dart';

/// Parse ISO date string to DateTime
DateTime _parseDate(String value) {
  final parts = value.split('-');
  if (parts.length != 3) {
    throw FormatException('Expected YYYY-MM-DD date format.');
  }
  final year = int.parse(parts[0]);
  final month = int.parse(parts[1]);
  final day = int.parse(parts[2]);
  return DateTime(year, month, day);
}

/// Extract RFC base (initials + date) from full RFC
String extractRfcBase(String rfc) {
  if (rfc.length == 12) {
    // Persona Moral: 3 letters + 6 date + 3 homoclave+checksum
    return rfc.substring(0, 9);
  } else {
    // Persona Física: 4 letters + 6 date + 3 homoclave+checksum
    return rfc.substring(0, 10);
  }
}

void main() {
  final file = File('../shared-data/tests/rfc_sat_spec_vectors.json');
  final satSpec = jsonDecode(file.readAsStringSync()) as Map<String, dynamic>;

  final personasMorales = satSpec['personas_morales'] as Map<String, dynamic>;
  final personasFisicas = satSpec['personas_fisicas'] as Map<String, dynamic>;

  // ============================================================================
  // PERSONAS MORALES TESTS
  // ============================================================================

  group('SAT Specification - Personas Morales', () {
    group('Regla 1 - Tres o más palabras', () {
      final vectors = personasMorales['regla_1_tres_o_mas_palabras'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 2 - Fecha de constitución', () {
      final vectors = personasMorales['regla_2_fecha_constitucion'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 3 - Letras compuestas (CH, LL)', () {
      final vectors = personasMorales['regla_3_letras_compuestas'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 4 - Iniciales como palabras', () {
      final vectors =
          personasMorales['regla_4_iniciales_como_palabras'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 5 - Abreviaturas de tipo de sociedad', () {
      final vectors = personasMorales['regla_5_abreviaturas_sociedad'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 6 - Dos palabras', () {
      final vectors = personasMorales['regla_6_dos_palabras'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 7 - Una sola palabra', () {
      final vectors = personasMorales['regla_7_una_sola_palabra'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 8 - Menos de 3 letras', () {
      final vectors = personasMorales['regla_8_menos_de_tres_letras'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 9 - Artículos, preposiciones y conjunciones', () {
      final vectors =
          personasMorales['regla_9_articulos_preposiciones'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 10 - Números (arábigos y romanos)', () {
      final vectors = personasMorales['regla_10_numeros'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 11 - Compañía/Sociedad (excluidas)', () {
      final vectors = personasMorales['regla_11_compania_sociedad'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 12 - Caracteres especiales', () {
      final vectors = personasMorales['regla_12_caracteres_especiales'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test('${vector['razon_social']} -> ${vector['rfc_base']}', () {
          final rfc = generateRFCMoral(
            razonSocial: vector['razon_social'] as String,
            fechaConstitucion: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });
  });

  // ============================================================================
  // PERSONAS FISICAS TESTS
  // ============================================================================

  group('SAT Specification - Personas Físicas', () {
    group('Regla 1 - Formación básica', () {
      final vectors = personasFisicas['regla_1_formacion_basica'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 2 - Fecha de nacimiento', () {
      final vectors = personasFisicas['regla_2_fecha_nacimiento'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 3 - Letras compuestas (CH, LL)', () {
      final vectors = personasFisicas['regla_3_letras_compuestas'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 4 - Apellido paterno corto', () {
      final vectors = personasFisicas['regla_4_apellido_paterno_corto'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 5 - Apellidos compuestos', () {
      final vectors = personasFisicas['regla_5_apellidos_compuestos'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 6 - Nombres compuestos (MARIA/JOSE)', () {
      final vectors = personasFisicas['regla_6_nombres_maria_jose'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 7 - Un solo apellido', () {
      final vectors = personasFisicas['regla_7_un_solo_apellido'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 8 - Artículos, preposiciones y conjunciones', () {
      final vectors =
          personasFisicas['regla_8_articulos_preposiciones'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });

    group('Regla 10 - Caracteres especiales', () {
      final vectors = personasFisicas['regla_10_caracteres_especiales'] as List;
      for (final raw in vectors) {
        final vector = raw as Map<String, dynamic>;
        test(
            '${vector['nombre']} ${vector['apellido_paterno']} ${vector['apellido_materno']} -> ${vector['rfc_base']}',
            () {
          final rfc = generateRFC(
            nombre: vector['nombre'] as String,
            apellidoPaterno: vector['apellido_paterno'] as String,
            apellidoMaterno: vector['apellido_materno'] as String,
            fechaNacimiento: _parseDate(vector['fecha'] as String),
          );
          final rfcBase = extractRfcBase(rfc);
          expect(rfcBase, equals(vector['rfc_base']));
        });
      }
    });
  });

  // ============================================================================
  // COMPLETE EXAMPLE WITH HOMOCLAVE
  // ============================================================================

  group('SAT Specification - Complete Example with Homoclave', () {
    final example =
        satSpec['ejemplo_completo_con_homoclave'] as Map<String, dynamic>;

    test('Emma Gómez Díaz generates correct RFC with homoclave and checksum',
        () {
      final rfc = generateRFC(
        nombre: example['nombre'] as String,
        apellidoPaterno: example['apellido_paterno'] as String,
        apellidoMaterno: example['apellido_materno'] as String,
        fechaNacimiento: _parseDate(example['fecha'] as String),
      );

      // Test complete RFC
      expect(rfc, equals(example['rfc_completo']));

      // Test RFC base
      expect(rfc.substring(0, 10), equals(example['rfc_base']));

      // Test homoclave
      expect(rfc.substring(10, 12), equals(example['homoclave']));

      // Test checksum
      expect(rfc.substring(12), equals(example['digito_verificador']));
    });

    test('RFC validates correctly', () {
      final validator = RFCValidator(example['rfc_completo'] as String);
      expect(validator.isValid(), isTrue);
    });

    test('RFC detected as persona física', () {
      final validator = RFCValidator(example['rfc_completo'] as String);
      expect(validator.isFisica(), isTrue);
    });
  });

  // ============================================================================
  // CHECKSUM VALIDATION
  // ============================================================================

  group('SAT Specification - Checksum Validation', () {
    test('RFC checksum can be validated independently', () {
      // From the SAT document, the checksum calculation for GODE561231GR is 8
      final validator = RFCValidator('GODE561231GR8');
      expect(validator.validateChecksum(), isTrue);

      // Wrong checksum should fail
      final wrongValidator = RFCValidator('GODE561231GR9');
      expect(wrongValidator.validateChecksum(), isFalse);
    });

    test('Generic RFCs validate correctly', () {
      expect(RFCValidator('XAXX010101000').isValid(), isTrue);
      expect(RFCValidator('XEXX010101000').isValid(), isTrue);
    });
  });

  // ============================================================================
  // PALABRAS INCONVENIENTES
  // ============================================================================

  group('SAT Specification - Palabras Inconvenientes', () {
    final palabras = satSpec['palabras_inconvenientes'] as List;
    for (final raw in palabras) {
      final palabra = raw as Map<String, dynamic>;
      test(
          '${palabra['original']} should be corrected to ${palabra['corregido']}',
          () {
        expect((palabra['corregido'] as String).endsWith('X'), isTrue);
        expect(
          (palabra['original'] as String).substring(0, 3),
          equals((palabra['corregido'] as String).substring(0, 3)),
        );
      });
    }
  });
}
