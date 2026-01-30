"""
Routes module for JusBrasil Clone
Handles all URL routing and view functions
"""

import logging
from flask import render_template, request, redirect, url_for, flash
from app import app

# Configure logging
logger = logging.getLogger(__name__)

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
    },
    {
        'id': 4,
        'name': 'Usuário',
        'age_range': '35 a 45 anos',
        'location': 'Minas Gerais',
        'cpf_masked': '***.***.***-**',
        'processes_count': 2,
        'has_processes': True
    },
    {
        'id': 5,
        'name': 'Usuário',
        'age_range': '28 a 35 anos',
        'location': 'Bahia',
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
                'description': 'Juntada de petição - Manifestação da parte requerente sobre documentos apresentados'
            },
            {
                'date': '12/01/2025',
                'description': 'Intimação das partes - Prazo de 15 dias para manifestação'
            },
            {
                'date': '10/01/2025',
                'description': 'Despacho do juiz - Determinada intimação das partes'
            },
            {
                'date': '05/01/2025',
                'description': 'Distribuição do processo - Processo autuado e distribuído'
            }
        ]
    },
    {
        'id': 2,
        'number': '1002345-67.2023.8.26.0100',
        'tribunal': 'TJSP - Tribunal de Justiça de São Paulo',
        'type': 'Ação de Indenização por Danos Morais',
        'status': 'Aguardando sentença',
        'last_update': '18/01/2025',
        'parties': {
            'polo_ativo': 'JOÃO SILVA SANTOS',
            'polo_passivo': 'EMPRESA XYZ LTDA',
            'advogado': 'DRA. MARIA FERNANDA COSTA'
        },
        'movements': [
            {
                'date': '18/01/2025',
                'description': 'Conclusão dos autos ao juiz para sentença'
            },
            {
                'date': '15/01/2025',
                'description': 'Alegações finais apresentadas pelas partes'
            },
            {
                'date': '10/01/2025',
                'description': 'Encerramento da instrução processual'
            }
        ]
    }
]

OFFICIAL_DIARIES = [
    {
        'content': 'USUÁRIO POLO PASSIVO : USUÁRIO SEGREDO JUSTIÇA : NÃO PARTE INTIMADA : USUÁRIO ADVG... PARTE : 50826 GO - USUÁRIO PARTE INTIMADA : USUÁRIO...',
        'date': '15/01/2025',
        'source': 'Diário Oficial do Estado de Goiás',
        'type': 'Intimação'
    },
    {
        'content': 'TRIBUNAL DE JUSTIÇA DO ESTADO DE GOIÁS - COMARCA DE ANÁPOLIS - 1ª VARA CÍVEL - PROCESSO Nº 5008264-89.2023.8.09.0137 - INTIMAÇÃO - Ficam as partes intimadas para manifestação no prazo legal.',
        'date': '12/01/2025',
        'source': 'Diário Oficial do Estado de Goiás',
        'type': 'Publicação Oficial'
    }
]

@app.route('/')
def index():
    """Homepage with search functionality"""
    logger.info("Accessing homepage")
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    """Search page for processes and people"""
    logger.info(f"Search page accessed - Method: {request.method}")
    
    if request.method == 'POST':
        search_term = request.form.get('search_term', '').strip()
        search_type = request.form.get('search_type', 'name')
        
        logger.info(f"Search performed - Term: {search_term}, Type: {search_type}")
        
        if not search_term:
            flash('Por favor, digite um termo para busca.', 'error')
            return render_template('search.html')
        
        # Filter persons based on search term and type
        found_persons = []
        found_processes = []
        
        if search_type == 'name':
            for person in SAMPLE_PERSONS:
                if search_term.lower() in person['name'].lower():
                    found_persons.append(person)
        elif search_type == 'process':
            for process in SAMPLE_PROCESSES:
                if search_term in process['number']:
                    found_processes.append(process)
        elif search_type == 'cpf':
            # In a real application, this would search by actual CPF
            # For demo purposes, we'll show a message about CPF search
            flash('Busca por CPF requer dados específicos. Utilize a busca por nome para demonstração.', 'info')
        
        # Get relevant diary entries
        relevant_diaries = []
        if found_persons:
            relevant_diaries = OFFICIAL_DIARIES
        
        logger.info(f"Search results - Persons: {len(found_persons)}, Processes: {len(found_processes)}")
        
        return render_template('search.html', 
                             search_term=search_term,
                             search_type=search_type,
                             persons=found_persons,
                             processes=found_processes,
                             diaries=relevant_diaries)
    
    return render_template('search.html')

@app.route('/person/<int:person_id>')
def person_profile(person_id):
    """Person profile page showing their processes"""
    logger.info(f"Person profile accessed - ID: {person_id}")
    
    person = None
    for p in SAMPLE_PERSONS:
        if p['id'] == person_id:
            person = p
            break
    
    if not person:
        logger.warning(f"Person not found - ID: {person_id}")
        flash('Pessoa não encontrada.', 'error')
        return redirect(url_for('login'))
    
    # Get processes for this person
    person_processes = []
    if person['has_processes']:
        # In a real application, this would filter by person
        for process in SAMPLE_PROCESSES:
            if person['name'].upper() in process['parties']['polo_passivo'].upper() or \
               person['name'].upper() in process['parties']['polo_ativo'].upper():
                person_processes.append(process)
    
    logger.info(f"Person profile loaded - Name: {person['name']}, Processes: {len(person_processes)}")
    
    return render_template('person_profile.html', 
                         person=person, 
                         processes=person_processes)

