# 3. Operación del script

## Preparación

Desde Kali, en la carpeta del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`inventory.json` contiene los routers autorizados; agregar entradas permite recorrer varios equipos con las mismas credenciales. Se consultan equipos conocidos, no se hace descubrimiento de toda la subred.

## Auditoría sin cambios

```bash
python scripts/cis_ios.py audit --inventory inventory.json
```

Solicita usuario, contraseña y secreto de enable. Ejecuta comandos `show`, genera informe y exporta el running-config. Netmiko ajusta parámetros de la sesión de terminal, pero no entra en configuración ni guarda cambios en este modo.

## Aplicar e informar

```bash
python scripts/cis_ios.py apply --inventory inventory.json
```

Secuencia: versión → respaldo original → evaluación previa → comandos de corrección → lectura nueva del dispositivo → informe posterior → comprobación de una conexión SSH nueva con enable → guardar startup-config solo si todos los controles pasan y la reconexión funciona.

Si un comando falla, puede haber cambios parciales: se intenta igualmente leer el estado posterior y se registra el error. No existe rollback automático. Se conserva la consola para recuperación. La salida es `0` si todos los equipos cumplen y no hubo errores, `1` ante fallos/UNKNOWN/errores y `2` ante argumentos o inventario inválidos.

## Archivos generados

| Ruta | Contenido |
|---|---|
| `reports/<UTC>/report.json` | Antes/después, comandos planificados, errores y guardado por equipo |
| `reports/<UTC>/report.md` | Resumen legible |
| `configs/running/<UTC>-<equipo>-before.cfg` | Running-config real sanitizado previo |
| `configs/running/<UTC>-<equipo>-after.cfg` | Running-config real sanitizado posterior, en apply |
| `private/<UTC>/` | Respaldo original previo y salida `show version`, no publicables automáticamente |

La sanitización elimina líneas de credenciales y bloques de certificados. Revisar además manualmente cada configuración antes de publicar: no es un detector universal de secretos. El archivo original se conserva localmente para recuperar. Los informes no incluyen contraseñas ni transcripciones completas de configuración.

## Recuperación por consola

Si se pierde SSH, entrar por consola GNS3. Revisar `show ip ssh`, direcciones y líneas VTY. Para recuperar acceso seguro:

```text
enable
configure terminal
ip ssh version 2
line vty 0 4
login local
transport input ssh
end
```

Revisar rangos VTY adicionales. Como el script no guarda si la evaluación/reconexión falla, se puede volver a la configuración inicial con `reload` y responder **no** a guardar, únicamente si startup-config sigue siendo la base deseada. Si ya se guardó otra configuración, restaurar desde el respaldo original por consola o mediante un snapshot previo; no pegar un archivo sanitizado para recuperar credenciales.
