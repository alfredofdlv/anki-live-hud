# Usarlo y publicar Anki Live HUD

## ¿Lo puedo usar ya?

**Sí.** Instala `dist/anki-live-hud-0.1.0-rc.1.ankiaddon` desde
**Anki → Herramientas → Complementos → Instalar desde archivo…** y reinicia Anki.
En una interfaz inglesa: **Tools → Add-ons → Install from file…**.

Necesitas Anki Desktop **26.09.3 o posterior**. La versión comprobada en este
equipo es 26.09.3 para Windows. El HUD aparecerá al comenzar a repasar.
No necesitas publicar nada, una cuenta de GitHub ni un código de AnkiWeb para usarlo.
El archivo y el código fuente ya están guardados en este directorio.

Consulta la [guía de instalación](install-windows.md) para configurar el objetivo,
las animaciones, los temas, el tamaño y la visibilidad. Si las animaciones no se
ven, comprueba también la preferencia de movimiento reducido de Anki y de Windows.

## ¿Está listo para que lo usen otras personas?

**Sí, como versión preliminar pública `v0.1.0-rc.1`.** El núcleo funciona y se
ha probado con Anki real, pero todavía no hay suficiente experiencia de usuarios
como para presentarlo como una versión estable probada en todos los sistemas.

Se han ejecutado 28 pruebas Python, 21 comprobaciones del frontend y pruebas del
Anki instalado con un perfil temporal: respuestas con teclado y ratón, deshacer,
temas, ajustes, tamaño, reinicio y final de la cola. El instalador de Anki acepta
el paquete. El [informe](testing.md) conserva las limitaciones y las evidencias.

Lo que falta validar antes de ampliar las promesas de compatibilidad:

- Interfaz nativa en macOS y Linux.
- Combinaciones con otros complementos, especialmente los que cambian el reviewer.
- Uso cotidiano por varias personas y sincronización real con cuentas de AnkiWeb.

Esas limitaciones no impiden compartir una versión preliminar con compatibilidad
declarada. No hay que esperar a implementar FSRS, rachas o gamificación para publicarla.

## GitHub y descargas

- Código: https://github.com/alfredofdlv/anki-live-hud
- Versión inicial: https://github.com/alfredofdlv/anki-live-hud/releases/tag/v0.1.0-rc.1
- Pruebas automatizadas: https://github.com/alfredofdlv/anki-live-hud/actions

La descarga que instala un usuario es el archivo **`.ankiaddon`** adjunto a la
release. El ZIP de código fuente es para leer o desarrollar el proyecto; no es el
archivo que hay que seleccionar en el instalador de Anki.

Una prerelease no siempre aparece bajo `/releases/latest`. Comparte el enlace
con la etiqueta concreta de arriba o el enlace directo a su archivo:

https://github.com/alfredofdlv/anki-live-hud/releases/download/v0.1.0-rc.1/anki-live-hud-0.1.0-rc.1.ankiaddon

GitHub conserva el código y las versiones publicadas; la copia local conserva
también el entorno de desarrollo y los resultados de las pruebas. Los entornos,
perfiles temporales, credenciales y registros privados quedan fuera del repositorio.

## Subirlo a AnkiWeb

GitHub no lo registra automáticamente como complemento de AnkiWeb. Para obtener
un código numérico instalable desde **Obtener complementos / Get Add-ons**:

