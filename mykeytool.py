#!/usr/bin/env python3
"""Simulador CLI de Java Keytool (genkeypair y certreq) con almacén JKS."""

import argparse
import getpass
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jks
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

KEYSTORE_FILE = Path("keystore.jks")


def pedir_password(texto="Contraseña del KeyStore: "):
    password = getpass.getpass(texto)
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    return password


def abrir_almacen(password):
    if not KEYSTORE_FILE.exists():
        raise FileNotFoundError("No existe keystore.jks. Ejecuta primero --genkeypair.")
    try:
        return jks.KeyStore.load(str(KEYSTORE_FILE), password)
    except Exception as exc:
        raise ValueError(
            "No se pudo abrir el KeyStore: contraseña incorrecta o archivo dañado."
        ) from exc


def pedir_titular():
    print("Datos del titular (Distinguished Name):")
    campos = [
        ("CN", NameOID.COMMON_NAME, "CN (Nombre común): "),
        ("OU", NameOID.ORGANIZATIONAL_UNIT_NAME, "OU (Unidad organizativa): "),
        ("O", NameOID.ORGANIZATION_NAME, "O (Organización): "),
        ("L", NameOID.LOCALITY_NAME, "L (Localidad): "),
        ("ST", NameOID.STATE_OR_PROVINCE_NAME, "ST (Provincia/Estado): "),
        ("C", NameOID.COUNTRY_NAME, "C (País, 2 letras): "),
    ]
    atributos = []
    for clave, oid, texto in campos:
        valor = input(texto).strip()
        if clave == "C":
            valor = valor.upper()
            if valor and len(valor) != 2:
                raise ValueError("C debe contener exactamente dos letras.")
        if clave == "CN" and not valor:
            raise ValueError("CN no puede estar vacío.")
        if valor:
            atributos.append(x509.NameAttribute(oid, valor))
    return x509.Name(atributos)


def genkeypair():
    password = pedir_password()
    if password != getpass.getpass("Confirma la contraseña: "):
        raise ValueError("Las contraseñas no coinciden.")

    alias = input("Alias: ").strip().lower()
    if not alias:
        raise ValueError("El alias no puede estar vacío.")

    if KEYSTORE_FILE.exists():
        almacen = abrir_almacen(password)
    else:
        almacen = jks.KeyStore.new("jks", [])

    if alias in almacen.entries:
        raise ValueError(f"El alias '{alias}' ya existe.")

    titular = pedir_titular()

    clave = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ahora = datetime.now(timezone.utc)
    certificado = (
        x509.CertificateBuilder()
        .subject_name(titular)
        .issuer_name(titular)
        .public_key(clave.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(ahora)
        .not_valid_after(ahora + timedelta(days=365))
        .sign(clave, hashes.SHA256())
    )

    clave_der = clave.private_bytes(
        serialization.Encoding.DER,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    cert_der = certificado.public_bytes(serialization.Encoding.DER)

    entrada = jks.PrivateKeyEntry.new(alias, [cert_der], clave_der, key_format="pkcs8")
    entrada.encrypt(password)

    # entries es el diccionario real; private_keys es solo una copia de lectura.
    almacen.entries[alias] = entrada
    almacen.save(str(KEYSTORE_FILE), password)

    # Comprobación: releer el archivo y confirmar que la clave está dentro.
    if alias not in jks.KeyStore.load(str(KEYSTORE_FILE), password).private_keys:
        raise ValueError("El almacén se guardó pero no contiene la clave privada.")

    print("Clave RSA de 2048 bits guardada correctamente.")
    print(f"Alias: {alias}")
    print(f"KeyStore: {KEYSTORE_FILE.resolve()}")


def certreq():
    password = pedir_password()
    alias = input("Alias: ").strip().lower()

    almacen = abrir_almacen(password)
    if alias not in almacen.private_keys:
        raise ValueError(f"No existe una clave privada con el alias '{alias}'.")

    entrada = almacen.private_keys[alias]
    try:
        entrada.decrypt(password)
        clave = serialization.load_der_private_key(entrada.pkey_pkcs8, password=None)
    except Exception as exc:
        raise ValueError(
            "No se pudo descifrar la clave privada. Comprueba la contraseña."
        ) from exc

    if not entrada.cert_chain:
        raise ValueError("La entrada no contiene un certificado.")
    certificado = x509.load_der_x509_certificate(entrada.cert_chain[0][1])

    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(certificado.subject)
        .sign(clave, hashes.SHA256())
    )

    ruta = Path(f"{alias}.csr")
    ruta.write_bytes(csr.public_bytes(serialization.Encoding.PEM))
    print(f"CSR creado correctamente: {ruta.resolve()}")


def main():
    parser = argparse.ArgumentParser(
        description="Simulador CLI de Java Keytool en Python"
    )
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument(
        "--genkeypair", action="store_true",
        help="Genera un par RSA de 2048 bits y lo guarda en keystore.jks.",
    )
    grupo.add_argument(
        "--certreq", action="store_true",
        help="Genera una solicitud CSR (PEM) a partir de un alias.",
    )
    args = parser.parse_args()

    try:
        if args.genkeypair:
            genkeypair()
        else:
            certreq()
    except (ValueError, FileNotFoundError, OSError, jks.KeystoreException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
