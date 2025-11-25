# NSS validator/generator parity (TS, Python, Dart)

Field order is the same in every implementation:

- `SS` (2) subdelegation (IMSS office)
- `AA` (2) registration year (YY, 19YY/20YY)
- `BB` (2) birth year (YY, 19YY/20YY)
- `NNNN` (4) sequential
- `C` (1) check digit (modified Luhn)

## TypeScript

```ts
import { NSSValidator, generateNss } from 'catalogmx';

const validator = new NSSValidator('12345678903');
validator.isValid(); // true
validator.getComponents();
// {
//   subdelegation: '12',
//   registrationYear: '34',
//   birthYear: '56',
//   sequential: '7890',
//   checkDigit: '3'
// }

const nss = generateNss('12', '34', '56', '7890'); // 12345678903
```

## Python

```python
from catalogmx.validators.nss import NSSValidator, generate_nss, get_nss_info

validator = NSSValidator("12345678903")
validator.is_valid()  # True
validator.get_parts()
# {
#   "subdelegation": "12",
#   "registration_year": "34",
#   "birth_year": "56",
#   "sequential": "7890",
#   "check_digit": "3",
#   "nss": "12345678903",
# }

nss = generate_nss("12", "34", "56", "7890")  # 12345678903
```

## Dart

```dart
import 'package:catalogmx/catalogmx.dart';

final validator = NSSValidator('12345678903');
validator.isValid(); // true
validator.getParts();
// {
//   'subdelegation': '12',
//   'registration_year': '34',
//   'birth_year': '56',
//   'sequential': '7890',
//   'check_digit': '3',
//   'nss': '12345678903',
// }

final nss = generateNSS(
  subdelegation: '12',
  registrationYear: '34',
  birthYear: '56',
  sequential: '7890',
); // 12345678903
```

All generators pad/truncate to the correct widths, and all validators share the same modified Luhn check digit logic. If you change the structure, update all three modules and their tests together.
