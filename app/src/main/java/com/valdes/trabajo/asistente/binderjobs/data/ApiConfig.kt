package com.valdes.trabajo.asistente.binderjobs.data

object ApiConfig {
    
    /**
     * URL del backend de BinderJobs.
     * 
     * INSTRUCCIONES:
     * 1. Para DESARROLLO (emulador Android): usa "http://10.0.2.2:8000"
     * 2. Para PRODUCCIÓN (Railway): cambia a tu URL de Railway
     *    Ejemplo: "https://binderjobs-backend.up.railway.app"
     * 
     * Después de desplegar en Railway, actualiza esta URL con la que te den.
     */
    
    // ============================================================
    // CAMBIA ESTA LÍNEA CON TU URL DE RAILWAY CUANDO LO DESPLIEGUES
    // ============================================================
    private const val PRODUCTION_URL = ""  // Ej: "https://binderjobs-backend.up.railway.app"
    
    // URL para desarrollo local (emulador)
    private const val DEVELOPMENT_URL = "http://10.0.2.2:8000"
    
    // Cambia a 'true' cuando tengas el backend en Railway
    private const val USE_PRODUCTION = false
    
    val BASE_URL: String
        get() = if (USE_PRODUCTION && PRODUCTION_URL.isNotBlank()) {
            PRODUCTION_URL
        } else {
            DEVELOPMENT_URL
        }
    
    // Timeouts
    const val CONNECT_TIMEOUT_MS = 15000
    const val READ_TIMEOUT_MS = 30000
}
