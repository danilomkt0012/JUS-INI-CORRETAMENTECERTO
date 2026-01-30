"""
4M Payments Gateway Integration
Módulo para integração com API 4M Payments para geração de PIX
"""

import os
import logging
import requests
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FourMPaymentsGateway:
    """Gateway para integração com 4M Payments"""
    
    def __init__(self):
        self.api_token = os.environ.get("FOURM_API_TOKEN")
        if not self.api_token:
            raise ValueError("FOURM_API_TOKEN não configurado nas variáveis de ambiente")
        
        self.base_url = "https://app.4mpagamentos.com/api/v1"
        
        logger.info("✅ 4M Payments Gateway inicializado")
        logger.info(f"✅ Base URL: {self.base_url}")
    
    def create_pix(
        self,
        customer_name: str,
        customer_email: str,
        customer_cpf: str,
        customer_phone: str,
        amount: float,
        description: str,
        product_id: Optional[int] = None
    ) -> dict:
        """
        Cria uma transação PIX via 4M Payments
        
        Args:
            customer_name: Nome do cliente
            customer_email: Email do cliente
            customer_cpf: CPF do cliente (apenas números)
            customer_phone: Telefone do cliente
            amount: Valor em reais (ex: 24.90)
            description: Descrição da transação
            product_id: ID do produto (opcional)
        
        Returns:
            dict: {
                "success": bool,
                "transaction_id": str,
                "pix_code": str,
                "amount": float,
                "status": str,
                "expires_at": str,
                "created_at": str
            }
        """
        try:
            # Limpar CPF e telefone removendo formatação
            clean_cpf = ''.join(filter(str.isdigit, customer_cpf))
            clean_phone = ''.join(filter(str.isdigit, customer_phone))
            
            logger.info(f"🚀 Criando PIX 4M Payments - Cliente: {customer_name}")
            logger.info(f"💰 Valor: R$ {amount:.2f}")
            logger.info(f"📄 CPF: ***{clean_cpf[-4:]}")
            
            # Preparar payload
            payload = {
                "amount": amount,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_cpf": clean_cpf,
                "customer_phone": clean_phone,
                "description": description
            }
            
            # Adicionar product_id se fornecido
            if product_id:
                payload["product_id"] = product_id
                logger.info(f"🏷️ Product ID: {product_id}")
            
            # Headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            
            # Fazer requisição
            url = f"{self.base_url}/payments"
            logger.info(f"🔄 POST {url}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            logger.info(f"📡 4M Payments Response: HTTP {response.status_code}")
            
            # Log do corpo da resposta (apenas primeiros 500 caracteres)
            response_text = response.text[:500] if len(response.text) > 500 else response.text
            logger.info(f"📡 4M Payments Response Body: {response_text}")
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # A resposta vem com estrutura {"success": true, "data": {...}}
                if response_data.get("success") and "data" in response_data:
                    data = response_data["data"]
                else:
                    data = response_data
                
                # Extrair campos da resposta
                transaction_id = data.get("transaction_id") or data.get("transactionId")
                pix_code = data.get("pix_code") or data.get("pixCode") or data.get("pix_qr_code") or data.get("pixQrCode")
                status = data.get("status", "pending")
                
                logger.info(f"✅ PIX 4M Payments criado - ID: {transaction_id}")
                logger.info(f"✅ Status: {status}")
                if pix_code:
                    logger.info(f"✅ PIX Code: {len(pix_code)} caracteres")
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "pix_code": pix_code,
                    "amount": data.get("amount"),
                    "status": status,
                    "expires_at": data.get("expires_at") or data.get("expiresAt"),
                    "created_at": data.get("created_at") or data.get("createdAt"),
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
            transaction_id: ID da transação (ex: PIX20250905183444A5843B1F)
        
        Returns:
            dict: {
                "success": bool,
                "transaction_id": str,
                "status": str,
                "amount": float,
                "paid_at": str (opcional)
            }
        """
        try:
            logger.info(f"🔍 Verificando status 4M Payments: {transaction_id}")
            
            # Endpoint público (sem autenticação) - usa /transactions não /payments
            url = f"{self.base_url}/transactions/{transaction_id}"
            
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                logger.info(f"✅ Status verificado: {status}")
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "status": status,
                    "amount": data.get("amount"),
                    "paid_at": data.get("paidAt"),
                    "raw_response": data
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


# Instância global do gateway
_gateway = None


def get_gateway() -> FourMPaymentsGateway:
    """Retorna instância do gateway (singleton)"""
    global _gateway
    if _gateway is None:
        _gateway = FourMPaymentsGateway()
    return _gateway


def create_fourm_pix(
    customer_name: str,
    customer_email: str,
    customer_cpf: str,
    customer_phone: str,
    amount: float,
    description: str,
    product_id: Optional[int] = None
) -> dict:
    """
    Função auxiliar para criar PIX via 4M Payments
    
    Args:
        customer_name: Nome do cliente
        customer_email: Email do cliente
        customer_cpf: CPF do cliente
        customer_phone: Telefone do cliente
        amount: Valor em reais (ex: 24.90)
        description: Descrição
        product_id: ID do produto (opcional)
    
    Returns:
        dict com resultado da criação
    """
    gateway = get_gateway()
    return gateway.create_pix(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_cpf=customer_cpf,
        customer_phone=customer_phone,
        amount=amount,
        description=description,
        product_id=product_id
    )


def check_fourm_status(transaction_id: str) -> dict:
    """
    Função auxiliar para verificar status de pagamento
    
    Args:
        transaction_id: ID da transação
    
    Returns:
        dict com status da transação
    """
    gateway = get_gateway()
    return gateway.check_status(transaction_id)
