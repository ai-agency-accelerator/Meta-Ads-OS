# Token de usuario del sistema (modo avanzado de Meta)

Para quién: quien quiere que `herramientas/meta_ads.py` trabaje con su cuenta publicitaria (y `formularios_meta.py`,
`audiencias_meta.py` y `reglas_meta.py`, que usan el mismo token). Se hace una vez por portfolio, unos 15 minutos. Lo
guía `/conectar meta --avanzado`.

**Qué desbloquea** (y el MCP de Meta no hace):
- subir vídeos e imágenes;
- crear creatividades con **todas** las mejoras automáticas desactivadas, y comprobarlo después;
- montar un plan de campaña entero en pausa, sin duplicar nada si se corta;
- crear anuncios desde publicaciones que ya existen en Instagram o en la Página;
- crear formularios instantáneos y descargar sus leads (`formularios_meta.py`);
- leer sin nadie delante (brief diario, anuncios rechazados con `anuncios --estado`);
- comprobar el **tope diario total** de la ficha antes de activar o subir presupuesto.

**Cuándo no hace falta:** para leer, diagnosticar y hacer cambios sueltos con alguien delante basta el MCP oficial
(`/conectar meta`). Sin token, los vídeos se suben en Ads Manager.

«No verificado» quiere decir que no se ha podido comprobar en la documentación oficial el 2026-11-09: los nombres de los
menús de Business Settings cambian a menudo. Busca el equivalente en tu pantalla.

---

## 1. Quién es dueño de qué

Contexto: `meta-ads-kb/08-cuenta-politicas-seguridad/03-seguridad-business-portfolio-roles-partners.md` §2 y §4.

- **Tu propio negocio:** el usuario del sistema se crea en tu portfolio, el dueño de la cuenta publicitaria.
- **Agencia con clientes:** el cliente añade a tu agencia como **partner** y le comparte la cuenta publicitaria, la
  Página y el dataset con las tareas mínimas. Tú creas el usuario del sistema **en el portfolio de tu agencia** y le
  asignas esos activos. Así, al terminar con un cliente, basta con que te quite como partner. No pidas «añádeme con
  control total de tu portfolio».
- Los tokens de usuario del sistema **no caducan cuando una persona deja el equipo**. Por eso hay que revisarlos y
  revocarlos a mano (§5).

## 2. Crear el usuario del sistema

1. **Una app de Meta** de tipo Empresa, en el mismo portfolio: developers.facebook.com → Mis apps → Crear app. El token
   se genera «para» una app. Si ya tienes una del portfolio, vale esa.
2. **Business Settings → Usuarios → Usuarios del sistema → Añadir.** Nombre: `meta-ads-os`. Rol: **Empleado**, no
   administrador. Con empleado solo ve lo que le asignas.
3. **Asignar activos** (botón *Asignar activos*), con lo mínimo:
   - **Cuenta publicitaria:** gestionar campañas y ver el rendimiento. Para crear anuncios no hace falta el control
     total.
   - **Página:** crear anuncios (y ver contenido). Sin esto, `crear` falla al hacer la creatividad y
     `formularios_meta.py crear` no puede crear el formulario.
   - **Dataset (píxel):** usarlo, para leer los eventos y optimizar a ellos.
   - **Cuenta de Instagram**, si los anuncios salen con ella.
   - **La app** del paso 1.
   - **Acceso a clientes potenciales**, si vas a descargar leads de formularios instantáneos: Business Settings →
     Integraciones → *Acceso a clientes potenciales* (*Leads Access*) → la Página → asigna el usuario del sistema (o
     la app de tu CRM). Sin esto, `formularios_meta.py leads` devuelve un error de permisos aunque el token tenga
     `leads_retrieval`. El nombre del menú no está verificado.
4. **Generar token** (botón *Generar nuevo token*):
   - App: la del paso 1.
   - Caducidad: **Nunca**. Si tu política de seguridad prefiere rotar, 60 días, y apúntate cuándo renovarlo.
   - Permisos:
     - `ads_management` y `ads_read`: imprescindibles;
     - `business_management`: para listar los activos del portfolio;
     - `pages_show_list` y `pages_read_engagement`: para usar la Página en los anuncios;
     - `pages_manage_ads`: para crear formularios instantáneos (`formularios_meta.py crear`);
     - `leads_retrieval`: para descargar sus leads (`formularios_meta.py leads`), con el acceso del paso 3.

     Si la consola te pide otros para la Página o Instagram (por ejemplo, `instagram_basic` para usar publicaciones
     de Instagram como anuncio), añade solo esos. La lista exacta que exige cada llamada no está verificada.
   - **Cópialo en ese momento**: no se vuelve a enseñar.
