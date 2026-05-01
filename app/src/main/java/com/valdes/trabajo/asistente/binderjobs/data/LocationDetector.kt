package com.valdes.trabajo.asistente.binderjobs.data

import com.valdes.trabajo.asistente.binderjobs.data.model.AppLocation
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class LocationDetector {
    fun detectByIp(): AppLocation? {
        return runCatching {
            val connection =
                URL("https://ipapi.co/json/").openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.connectTimeout = 5000
            connection.readTimeout = 5000
            connection.inputStream.bufferedReader().use { reader ->
                val json = JSONObject(reader.readText())
                AppLocation(
                    country = json.optString("country_name"),
                    state = json.optString("region"),
                    city = json.optString("city"),
                )
            }
        }.getOrNull()
    }
}
