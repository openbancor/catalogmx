package com.openbancor.catalogmx.utils

import java.io.File

object SharedData {
    private const val ENV_NAME = "CATALOGMX_SHARED_DATA"

    fun resolveRoot(): File {
        val env = System.getenv(ENV_NAME)
        if (!env.isNullOrBlank()) {
            val candidate = File(env)
            if (candidate.exists()) return candidate
        }

        val candidates = listOf(
            File("./shared-data"),
            File("../shared-data"),
            File("../../shared-data"),
            File("./packages/shared-data"),
        )

        for (candidate in candidates) {
            if (candidate.exists()) return candidate
        }

        throw IllegalStateException("shared-data not found. Set $ENV_NAME to a valid path.")
    }

    fun resolvePath(relative: String): File = File(resolveRoot(), relative)
}
