# 6. Usar el laboratorio ya instalado

## Abrir

1. Encender GNS3 VM en VMware.
2. En GNS3 abrir `C:\Users\axele\GNS3\projects\1fce01ae-aa13-4e79-baad-6a8b77da2a8e\A4-CIS-2024-2388.gns3`.
3. Iniciar los nodos desde GNS3. Kali usa la VM existente; la clonación enlazada está desactivada.
4. Iniciar sesión normalmente en Kali. El perfil `A4-ADMIN-20242388` configura `eth0` como `10.24.23.10/24` y la ruta a `10.24.88.0/24` vía `10.24.23.1`. Su prioridad de autoconexión es 100.

Si Kali no recibe la dirección del laboratorio:

```bash
sudo nmcli connection up A4-ADMIN-20242388
ip -br address
ping -c 3 10.24.23.1
```

No se necesita la interfaz NAT `eth1` para demostrar el laboratorio. Se utilizó temporalmente para instalar dependencias.

### Kali abierta en VMware, pero detenida en GNS3

Si GNS3 muestra `KALI-ADMIN` detenido aunque su escritorio esté abierto, y al iniciarlo aparece `The VM is already running in VMware`, la máquina está fuera del ciclo de arranque de GNS3. La IP puede ser correcta y aun así no existir la conexión al switch del laboratorio.

Guardar el trabajo de Kali y apagarla normalmente con `sudo poweroff`. Cuando termine de apagarse, hacer clic derecho en `KALI-ADMIN` dentro de GNS3 y seleccionar **Start**. No volver a encenderla directamente desde VMware. Iniciar sesión de nuevo y comprobar:

```bash
ping -c 3 10.24.23.1
nmap -sT -Pn -p 22,23 10.24.23.1
```

El ping debe responder, TCP 22 debe estar abierto y TCP 23 cerrado. Solo después iniciar `probar_timeout.py`. Un error `NoValidConnectionsError` significa que la sesión SSH no se estableció; no demuestra el cierre por inactividad.

## Auditar y mostrar

```bash
cd /home/axel/A4-CIS-2024-2388
source .venv/bin/activate
python scripts/cis_ios.py audit --inventory inventory.json
nmap -sT -Pn -p 22,23 10.24.23.1
ping -c 5 10.24.88.20
```

El usuario del router es `axel`. Las contraseñas del laboratorio están en `private/lab-credentials.json`, tanto en la carpeta local de Windows como dentro de Kali. No están publicadas y no deben mostrarse durante el video. El script interactivo solicita contraseña SSH y secreto de enable.

Para aplicar únicamente correcciones necesarias:

```bash
python scripts/cis_ios.py apply --inventory inventory.json
```

El router ya está endurecido: es normal que esta ejecución no planifique comandos. Para mostrar el estado anterior, usar el informe histórico, identificándolo como evidencia guardada:

```bash
python scripts/mostrar_resultados.py audit
python scripts/mostrar_resultados.py apply
```

## Qué guardar para la entrega

El repositorio contiene los scripts, informes reales, running-configs sanitizados, documentación y captura de GNS3. Falta la demostración personal en YouTube, con cara, voz y hora/fecha, y colocar su URL al principio del README y en `AxelEnriqueVasquezPena_20242388_A4.txt`.

## Scripts auxiliares

- `crear_topologia.py`, `gns3_local.py`, `rotular_topologia.py`: construcción y gestión de GNS3.
- `preparar_equipos.py`: bootstrap inicial; rechaza sobrescribir un router ya direccionado.
- `kali_guest.py`, `desplegar_kali.py`, `preparar_kali.py`, `activar_red_kali.py`: despliegue mediante VMware Tools y configuración de Kali.
- `demostrar_kali.py`, `ejecutar_fase.py`, `exportar_resultados.py`: ejecución y recuperación de pruebas reales.
- `consola_evidencias.py`, `probar_autenticacion.py`, `probar_timeout.py`, `probar_consola_timeout.py`: verificaciones de funcionamiento.
- `capturar_ventana.ps1`, `capturar_kali.py`, `mostrar_resultados.py`: captura y presentación; las capturas fallidas no se incluyen como evidencia.

Los auxiliares de Windows requieren los archivos privados de credenciales ya creados. El auditor principal no los requiere: permite introducir las credenciales de forma interactiva.
