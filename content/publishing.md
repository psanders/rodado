# Publicar · programar la semana en Meta Business Suite

Herramienta: Meta Business Suite (gratis, oficial) en computadora: business.facebook.com → Planificador.
Respaldo: la app de Instagram (Crear → Configuración avanzada → Programar publicación; hasta 75 días antes).

## Requisitos (una sola vez)
- [ ] Instagram como cuenta profesional (Empresa o Creador).
- [ ] Instagram conectado a la página de Facebook de Rodado y a Business Suite (Configuración → Cuentas comerciales / Activos).
- [ ] Confirmar en el Planificador que se puede elegir "Reel de Instagram" y "Publicación de Instagram" con varias imágenes.

## Cada lunes (30 min)
Para cada carpeta de `calendar/YYYY-Wnn/` con `status: ready`:
1. Planificador → Crear → Reel (o Publicación para carrusel/estático).
2. Elegir solo Instagram (desmarcar Facebook si no queremos duplicar).
3. Subir lo que hay en `final/`: el video + portada, o las láminas en orden (01, 02…).
4. Pegar el caption del `post.md`.
5. Programar con `fecha` y `hora` del `post.md` (hora RD).
6. Cambiar `status: scheduled` en el `post.md` y en `week.md`.

Al terminar, abrir la vista de calendario del Planificador y comprobar los 7.

## Datos útiles
- Reels: 9:16, 1080 × 1920, hasta 90 s para que cuenten como Reel. Portada aparte.
- Carruseles: hasta 10 láminas (usamos 4:5, 1080 × 1350). Mismo tamaño en todas.
- Business Suite no tiene carga masiva: son 7 publicaciones, una por una (~3 min cada una).
- Lo no verificado aún (confirmar la primera vez): límite de días hacia adelante en Business Suite y si exige página de Facebook.

## Automatizar del todo (más adelante, opcional)
La API de Instagram (Content Publishing) publica Reels y carruseles pero no programa: haría falta un script con cron,
una app de Meta con permiso `instagram_business_content_publish` y los archivos en una URL pública.
Tiene sentido cuando el sistema esté estable (semana 8+). Herramientas de terceros (Buffer, Metricool) cobran
o limitan el plan gratis por debajo de 7 posts por semana.
