# 1. Montaje en GNS3

## Direccionamiento derivado de la matrícula

De `2024-2388` se toman `24`, `23` y `88`. Se utiliza el bloque privado 10.0.0.0/8: ADMIN `10.24.23.0/24` y CLIENTES `10.24.88.0/24`. Todas las direcciones son válidas y la relación con la matrícula es reproducible.

| Equipo | Interfaz | Dirección | Gateway |
|---|---|---|---|
| R1-AXEL | Fa0/0 | 10.24.23.1/24 | No requerido |
| R1-AXEL | Fa0/1 | 10.24.88.1/24 | No requerido |
| Kali ADMIN | Adaptador del laboratorio | 10.24.23.10/24 | 10.24.23.1 |
| VPCS CLIENTE | eth0 | 10.24.88.20/24 | 10.24.88.1 |

## Crear y conectar

**En el equipo de Axel, el montaje y el hardening ya están realizados.** Para utilizarlo, consultar [uso instalado](06-uso-instalado.md). Los pasos siguientes sirven para reproducir el diseño desde cero; no volver a pegar el bootstrap sobre el router ya endurecido.

1. Crear proyecto `Axel-2024-2388-CIS-IOS12`.
2. Arrastrar un **c2691**, dos **Ethernet switch**, **Kali Linux** y **VPCS**.
3. Renombrar: `R1-AXEL`, `SW-ADMIN`, `SW-CLIENTES`, `KALI-ADMIN`, `PC-CLIENTE`.
4. Kali → SW-ADMIN → R1 FastEthernet0/0. R1 FastEthernet0/1 → SW-CLIENTES → VPCS.
5. Iniciar los nodos. Ajustar Idle-PC del router si el consumo de CPU es excesivo.
6. Abrir consola de R1, rechazar el asistente inicial y ejecutar `show version`. Guardar captura con IOS 12.4 visible.
7. Adaptar y pegar `configs/bootstrap-R1.txt`. Crear claves RSA de 2048 bits usando los pasos indicados allí. Guardar la configuración inicial.

Los switches integrados de GNS3 son conectores del laboratorio, no dispositivos IOS auditados. El activo analizado es R1. No se necesitan imágenes adicionales ni se distribuyen imágenes Cisco.

## Kali

Instalar Python, venv, Nmap y Netmiko mientras Kali tenga Internet (por ejemplo, temporalmente usando NAT en otra interfaz). No conectar el router de práctica a Internet.

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nmap git
ip -br link
```

Identificar el adaptador conectado al switch (ejemplo `eth0`). Configurarlo en NetworkManager con `10.24.23.10/24`, gateway `10.24.23.1`, o usar temporalmente:

```bash
sudo ip address add 10.24.23.10/24 dev eth0
sudo ip link set eth0 up
sudo ip route replace 10.24.88.0/24 via 10.24.23.1 dev eth0
ping -c 3 10.24.23.1
```

No duplicar una dirección si NetworkManager ya la asignó. Clonar el repositorio y preparar el entorno según el README.

## VPCS

```text
ip 10.24.88.20/24 10.24.88.1
save
ping 10.24.23.10
```

## Comprobar acceso

Desde Kali, probar SSH a `axel@10.24.23.1` y después `enable`. IOS 12.4 puede necesitar negociación heredada. Si OpenSSH la rechaza, habilitar únicamente el algoritmo que indique el error, para este host. Ejemplo según los algoritmos anunciados:

```bash
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1 -oHostKeyAlgorithms=+ssh-rsa -c aes128-cbc axel@10.24.23.1
```

No modificar globalmente `/etc/ssh/ssh_config`. Netmiko/Paramiko negocia de forma independiente; un fallo de conexión se informa como error, no como incumplimiento CIS. Mantener la consola de GNS3 abierta durante la primera aplicación.

**Compatibilidad comprobada:** Paramiko 5 retiró los intercambios SHA-1 que ofrece esta imagen IOS 12.4 y devolvió `no acceptable kex algorithm` en la primera conexión real. `requirements.txt` fija Paramiko 3.5.x dentro del entorno virtual del laboratorio. Esto permite administrar la imagen histórica; SSHv2 no elimina sus limitaciones criptográficas.

Capturar la topología real y guardarla como `docs/evidencias/01-topologia.png`. Exportar el proyecto portable sin imágenes ni secretos si se desea incluirlo.
