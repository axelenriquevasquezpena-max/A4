# Proyecto de GNS3 A4



Ese es el proyecto de trabajo. El archivo `.gns3` de esta carpeta es una copia de su topología para el repositorio, no un paquete portable con máquinas virtuales.

## Qué está creado

- R1-AXEL: Cisco c2691 en GNS3 VM, imagen IOS 12.4 instalada.
- KALI-ADMIN: máquina VMware Kali Linux existente, sin clonación enlazada.
- SW-ADMIN y SW-CLIENTES: switches Ethernet integrados.
- PC-CLIENTE: VPCS local.
- Cuatro enlaces: Kali → switch ADMIN → router → switch CLIENTES → VPCS.
- Rótulo con matrícula, direccionamiento y objetivo del laboratorio.

Los cinco nodos y cuatro enlaces están creados. Router, Kali y VPCS están configurados con las direcciones del diseño. Se ejecutaron auditoría, hardening, Nmap y ping desde Kali; los diez controles pasan y persisten tras reiniciar el router. Véase `docs/04-pruebas.md`.

## Continuar

1. Tener encendida y conectada la GNS3 VM.
2. Abrir el proyecto e iniciar los nodos. Kali usa la máquina existente; no encenderla simultáneamente desde otro proyecto de GNS3.
3. En esta instalación, las IP, las claves RSA y el hardening ya están guardados. No volver a pegar el bootstrap sobre el router configurado.
4. En Kali, usar `/home/axel/A4-CIS-2024-2388`, siguiendo `docs/06-uso-instalado.md`.
5. Ejecutar una auditoría para comprobar el estado actual y grabar la demostración personal.

### Error de clonación corregido

El 12 de noviembre se corrigió `linked_clone: true` a `false`: VMware rechazaba crear un clon porque la Kali original estaba encendida. El proyecto usa ahora esa máquina existente. Se verificó la apertura del proyecto y el arranque de `KALI-ADMIN` después de la corrección. La plantilla de creación también se corrigió.

## Reproducir la creación

`python scripts/crear_topologia.py` utiliza la API local de GNS3 2.2 y sus credenciales ya configuradas en Windows, sin publicarlas. Requiere las plantillas `c2691` y `Kali Linux`. Reutiliza el proyecto de A4 por nombre y los nodos/enlaces existentes; no inicia ni configura los invitados.

La copia `.gns3` depende de la imagen Cisco, de GNS3 VM y de la ruta local de Kali (`C:\Virtual Machines\Kali Linux\Kali Linux.vmx`). En otro equipo se deben adaptar esas dependencias o reconstruir el proyecto usando las propias plantillas. No se incluyen discos VMware ni imágenes Cisco en GitHub.
