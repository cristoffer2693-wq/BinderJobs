package com.valdes.trabajo.asistente.binderjobs.data

import com.valdes.trabajo.asistente.binderjobs.data.model.JobOffer
import com.valdes.trabajo.asistente.binderjobs.data.model.UserPreferences
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder
import java.nio.charset.StandardCharsets

class JobRepository {
    
    private val baseUrl: String
        get() = ApiConfig.BASE_URL
    
    private val connectTimeout: Int
        get() = ApiConfig.CONNECT_TIMEOUT_MS
    
    private val readTimeout: Int
        get() = ApiConfig.READ_TIMEOUT_MS
    
    fun fetchJobs(query: String, preferences: UserPreferences): List<JobOffer> {
        val remote = searchJobs(query, preferences)
        return if (remote.isNotEmpty()) remote else getFallbackJobs(query, preferences)
    }
    
    fun searchJobs(query: String, preferences: UserPreferences): List<JobOffer> {
        return runCatching {
            val searchQuery = query.ifBlank { preferences.preferredRole }
            val params = buildSearchParams(searchQuery, preferences)
            val url = "$baseUrl/jobs/search?$params"
            
            fetchFromUrl(url)
        }.getOrDefault(emptyList())
    }
    
    fun searchNearbyJobs(preferences: UserPreferences, query: String = ""): List<JobOffer> {
        if (preferences.city.isBlank()) return emptyList()
        
        return runCatching {
            val params = buildString {
                append("city=").append(encode(preferences.city))
                append("&country=").append(encode(preferences.country))
                append("&radius_km=").append(preferences.radiusKm)
                if (query.isNotBlank()) {
                    append("&q=").append(encode(query))
                }
                append("&limit=50")
            }
            val url = "$baseUrl/jobs/nearby?$params"
            
            fetchFromUrl(url)
        }.getOrDefault(emptyList())
    }
    
    fun searchJobsAdvanced(
        query: String,
        preferences: UserPreferences,
        limit: Int = 100,
    ): SearchResult {
        return runCatching {
            val requestBody = JSONObject().apply {
                put("query", query.ifBlank { preferences.preferredRole })
                put("country", preferences.country)
                put("city", preferences.city)
                put("state", preferences.state)
                put("modality", preferences.preferredModality)
                put("salary_min", preferences.salaryMin)
                put("limit", limit)
                put("preferred_roles", JSONArray(preferences.searchHistory.take(5)))
                put("excluded_companies", JSONArray(preferences.excludedCompanies))
                put("preferred_sources", JSONArray(preferences.preferredSources))
            }
            
            val connection = URL("$baseUrl/jobs/search").openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.connectTimeout = connectTimeout
            connection.readTimeout = readTimeout
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true
            
            connection.outputStream.bufferedWriter().use { writer ->
                writer.write(requestBody.toString())
            }
            
            val responseCode = connection.responseCode
            if (responseCode != HttpURLConnection.HTTP_OK) {
                return@runCatching SearchResult(emptyList(), 0, 0)
            }
            
            val body = connection.inputStream.bufferedReader().use { it.readText() }
            val response = JSONObject(body)
            
            val jobs = parseJobsArray(response.getJSONArray("jobs"))
            val totalFound = response.optInt("total_found", jobs.size)
            val sourcesSearched = response.optInt("sources_searched", 0)
            
            SearchResult(jobs, totalFound, sourcesSearched)
        }.getOrDefault(SearchResult(emptyList(), 0, 0))
    }
    
    fun backgroundSearch(preferences: UserPreferences): List<JobOffer> {
        return runCatching {
            val requestBody = JSONObject().apply {
                put("query", preferences.preferredRole)
                put("country", preferences.country)
                put("city", preferences.city)
                put("state", preferences.state)
                put("modality", preferences.preferredModality)
                put("salary_min", preferences.salaryMin)
                put("limit", 30)
            }
            
            val connection = URL("$baseUrl/background/search").openConnection() as HttpURLConnection
            connection.requestMethod = "POST"
            connection.connectTimeout = connectTimeout
            connection.readTimeout = readTimeout
            connection.setRequestProperty("Content-Type", "application/json")
            connection.doOutput = true
            
            connection.outputStream.bufferedWriter().use { writer ->
                writer.write(requestBody.toString())
            }
            
            if (connection.responseCode != HttpURLConnection.HTTP_OK) {
                return@runCatching emptyList()
            }
            
            val body = connection.inputStream.bufferedReader().use { it.readText() }
            val response = JSONObject(body)
            
            parseJobsArray(response.getJSONArray("jobs"))
        }.getOrDefault(emptyList())
    }
    