5. Pégalo tú en `.env`, nunca en el chat:
   ```
   META_TOKEN_ACME=...        # por cliente (slug en mayúsculas, guion bajo)
   META_TOKEN=...             # o uno global, si un solo token ve todas tus cuentas
   META_TOKEN_PAGINA_ACME=... # opcional: token de la Página para formularios; si falta, se pide con META_TOKEN
   ```
   Si un cliente tiene su propio token, ese manda sobre el global.

**Nivel de acceso de la app.** Una app nueva puede gestionar las cuentas de su propio portfolio y las que le comparten
como partner. Para muchas cuentas de terceros, Meta puede pedir un nivel de acceso superior a la API de marketing, con
revisión de la app. Según una fuente secundaria, Meta renombró estos niveles en mayo de 2026. Ni lo uno ni lo otro está
verificado en la documentación oficial: si ves un error de permisos de la app (no del token), revisa
*Revisión de la app* en el panel de la app.

## 3. La clave secreta de la app (opcional)

Si en la configuración avanzada de la app está activado **«Exigir la clave secreta de la app»** (*Require App Secret*),
cada llamada tiene que ir firmada. Copia la clave secreta (App → Configuración → Básica) en `.env`:

```
META_APP_SECRET=...           # o META_APP_SECRET_ACME
```

`meta_ads.py` firma entonces cada llamada (`appsecret_proof`) sin enseñar nunca ni el token ni la clave. Si no está
activado, no la pongas: no hace falta.

## 4. Comprobar que funciona

```
python3 -I herramientas/meta_ads.py cuentas --cliente acme     # la cuenta de la ficha aparece marcada «← ficha»
python3 -I herramientas/meta_ads.py activos --cliente acme     # Página, Instagram, datasets y públicos
python3 -I herramientas/meta_ads.py vigente --cliente acme     # lo que puede gastar hoy la cuenta
```

- **Salida 2 y «Meta rechaza el token (caducado o revocado)»** (código 190 de Meta): el token está mal copiado,
  caducado o revocado. Genera otro.
- **Salida 2 y «Error de Meta (10/…)» o «(200/…)» hasta «(299/…)»:** falta un permiso en el token o un activo sin
  asignar al usuario del sistema.
- **`cuentas` no ve la cuenta:** no está asignada al usuario del sistema (§2, paso 3).
- **`activos` dice «límite de gasto de la cuenta: NINGUNO»:** ponle un límite de gasto a la cuenta en Ads Manager
  (Facturación). Es el freno de daños si alguien entra (`08-…/03-…` §3.8). Hazlo con `/configurar-meta`.

Después marca el modo avanzado como hecho (`/conectar` lo apunta en `contexto/instalacion.json`).

## 5. Seguridad

- **El token mueve dinero.** Está en `.env` (permisos 600, fuera de git). Las herramientas lo cargan solas y Claude no
  lo lee. Nunca lo pegues en el chat, en un issue ni en un flujo de n8n o Make que se exporte.
- **Todo lo que crea `meta_ads.py` nace en pausa.** Activar y subir presupuesto exigen `--confirmo` y respetan los
  topes de la ficha (`topes.cambio_dia` y `topes.total_dia`). Cada escritura queda en `logs/cambios.jsonl` y los hooks
  piden confirmación.
- **Límites de Meta:** por ejemplo, 4 cambios de presupuesto por conjunto y hora. Pasarse produce frenazos
  (*throttling*), no baneos documentados (`08-…/03-…` §4).
- **Revocar:** Business Settings → Usuarios del sistema → el usuario → *Revocar tokens*. Hazlo cuando acabes con un
  cliente, si el token se filtra (chat, captura, repositorio) o si sale del equipo alguien que lo tuvo.
- **Revisión mensual** (`08-…/03-…` §8): qué usuarios del sistema y apps existen y qué activos tiene cada uno.
- **Reglas del servidor MCP de anuncios** en Business Settings → Integraciones: siguen aplicando a la vía del MCP.
  Endurécelas al conectar (`08-…/03-…` §4).

## 6. Versión de la API

Las herramientas usan la **v27.0** de la Graph API desde el 2026-11-10 (Meta la publicó el 2026-11-04). Se adoptó tras
revisar su registro de cambios: para lo que hace el sistema no rompe nada, y trae tres cosas que las herramientas ya
tienen en cuenta:
- En Ventas, un conjunto que segmenta por dispositivo o sistema operativo deja que Meta entregue fuera de él. `crear`
  lo desactiva (`targeting_automation.individual_setting.device = 0`) salvo que el plan diga
  `"expansion_dispositivos": true`.
- El escaparate de productos (`product_extensions`) viene activado por defecto: `crear` lo apaga con
  `mejoras_automaticas: off` o `revisar`.
- La verificación del teléfono de los formularios instantáneos tiene un campo nuevo (`phone_otp_verification_type`).

Para volver a la v26.0 mientras siga viva (Meta no ha fijado su fin), `META_API_VERSION=v26.0` en `.env`, sin tocar
código. Con la v26.0, `formularios_meta.py` usa el campo antiguo de verificación y no admite el modo opcional.
