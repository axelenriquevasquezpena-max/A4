# 2. Controles CIS seleccionados

**Referencia:** CIS Cisco IOS 12 Benchmark, v4.0.0, 29 de enero de 2016, nivel 1. Es un benchmark archivado y específico de IOS 12; no se utiliza el de IOS XE ni el de IOS 17.

Fuentes consultadas:
- [Catálogo oficial CIS Cisco](https://www.cisecurity.org/benchmark/cisco) y su acceso a versiones archivadas.
- [NIST NCP checklist 1127: IOS 12 v4.0.0](https://ncp.nist.gov/checklist/1127).
- [Índice de auditoría Tenable IOS 12 nivel 1](https://www.tenable.com/audits/CIS_Cisco_IOS_12_v4.0.0_Level_1).

| ID CIS | Recomendación aplicada | Motivo | Validación |
|---|---|---|---|
| 1.2.2 | `transport input ssh` en todas las VTY | Evitar administración Telnet sin cifrado | Config y Nmap TCP 23; SSH debe seguir funcionando |
| 1.2.3 | `no exec` en AUX | Impedir shell por puerto auxiliar no utilizado | Bloque `line aux 0` |
| 1.2.7 | `exec-timeout 5 0` en consola | Cerrar sesiones abandonadas | Config y prueba de inactividad |
| 1.2.9 | `exec-timeout 5 0` en todas las VTY | Limitar exposición de sesiones remotas | Config y SSH inactivo durante cinco minutos |
| 2.1.1.1.4 | `ip ssh time-out 60` | Limitar espera durante autenticación incompleta | `show ip ssh`: timeout entre 1 y 60 segundos |
| 2.1.1.1.5 | `ip ssh authentication-retries 2` | Limitar intentos por conexión | `show ip ssh`: entre 1 y 3 intentos; prueba manual |
| 2.1.1.2 | `ip ssh version 2` | Desactivar compatibilidad con SSHv1 | Config y estado efectivo SSH 2.0 |
| 2.1.2 | `no cdp run` | Evitar divulgar información de infraestructura por CDP | Config y `show cdp` |
| 2.1.6 | `service tcp-keepalives-in` | Detectar conexiones TCP entrantes abandonadas | Running-config |
| 2.1.7 | `service tcp-keepalives-out` | Detectar conexiones TCP salientes abandonadas | Running-config |

## Criterios del auditor

- Examina **cada bloque VTY**, incluyendo rangos adicionales a 0–4.
- Para `exec-timeout`, acepta de 1 a 600 segundos. Si no se imprime el comando, reconoce el valor predeterminado de IOS 12: 10 minutos. `0 0` falla.
- Verifica SSHv2 tanto en configuración como en `show ip ssh`. Timeout y reintentos se leen del estado operativo porque IOS puede omitir valores predeterminados del running-config.
- Si falta información necesaria, devuelve `UNKNOWN` y no presume cumplimiento. Un error de conexión no equivale a `PASS`.
- Solo aplica correcciones a controles `FAIL`. Si existen `UNKNOWN`, detiene la aplicación de ese dispositivo para revisar manualmente.
- Rechaza aplicar sobre versiones que no se identifiquen como IOS 12. No configura AAA, ACL, contraseñas, direccionamiento ni claves RSA: son prerrequisitos o controles fuera del alcance elegido.

## Límites

Estos controles protegen la administración; **no aíslan las dos LAN ni restringen SSH por IP de origen**. El enrutamiento entre ellas sigue permitido. Limitar reintentos por sesión no equivale a un bloqueo global contra fuerza bruta. Keepalives no establecen un tiempo exacto de cierre. No se declara cumplimiento íntegro de CIS ni se presentan comandos sin ejecutar como resultados.
