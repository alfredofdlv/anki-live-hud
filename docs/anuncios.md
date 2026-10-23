# Textos para anunciar Anki Live HUD

Estos son borradores para publicar tú. No se han enviado mensajes ni publicado
anuncios. Usa los enlaces de GitHub solo después de comprobar que la release
está publicada. Añade un código de AnkiWeb únicamente cuando se haya asignado uno real.
Los textos están en inglés para las comunidades indicadas, con una variante española al final.

## Dónde publicaría primero

1. **Foro oficial de Anki → Add-ons**:
   https://forums.ankiweb.net/c/anki/add-ons/11
   La descripción de esa categoría incluye publicaciones sobre complementos nuevos.
   Usa un solo tema como anuncio y soporte, y contesta las incidencias allí.
2. **r/Anki**, si las normas visibles del momento permiten el anuncio:
   https://www.reddit.com/r/Anki/
   Es el público más directamente relacionado con esta herramienta.
3. **r/AnkiAI**, como alternativa si los moderadores de r/Anki consideran que
   el proyecto encaja mejor allí por cómo se desarrolló. Aclara que el HUD no
   incorpora funciones de IA ni envía tarjetas a ningún servicio.
4. **r/medicalschoolanki**, de forma secundaria y solo si sus normas y
   moderadores permiten la autopromoción. No es una herramienta médica; no
   lo presentes como un producto validado para medicina ni prometas notas mejores.

