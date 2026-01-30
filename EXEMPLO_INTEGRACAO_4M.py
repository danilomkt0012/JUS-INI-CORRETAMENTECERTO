# 📖 EXEMPLO DE INTEGRAÇÃO 4M PAYMENTS NO FLASK

"""
Este arquivo mostra exemplos práticos de como integrar a 4M Payments
no seu projeto Flask.
"""

from flask import Flask, request, jsonify
from four_m_gateway import create_fourm_pix, check_fourm_status
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# =============================================================================
# EXEMPLO 1: CRIAR PIX (API DIRETA - Usa configurações globais)
# =============================================================================

@app.route('/api/gerar-pix-4m', methods=['POST'])
def gerar_pix_4m():
    """
    Endpoint para gerar PIX 4M Payments
    
    EXEMPLO DE REQUEST:
    {
        "nome": "JOÃO DA SILVA",
        "cpf": "12345678901",
        "email": "joao@email.com",
        "telefone": "11999887766"
    }
    """
    try:
        data = request.get_json()
        
        # Extrair dados do cliente
        nome = data.get('nome', '')
        cpf = data.get('cpf', '')
        email = data.get('email', '')
        telefone = data.get('telefone', f"11{cpf[-8:]}")
        
        logging.info(f"Criando PIX para {nome} - CPF: ***{cpf[-4:]}")
        
        # Criar PIX via 4M Payments (API Direta)
        resultado = create_fourm_pix(
            customer_name=nome,
            customer_email=email,
            customer_cpf=cpf,
            customer_phone=telefone,
            amount=24.90,
            description="Curso Digital"
            # SEM product_id = usa configurações GLOBAIS
        )
        
        if resultado.get("success"):
            logging.info(f"✅ PIX criado: {resultado.get('transaction_id')}")
            return jsonify(resultado), 200
        else:
            logging.error(f"❌ Erro: {resultado.get('error')}")
            return jsonify({
                "success": False,
                "error": resultado.get('error')
            }), 400
            
    except Exception as e:
        logging.error(f"Erro interno: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =============================================================================
# EXEMPLO 2: CRIAR PIX (PRODUTO ESPECÍFICO - Usa configurações do produto)
# =============================================================================

@app.route('/api/gerar-pix-produto-4m', methods=['POST'])
def gerar_pix_produto_4m():
    """
    Endpoint para gerar PIX com produto específico
    
    EXEMPLO DE REQUEST:
    {
        "nome": "JOÃO DA SILVA",
        "cpf": "12345678901",
        "email": "joao@email.com",
        "telefone": "11999887766",
        "product_id": 123
    }
    """
    try:
        data = request.get_json()
        
        # Extrair dados
        nome = data.get('nome', '')
        cpf = data.get('cpf', '')
        email = data.get('email', '')
        telefone = data.get('telefone', f"11{cpf[-8:]}")
        product_id = data.get('product_id')  # ID do produto
        
        logging.info(f"Criando PIX com produto {product_id} para {nome}")
        
        # Criar PIX com produto específico
        resultado = create_fourm_pix(
            customer_name=nome,
            customer_email=email,
            customer_cpf=cpf,
            customer_phone=telefone,
            amount=24.90,
            description="Curso Digital",
            product_id=product_id  # ← COM product_id = usa configurações do PRODUTO
        )
        
        if resultado.get("success"):
            logging.info(f"✅ PIX criado: {resultado.get('transaction_id')}")
            return jsonify(resultado), 200
        else:
            logging.error(f"❌ Erro: {resultado.get('error')}")
            return jsonify({
                "success": False,
                "error": resultado.get('error')
            }), 400
            
    except Exception as e:
        logging.error(f"Erro interno: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =============================================================================
# EXEMPLO 3: VERIFICAR STATUS DE PAGAMENTO
# =============================================================================

@app.route('/api/verificar-status-4m/<transaction_id>', methods=['GET'])
def verificar_status_4m(transaction_id):
    """
    Endpoint para verificar status de pagamento
    
    EXEMPLO DE REQUEST:
    GET /api/verificar-status-4m/PIX20250905183444A5843B1F
    """
    try:
        logging.info(f"Verificando status: {transaction_id}")
        
        resultado = check_fourm_status(transaction_id)
        
        if resultado.get("success"):
            status = resultado.get("status")
            logging.info(f"✅ Status: {status}")
            
            # Lógica baseada no status
            if status == "paid":
                logging.info("🎉 PAGAMENTO CONFIRMADO!")
            elif status == "pending":
                logging.info("⏳ Aguardando pagamento...")
            elif status in ["expired", "cancelled"]:
                logging.info("❌ Transação finalizada sem pagamento")
            
            return jsonify(resultado), 200
        else:
            logging.error(f"❌ Erro: {resultado.get('error')}")
            return jsonify(resultado), 400
            
    except Exception as e:
        logging.error(f"Erro interno: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =============================================================================
# EXEMPLO 4: PÁGINA DE CHECKOUT COM VERIFICAÇÃO AUTOMÁTICA
# =============================================================================

@app.route('/checkout-4m')
def checkout_4m():
    """Página de checkout com verificação automática de status"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Checkout 4M Payments</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
            <h1 class="text-2xl font-bold mb-4">Checkout PIX</h1>
            
            <form id="checkoutForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium mb-1">Nome</label>
                    <input type="text" id="nome" class="w-full border rounded p-2" required>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">CPF</label>
                    <input type="text" id="cpf" class="w-full border rounded p-2" required>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-1">Email</label>
                    <input type="email" id="email" class="w-full border rounded p-2" required>
                </div>
                <button type="submit" class="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700">
                    Gerar PIX R$ 24,90
                </button>
            </form>
            
            <div id="pixArea" class="mt-6 hidden">
                <h2 class="text-xl font-bold mb-2">QR Code PIX</h2>
                <div id="qrcode" class="mb-4"></div>
                <textarea id="pixCode" class="w-full border rounded p-2 text-xs" rows="4" readonly></textarea>
                <div id="status" class="mt-4 p-3 rounded bg-yellow-100 text-yellow-800">
                    ⏳ Aguardando pagamento...
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.1/build/qrcode.min.js"></script>
        <script>
            let transactionId = null;
            let checkInterval = null;
            
            // Enviar formulário
            document.getElementById('checkoutForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                
                const data = {
                    nome: document.getElementById('nome').value,
                    cpf: document.getElementById('cpf').value,
                    email: document.getElementById('email').value
                };
                
                try {
                    const response = await fetch('/api/gerar-pix-4m', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        transactionId = result.transaction_id;
                        
                        // Mostrar QR Code
                        document.getElementById('pixArea').classList.remove('hidden');
                        document.getElementById('pixCode').value = result.pix_code;
                        
                        // Gerar QR Code
                        const qrcodeContainer = document.getElementById('qrcode');
                        qrcodeContainer.innerHTML = '';
                        new QRCode(qrcodeContainer, {
                            text: result.pix_code,
                            width: 256,
                            height: 256
                        });
                        
                        // Iniciar verificação automática (a cada 5 segundos)
                        iniciarVerificacaoStatus();
                    } else {
                        alert('Erro: ' + result.error);
                    }
                } catch (error) {
                    alert('Erro ao gerar PIX: ' + error);
                }
            });
            
            // Verificar status automaticamente
            function iniciarVerificacaoStatus() {
                checkInterval = setInterval(async () => {
                    try {
                        const response = await fetch(`/api/verificar-status-4m/${transactionId}`);
                        const result = await response.json();
                        
                        const statusDiv = document.getElementById('status');
                        
                        if (result.status === 'paid') {
                            statusDiv.className = 'mt-4 p-3 rounded bg-green-100 text-green-800';
                            statusDiv.innerHTML = '✅ PAGAMENTO CONFIRMADO!';
                            clearInterval(checkInterval);
                            
                            // Redirecionar após 2 segundos
                            setTimeout(() => {
                                window.location.href = '/sucesso';
                            }, 2000);
                        } else if (result.status === 'expired' || result.status === 'cancelled') {
                            statusDiv.className = 'mt-4 p-3 rounded bg-red-100 text-red-800';
                            statusDiv.innerHTML = '❌ Transação expirada ou cancelada';
                            clearInterval(checkInterval);
                        }
                    } catch (error) {
                        console.error('Erro ao verificar status:', error);
                    }
                }, 5000); // ✅ 5 segundos - RECOMENDADO
            }
        </script>
    </body>
    </html>
    '''


# =============================================================================
# TESTE RÁPIDO
# =============================================================================

if __name__ == '__main__':
    # Teste direto do gateway
    print("=== TESTE 4M PAYMENTS ===\n")
    
    resultado = create_fourm_pix(
        customer_name="TESTE FUNCIONANDO",
        customer_email="teste@email.com",
        customer_cpf="12345678901",
        customer_phone="11999887766",
        amount=24.90,
        description="Teste de Integração"
    )
    
    print("\n=== RESULTADO ===")
    print(f"Sucesso: {resultado.get('success')}")
    print(f"Transaction ID: {resultado.get('transaction_id')}")
    print(f"PIX Code (primeiros 50 chars): {resultado.get('pix_code', '')[:50]}...")
    
    if resultado.get('success') and resultado.get('transaction_id'):
        # Testar verificação de status
        print("\n=== VERIFICANDO STATUS ===")
        transaction_id = resultado.get('transaction_id', '')
        status_resultado = check_fourm_status(transaction_id)
        print(f"Status: {status_resultado.get('status')}")
    
    print("\n=== INICIANDO SERVIDOR FLASK ===")
    app.run(host='0.0.0.0', port=5000, debug=True)
