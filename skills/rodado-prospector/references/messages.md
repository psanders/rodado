# Suggested first message (for Pedro to send himself)

Spanish (neutral Dominican, "tú" unless the brand clearly writes "usted"), short, one true observation about the brand, one question. The door-opener is Rodado's **free storyboard with 2 creative directions in 48 h, with their real product**.

## Email version (max ~110 words)
```
Asunto: idea para el próximo anuncio de <Marca>

Hola <Nombre / equipo de <Marca>>,

Vi <observación concreta y verificable: el lanzamiento de <producto> en Instagram / que sus publicaciones son casi todas fotos de producto / que ya están en Sirena y Nacional / …>.

Hago anuncios en video para marcas dominicanas a partir de fotos del producto real, sin rodaje: un anuncio en 3 duraciones (30, 20 y 15 s) en 7 días hábiles.

Si te sirve, te preparo gratis un storyboard con 2 direcciones creativas para <producto concreto> en 48 horas. ¿Te lo mando?

Pedro Sanders
Rodado Creativo · roda.do
WhatsApp +1 (785) 317-8070
```

## Instagram DM version (max ~50 words)
```
Hola <Marca>! Vi <observación>. Hago anuncios en video para marcas dominicanas a partir de fotos del producto, sin rodaje. Si les sirve, les preparo gratis un storyboard con 2 ideas para <producto> en 48 h. ¿Se lo mando? — Pedro, Rodado Creativo
```

## Lead file (for `leads.py add`)
```json
{
  "company": "Café Ejemplo",
  "website": "https://cafeejemplo.com.do",
  "instagram": "@cafeejemplo",
  "category": "coffee",
  "city": "Santo Domingo",
  "contact_name": "María Pérez",
  "role": "Gerente de Mercadeo",
  "email": "mercadeo@cafeejemplo.com.do",
  "email_source": "https://cafeejemplo.com.do/contacto",
  "ad_library": "https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=DO&search_type=keyword_unordered&q=Caf%C3%A9%20Ejemplo",
  "why": "Fit 3 · new 1 lb bag launched in September · in Sirena and Nacional · posts product photos weekly",
  "source": "supermarket-catalog",
  "message_email": "Asunto: …\n\nHola María,\n\n…",
  "message_dm": "Hola Café Ejemplo! …"
}
```
`company` and `why` are required. `email` is optional; when present, `email_source` is required.