@app.route('/process/<int:process_id>')
def process_details(process_id):
    """Process details page"""
    logger.info(f"Process details accessed - ID: {process_id}")
    
    process = None
    for p in SAMPLE_PROCESSES:
        if p['id'] == process_id:
            process = p
            break
    
    if not process:
        logger.warning(f"Process not found - ID: {process_id}")
        flash('Processo não encontrado.', 'error')
        return redirect(url_for('login'))
    
    logger.info(f"Process details loaded - Number: {process['number']}")
    
    return render_template('process_details.html', process=process)

@app.route('/consulta-processual')
def consulta_processual():
    """Direct route to match JusBrasil URL structure"""
    logger.info("Redirecting to search from consulta-processual")
    return redirect(url_for('search'))

@app.route('/jurisprudencia')
def jurisprudencia():
    """Jurisprudence page (placeholder)"""
    logger.info("Jurisprudence page accessed")
    flash('Funcionalidade de Jurisprudência em desenvolvimento.', 'info')
    return redirect(url_for('login'))

@app.route('/doutrina')
def doutrina():
    """Doctrine page (placeholder)"""
    logger.info("Doctrine page accessed")
    flash('Funcionalidade de Doutrina em desenvolvimento.', 'info')
    return redirect(url_for('login'))

@app.route('/diarios-oficiais')
def diarios_oficiais():
    """Official diaries page"""
    logger.info("Official diaries page accessed")
    return render_template('diarios_oficiais.html', diaries=OFFICIAL_DIARIES)

@app.route('/sobre')
def sobre():
    """About page"""
    logger.info("About page accessed")
    return render_template('sobre.html')

@app.route('/ajuda')
def ajuda():
    """Help page"""
    logger.info("Help page accessed")
    return render_template('ajuda.html')

@app.route('/api/search/suggestions')
def search_suggestions():
    """API endpoint for search suggestions (for future AJAX implementation)"""
    query = request.args.get('q', '').strip().lower()
    
    if len(query) < 2:
        return {'suggestions': []}
    
    suggestions = []
    for person in SAMPLE_PERSONS:
        if query in person['name'].lower():
            suggestions.append({
                'type': 'person',
                'name': person['name'],
                'location': person['location'],
                'id': person['id']
            })
    
    for process in SAMPLE_PROCESSES:
        if query in process['number'].lower() or query in process['type'].lower():
            suggestions.append({
                'type': 'process',
                'number': process['number'],
                'type_name': process['type'],
                'id': process['id']
            })
    
    return {'suggestions': suggestions[:5]}  # Limit to 5 suggestions

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error - Path: {request.path}")
    flash('Página não encontrada.', 'error')
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error - Path: {request.path}, Error: {error}")
    flash('Erro interno do servidor. Tente novamente mais tarde.', 'error')
    return render_template('index.html'), 500

@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    logger.warning(f"403 error - Path: {request.path}")
    flash('Acesso negado.', 'error')
    return redirect(url_for('login'))

# Helper functions for data processing
def format_cpf(cpf):
    """Format CPF with proper masking"""
    if not cpf or len(cpf) < 11:
        return '***.***.***-**'
    
    # Keep only first 3 and last 2 digits visible
    return f"{cpf[:3]}.***.**-{cpf[-2:]}"

def format_process_number(number):
    """Format process number according to CNJ standard"""
    if not number:
        return ''
    
    # Remove any existing formatting
    clean_number = ''.join(filter(str.isdigit, number))
    
    if len(clean_number) == 20:
        # CNJ format: NNNNNNN-DD.AAAA.J.TR.OOOO
        return f"{clean_number[:7]}-{clean_number[7:9]}.{clean_number[9:13]}.{clean_number[13]}.{clean_number[14:16]}.{clean_number[16:]}"
    
    return number

def validate_cpf(cpf):
    """Validate Brazilian CPF"""
    # Remove non-numeric characters
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Check basic format
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    
    # Calculate first check digit
    sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digit1 = 11 - (sum1 % 11)
    if digit1 >= 10:
        digit1 = 0
    
    # Calculate second check digit
    sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digit2 = 11 - (sum2 % 11)
    if digit2 >= 10:
        digit2 = 0
    
    # Check if calculated digits match
    return int(cpf[9]) == digit1 and int(cpf[10]) == digit2

# Context processors for templates
@app.context_processor
def utility_processor():
    """Inject utility functions into templates"""
    return {
        'format_cpf': format_cpf,
        'format_process_number': format_process_number,
        'len': len
    }

# Before request handlers
@app.before_request
def log_request_info():
    """Log request information for debugging"""
    logger.debug(f"Request: {request.method} {request.path} - IP: {request.remote_addr}")

@app.after_request
def log_response_info(response):
    """Log response information"""
    logger.debug(f"Response: {response.status_code} for {request.path}")
    return response
