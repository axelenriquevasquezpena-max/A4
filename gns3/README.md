# Proyecto de GNS3 A4

## Abrir en el equipo de Axel

En GNS3 seleccionar **File → Open project** y abrir:

```text
C:\Users\axele\GNS3\projects\1fce01ae-aa13-4e79-baad-6a8b77da2a8e\A4-CIS-2024-2388.gns3
```

Ese es el proyecto de trabajo. El archivo `.gns3` de esta carpeta es una copia de su topología para el repositorio, no un paquete portable con máquinas virtuales.

## Qué está creado

- R1-AXEL: Cisco c2691 en GNS3 VM, imagen IOS 12.4 instalada.
- KALI-ADMIN: plantilla VMware Kali Linux, configurada para usar un clon enlazado.
- SW-ADMIN y SW-CLIENTES: switches Ethernet integrados.
- PC-CLIENTE: VPCS local.
- Cuatro enlaces: Kali → switch ADMIN → router → switch CLIENTES → VPCS.
- Rótulo con matrícula, direccionamiento y objetivo del laboratorio.

Se comprobó la existencia de los cinco nodos y cuatro enlaces mediante la API del servidor. **Todavía no se han configurado ni probado los sistemas invitados.** Las direcciones mostradas en el rótulo son el plan, no direcciones ya aplicadas.

## Continuar

1. Tener encendida y conectada la GNS3 VM.
2. Abrir el proyecto e iniciar los nodos. El primer arranque de Kali puede crear su clon enlazado.
3. Abrir consola de R1 y aplicar la plantilla `configs/bootstrap-R1.txt` siguiendo `docs/01-montaje.md`; elegir las contraseñas y generar claves RSA.
4. Configurar las IP de Kali y VPCS según esa guía.
5. Desde Kali ejecutar la auditoría y después la aplicación del hardening.
6. Capturar pruebas, subir los informes y running-configs sanitizados y grabar el video.

## Reproducir la creación

`python scripts/crear_topologia.py` utiliza la API local de GNS3 2.2 y sus credenciales ya configuradas en Windows, sin publicarlas. Requiere las plantillas `c2691` y `Kali Linux`. Reutiliza el proyecto de A4 por nombre y los nodos/enlaces existentes; no inicia ni configura los invitados.

La copia `.gns3` depende de la imagen Cisco, de GNS3 VM y de la ruta local de Kali (`C:\Virtual Machines\Kali Linux\Kali Linux.vmx`). En otro equipo se deben adaptar esas dependencias o reconstruir el proyecto usando las propias plantillas. No se incluyen discos VMware ni imágenes Cisco en GitHub.