La revisión se hizo el 23 de octubre de 2026. El
[anuncio de los moderadores de r/Anki](https://www.reddit.com/r/Anki/comments/1ray0h6/ranki_rule_updates_aigenerated_content_and_ai/)
pide indicar precio/licencia y declarar los proyectos desarrollados mayoritariamente
con IA. También advierte contra contenido de poco esfuerzo y autopromoción repetitiva.
No pude obtener el texto completo de las páginas de reglas mediante su vista
pública, así que revisa sus normas dentro de Reddit antes de enviar un anuncio.
La [categoría oficial Add-ons](https://forums.ankiweb.net/c/anki/add-ons/11) sí
indica expresamente que admite publicaciones sobre complementos nuevos.

Publica una demostración real, revisa el texto para que refleje tu forma de hablar
y responde a los comentarios. No pegues el mismo anuncio en muchas comunidades
en una sola sesión ni lo vuelvas a publicar por falta de votos. No solicites
votos o reseñas positivas: pide errores reproducibles y opiniones sobre el uso.

## r/Anki — anuncio principal

**Title**

Anki Live HUD: a free sidebar with animated review stats — first public prerelease

**Body**

I'm sharing the first public prerelease of **Anki Live HUD**, a free, MIT-licensed
add-on for Anki Desktop. It puts a compact statistics sidebar beside your cards
and animates the changes after each Again, Hard, Good or Easy answer.

It shows today's answer count, unique cards, correct/Again answers, answer
accuracy, Anki's actual queue remaining and a configurable daily goal. It handles
undo and can be resized, collapsed or hidden. There are light/dark themes,
a compact layout and reduced-motion support.

The statistics come from the collection's review log. “Accuracy” here means
Hard + Good + Easy divided by all rated answers; it is **not True Retention**.
Daily figures cover the whole collection; remaining follows the selected study deck.
The add-on does not modify card templates or scheduling, and it works offline
without accounts, subscriptions or telemetry.

**Current status:** v0.1.0-rc.1, requiring Anki Desktop 26.09.3+. Native testing
was done on Windows with an isolated test profile, including keyboard/mouse
answers, undo, restart and queue completion. macOS/Linux and combinations with
other UI add-ons still need testing. It does not run on AnkiMobile or AnkiDroid.

**Disclosure:** I'm the project maintainer. The project was largely developed
with AI assistance; the repository includes the source, automated checks and
evidence from real Anki tests. The HUD itself does not use an AI service.

Demo: https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/images/native-review.gif

Download and installation: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1

Source and issues: https://github.com/alfredofdlv/anki-live-hud

Install the `.ankiaddon` through Tools → Add-ons → Install from file, then restart.
If you try it, I'd especially like feedback on whether the panel feels useful or
distracting during normal reviews, and reports of layout conflicts with other
add-ons. Please include your OS and Anki version with a bug report.

## Foro de Anki — anuncio y tema de soporte

**Title**

Anki Live HUD — animated reviewer statistics sidebar [v0.1.0-rc.1, free/MIT]

**Body**

Anki Live HUD is an open-source Anki Desktop add-on that keeps a small animated
statistics panel beside the reviewer. This is its first public prerelease.

The panel updates from actual collection data after a rating. It displays daily
answer events and unique cards, correct and Again answers, answer accuracy,
scheduler queue remaining, answer distribution and a configurable daily goal.
Undo restores the totals from the review log. The dock stays alive across
questions, answers and cards, and supports resizing, collapsing and hiding.

The reviewer card HTML and scheduler are unchanged. The UI is a separate Qt
dock/webview using official GUI hooks. There are no remote assets, telemetry
or additional runtime dependencies beyond Anki. Anki/OS reduced-motion
preferences take precedence over the animation switch.

Accuracy is `(Hard + Good + Easy) / all rated answers`, including learning;
it is not Anki's True Retention. Daily totals are collection-wide. Remaining
uses the selected study deck's actual scheduler counts and may not decrease
after a learning answer.

**Compatibility:** requires Anki Desktop 26.09.3+, Qt 6. Tested natively on
Windows/Anki 26.09.3. macOS/Linux and combinations with other reviewer layout
add-ons are unverified. This is a prerelease rather than a broadly validated
stable version.

**Price/license:** free, MIT. No account or subscription. I maintain the project;
it was largely developed with AI assistance. The source and testing evidence
are included, and the add-on itself has no AI functionality.

- Source: https://github.com/alfredofdlv/anki-live-hud
- Download: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1
- Tests: https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/testing.md
- Demo: https://github.com/alfredofdlv/anki-live-hud/blob/main/docs/images/native-review.gif

Install the `.ankiaddon` using Tools → Add-ons → Install from file, restart,
then open a deck and start reviewing. Settings are under Tools → Anki Live HUD.
An AnkiWeb installation code is not available yet.

Bug reports are welcome in this thread or on GitHub. Include the OS, exact Anki
version, other enabled add-ons and a sample-deck reproduction without private data.

## r/medicalschoolanki — variante breve, sujeta a sus normas

**Title**

Free Anki Desktop add-on: live review statistics beside your cards [prerelease]

**Body**

I'm the maintainer of Anki Live HUD, a free MIT-licensed desktop add-on that
shows animated review statistics beside the card: today's answer count,
correct/Again answers, answer accuracy, queue remaining and a daily goal.
It supports undo, light/dark themes, reduced motion, collapsing and hiding.

It is a general review UI tool, not medical content or a scheduling change.
“Accuracy” means Hard/Good/Easy divided by all answers, not True Retention.
It does not modify decks or card templates and makes no claims about exam
performance or better retention.

This is the first public prerelease, requiring Anki Desktop 26.09.3+. Native
tests were run on Windows; macOS/Linux and combinations with popular medical
reviewer add-ons still need testing. The project was largely built with AI
assistance; source and test evidence are public. The add-on has no AI service,
account, fee or telemetry.

Demo/source: https://github.com/alfredofdlv/anki-live-hud

Download: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1

I'd appreciate reports of layout or shortcut conflicts during actual reviews.
If you try it, please include your Anki version and the other reviewer add-ons
you use when reporting an issue.

## r/AnkiAI — alternativa, si encaja con sus normas

**Title**

AI-assisted open-source project: an animated statistics HUD for the native Anki reviewer

**Body**

I'm sharing Anki Live HUD, a free MIT-licensed Anki Desktop add-on largely
developed with AI assistance. The functionality is a persistent statistics
sidebar during normal reviews; it doesn't generate cards or run an AI model.

Each rating updates animated counters, answer accuracy, queue remaining and
a daily-goal bar from Anki's actual collection data. Undo, compact/light/dark
layouts, collapse/hide and reduced-motion preferences are supported.

The repository includes source, 28 Python tests, 21 browser checks and native
Anki test evidence. The native Windows tests cover keyboard/mouse ratings,
undo, restart and natural queue completion in a disposable profile.

This is v0.1.0-rc.1 for Anki Desktop 26.09.3+. macOS/Linux and third-party add-on
combinations remain unverified. It is offline, with no account, fee or telemetry.

Source/demo: https://github.com/alfredofdlv/anki-live-hud

Download: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1

I'm interested in concrete feedback on UI distraction, undo behavior and
compatibility rather than suggestions for adding more gamification immediately.

## Variante en español para una comunidad donde esté permitido

**Título**

Anki Live HUD: estadísticas animadas junto a tus tarjetas — complemento gratuito y abierto

**Texto**

Comparto la primera versión preliminar de Anki Live HUD, un complemento gratuito
con licencia MIT para Anki Desktop. Añade un panel lateral pequeño que actualiza
sus contadores y la barra de objetivo diario cada vez que calificas una tarjeta.

Muestra las respuestas de hoy, las tarjetas únicas, las respuestas correctas y
Again, el porcentaje Hard/Good/Easy y la cola restante de Anki. Permite deshacer,
cambiar el tema, reducir su tamaño, contraerlo u ocultarlo. No cambia la
programación ni el diseño de las tarjetas y funciona sin conexión.

Lo mantengo yo y se ha desarrollado mayoritariamente con asistencia de IA.
El código y los resultados de pruebas están disponibles. El complemento no
incorpora funciones de IA ni envía datos de las tarjetas a servicios externos.

Requiere Anki Desktop 26.09.3 o posterior. Está probado en Windows; todavía faltan
pruebas en macOS/Linux y con otros complementos. Es una versión preliminar,
no una garantía de compatibilidad universal. El porcentaje de respuestas no
es la estadística True Retention.

Código, capturas y demostración: https://github.com/alfredofdlv/anki-live-hud

Descarga: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1

Para instalarlo, descarga el `.ankiaddon`, abre Herramientas → Complementos →
Instalar desde archivo y reinicia Anki. Me sirven especialmente los comentarios
sobre si distrae durante el repaso y los errores que se puedan reproducir.

## Imágenes y respuestas breves

Adjunta `docs/images/native-review.gif` al anuncio principal si la plataforma
admite GIF. Si no, utiliza `reviewer-answered-dark.png` y enlaza el GIF. Las
capturas son de un mazo de prueba; no utilices capturas de tarjetas privadas.

**“Is it free?”** — Yes. It is free and MIT licensed. There is no account,
subscription or AI API dependency.

**“Does it change FSRS or improve retention?”** — It does not change the scheduler.
There is no measured claim of improved retention. The displayed accuracy is a
rating-based answer percentage, not True Retention.

**“AnkiWeb code?”** — Not available yet. The prerelease can be installed directly
from its `.ankiaddon` file on GitHub. This answer must be updated once a real
AnkiWeb listing exists.

**“Mobile?”** — No. This is an Anki Desktop add-on. AnkiMobile and AnkiDroid do
not load desktop add-ons.

**“Why aren't the counters moving?”** — Check the HUD animation switch and
Anki's and your OS's reduced-motion settings. Reduced motion takes precedence.
