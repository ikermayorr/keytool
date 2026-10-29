# Simulación CLI de Java Keytool en Python

Este proyecto es una aplicación de línea de comandos (CLI) desarrollada en Python que simula las funcionalidades esenciales de la herramienta oficial `keytool` de Java. Permite generar pares de claves asimétricas RSA (2048 bits), almacenarlas de forma segura (cifradas) en un archivo JSON y generar Solicitudes de Firma de Certificado (CSR).

## 👥 Integrantes del Equipo
Iker Mayor Oñate
Enzo Ruiz Loze

## ⚙️ Requisitos e Instalación

Para ejecutar este proyecto, necesitas tener Python 3 instalado en tu sistema. Además, el programa depende de la librería `cryptography` para gestionar la generación de claves y el cifrado.

Instala las dependencias ejecutando el siguiente comando en tu terminal:

```bash
pip install cryptography
```

## 🚀 Guía de Uso de la CLI

El script se ejecuta a través de la terminal usando `python3 mykeytool.py` seguido del comando que deseas utilizar.

### 1. Menú de Ayuda (`--help`)
Muestra el listado de comandos disponibles y su sintaxis.
```bash
python mykeytool.py --help
```
**Ejemplo de salida:**
```text
usage: mykeytool.py [-h] (--genkeypair | --certreq)

Simulador sencillo de Java Keytool en Python

options:
  -h, --help    show this help message and exit
  --genkeypair, --genkey
                Genera un par de claves RSA y lo guarda en el almacén
  --certreq     Genera una solicitud de certificado (CSR)
```

### 2. Generar un Par de Claves (`--genkeypair`)
Crea un nuevo par de claves RSA (2048 bits) y lo guarda cifrado en el almacén `keystore.json`. Te pedirá una contraseña, un alias y los datos del titular.
```bash
python mykeytool.py --genkeypair
```
**Ejemplo de consola:**
```text
Contraseña del almacén: 
Repite la contraseña: 
Alias para la clave: mi_clave
Introduce los datos del titular:
Nombre y Apellidos (CN): Juan Perez
Unidad Organizativa / Departamento (OU): Desarrollo
Organización / Empresa (O): Mi Empresa
Localidad / Ciudad (L): Barcelona
Estado / Provincia (ST): Barcelona
Código de País (C - ej. ES): ES
Par de claves creado y guardado con el alias 'mi_clave'.
Almacén: keystore.json
```

### 3. Extraer una Solicitud de Certificado (`--certreq`)
Recupera la clave privada de un alias específico y genera un archivo `.csr` en formato PEM.
```bash
python mykeytool.py --certreq
```
**Ejemplo de consola:**
```text
Alias de la clave para el CSR: mi_clave
Contraseña del almacén/alias: 
Solicitud de firma de certificado (CSR) generada con éxito: mi_clave.csr
```

## 🧪 Matriz de Pruebas Ejecutadas

El sistema cuenta con manejo de excepciones para evitar que el programa se cierre abruptamente. A continuación, se detallan las pruebas realizadas:

| Caso de Prueba | Acción Realizada | Resultado Esperado | Estado |
| :--- | :--- | :--- | :---: |
| **Contraseña vacía** | Ejecutar `--genkeypair` y dejar la contraseña en blanco. | Muestra `Error: La contraseña no puede estar vacía.` | ✅ OK |
| **Contraseñas no coinciden** | Ejecutar `--genkeypair` e introducir claves distintas. | Muestra `Error: Las contraseñas no coinciden.` | ✅ OK |
| **Alias duplicado** | Ejecutar `--genkeypair` con un alias que ya existe en `keystore.json`. | Muestra `Error: El alias '[alias]' ya existe.` | ✅ OK |
| **País incorrecto** | Introducir un país de más/menos de 2 letras en `--genkeypair`. | Muestra `Error: El país (C) debe tener dos letras...` | ✅ OK |
| **CSR con alias erróneo** | Ejecutar `--certreq` y poner un alias que no existe. | Muestra `Error: El alias '[alias]' no existe en el almacén.` | ✅ OK |
| **Contraseña incorrecta (CSR)**| Ejecutar `--certreq` y fallar la contraseña del almacén. | Muestra `Error: La contraseña es incorrecta...` | ✅ OK |
