# JusBrasil Clone

## Overview

This is a Flask-based web application that replicates core functionality of JusBrasil, a Brazilian legal platform for searching court processes and legal information. The application provides a user-friendly interface for searching legal processes by person name, CPF, CNPJ, or process number, displaying detailed information about legal proceedings and parties involved.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Uses Flask's Jinja2 templating system with a base template pattern for consistent UI
- **CSS Framework**: Tailwind CSS for responsive design and consistent styling
- **JavaScript**: Vanilla JavaScript for interactive functionality including form validation, tooltips, and loading states
- **Responsive Design**: Mobile-first approach optimized for various screen sizes

### Backend Architecture
- **Web Framework**: Flask (Python) with modular routing structure
- **Application Structure**: 
  - `app.py` - Main Flask application configuration
  - `routes.py` - URL routing and view functions (appears to be planned but not fully implemented)
  - `main.py` - Application entry point
- **Data Layer**: Currently uses in-memory sample data structures (SAMPLE_PERSONS, SAMPLE_PROCESSES) for demonstration
- **Session Management**: Flask sessions with configurable secret key

### Core Features
- **Search Functionality**: Multi-type search supporting names, CPF, CNPJ, and process numbers
- **Person Profiles**: Detailed views showing individual information and associated legal processes
- **Process Details**: Comprehensive process information including status, tribunal, and parties involved
- **Responsive Navigation**: Mobile-optimized header with search and user account access

### Data Models
The application uses dictionary-based data structures representing:
- **Persons**: ID, name, age range, location, masked CPF, process count
- **Processes**: ID, process number, tribunal, type, status, last update date, and associated parties

### Design Patterns
- **Template Inheritance**: Base template with block overrides for consistent layout
- **Modular CSS**: Custom CSS variables for brand colors and reusable component styles
- **Progressive Enhancement**: JavaScript functionality that degrades gracefully

## External Dependencies

### Frontend Libraries
- **Tailwind CSS**: CDN-hosted CSS framework for styling
- **Font Awesome**: Icon library for UI elements
- **Google Fonts**: Roboto font family for typography

### Backend Dependencies
- **Flask**: Core web framework
- **Python Standard Library**: Logging, OS environment variables

### Development Dependencies
- **Static Assets**: Custom CSS and JavaScript files served through Flask's static file handling

### Current Integrations
- **CPF API**: Full integration with Amnesia Tecnologia API for real user data
  - API URL: https://api.amnesiatecnologia.rocks/
  - Token: Configurado via CPF_API_TOKEN environment variable (default: 261207b9-0ec2-468a-ac04-f9d38a51da88)
  - Request Format: ?token={token}&cpf={cpf}
  - Returns: { "DADOS": { "cpf", "nome", "nome_mae", "data_nascimento", "sexo" } }
- **SPC Button**: Redirects to https://www.debitospc.com (appends user CPF)
- **BlackCat Pagamentos**: Gateway PIX principal ativo (GATEWAY ATUAL EM USO) - Versão Atualizada
  - **Gateway**: BlackCat Pagamentos (Nova API)
    - API Key: Configurada via BLACKCAT_API_KEY (secret)
    - API URL: https://api.blackcatpagamentos.online/api
    - Status: ✅ ATIVO - Gateway principal em produção
    - Features: 
      - Gera códigos PIX reais
      - Autenticação via Header X-API-Key
      - Suporta transações PIX com customer data completo
      - Verificação de status via GET /sales/status/{transactionId}
      - Webhook/postback URL configurável
      - Metadados e referência externa opcionais
      - Status suportados: PENDING, PAID, COMPLETED, APPROVED, CONFIRMED, EXPIRED, CANCELLED
    - Endpoints: 
      - /api/gerar-pix-blackcat (criação PIX)
      - /api/verificar-status-blackcat/<id> (verificação status)
    - Arquivo: blackcat_gateway.py
    - Request Body Format:
      - amount: valor em centavos
      - currency: "BRL"
      - paymentMethod: "pix"
      - items: array com título, quantidade, tangible
      - customer: name, email, phone, document (number, type)
      - pix: { expiresInDays: 2 }
      - postbackUrl, metadata, externalRef (opcionais)
    - Response Format:
      - transactionId: ID da transação (ex: TRX17678276292767ZNI9J)
      - status: PENDING, PAID, etc.
      - paymentData: qrCode, copyPaste, expiresAt
      - invoiceUrl: link para checkout
