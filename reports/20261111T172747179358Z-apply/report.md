# Informe de ejecución

UTC: 2026-11-11T17:27:47.179358+00:00
Modo: apply

Alcance: 10 controles CIS IOS 12 v4.0.0 seleccionados.

## R1-AXEL — 10.24.23.1

Startup guardado: True

### before

| CIS | Control | Estado |
|---|---|---|
| 1.2.2 | Solo SSH en todas las VTY | FAIL |
| 1.2.3 | AUX sin EXEC | FAIL |
| 1.2.7 | Timeout consola <= 10 minutos | FAIL |
| 1.2.9 | Timeout VTY <= 10 minutos | FAIL |
| 2.1.1.1.4 | SSH autenticacion <= 60 segundos | FAIL |
| 2.1.1.1.5 | SSH reintentos <= 3 | FAIL |
| 2.1.1.2 | Solo SSHv2 | FAIL |
| 2.1.2 | CDP desactivado | FAIL |
| 2.1.6 | TCP keepalives entrantes | FAIL |
| 2.1.7 | TCP keepalives salientes | FAIL |

### after

| CIS | Control | Estado |
|---|---|---|
| 1.2.2 | Solo SSH en todas las VTY | PASS |
| 1.2.3 | AUX sin EXEC | PASS |
| 1.2.7 | Timeout consola <= 10 minutos | PASS |
| 1.2.9 | Timeout VTY <= 10 minutos | PASS |
| 2.1.1.1.4 | SSH autenticacion <= 60 segundos | PASS |
| 2.1.1.1.5 | SSH reintentos <= 3 | PASS |
| 2.1.1.2 | Solo SSHv2 | PASS |
| 2.1.2 | CDP desactivado | PASS |
| 2.1.6 | TCP keepalives entrantes | PASS |
| 2.1.7 | TCP keepalives salientes | PASS |
