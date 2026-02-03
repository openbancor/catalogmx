package com.openbancor.catalogmx.cfdi

data class TimbradoResult(
    val xmlTimbrado: String,
    val uuid: String? = null,
    val fechaTimbrado: String? = null,
)

interface PacTimbrador {
    fun timbrar(xml: String): TimbradoResult
}

class PacTimbradorMock : PacTimbrador {
    override fun timbrar(xml: String): TimbradoResult = TimbradoResult(xml)
}