- **Dynamic User Data Generation**: 
  - Email: first name + CPF suffix + @cursodigital.com
  - Phone: Dynamic based on CPF (11 + CPF digits)
  - Address: Street number and ZIP code generated from CPF

### Heroku Deploy Configuration
The application is fully configured for Heroku deployment with:
- Procfile for gunicorn web server configuration
- runtime.txt specifying Python 3.11.6
- app.json for automatic deployment with environment variables
- Production logging configuration
- Port configuration for Heroku's dynamic port assignment
- All API credentials secured in environment variables

### Environment Configuration
- Session secret key configurable via environment variables
- Production/development logging levels
- Host and port configuration for deployment flexibility
- Nova Era Pagamentos credentials (Public Key, Secret Key) secured via environment variables
- CPF API credentials secured
- Ready for Heroku, Replit, or any cloud platform deployment

### Payment Gateway Integrations

#### 4M Payments (GATEWAY PRINCIPAL - ATIVO)
- **Status**: ✅ ATIVO - Gateway principal em produção
- **API URL**: https://app.4mpagamentos.com/api/v1
- **Token**: 3mpag_h0uymyduo_mgtqu1j9 (configurado via FOURM_API_TOKEN)
- **Features**:
  - Gera códigos PIX reais de R$ 24,90
  - Autenticação Bearer Token para criação (POST /payments)
  - Verificação de status via GET /transactions/{transaction_id} (endpoint público, sem autenticação)
  - Status suportados: waiting_payment, paid, expired, cancelled, pending
  - Suporte a product_id para configurações específicas de produtos
  - Sanitização automática de CPF e telefone (remove formatação)
- **Endpoints Flask**: 
  - `/api/gerar-pix` (criação de PIX - ENDPOINT PRINCIPAL)
  - `/api/verificar-pagamento/<transaction_id>` (verificação - ENDPOINT PRINCIPAL)
  - `/api/gerar-pix-4m` (criação de PIX - endpoint alternativo)
  - `/api/verificar-status-4m/<transaction_id>` (verificação - endpoint alternativo)
- **Arquivos**: four_m_gateway.py
- **Valor Fixo**: R$ 24,90
- **Descrição Padrão**: "Curso Digital"
- **Response Format**: {"success": true, "data": {"transaction_id": "4M...", "pix_code": "...", "status": "..."}}

#### Nova Era Pagamentos (GATEWAY SECUNDÁRIO - DISPONÍVEL)
- **Status**: ⚠️ DISPONÍVEL - Gateway secundário (não usado atualmente)
- **Public Key**: pk_yG6_FUX6tAUnZrzx4TUfvf-tyDeECA5ikwn3cp0uDAG-_okM
- **Secret Key**: sk_M7x3fbfpQjgKPX2G5Hu54nIe7urS-YpLm-oG3q5YP-JeVA5Y (via environment variable)
- **API URL**: https://api.novaera-pagamentos.com/api/v1
- **Features**: 
  - Gera códigos PIX reais de R$ 24,90
  - Autenticação Basic Auth (base64 de secret:public_key)
  - Suporta transações PIX com customer data completo
  - Verificação de status via GET /transactions/{id}
  - Status suportados: waiting_payment, paid, expired, cancelled, failed
- **Arquivos**: nova_era_gateway.py, NOVA_ERA_PAGAMENTOS_DOCS.md
- **Nota**: Código disponível mas não integrado aos endpoints principais

### Architectural Changes (September-November 2025)
- **Removed**: AllPay, AssetPay, For4Payments, Vexy Payments gateways
- **November 2025**: Nova Era Pagamentos implementado inicialmente
- **November 2025**: 4M Payments re-implementado e definido como gateway principal
- **Architecture**: Gateway PIX principal: 4M Payments
- **Benefits**: API estável, endpoint público para verificação, PIX codes reais