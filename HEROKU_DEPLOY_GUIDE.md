# Guia de Deploy no Heroku - JusBrasil Clone

## Pré-requisitos

1. Conta no Heroku (https://heroku.com)
2. Heroku CLI instalado (https://devcenter.heroku.com/articles/heroku-cli)
3. Git instalado

## Estrutura de Arquivos para Deploy

Os seguintes arquivos foram criados/configurados para o Heroku:

### 1. Procfile
```
web: gunicorn main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

### 2. .python-version
```
3.11
```

### 3. app.json
Arquivo de configuração para deploy automático com todas as variáveis de ambiente necessárias.

### 4. heroku_requirements.txt
Lista de dependências Python (renomeie para requirements.txt durante o deploy).

## Passos para Deploy

### Método 1: Deploy via Git

1. **Inicializar repositório Git (se não existir)**
```bash
git init
git add .
git commit -m "Initial commit for Heroku deploy"
```

2. **Login no Heroku**
```bash
heroku login
```

3. **Criar aplicação no Heroku**
```bash
heroku create nome-da-sua-app
```

4. **Renomear arquivo de dependências**
```bash
mv heroku_requirements.txt requirements.txt
```

**IMPORTANTE**: O Heroku agora usa o gerenciador `uv` que requer `.python-version` em vez de `runtime.txt`

5. **Configurar variáveis de ambiente**
```bash
heroku config:set SESSION_SECRET="sua-chave-secreta-aqui"
heroku config:set ALLPAY_API_TOKEN="j1IZn0g233LV9kca0xvo2szLN7DSEQfI3EqYBBFWWvPGZK3ZCrtkTncGfIac"
heroku config:set ALLPAY_PRODUCT_HASH="4grso93qjz"
heroku config:set ALLPAY_OFFER_HASH="cu1a6348wi"
heroku config:set IRONPAY_API_TOKEN="xYipgGdsLKk2779ZQHqpfm0TfZqJqJP8q5iRj272pogLoOhV5dJjY7jpftrD"
heroku config:set IRONPAY_PRODUCT_HASH="oq5y39ejpa"
heroku config:set IRONPAY_OFFER_HASH="ksrx34dlgv"
heroku config:set CPF_API_TOKEN="1285fe4s-e931-4071-a848-3fac8273c55a"
```

6. **Deploy**
```bash
git add .
git commit -m "Configure for Heroku"
git push heroku main
```

### Método 2: Deploy via GitHub (Recomendado)

1. **Subir código para GitHub**
   - Crie um repositório no GitHub
   - Faça push do código

2. **Conectar Heroku ao GitHub**
   - Acesse o dashboard do Heroku
   - Vá em "Deploy" > "Deployment method" > "GitHub"
   - Conecte sua conta GitHub
   - Selecione o repositório

3. **Configurar variáveis de ambiente**
   - Vá em "Settings" > "Config Vars"
   - Adicione todas as variáveis listadas acima

4. **Deploy automático**
   - Ative "Automatic deploys" se desejar
   - Clique em "Deploy Branch"

### Método 3: Deploy com app.json (Um clique)

1. **Botão de Deploy Direto**
   
   [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/SEU_USUARIO/SEU_REPOSITORIO)

   Substitua a URL pelo seu repositório GitHub que contém o arquivo app.json.

## Configurações Importantes

### Variáveis de Ambiente Obrigatórias:

- `SESSION_SECRET`: Chave secreta para sessões Flask
- `ALLPAY_API_TOKEN`: Token da API All Pay
- `ALLPAY_PRODUCT_HASH`: Hash do produto All Pay
- `ALLPAY_OFFER_HASH`: Hash da oferta All Pay
- `IRONPAY_API_TOKEN`: Token da API Iron Pay (backup)
- `IRONPAY_PRODUCT_HASH`: Hash do produto Iron Pay
- `IRONPAY_OFFER_HASH`: Hash da oferta Iron Pay
- `CPF_API_TOKEN`: Token da API de consulta CPF

### Configurações de Produção:

1. **Logging**: Configurado para INFO em produção
2. **Debug**: Desabilitado automaticamente
3. **Workers**: 1 worker para tier básico do Heroku
4. **Timeout**: 120 segundos para requisições

## Verificação Pós-Deploy

1. **Verificar logs**
```bash
heroku logs --tail
```

2. **Abrir aplicação**
```bash
heroku open
```

3. **Testar funcionalidades**
   - Acesso com CPF: `https://sua-app.herokuapp.com/01542521157`
   - Página de checkout: `https://sua-app.herokuapp.com/checkout/01542521157`
   - API PIX: `https://sua-app.herokuapp.com/api/gerar-pix`

## Troubleshooting

### Erro de Build
- Verificar se `requirements.txt` existe e está correto
- Confirmar versão do Python no `runtime.txt`

### Erro de Port
- Heroku define a variável `PORT` automaticamente
- O código já está configurado para usar `os.environ.get('PORT', 5000)`

### Erro de Timeout
- APIs PIX podem demorar, timeout configurado para 120s
- Verificar logs para identificar gargalos

### Erro de Variáveis de Ambiente
- Confirmar que todas as variáveis estão configuradas no Heroku
- Usar `heroku config` para listar variáveis

## Monitoramento

1. **Logs em tempo real**
```bash
heroku logs --tail
```

2. **Métricas**
   - Acesse o dashboard do Heroku
   - Vá em "Metrics" para monitorar performance

3. **Alertas**
   - Configure alertas no Heroku para problemas de performance

## Custos

- **Tier Gratuito**: Disponível com limitações (dorme após 30min de inatividade)
- **Hobby ($7/mês)**: Recomendado para produção, sem sleep
- **Standard ($25/mês)**: Para maior tráfego

## Domínio Personalizado

Para usar domínio próprio:

```bash
heroku domains:add www.seudominio.com
```

Depois configure o DNS do seu provedor para apontar para o Heroku.

## Backup e Manutenção

1. **Backup do código**: Manter no GitHub
2. **Logs**: Heroku mantém por 1500 linhas gratuitamente
3. **Atualizações**: Use Git para atualizações

## Sucesso!

Sua aplicação JusBrasil Clone estará disponível em:
`https://nome-da-sua-app.herokuapp.com`

Todas as funcionalidades estarão operacionais:
- Consulta por CPF
- Integração PIX All Pay e Iron Pay
- Redirecionamento SPC Brasil
- Sistema de pagamentos