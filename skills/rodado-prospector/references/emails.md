# The emails

Three emails per lead, in one thread. Spanish (neutral Dominican, "tú" unless the brand clearly writes "usted"), from Pedro, plain text, short. The goal of the sequence is one thing: a reply ("sí, mándame el storyboard" or a WhatsApp chat). The door-opener is Rodado's **free storyboard with 2 creative directions in 48 h, using their real product**.

## Rules for every email
- Max ~110 words (follow-ups max ~60). Short paragraphs. No bullet lists, no bold, no emojis.
- One concrete, true observation about *their* ads or product (from your evidence). Never invent.
- One question as the CTA. No "agenda una llamada" links.
- Greeting with the person's first name if you know it from a public source; otherwise "Hola, equipo de <Marca>".
- Subject: lowercase-ish, specific, under 50 characters, no clickbait ("idea para el próximo anuncio de <Marca>").
- Every email ends with the signature and the opt-out line below.
- At most one link (roda.do or instagram.com/rodado.creativo). No attachments.

Signature (exactly):
```
Pedro Sanders
Rodado Creativo · roda.do
WhatsApp +1 (785) 317-8070
```
Opt-out line (last line, exactly): `Si no es para ti, respóndeme "no" y no te escribo más.`

## Email 1 (day 0) — the observation + the free storyboard
```
Hola <Nombre>,

Vi que <Marca> tiene <N> anuncios activos en Instagram y Facebook, casi todos <observación concreta: fotos de producto / el mismo video desde junio / …>.

Hago anuncios en video para marcas dominicanas a partir de fotos del producto real, sin rodaje: un anuncio en 3 duraciones (30, 20 y 15 s) en 7 días hábiles.

Si te sirve, te preparo gratis un storyboard con 2 direcciones creativas para <producto concreto> en 48 horas. ¿Te lo mando?

Pedro Sanders
Rodado Creativo · roda.do
WhatsApp +1 (785) 317-8070

Si no es para ti, respóndeme "no" y no te escribo más.
```

## Email 2 (day 3) — short bump, adds one proof
```
Hola <Nombre>, te escribo de nuevo por si se perdió el correo.

Aquí puedes ver cómo queda un anuncio hecho así, del storyboard al video final: instagram.com/rodado.creativo

¿Te preparo el de <producto>?

Pedro
```
(+ the opt-out line)

## Email 3 (day 8) — polite close
```
Hola <Nombre>, último correo de mi parte para no llenarte el buzón.

Si en algún momento necesitas anuncios nuevos para <Marca> sin coordinar un rodaje, me escribes aquí o por WhatsApp y lo arrancamos.

Éxitos con <lanzamiento / temporada / el producto>.

Pedro
```
(+ the opt-out line)

Adapt the wording to each brand; keep the structure, length and the offer.

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
  "why": "Fit 3 · 7 active Meta ads, all static product photos, oldest from June · in Sirena and Nacional · new 1 lb bag launched in September",
  "source": "meta-ad-library",
  "first_email": {"subject": "idea para el próximo anuncio de Café Ejemplo", "body": "Hola María,\n\n…"},
  "followups": ["Hola María, te escribo de nuevo…", "Hola María, último correo…"]
}
```
Bodies are the full plain text, signature and opt-out line included.
