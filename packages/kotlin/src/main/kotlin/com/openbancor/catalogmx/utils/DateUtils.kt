package com.openbancor.catalogmx.utils

import java.time.LocalDate
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException

/**
 * Date utility functions for Mexican document processing
 */
object DateUtils {
    private val yymmddPattern = DateTimeFormatter.ofPattern("yyMMdd")
    private val yymmddDashPattern = DateTimeFormatter.ofPattern("yy-MM-dd")

    /**
     * Formats a date as YYMMDD string
     */
    @JvmStatic
    fun dateToYYMMDD(date: LocalDate): String = date.format(yymmddPattern)

    /**
     * Parses a YYMMDD string to LocalDate
     *
     * Handles century disambiguation:
     * - 00-29 -> 2000-2029
     * - 30-99 -> 1930-1999
     */
    @JvmStatic
    fun parseDateYYMMDD(dateStr: String): LocalDate? {
        if (dateStr.length != 6 || !dateStr.all { it.isDigit() }) return null

        return try {
            val yy = dateStr.substring(0, 2).toInt()
            val mm = dateStr.substring(2, 4).toInt()
            val dd = dateStr.substring(4, 6).toInt()

            // Validate month and day ranges
            if (mm < 1 || mm > 12) return null
            if (dd < 1 || dd > 31) return null

            // Century disambiguation
            val year = if (yy < 30) 2000 + yy else 1900 + yy

            LocalDate.of(year, mm, dd)
        } catch (e: Exception) {
            null
        }
    }

    /**
     * Validates if a YYMMDD string represents a valid date
     */
    @JvmStatic
    fun isValidDateYYMMDD(dateStr: String): Boolean = parseDateYYMMDD(dateStr) != null

    /**
     * Parses an ISO date string (YYYY-MM-DD) to LocalDate
     */
    @JvmStatic
    fun parseISODate(dateStr: String): LocalDate? {
        return try {
            LocalDate.parse(dateStr)
        } catch (e: DateTimeParseException) {
            null
        }
    }

    /**
     * Calculates age from birth date to a reference date
     */
    @JvmStatic
    @JvmOverloads
    fun calculateAge(birthDate: LocalDate, referenceDate: LocalDate = LocalDate.now()): Int {
        var age = referenceDate.year - birthDate.year
        if (referenceDate.monthValue < birthDate.monthValue ||
            (referenceDate.monthValue == birthDate.monthValue && referenceDate.dayOfMonth < birthDate.dayOfMonth)
        ) {
            age--
        }
        return age
    }
}
