# 🚨 CORREÇÃO DEFINITIVA - Deploy Heroku

## ❌ Problema Identificado
O arquivo `.python-version` existe no Replit mas não está sendo enviado para o Heroku via Git.

## ✅ SOLUÇÃO FINAL

Execute estes comandos exatamente na ordem:

### 1. Verificar Arquivos (no terminal local/Replit)
```bash
# Confirmar que está no diretório correto
pwd
ls -la .python-version Procfile

# Verificar conteúdo
echo "Conteúdo do .python-version:"
cat .python-version
echo "Deve mostrar: 3.13"
```

### 2. Preparar para Deploy
```bash
# Copiar requirements
cp heroku_requirements.txt requirements.txt

# Confirmar que .python-version está correto
echo "3.13" > .python-version

# Verificar estrutura final
ls -la .python-version requirements.txt Procfile app.py main.py
```

### 3. Comandos Git (EXECUTE VOCÊ MESMO)
```bash
# Inicializar Git se necessário
git init

# Adicionar TODOS os arquivos
git add .python-version
git add requirements.txt  
git add Procfile
git add app.py
git add main.py
git add templates/
git add static/
git add *.py
git add .

# Verificar o que será commitado
git status

# Commit
git commit -m "Fix Heroku deploy with Python 3.13"

# Verificar se .python-version está no commit
git show --name-only
```

### 4. Deploy Heroku
```bash
# Login
heroku login

# Criar app
heroku create seu-jusbrasil-clone

# IMPORTANTE: Verificar se .python-version vai ser enviado
git ls-files | grep python-version

# Deploy
git push heroku main
```

### 5. Se Ainda Der Erro

Execute este diagnóstico:
```bash
# Verificar o que está no Git
git ls-files | head -20

# Se .python-version não aparecer, adicione manualmente:
git add .python-version -f
git commit -m "Force add python-version"
git push heroku main
```

## 🔧 ALTERNATIVA: Usar pyproject.toml

Se o .python-version continuar não funcionando, crie um pyproject.toml:

```bash
cat > pyproject.toml << EOF
[tool.uv]
python = "3.13"

[project]
name = "jusbrasil-clone"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "Flask>=3.1.1",
    "gunicorn>=23.0.0",
    "requests>=2.32.4",
    "qrcode[pil]>=8.2",
    "pytz>=2025.2",
    "email-validator>=2.2.0",
    "psycopg2-binary>=2.9.10",
    "flask-sqlalchemy>=3.1.1"
]
EOF
```

## ⚡ COMANDO ÚNICO PARA TESTAR

Execute tudo de uma vez:
```bash
echo "3.13" > .python-version && \
cp heroku_requirements.txt requirements.txt && \
git add . && \
git commit -m "Heroku deploy fix" && \
heroku create meu-jusbrasil-$(date +%s) && \
git push heroku main
```

## 🎯 VARIÁVEIS DE AMBIENTE (após deploy)

```bash
heroku config:set \
SESSION_SECRET="$(openssl rand -base64 32)" \
ALLPAY_API_TOKEN="j1IZn0g233LV9kca0xvo2szLN7DSEQfI3EqYBBFWWvPGZK3ZCrtkTncGfIac" \
ALLPAY_PRODUCT_HASH="4grso93qjz" \
ALLPAY_OFFER_HASH="cu1a6348wi" \
IRONPAY_API_TOKEN="xYipgGdsLKk2779ZQHqpfm0TfZqJqJP8q5iRj272pogLoOhV5dJjY7jpftrD" \
IRONPAY_PRODUCT_HASH="oq5y39ejpa" \
IRONPAY_OFFER_HASH="ksrx34dlgv" \
CPF_API_TOKEN="1285fe4s-e931-4071-a848-3fac8273c55a"
```

## 📱 TESTE FINAL

Acesse: `https://SEU-APP.herokuapp.com/01542521157`

**IMPORTANTE**: O problema é que o Git não está enviando o arquivo .python-version. Execute os comandos Git manualmente!