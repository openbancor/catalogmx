/// The default data mode is offline: the updater never downloads unless asked.
library;

import 'package:catalogmx/src/data/updater.dart';
import 'package:test/test.dart';

void main() {
  test('DataUpdaterConfig does not auto-update by default', () {
    expect(const DataUpdaterConfig().autoUpdate, isFalse);
  });

  test('DataUpdaterConfig still allows opting in to downloads', () {
    expect(const DataUpdaterConfig(autoUpdate: true).autoUpdate, isTrue);
  });
}
