## Credenciales a configurar dentro de n8n (no en .env)

| Credencial | Tipo | Header |
|---|---|---|
| OpenAQ API Key | Header Auth | X-API-Key |
| Groq API Key | Header Auth | Authorization: Bearer <key> |
| Gemini API Key | Header Auth | x-goog-api-key |
| PostgreSQL - Escritura | Postgres | host: postgres, user: [nuevo] |
| PostgreSQL - Solo Lectura | Postgres | host: postgres, user: nlq_reader |