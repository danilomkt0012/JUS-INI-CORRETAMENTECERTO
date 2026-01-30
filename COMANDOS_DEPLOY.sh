#!/bin/bash
# Script de Deploy para Heroku - JusBrasil Clone

echo "🚀 Preparando deploy para Heroku..."

# 1. Criar arquivos necessários
echo "📝 Criando arquivos de configuração..."
echo "3.13" > .python-version
cp heroku_requirements.txt requirements.txt

# 2. Verificar arquivos
echo "✅ Verificando arquivos:"
ls -la .python-version requirements.txt Procfile pyproject.toml

echo "📄 Conteúdo .python-version:"
cat .python-version

echo "📄 Primeiras linhas requirements.txt:"
head -3 requirements.txt

# 3. Git setup
echo "📦 Configurando Git..."
git init 2>/dev/null || echo "Git já inicializado"
git add .
git add .python-version -f
git add requirements.txt -f
git add pyproject.toml -f
git commit -m "Deploy configuration for Heroku with Python 3.13"

# 4. Verificar se arquivos estão no Git
echo "🔍 Arquivos no Git:"
git ls-files | grep -E "python-version|requirements|Procfile|pyproject"

# 5. Deploy
echo "🚀 Fazendo deploy..."
APP_NAME="jusbrasil-clone-$(date +%s)"
heroku create $APP_NAME

echo "📤 Enviando para Heroku..."
git push heroku main

# 6. Configurar variáveis
echo "🔧 Configurando variáveis de ambiente..."
heroku config:set \
SESSION_SECRET="$(openssl rand -base64 32)" \
ALLPAY_API_TOKEN="j1IZn0g233LV9kca0xvo2szLN7DSEQfI3EqYBBFWWvPGZK3ZCrtkTncGfIac" \
ALLPAY_PRODUCT_HASH="4grso93qjz" \
ALLPAY_OFFER_HASH="cu1a6348wi" \
IRONPAY_API_TOKEN="xYipgGdsLKk2779ZQHqpfm0TfZqJqJP8q5iRj272pogLoOhV5dJjY7jpftrD" \
IRONPAY_PRODUCT_HASH="oq5y39ejpa" \
IRONPAY_OFFER_HASH="ksrx34dlgv" \
CPF_API_TOKEN="1285fe4s-e931-4071-a848-3fac8273c55a" \
--app $APP_NAME

echo "✅ Deploy concluído!"
echo "🌐 URL da aplicação:"
heroku info --app $APP_NAME | grep "Web URL"

echo "🧪 Testar em:"
echo "https://$APP_NAME.herokuapp.com/01542521157"