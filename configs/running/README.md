# Running-configs reales

Esta carpeta contiene running-configs reales de las ejecuciones de auditoría, aplicación, idempotencia y reinicio, además de exportaciones de startup-config. Las credenciales se sustituyen por comentarios de omisión; los originales restaurables quedan en `private/` fuera de Git.

- `20261111T172747179358Z-apply-R1-AXEL-before.cfg`: configuración anterior al hardening.
- `20261111T172747179358Z-apply-R1-AXEL-after.cfg`: configuración posterior.
- `after-startup-real-sanitizado.cfg`: configuración guardada en NVRAM.
- `20261112T043152058666Z-restart-R1-AXEL-before.cfg`: configuración obtenida tras el reinicio.

`../bootstrap-R1.txt` sigue siendo una plantilla, no evidencia. El prefijo `before` en un archivo de auditoría indica la lectura de esa ejecución; no implica necesariamente un router sin hardening.
