# 4. Plan de pruebas y evidencia real

**Estado inicial de todas las pruebas de red: PENDIENTE.** Completar resultados observados y enlaces tras ejecutar; los resultados esperados no son evidencia.

Antes de comenzar, registrar `date -Is` en Kali y `show clock` / `show version` en R1. Ajustar la fecha si es incorrecta y mantenerla visible al grabar.

| Prueba | Procedimiento | Resultado esperado | Observado / evidencia |
|---|---|---|---|
| Enrutamiento previo | Kali: `ping -c 3 10.24.88.20` | Respuesta del cliente | PENDIENTE |
| Superficie previa | Kali: `nmap -sT -Pn -p 22,23 10.24.23.1` | SSH y Telnet abiertos en la base | PENDIENTE |
| Auditoría | Ejecutar modo audit; comparar `show running-config` antes/después | Informe, sin cambios persistentes | PENDIENTE |
| Aplicación | Ejecutar modo apply | Informe before/after, correcciones y guardado | PENDIENTE |
| Telnet posterior | Repetir Nmap | 23 cerrado; 22 abierto | PENDIENTE |
| SSH funcional | Nueva conexión SSH y `enable` | Acceso autorizado conservado | PENDIENTE |
| Inactividad VTY | Mantener sesión SSH sin pulsar teclas >5 minutos, keepalive de cliente desactivado | Sesión cerrada; registrar tiempo real | PENDIENTE |
| Inactividad consola | Dejar EXEC de consola inactivo >5 minutos | Regreso a estado de inicio de sesión | PENDIENTE |
| Reintentos SSH | Nueva sesión, introducir claves erróneas; registrar comportamiento | Desconexión según límite efectivo del servidor | PENDIENTE |
| AUX y CDP | `show running-config`, `show cdp` | AUX no exec, CDP desactivado | PENDIENTE |
| Keepalives | `show running-config` | Ambos comandos configurados | PENDIENTE |
| Enrutamiento posterior | Repetir ping al cliente | Sigue funcionando | PENDIENTE |
| Persistencia | `show startup-config`; reinicio controlado y nueva auditoría | Controles conservados | PENDIENTE |
| Idempotencia | Ejecutar apply otra vez | Sin comandos correctivos; PASS | PENDIENTE |

Guardar salidas Nmap con `-oN docs/evidencias/nmap-antes.txt` y `-oN docs/evidencias/nmap-despues.txt`. Para imágenes: topología, versión, informe previo, informe posterior, Nmap, SSH y enrutamiento. Añadirlas a esta página usando `![Descripción](evidencias/archivo.png)`.

Las pruebas unitarias del repositorio usan datos sintéticos y verifican el software, no el dispositivo. El informe calcula cumplimiento solo sobre los diez controles seleccionados. Adjuntar las capturas y los archivos generados de la ejecución real para demostrar los requisitos.
