import Flutter
import Foundation

final class CfdiChannel: NSObject, FlutterPlugin {
  static func register(with registrar: FlutterPluginRegistrar) {
    let channel = FlutterMethodChannel(name: "catalogmx_cfdi", binaryMessenger: registrar.messenger())
    let instance = CfdiChannel()
    registrar.addMethodCallDelegate(instance, channel: channel)
  }

  func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    // iOS: implementar con libxml2 + XSLT si se requiere validación/cadena original.
    // Por ahora, se deja como stub para que la app decida implementación nativa.
    result(FlutterError(code: "UNAVAILABLE", message: "CFDI native handler not implemented on iOS", details: nil))
  }
}
