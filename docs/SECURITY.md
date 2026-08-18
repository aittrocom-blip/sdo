# Guía de seguridad — Sol de Oro Hotel & Suites

> Este sitio es **100% estático** (HTML, CSS, JavaScript, imágenes). No hay backend, base de datos ni código del lado servidor. Esto reduce drásticamente la superficie de ataque, pero hay medidas importantes que deben aplicarse a nivel de **hosting** y **operación** que ningún archivo de código puede resolver por sí solo.

---

## ✅ Lo que YA está aplicado en el código

Estos archivos están listos en el proyecto:

| Archivo | Para qué hosting | Qué hace |
|---|---|---|
| `.htaccess` | Apache / LiteSpeed (cPanel, hosting compartido común) | Fuerza HTTPS, aplica headers de seguridad, bloquea acceso a archivos internos, desactiva listado de directorios. |
| `_headers` | Netlify, Cloudflare Pages, Vercel | Mismos headers de seguridad. |
| `web.config` | Microsoft IIS (Azure App Service) | Mismos headers + reglas IIS específicas. |
| `robots.txt` | Todos | Excluye paths administrativos del rastreo de buscadores. |
| Meta tags `<meta http-equiv>` | Todos los HTMLs | Fallback de CSP y otros headers si el servidor no los aplica. |

### Headers aplicados
- **Strict-Transport-Security** (HSTS) — fuerza HTTPS por 1 año.
- **X-Frame-Options: DENY** — evita que la web sea embebida en iframes de terceros (anti-clickjacking).
- **X-Content-Type-Options: nosniff** — evita ataques por MIME confusion.
- **Content-Security-Policy** — limita orígenes desde donde se pueden cargar scripts, estilos, imágenes y fuentes.
- **Referrer-Policy: strict-origin-when-cross-origin** — controla qué información se envía al navegar a otros sitios.
- **Permissions-Policy** — bloquea cámara, micrófono, USB y FLoC.
- **Cross-Origin-Opener-Policy / Cross-Origin-Resource-Policy** — aislamiento contra ataques tipo Spectre.
- **Eliminar `X-Powered-By` y `Server`** — no revela qué tecnología corre el servidor.

### Otras medidas en código
- Todos los `target="_blank"` tienen `rel="noopener noreferrer"`.
- No hay formularios que envíen datos a un backend (solo demos con `alert`).
- Pagos y reservas reales se delegan al motor externo `soldeoro.ihotelier.com` (responsabilidad de ese proveedor mantener PCI-DSS).

---

## ⚠️ Lo que DEBE configurar el cliente (hosting / operación)

Ningún archivo de código sustituye esto. **Sin estas medidas, el sitio sigue siendo vulnerable**:

### Crítico
1. **HTTPS / SSL certificate**
   - Activar SSL en el hosting (Let's Encrypt es gratuito en casi todos).
   - El `.htaccess` ya redirige HTTP → HTTPS, pero requiere certificado válido.

2. **Acceso al panel de hosting**
   - Contraseña fuerte (mínimo 16 caracteres, gestor de contraseñas).
   - **2FA (autenticación en 2 pasos)** en panel de hosting, cPanel, dominio y registrador.
   - Cuentas separadas para cada persona que tenga acceso (no compartir credenciales).

3. **Editor administrativo**
   - `editor-imagenes.html` permite editar el JSON de imágenes vía localStorage. **No es un riesgo de seguridad real porque guarda en el navegador del usuario, no en el servidor**. Aun así:
     - Si quieres ocultarlo del público: el `.htaccess` y `web.config` ya bloquean su acceso. Para habilitarlo en producción, restringe por IP en `.htaccess`.

4. **Backups automáticos**
   - Configurar respaldo diario/semanal del hosting.
   - Mantener al menos 4 semanas de retención.
   - Probar restauración al menos una vez.

### Recomendado
5. **WAF (Web Application Firewall)**
   - **Cloudflare** es gratuito y bloquea ataques comunes (SQL injection, XSS, bots maliciosos, DDoS).
   - Activar "Bot Fight Mode" en Cloudflare.
   - Configurar "Security Level: Medium" o "High".

6. **DNSSEC**
   - Activarlo en el registrador del dominio (Cloudflare, GoDaddy, etc.) para evitar secuestro DNS.

7. **Headers Reporting**
   - Activar reporte de CSP en `report-to` para detectar intentos de inyección.

8. **Monitoreo**
   - **UptimeRobot** (gratis) — alertas si la web cae.
   - **Google Search Console** — alertas si Google detecta malware.
   - **SecurityHeaders.com** — pegar la URL y verificar grado A+.

### Auditoría periódica
9. **Cada 6 meses:**
   - Revisar este `SECURITY.md`.
   - Verificar grado de seguridad en https://securityheaders.com y https://www.ssllabs.com/ssltest/.
   - Actualizar fechas de expiración del certificado SSL.

---

## 🚨 Lo que NO debe pasar nunca

- ❌ Subir archivos con extensiones `.md`, `.ps1`, `.py`, `.env` al servidor público.
- ❌ Compartir la carpeta `extraccion-web/` al público — es material interno.
- ❌ Compartir credenciales de hosting por email, WhatsApp o Slack.
- ❌ Dejar `editor-imagenes.html` accesible al público sin restricción de IP.
- ❌ Conectar el motor de reservas con credenciales hardcodeadas en el JS.

---

## ✅ Checklist antes de publicar a producción

- [ ] Hosting con HTTPS activo (Let's Encrypt o similar).
- [ ] `.htaccess` (Apache) o `_headers` (Netlify) o `web.config` (IIS) en el root.
- [ ] Probado en https://securityheaders.com → grado **A o A+**.
- [ ] Probado en https://www.ssllabs.com/ssltest/ → grado **A o A+**.
- [ ] Cloudflare configurado delante del dominio (recomendado).
- [ ] 2FA en panel de hosting + registrador.
- [ ] Backup automático configurado.
- [ ] `editor-imagenes.html` bloqueado o eliminado del público.
- [ ] Carpeta `extraccion-web/` y archivos `.md`, `.ps1`, `.py` no publicados.

---

## Contacto en caso de incidente

Si detectas comportamiento sospechoso (defacement, lentitud anormal, alertas de Google):

1. Cambiar contraseñas de hosting + 2FA.
2. Restaurar último backup conocido bueno.
3. Verificar logs del servidor para identificar punto de entrada.
4. Si la información de huéspedes pudo verse afectada, notificar a la ANPDP (Autoridad Nacional de Protección de Datos Personales) dentro de 72 horas según la Ley N.° 29733.

---

*Última actualización: 11 de mayo de 2026.*
