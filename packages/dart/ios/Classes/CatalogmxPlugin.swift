import Flutter
import Foundation
import Security
import libxml2
#if canImport(libxslt)
import libxslt
#endif

public class CatalogmxPlugin: NSObject, FlutterPlugin {
  public static func register(with registrar: FlutterPluginRegistrar) {
    let channel = FlutterMethodChannel(name: "catalogmx_cfdi", binaryMessenger: registrar.messenger())
    let instance = CatalogmxPlugin()
    registrar.addMethodCallDelegate(instance, channel: channel)
  }

  public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
    switch call.method {
    case "generateCadenaOriginal":
      guard let args = call.arguments as? [String: Any],
            let xml = args["xml"] as? String,
            let xslt = args["xslt"] as? String else {
        result(FlutterError(code: "ARG", message: "xml/xslt requerido", details: nil))
        return
      }
      do {
        let cadena = try generateCadenaOriginal(xml: xml, xslt: xslt)
        result(cadena)
      } catch {
        result(FlutterError(code: "XSLT", message: error.localizedDescription, details: nil))
      }
    case "validateXsd":
      guard let args = call.arguments as? [String: Any],
            let xml = args["xml"] as? String,
            let xsd = args["xsd"] as? String else {
        result(FlutterError(code: "ARG", message: "xml/xsd requerido", details: nil))
        return
      }
      let outcome = validateXsd(xml: xml, xsd: xsd)
      result(["valid": outcome.valid, "errors": outcome.errors])
    case "signCadenaOriginal":
      guard let args = call.arguments as? [String: Any],
            let cadena = args["cadena"] as? String,
            let privateKeyPem = args["privateKeyPem"] as? String else {
        result(FlutterError(code: "ARG", message: "cadena/privateKeyPem requerido", details: nil))
        return
      }
      do {
        let sello = try signCadenaOriginal(cadena: cadena, privateKeyPem: privateKeyPem)
        result(sello)
      } catch {
        result(FlutterError(code: "SIGN", message: error.localizedDescription, details: nil))
      }
    default:
      result(FlutterMethodNotImplemented)
    }
  }

  private func generateCadenaOriginal(xml: String, xslt: String) throws -> String {
#if canImport(libxslt)
    guard let xmlDoc = readXmlDoc(xml),
          let xsltDoc = readXmlDoc(xslt) else {
      throw NSError(domain: "catalogmx", code: 1, userInfo: [NSLocalizedDescriptionKey: "XML/XSLT inválido"])
    }
    defer {
      xmlFreeDoc(xmlDoc)
      xmlFreeDoc(xsltDoc)
    }
    guard let style = xsltParseStylesheetDoc(xsltDoc) else {
      throw NSError(domain: "catalogmx", code: 2, userInfo: [NSLocalizedDescriptionKey: "No se pudo parsear XSLT"])
    }
    defer { xsltFreeStylesheet(style) }
    guard let resultDoc = xsltApplyStylesheet(style, xmlDoc, nil) else {
      throw NSError(domain: "catalogmx", code: 3, userInfo: [NSLocalizedDescriptionKey: "No se pudo aplicar XSLT"])
    }
    defer { xmlFreeDoc(resultDoc) }
    var output: UnsafeMutablePointer<xmlChar>? = nil
    var length: Int32 = 0
    xsltSaveResultToString(&output, &length, resultDoc, style)
    guard let out = output else {
      throw NSError(domain: "catalogmx", code: 4, userInfo: [NSLocalizedDescriptionKey: "Resultado XSLT vacío"])
    }
    defer { xmlFree(out) }
    let data = Data(bytes: out, count: Int(length))
    return String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
#else
    throw NSError(domain: "catalogmx", code: 5, userInfo: [NSLocalizedDescriptionKey: "XSLT no disponible en iOS"])
#endif
  }

  private func validateXsd(xml: String, xsd: String) -> (valid: Bool, errors: [String]) {
    guard let xmlDoc = readXmlDoc(xml),
          let xsdDoc = readXmlDoc(xsd) else {
      return (false, ["XML/XSD inválido"])
    }
    defer {
      xmlFreeDoc(xmlDoc)
      xmlFreeDoc(xsdDoc)
    }

    guard let parserCtxt = xmlSchemaNewDocParserCtxt(xsdDoc) else {
      return (false, ["No se pudo crear parser de XSD"])
    }
    defer { xmlSchemaFreeParserCtxt(parserCtxt) }
    guard let schema = xmlSchemaParse(parserCtxt) else {
      return (false, ["No se pudo parsear XSD"])
    }
    defer { xmlSchemaFree(schema) }
    guard let validCtxt = xmlSchemaNewValidCtxt(schema) else {
      return (false, ["No se pudo crear contexto de validación"])
    }
    defer { xmlSchemaFreeValidCtxt(validCtxt) }

    let result = xmlSchemaValidateDoc(validCtxt, xmlDoc)
    if result == 0 {
      return (true, [])
    }
    let lastError = xmlGetLastError()
    let message = lastError?.pointee.message.map { String(cString: $0) } ?? "XSD validation error"
    return (false, [message.trimmingCharacters(in: .whitespacesAndNewlines)])
  }

  private func signCadenaOriginal(cadena: String, privateKeyPem: String) throws -> String {
    let clean = privateKeyPem
      .replacingOccurrences(of: "-----BEGIN PRIVATE KEY-----", with: "")
      .replacingOccurrences(of: "-----END PRIVATE KEY-----", with: "")
      .replacingOccurrences(of: "-----BEGIN RSA PRIVATE KEY-----", with: "")
      .replacingOccurrences(of: "-----END RSA PRIVATE KEY-----", with: "")
      .replacingOccurrences(of: "\n", with: "")
      .replacingOccurrences(of: "\r", with: "")
      .trimmingCharacters(in: .whitespacesAndNewlines)
    guard let keyData = Data(base64Encoded: clean) else {
      throw NSError(domain: "catalogmx", code: 10, userInfo: [NSLocalizedDescriptionKey: "PEM inválido"])
    }
    guard let privateKey = loadPrivateKey(from: keyData) else {
      throw NSError(domain: "catalogmx", code: 11, userInfo: [NSLocalizedDescriptionKey: "No se pudo cargar la llave privada"])
    }
    let data = Data(cadena.utf8)
    var error: Unmanaged<CFError>?
    guard let signature = SecKeyCreateSignature(privateKey, .rsaSignatureMessagePKCS1v15SHA256, data as CFData, &error) else {
      let message = error?.takeRetainedValue().localizedDescription ?? "Error al firmar"
      throw NSError(domain: "catalogmx", code: 12, userInfo: [NSLocalizedDescriptionKey: message])
    }
    return (signature as Data).base64EncodedString()
  }

  private func loadPrivateKey(from data: Data) -> SecKey? {
    let attributes: [String: Any] = [
      kSecAttrKeyType as String: kSecAttrKeyTypeRSA,
      kSecAttrKeyClass as String: kSecAttrKeyClassPrivate,
      kSecReturnPersistentRef as String: false
    ]
    return SecKeyCreateWithData(data as CFData, attributes as CFDictionary, nil)
  }

  private func readXmlDoc(_ xml: String) -> xmlDocPtr? {
    let bytes = Array(xml.utf8)
    return bytes.withUnsafeBufferPointer { buffer in
      xmlReadMemory(buffer.baseAddress, Int32(buffer.count), nil, nil, Int32(XML_PARSE_NONET))
    }
  }
}