    private fun buildSearchParams(query: String, preferences: UserPreferences): String {
        return buildString {
            append("q=").append(encode(query))
            append("&country=").append(encode(preferences.country))
            append("&city=").append(encode(preferences.city))
            append("&state=").append(encode(preferences.state))
            if (preferences.preferredModality.isNotBlank()) {
                append("&modality=").append(encode(preferences.preferredModality))
            }
            if (preferences.salaryMin > 0) {
                append("&salary_min=").append(preferences.salaryMin)
            }
            append("&limit=100")
        }
    }
    
    private fun fetchFromUrl(url: String): List<JobOffer> {
        val connection = URL(url).openConnection() as HttpURLConnection
        connection.requestMethod = "GET"
        connection.connectTimeout = connectTimeout
        connection.readTimeout = readTimeout
        connection.setRequestProperty("Accept", "application/json")
        
        val responseCode = connection.responseCode
        if (responseCode != HttpURLConnection.HTTP_OK) {
            return emptyList()
        }
        
        val body = connection.inputStream.bufferedReader().use { it.readText() }
        return parseJobsArray(JSONArray(body))
    }
    
    private fun parseJobsArray(array: JSONArray): List<JobOffer> {
        return buildList {
            for (i in 0 until array.length()) {
                val item = array.getJSONObject(i)
                add(parseJobOffer(item))
            }
        }
    }
    
    private fun parseJobOffer(item: JSONObject): JobOffer {
        return JobOffer(
            id = item.optString("id", ""),
            title = item.optString("title", "Sin título"),
            company = item.optString("company", "Empresa"),
            country = item.optString("country", ""),
            city = item.optString("city", ""),
            modality = item.optString("modality", "No especificado"),
            salary = item.optString("salary", null).takeIf { it.isNotBlank() && it != "null" },
            summary = item.optString("summary", ""),
            sourceName = item.optString("source", ""),
            url = item.optString("url", ""),
            publishedAt = item.optString("published_at", "Reciente"),
            score = item.optDouble("score", 0.0),
            relevanceScore = item.optDouble("relevance_score", 0.0),
            locationScore = item.optDouble("location_score", 0.0),
            preferenceScore = item.optDouble("preference_score", 0.0),
        )
    }
    
    private fun encode(value: String): String {
        return URLEncoder.encode(value, StandardCharsets.UTF_8.toString())
    }
    
    private fun getFallbackJobs(query: String, preferences: UserPreferences): List<JobOffer> {
        val fallbackJobs = listOf(
            JobOffer(
                id = "offline-1",
                title = "Desarrollador Android",
                company = "TechBolivia",
                country = "Bolivia",
                city = "Tarija",
                modality = "Presencial",
                salary = "Bs. 5,000 - 8,000",
                summary = "Desarrollo de aplicaciones móviles con Kotlin y Android Studio.",
                sourceName = "Local",
                url = "https://www.computrabajo.com.bo/",
                publishedAt = "Ejemplo offline",
                score = 0.9,
            ),
            JobOffer(
                id = "offline-2",
                title = "Analista de Sistemas",
                company = "YPFB",
                country = "Bolivia",
                city = "Tarija",
                modality = "Presencial",
                salary = "Bs. 6,000+",
                summary = "Análisis y desarrollo de sistemas para el sector energético.",
                sourceName = "Local",
                url = "https://www.trabajo.bo/",
                publishedAt = "Ejemplo offline",
                score = 0.85,
            ),
            JobOffer(
                id = "offline-3",
                title = "Programador Web",
                company = "RemoteLATAM",
                country = "Bolivia",
                city = "Remoto",
                modality = "Remoto",
                salary = "USD 800 - 1,500",
                summary = "Desarrollo web full-stack con React y Node.js.",
                sourceName = "Local",
                url = "https://remoteok.com/",
                publishedAt = "Ejemplo offline",
                score = 0.80,
            ),
        )
        
        val queryLower = query.lowercase()
        return fallbackJobs.filter { job ->
            val matchesQuery = queryLower.isBlank() ||
                job.title.lowercase().contains(queryLower) ||
                job.summary.lowercase().contains(queryLower)
            
            val matchesLocation = preferences.city.isBlank() ||
                job.city.equals(preferences.city, ignoreCase = true) ||
                job.modality == "Remoto"
            
            matchesQuery && matchesLocation
        }
    }
}

data class SearchResult(
    val jobs: List<JobOffer>,
    val totalFound: Int,
    val sourcesSearched: Int,
)
