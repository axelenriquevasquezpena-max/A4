# Guion A4 — Demostración de seguridad de la topología

**Axel Enrique Vasquez Peña · 2024-2388**

**Duración prevista: 7–8 minutos. Límite: 10 minutos.** Cada bloque contiene una acción sobre el laboratorio y una frase breve que explica el resultado observado.

## Preparación fuera de la grabación

- Abrir `A4-CIS-2024-2388` e iniciar los cinco nodos.
- En Kali, comprobar que el perfil `A4-ADMIN-20242388` está activo y que VPCS tiene `10.24.88.20/24`.
- Preparar **tres terminales** de Kali: A para la medición de inactividad, B para las pruebas y C para la auditoría.
- En A y C ejecutar:

  ```bash
  cd /home/axel/A4-CIS-2024-2388
  source .venv/bin/activate
  ```

- Tener disponibles la contraseña SSH y el secreto de enable del router. Se encuentran en `private/lab-credentials.json`; consultarlos antes de grabar y cerrar ese archivo.
- Probar previamente el comando SSH del bloque 4 y aceptar la huella del router después de verificar que se está conectando al equipo del laboratorio.
- Preparar OBS con pantalla y cámara visibles; comprobar que se escucha la voz. Aumentar el tamaño de letra de las terminales.
- Comprobar la fecha y hora de Kali. Las marcas de tiempo del video deben corresponder al momento real de grabación.

## 1. 00:00–00:40 — Objetivo y topología real

**Pantalla:** GNS3 con los equipos encendidos; después, terminal B:

```bash
date '+%Y-%m-%d %H:%M:%S %Z'
```

**Decir:**

> «Soy Axel Enrique Vasquez Peña, matrícula 2024-2388. Esta es la demostración de la práctica A4; en pantalla se ve la fecha y hora actual. El objetivo es proteger la administración del router: permitir SSH versión 2, bloquear Telnet y limitar las sesiones, manteniendo la comunicación entre las dos redes.»

Señalar Kali, R1 y VPCS en GNS3:

> «Desde Kali, 10.24.23.10, comprobaré el router 10.24.23.1 y la comunicación con el cliente 10.24.88.20.»

## 2. 00:40–01:05 — Iniciar la prueba real de inactividad

**Terminal A:**

```bash
date '+Inicio de prueba: %Y-%m-%d %H:%M:%S %Z'
python -u scripts/probar_timeout.py
```

**Decir:**

> «Inicio una conexión SSH autenticada que permanecerá inactiva, sin enviar keepalives. El router está configurado para cerrarla a los cinco minutos. Mientras transcurre ese tiempo, haré las otras pruebas.»

Dejar el proceso ejecutándose. Es normal que todavía no imprima el resultado. **No interrumpirlo ni reiniciar los equipos.** El script abre su propia conexión; trabajar en otras terminales no reinicia su temporizador.

## 3. 01:05–02:20 — Comunicación conservada y Telnet bloqueado

**Terminal B:**

```bash
ping -c 5 10.24.88.20
nmap -sT -Pn -p 22,23 10.24.23.1
```

**Decir, según lo que aparezca:**

> «El cliente de la otra red responde al ping: el enrutamiento sigue funcionando con el hardening aplicado.»

Señalar las filas de Nmap:

> «El puerto 22 está abierto para SSH. El puerto 23 está cerrado: Telnet ya no está disponible en el router.»

Leer el número real de respuestas del ping. Si se pierde algún paquete, indicarlo; no afirmar cero pérdida si la salida muestra otra cosa.

## 4. 02:20–04:00 — Acceso autorizado y controles efectivos

**Terminal B:** conectarse realmente al router:

```bash
ssh -oKexAlgorithms=+diffie-hellman-group14-sha1,diffie-hellman-group1-sha1 -oHostKeyAlgorithms=+ssh-rsa -oCiphers=+aes128-cbc axel@10.24.23.1
```

