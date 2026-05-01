# Guardrails legales y operativos

## Marco de cumplimiento para scraping global agresivo

1. Revisar términos de uso por fuente antes de habilitar un conector.
2. Respetar `robots.txt` y políticas anti-bot cuando aplique.
3. No extraer datos personales sensibles.
4. Conservar solo campos necesarios para matching laboral.
5. Deshabilitar de inmediato fuentes con reclamos legales.

## Guardrails técnicos

1. Limitar tasa por dominio (`rate limit`) y usar reintentos exponenciales.
2. Aislar cada conector para evitar caída total del sistema.
3. Añadir timeout y circuit breaker por fuente.
4. Registrar errores por conector y métricas de disponibilidad.
5. Aplicar deduplicación canónica para minimizar ruido y spam.

## Reglas de notificación

1. Máximo 3 notificaciones por hora por usuario.
2. No notificar vacantes duplicadas.
3. Priorizar vacantes con score alto y recientes.
4. Permitir desactivación total desde ajustes del usuario.
