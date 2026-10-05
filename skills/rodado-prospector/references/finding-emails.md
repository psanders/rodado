# Finding the email

The goal is one address the company itself published for business contact, ideally marketing.

## Order
1. **Website** (`scripts/find_email.py <site>`): home + contacto/contact/nosotros/about/prensa pages. It reads `mailto:` links, plain text and "mercadeo [at] marca [dot] com [dot] do" forms, drops addresses on other domains (web agencies, plugins) and checks MX.
2. **Social profiles**: Instagram's Email/Contact button, Facebook page "About"/"Información" (business email field), the bio. Public business info only.
3. **Search** for the domain: `"@marca.com.do"`, `"Marca" mercadeo correo`, `"Marca" gerente de mercadeo`. Accept only pages the company controls, official press releases, or chamber/association member listings.
4. **Named person**: if a marketing manager's name is public (LinkedIn, press) and their work address appears on a company page or press release, use it. Use the name for the greeting even when you write to info@.

## Ranking (find_email.py `kind`)
| kind | example | use |
| --- | --- | --- |
| marketing | mercadeo@, marketing@, comunicaciones@, publicidad@ | best |
| named | maria.perez@ (published by the company) | best, greet by name |
| general | info@, contacto@, hola@, servicio@ | fine; address the email "Hola, equipo de <Marca>" and ask to forward to marketing |
| sales | ventas@, pedidos@ | only if nothing else |
| other | rrhh@, facturacion@, soporte@, webmaster@, noreply@ | never |

## Hard rules
- No pattern guessing (nombre.apellido@…) and no "email finder" guesses: unverified guesses bounce and hurt Pedro's sender reputation when he writes.
- Free webmail (gmail/hotmail) only if it's clearly the brand's official published contact.
- `mx: false` → don't use the domain. `mx: null` means the check couldn't run; use the address only if it was clearly published.
- Keep `email_source` = the URL where the address appears. If Pedro asks "where did you get this?", that's the answer.

## Optional later
A Hunter.io key (`HUNTER_API_KEY`) would add a domain search that returns the source URL of each published address plus a deliverability check. Not needed to start; ask Pedro before adding it.
