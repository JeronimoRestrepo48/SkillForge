import hashlib
import hmac
import json
import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger("transactions")

class WompiPaymentGateway:
    @staticmethod
    def generate_integrity_signature(reference: str, amount_in_cents: int, currency: str = "COP") -> str:
        """
        Genera la firma de integridad requerida para iniciar transacciones en Wompi Sandbox/Producción.
        Fórmula: sha256(referencia + monto_en_centavos + moneda + secreto_de_integridad)
        """
        raw_string = f"{reference}{amount_in_cents}{currency}{settings.WOMPI_INTEGRITY_SECRET}"
        signature = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
        logger.debug(f"Integrity signature generated for {reference} ({amount_in_cents} cents): {signature}")
        return signature

    @staticmethod
    def validate_webhook_signature(payload: Dict[str, Any]) -> bool:
        """
        Valida la firma de eventos (webhook) de Wompi.
        Concatenación ordenada de valores indicados en 'signature.properties' + timestamp + WOMPI_EVENTS_SECRET.
        Genera SHA-256 y compara con 'signature.checksum'.
        """
        try:
            signature_info = payload.get("signature", {})
            properties = signature_info.get("properties", [])
            checksum = signature_info.get("checksum", "")
            timestamp = payload.get("timestamp")
            
            if not properties or not checksum or timestamp is None:
                logger.error("Missing signature properties, checksum or timestamp in Wompi payload")
                return False
                
            # Extraer los valores según el orden de propiedades especificado (ej: 'transaction.id')
            concatenated_values = ""
            for prop in properties:
                # Resolver propiedad anidada (ej: data.transaction.id -> data -> transaction -> id)
                parts = prop.split(".")
                val = payload.get("data", {})
                for part in parts:
                    if isinstance(val, dict):
                        # Si la parte es 'transaction', entramos al diccionario, si es 'id' extraemos el valor
                        if part == "transaction":
                            val = val.get("transaction", {})
                        else:
                            val = val.get(part)
                    else:
                        val = None
                        break
                
                if val is not None:
                    concatenated_values += str(val)
            
            # Concatenar timestamp y events_secret
            raw_string = f"{concatenated_values}{timestamp}{settings.WOMPI_EVENTS_SECRET}"
            calculated_checksum = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
            
            is_valid = hmac.compare_digest(calculated_checksum, checksum)
            if not is_valid:
                logger.warning(f"Invalid Webhook signature! Calculated: {calculated_checksum}, Expected: {checksum}")
            else:
                logger.info("Webhook signature validated successfully")
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating Wompi webhook signature: {str(e)}", exc_info=True)
            return False
