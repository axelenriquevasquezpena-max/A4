# Informes

Informes reales generados por `scripts/cis_ios.py`, invocado desde Kali por `scripts/demostrar_kali.py`:

| Ejecución UTC | Resultado |
|---|---|
| [11 noviembre 17:27:00 — audit](20261111T172700822966Z-audit/report.md) | Diez FAIL; sin cambios |
| [11 noviembre 17:27:47 — apply](20261111T172747179358Z-apply/report.md) | Diez PASS; reconexión SSH y guardado |
| [11 noviembre 17:28:35 — idempotencia](20261111T172835133963Z-idempotence/report.md) | Diez PASS; cero comandos correctivos |
| [12 noviembre 04:29:52 — primer intento tras reinicio](20261112T042952760586Z-restart/report.md) | Error de conectividad: Kali seleccionó el perfil DHCP anterior |
| [12 noviembre 04:31:52 — tras activar perfil A4](20261112T043152058666Z-restart/report.md) | Diez PASS; persistencia confirmada |

El fallo de conectividad se conserva como parte del registro. Se corrigió dando prioridad de autoconexión al perfil estático A4. No se presenta el error como incumplimiento ni como aprobación de controles.
