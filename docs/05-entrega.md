# 5. Video y entrega

## Guion de máximo 10 minutos

| Tiempo | Demostración |
|---|---|
| 00:00–00:35 | Cara y voz, nombre/matrícula, fecha y hora visibles |
| 00:35–01:20 | Topología real, direccionamiento y propósito |
| 01:20–02:10 | Ping y Nmap previo; Telnet disponible |
| 02:10–03:10 | Auditoría sin cambios y sus hallazgos |
| 03:10–04:30 | Aplicar hardening; abrir informe posterior |
| 04:30–05:40 | Nmap posterior, nueva sesión SSH, ping conservado |
| 05:40–07:00 | `show ip ssh`, VTY, AUX, CDP y keepalives |
| 07:00–08:20 | Evidencia de timeout ya capturada y segunda auditoría |
| 08:20–09:20 | Running-configs, controles y documentación en GitHub |
| 09:20–09:50 | Conclusión basada en resultados reales |

Grabar con OBS o herramienta equivalente, cámara y micrófono habilitados. No hace falta esperar cinco minutos en vivo: realizar antes la prueba de inactividad, mostrar su evidencia y explicar qué se observó. No presentar una ejecución grabada como si fuera una ejecución distinta.

Subir a YouTube, comprobar acceso desde una ventana sin sesión y colocar el enlace al principio del README. Cada infraestructura adicional necesitaría su propio repositorio y video; esta propuesta contiene una sola infraestructura.

## TXT obligatorio

Práctica confirmada: **A4**. Archivo creado en la raíz del repositorio:

`AxelEnriqueVasquezPena_20242388_A4.txt`

Se normalizan espacios, ñ y guion de matrícula para seguir el ejemplo de la consigna. Confirmar si el docente exige conservar el guion; en ese caso usar `2024-2388`.

Contenido:

```text
Nombre: Axel Enrique Vasquez Peña
Matrícula: 2024-2388
Práctica: A4
Repositorio: https://github.com/axelenriquevasquezpena-max/cis-c2691-2024-2388
Video: REEMPLAZAR_POR_ENLACE_YOUTUBE
```

## Antes de entregar

- Completar todas las evidencias de red y resultados observados.
- Subir informes y running-configs sanitizados reales.
- Incluir capturas dentro de la documentación, además del diagrama SVG.
- Verificar que no se publican claves ni imágenes Cisco.
- Añadir YouTube al README y al TXT; comprobar duración y cara/voz/fecha/hora.
- Sustituir el estado pendiente del README solo cuando corresponda.
- Subir cambios con `git add`, `git commit` y `git push`.
