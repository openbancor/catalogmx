package com.openbancor.catalogmx.cfdi

import com.openbancor.catalogmx.utils.SharedData

object CfdiResources {
    fun satUrlToLocalPath(url: String): String {
        val uri = java.net.URI(url)
        return SharedData.resolvePath("sat/xsd/resources/${uri.host}${uri.path}").absolutePath
    }

    fun cfdi40Xsd(): String = satUrlToLocalPath(
        "http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"
    )

    fun cadenaOriginal40Xslt(): String = satUrlToLocalPath(
        "http://www.sat.gob.mx/sitio_internet/cfd/4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt"
    )
}