Estas opciones son específicas de la imagen IOS 12.4 del laboratorio. Introducir la contraseña cuando se solicite; no se muestra al escribirla.

En IOS:

```text
enable
show ip ssh
show running-config | section line
show cdp
show running-config | include ^service tcp-keepalives
```

Introducir el secreto de enable en su solicitud. Mostrar solo estas salidas filtradas.

**Decir mientras se observan los resultados:**

> «La conexión SSH con el usuario autorizado funciona. El router confirma SSH versión 2, sesenta segundos para completar la autenticación y dos intentos de contraseña por conexión.»

> «Las líneas VTY aceptan únicamente SSH y tienen cinco minutos de inactividad máxima. La consola también tiene ese límite. El puerto auxiliar tiene EXEC desactivado.»

> «CDP está desactivado y ambos keepalives TCP están configurados.»

Salir de esta conexión:

```text
exit
```

Esta es una conexión distinta de la medición de inactividad que sigue ejecutándose en A.

## 5. 04:00–05:45 — Auditoría actual del router

**Terminal C**, con el entorno virtual preparado:

```bash
python scripts/cis_ios.py audit --inventory inventory.json
```

Introducir usuario `axel`, contraseña SSH y secreto de enable. La herramienta imprime al terminar la ruta del nuevo `report.md`. Abrir ese archivo usando **la ruta que acaba de devolver**, por ejemplo:

```bash
cat reports/FECHA_Y_HORA_DE_ESTA_EJECUCION/report.md
```

`FECHA_Y_HORA_DE_ESTA_EJECUCION` es un marcador para sustituir, no una carpeta literal.

**Decir solo si el informe lo confirma:**

> «Esta auditoría acaba de consultar el router sin aplicar cambios. Los diez controles CIS seleccionados aparecen en PASS. El resultado corresponde a este equipo en ejecución.»

No hace falta explicar el código ni recorrer archivos: señalar la tabla de resultados y continuar.

## 6. 05:45–06:45 — Verificar el cierre por inactividad

Volver a **terminal A**. Si el proceso aún no termina, continuar hasta que devuelva el resultado. Deben haber pasado cinco minutos desde su inicio, no desde el comienzo del video.

Mostrar estos campos de la salida JSON:

```text
"configured_timeout_seconds": 300
"keepalive": false
"closed_by_server": true
"elapsed_wall_seconds": ...
```

**Decir usando el tiempo real mostrado:**

> «El servidor cerró la sesión que permaneció inactiva. La medición fue de [leer el valor] segundos, aproximadamente los cinco minutos configurados. Así se limita el tiempo durante el cual una sesión abandonada queda disponible.»

La ejecución previa del repositorio midió 300,59 segundos; **en el video leer el valor de la ejecución que se está mostrando**, que puede variar ligeramente.

## 7. 06:45–07:30 — Comprobación final y cierre

**Terminal B:**

```bash
ping -c 3 10.24.88.20
date '+Fin de demostracion: %Y-%m-%d %H:%M:%S %Z'
```

**Decir según los resultados observados:**

> «La comunicación con el cliente continúa operativa. He demostrado que Telnet está bloqueado, que la administración autorizada funciona por SSH versión 2, que los controles seleccionados están aplicados y que una sesión inactiva se cierra automáticamente. Con esto se cumple el objetivo de proteger la administración sin impedir el enrutamiento entre las redes.»

Terminar la grabación con cara y voz presentes.

## Control del tiempo y de la demostración

- Reservar hasta un minuto adicional para introducir contraseñas o cambiar de ventana; terminar antes de 10:00.
- Si aparece un resultado distinto al esperado, explicar lo observado y corregir el laboratorio antes de grabar una nueva demostración. No recitar una aprobación que la pantalla no confirme.
- El inicio y final muestran fecha y hora; la cámara y el micrófono acompañan toda la demostración.
- La subida a GitHub/YouTube y la edición del TXT se hacen fuera del video.
