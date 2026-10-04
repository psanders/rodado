# Content · Rodado Creativo

Sistema para producir 7 publicaciones por semana en Instagram (@rodado.creativo), rápido y consistente.
Todo nace de una plantilla, todo vive en una carpeta, nada se inventa el mismo día.

> Ojo: este repo es público y se publica en roda.do. `prospects/` y `metrics/` están en `.gitignore`.

## Estructura

```
content/
  strategy-full.md        Estrategia completa (importada del doc), en inglés
  strategy.md             Resumen operativo: audiencia, meta, pilares, formatos, cadencia, decisiones
  voice.md                Cómo hablamos: tono, palabras, CTAs, reglas de copy
  instagram-profile.md    Bio, destacadas y publicaciones fijadas
  publishing.md           Cómo programar la semana en Meta Business Suite
  templates/              Una plantilla por formato + caption + brief de post
  ideas/bank.csv          Banco de ideas (siempre ~15 esperando)
  calendar/YYYY-Wnn/      Una carpeta por semana, una subcarpeta por post
  metrics/log.csv         Una fila por post publicado (privado)
  prospects/              Marcas objetivo para outbound (privado)
  scripts/new-week.sh     Crea la carpeta de la semana desde las plantillas
```

## Ritual semanal

| Cuándo | Qué | Tiempo |
| --- | --- | --- |
| Viernes | Llenar `metrics/log.csv` con la semana que termina | 15 min |
| Viernes | Agregar ideas nuevas a `ideas/bank.csv` | 15 min |
| Viernes | `scripts/new-week.sh 2026-W42` y elegir 7 ideas del banco | 20 min |
| Viernes | Escribir los 7 ganchos y CTAs en cada `post.md` | 10 min |
| Lunes | Producir martes a domingo en lote (Pencil + video) | 3-4 h |
| Lunes | Programar todo en Meta Business Suite (`publishing.md`) | 30 min |
| Diario | Responder comentarios y DMs; 10+ mensajes de outbound | 30 min |

## Nombres de archivo

`calendar/2026-W41/01-mon-reel-storyboard/` → `post.md` (brief + copy), `final/` (lo que se sube), `sources/` (archivos de trabajo).
Archivos finales: `2026-10-05-reel-storyboard-guaraguao.mp4`, `2026-10-06-carrusel-01.png` … `-08.png`.

## Reglas que ahorran tiempo

1. Un post = una idea = un gancho. Si necesita dos ideas, son dos posts.
2. Reusar antes que crear: cada proyecto de cliente da 3 posts (storyboard a anuncio, 3 cortes, una lección).
3. Clientes reales solo con logo reemplazado por uno inventado parecido. Nunca su marca real sin permiso.
4. Formato fijo por día (ver `strategy.md`) para comparar resultados semana a semana.
5. Cambiar una sola variable a la vez y anotarla en `log.csv` (columna `test`).
