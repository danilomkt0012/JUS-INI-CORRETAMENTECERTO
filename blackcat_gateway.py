"""
BlackCat Pagamentos Gateway Integration - Versão Atualizada
Módulo para integração com API BlackCat Pagamentos para geração de PIX
API: https://api.blackcatpagamentos.online/api/sales/create-sale
"""

import os
import logging
import requests
import io
import base64
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlackCatPaymentsGateway:
    """Gateway para integração com BlackCat Pagamentos - Nova Versão"""
    
    def __init__(self):
        self.api_key = os.environ.get("BLACKCAT_API_KEY")
        if not self.api_key:
            raise ValueError("BLACKCAT_API_KEY não configurado nas variáveis de ambiente")
        
        self.base_url = "https://api.blackcatpagamentos.online/api"
        
        logger.info("✅ BlackCat Payments Gateway inicializado (Nova API)")
        logger.info(f"✅ Base URL: {self.base_url}")
    
    def create_pix(
        self,
        customer_name: str,
        customer_email: str,
        customer_cpf: str,
        customer_phone: str,
        amount_cents: int,
        description: str,
        expires_in_days: int = 2,
        postback_url: Optional[str] = None,
        external_ref: Optional[str] = None,
        metadata: Optional[str] = None
    ) -> dict:
        """
        Cria uma transação PIX via BlackCat Pagamentos (Nova API)
        
        Args:
            customer_name: Nome do cliente
            customer_email: Email do cliente
            customer_cpf: CPF do cliente (apenas números)
            customer_phone: Telefone do cliente (apenas números)
            amount_cents: Valor em centavos (ex: 500 para R$ 5,00)
            description: Descrição do produto/serviço
            expires_in_days: Dias para expiração do PIX (padrão: 2)
            postback_url: URL para webhook de notificação
            external_ref: Referência externa opcional
            metadata: Metadados opcionais
        
        Returns:
            dict: {
                "success": bool,
                "transaction_id": str,
                "pix_code": str (código copia e cola),
                "qrcode_base64": str (imagem QR code em base64),
                "amount": int,
                "status": str,
                "invoice_url": str,
                "expiration_date": str
            }
        """
        try:
            clean_cpf = ''.join(filter(str.isdigit, customer_cpf))
            clean_phone = ''.join(filter(str.isdigit, customer_phone))
            
            amount_cents = int(amount_cents)
            
            logger.info(f"🚀 Criando PIX BlackCat (Nova API) - Cliente: {customer_name}")
            logger.info(f"💰 Valor: R$ {amount_cents/100:.2f} ({amount_cents} centavos)")
            logger.info(f"📄 CPF: ***{clean_cpf[-4:]}")
            
            payload = {
                "amount": amount_cents,
                "currency": "BRL",
                "paymentMethod": "pix",
                "items": [
                    {
                        "title": description,
                        "quantity": 1,
                        "tangible": False
                    }
                ],
                "customer": {
                    "name": customer_name,
                    "email": customer_email,
                    "phone": clean_phone,
                    "document": {
                        "number": clean_cpf,
                        "type": "cpf"
                    }
                },
                "pix": {
                    "expiresInDays": expires_in_days
                }
            }
            
            if postback_url:
                payload["postbackUrl"] = postback_url
            
            if external_ref:
                payload["externalRef"] = external_ref
            
            if metadata:
                payload["metadata"] = metadata
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            url = f"{self.base_url}/sales/create-sale"
            logger.info(f"🔄 POST {url}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"📡 BlackCat Response: HTTP {response.status_code}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                logger.info(f"📡 BlackCat Response: {str(response_data)[:300]}...")
                
                if response_data.get("success"):
                    data = response_data.get("data", {})
                    payment_data = data.get("paymentData", {})
                    
                    transaction_id = data.get("transactionId", "")
                    status = data.get("status", "PENDING")
                    amount = data.get("amount", amount_cents)
                    net_amount = data.get("netAmount", 0)
                    fees = data.get("fees", 0)
                    created_at = data.get("createdAt", "")
                    invoice_url = data.get("invoiceUrl", "")
                    
                    pix_id = payment_data.get("id", "")
                    qr_code = payment_data.get("qrCode", "")
                    copy_paste = payment_data.get("copyPaste", "")
                    qr_code_url = payment_data.get("qrCodeUrl", "")
                    qr_code_base64_api = payment_data.get("qrCodeBase64", "")
                    expires_at = payment_data.get("expiresAt", "")
                    
                    pix_code = copy_paste if copy_paste else qr_code
                    
                    logger.info(f"✅ PIX BlackCat criado - ID: {transaction_id}")
                    logger.info(f"✅ Status: {status}")
                    logger.info(f"✅ PIX Code: {len(pix_code)} caracteres")
                    logger.info(f"✅ Expira em: {expires_at}")
                    logger.info(f"✅ Invoice URL: {invoice_url}")
                    
                    qrcode_base64 = ""
                    if qr_code_base64_api:
                        qrcode_base64 = qr_code_base64_api if qr_code_base64_api.startswith("data:") else f"data:image/png;base64,{qr_code_base64_api}"
                    elif pix_code:
                        qrcode_base64 = self._generate_qrcode(pix_code)
                        if not qrcode_base64:
                            logger.warning("⚠️ QR Code não pôde ser gerado, frontend usará fallback")
                    
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "pix_id": pix_id,
                        "pix_code": pix_code,
                        "qr_code": qr_code,
                        "copy_paste": copy_paste,
                        "qrcode_base64": qrcode_base64 if qrcode_base64 else None,
                        "amount": amount,
                        "net_amount": net_amount,
                        "fees": fees,
                        "status": status,
                        "invoice_url": invoice_url,
                        "expiration_date": expires_at,
                        "created_at": created_at,
                        "raw_response": response_data
                    }
                else:
                    error_msg = response_data.get("message", "Erro desconhecido na API")
                    logger.error(f"❌ API retornou success=false: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "raw_response": response_data
                    }
            else:
                error_msg = f"Erro HTTP {response.status_code}: {response.text}"
                logger.error(f"❌ {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de requisição: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def check_status(self, transaction_id: str) -> dict:
        """
        Verifica o status de uma transação PIX
        
        Args:
            transaction_id: ID da transação (ex: TRX17678276292767ZNI9J)
        
        Returns:
            dict: {
                "success": bool,
                "transaction_id": str,
                "status": str,
                "paid": bool,
                "amount": int,
                "paid_at": str (opcional)
            }
        """
        try:
            logger.info(f"🔍 Verificando status BlackCat: {transaction_id}")
            
            url = f"{self.base_url}/sales/status/{transaction_id}"
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": self.api_key
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                
                if response_data.get("success"):
                    data = response_data.get("data", {})
                    status = data.get("status", "UNKNOWN")
                    paid_at = data.get("paidAt")
                    amount = data.get("amount", 0)
                    
                    paid = status.upper() in ["PAID", "COMPLETED", "APPROVED", "CONFIRMED"]
                    
                    logger.info(f"✅ Status verificado: {status} - Pago: {paid}")
                    
                    return {
                        "success": True,
                        "transaction_id": transaction_id,
                        "status": status,
                        "paid": paid,
                        "amount": amount,
                        "paid_at": paid_at,
                        "raw_response": response_data
                    }
                else:
                    error_msg = response_data.get("message", "Erro ao verificar status")
                    logger.error(f"❌ {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "raw_response": response_data
                    }
            else:
                error_msg = f"Erro HTTP {response.status_code}"
                logger.error(f"❌ {error_msg}")
                
                return {
                    "success": False,
                    "error": error_msg,
                    "status_code": response.status_code
                }
        
        except requests.exceptions.RequestException as e:
            error_msg = f"Erro de requisição: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
        
        except Exception as e:
            error_msg = f"Erro inesperado: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def _generate_qrcode(self, pix_code: str) -> str:
        """
        Gera imagem QR Code a partir do código PIX copia e cola
        
        Args:
            pix_code: Código PIX copia e cola
        
        Returns:
            str: QR Code em base64 (data:image/png;base64,...)
        """
        try:
            import qrcode as qr_lib
            
            img = qr_lib.make(pix_code)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_data = buffer.getvalue()
            img_base64 = base64.b64encode(img_data).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar QR Code: {str(e)}")
            return ""


_gateway = None


def get_gateway() -> BlackCatPaymentsGateway:
    """Retorna instância do gateway (singleton)"""
    global _gateway
    if _gateway is None:
        _gateway = BlackCatPaymentsGateway()
    return _gateway


def create_blackcat_pix(
    customer_name: str,
    customer_email: str,
    customer_cpf: str,
    customer_phone: str,
    amount_cents: int,
    description: str,
    expires_in_days: int = 2,
    postback_url: Optional[str] = None,
    external_ref: Optional[str] = None,
    metadata: Optional[str] = None
) -> dict:
    """
    Função auxiliar para criar PIX via BlackCat Pagamentos
    
    Args:
        customer_name: Nome do cliente
        customer_email: Email do cliente
        customer_cpf: CPF do cliente
        customer_phone: Telefone do cliente
        amount_cents: Valor em centavos (ex: 2490 para R$ 24.90)
        description: Descrição
        expires_in_days: Dias para expiração (padrão: 2)
        postback_url: URL webhook opcional
        external_ref: Referência externa opcional
        metadata: Metadados opcionais
    
    Returns:
        dict com resultado da criação
    """
    gateway = get_gateway()
    return gateway.create_pix(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_cpf=customer_cpf,
        customer_phone=customer_phone,
        amount_cents=amount_cents,
        description=description,
        expires_in_days=expires_in_days,
        postback_url=postback_url,
        external_ref=external_ref,
        metadata=metadata
    )


def check_blackcat_status(transaction_id: str) -> dict:
    """
    Função auxiliar para verificar status de pagamento
    
    Args:
        transaction_id: ID da transação
    
    Returns:
        dict com status da transação
    """
    gateway = get_gateway()
    return gateway.check_status(transaction_id)