1. Entra con tu cuenta en [AnkiWeb Add-ons](https://ankiweb.net/shared/addons).
2. Usa **Upload**, el formulario oficial para compartir complementos.
3. Sube únicamente `anki-live-hud-0.1.0-rc.1.ankiaddon`. No subas el ZIP del
   repositorio, la carpeta de desarrollo ni los perfiles de pruebas.
4. Usa el título y la descripción preparados en [ankiweb-listing.md](ankiweb-listing.md).
   Indica que es una versión preliminar, gratuita, con licencia MIT y para escritorio.
5. Si el formulario solicita la versión mínima compatible, indica **26.09.3**.
   El manifiesto ya contiene su representación `min_point_version: 260903`.
   No anuncies versiones anteriores ni plataformas que aún no has validado.
6. Añade capturas de `docs/images/`. Como principal utiliza
   `reviewer-answered-dark.png`; añade también la clara y la compacta.
   Usa el GIF si el formulario lo admite; en caso contrario enlázalo desde GitHub.
7. Enlaza el código fuente, la licencia y el apartado de incidencias de GitHub.
8. Revisa el contenido y completa la publicación según las indicaciones que
   AnkiWeb muestre en ese momento. Los campos y los controles pueden cambiar.
9. Cuando exista la ficha, guarda su URL y el código real. Añádelos al README,
   al anuncio y a la guía de instalación. No uses un código de ejemplo como si fuera real.

El [manual oficial de distribución](https://docs.ankiweb.net/addons/sharing)
explica el formato: el ZIP renombrado a `.ankiaddon` debe tener `__init__.py` y
el manifiesto en la raíz, sin carpeta contenedora ni `__pycache__`. El constructor
de este proyecto ya comprueba esa estructura.

**Cambio desde la instalación manual:** GitHub instala en `anki_live_hud`;
AnkiWeb puede utilizar una carpeta con su ID numérico. No habilites ambas copias
a la vez. Antes de instalar la versión de AnkiWeb, guarda tus ajustes, elimina la
copia manual desde el gestor de complementos y reinicia Anki. Eliminar el
complemento no elimina tarjetas ni historial de repasos. El traslado automático
de preferencias entre esas dos instalaciones no está implementado.

No se ha inventado un código de AnkiWeb ni se ha enviado un formulario en tu nombre.
Los anuncios deben decir «instalación desde GitHub» hasta que exista una ficha real.

## Anunciarlo

Los textos listos para adaptar están en [anuncios.md](anuncios.md). El orden que
seguiría es: publicar la prerelease, comprobar su descarga, abrir un único tema
de soporte en el foro de Anki y después hacer un anuncio en r/Anki si sus normas
vigentes lo permiten. Para una primera publicación no hace falta lanzarlo en
muchas comunidades a la vez.

Incluye el GIF real, el enlace de descarga, precio/licencia, compatibilidad y una
pregunta concreta sobre la experiencia de uso. Declara que mantienes el proyecto
y que se desarrolló mayoritariamente con asistencia de IA. No prometas una mejora
de retención o resultados de examen: esas afirmaciones no se han medido.

## Publicar la siguiente versión

1. Reproduce y corrige las incidencias en un perfil temporal.
2. Cambia la versión en `addon/__init__.py`, `addon/manifest.json`
   (`version` y `human_version`) y `pyproject.toml`. Actualiza el changelog.
3. Ejecuta las comprobaciones, construye el paquete y prueba su instalación:

   ```powershell
   .\.venv\Scripts\python -m pytest -q
   .\.venv\Scripts\ruff check addon tests scripts
   .\.venv\Scripts\ruff format --check addon tests scripts
   .\.venv\Scripts\python scripts\build.py
   .\.venv\Scripts\python scripts\test_native.py --installed-exe "$env:LOCALAPPDATA\Programs\Anki\Anki.exe"
   ```

   El harness nativo actual comprueba la primera versión; si cambia el escenario
   o la versión que construyes, revisa sus expectativas antes de reutilizarlo.

4. Haz un commit y `git push origin main`. Espera a que Actions termine correctamente.
5. Crea una etiqueta nueva, sin mover una etiqueta ya publicada, por ejemplo
   `v0.1.0-rc.2`. Súbela con `git push origin v0.1.0-rc.2`.
6. En GitHub → Releases → Draft a new release, selecciona esa etiqueta, añade
   las notas y adjunta `.ankiaddon` y `.sha256`. Marca **pre-release** si sigue
   siendo una versión preliminar. Publica después de revisar los adjuntos.
7. Actualiza la ficha existente de AnkiWeb cuando corresponda; no crees una
   ficha nueva para cada versión.

Para pasar a `v0.1.0` estable, primero recoge experiencia de uso y corrige los
problemas encontrados. Hasta entonces, conserva la etiqueta de preliminar.
