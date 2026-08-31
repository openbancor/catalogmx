Pod::Spec.new do |s|
  s.name             = 'catalogmx'
  s.version          = '0.7.0'
  s.summary          = 'CatalogMX Flutter plugin for CFDI validation/signing.'
  s.description      = <<-DESC
CatalogMX provides CFDI validation and signing helpers with native implementations.
DESC
  s.homepage         = 'https://github.com/openbancor/catalogmx'
  s.license          = { :file => '../LICENSE' }
  s.author           = { 'OpenBancor' => 'dev@openbancor.com' }
  s.source           = { :path => '.' }
  s.source_files     = 'Classes/**/*'
  s.requires_arc     = true
  s.dependency 'Flutter'
  s.frameworks = 'Security'
  s.libraries = 'xml2', 'xslt'
  s.pod_target_xcconfig = {
    'DEFINES_MODULE' => 'YES',
    'HEADER_SEARCH_PATHS' => '$(SDKROOT)/usr/include/libxml2'
  }
end
