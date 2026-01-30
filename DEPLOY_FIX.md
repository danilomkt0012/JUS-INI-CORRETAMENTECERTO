# 🔧 CORREÇÃO DEFINITIVA - Deploy Heroku

## Problema Identificado
O Heroku não está encontrando o arquivo `.python-version` ou ele não está no formato correto.

## ✅ Solução Completa

Execute estes comandos na ordem:

### 1. Preparar Arquivos
```bash
# Garantir que .python-version existe com Python 3.13
echo "3.13" > .python-version

# Renomear requirements
cp heroku_requirements.txt requirements.txt

# Verificar arquivos
ls -la .python-version requirements.txt Procfile
```

### 2. Confirmar Conteúdo dos Arquivos

**Arquivo .python-version deve conter apenas:**
```
3.13
```

**Arquivo requirements.txt deve conter:**
```
Flask>=3.1.1
gunicorn>=23.0.0
requests>=2.32.4
qrcode[pil]>=8.2
pytz>=2025.2
email-validator>=2.2.0
psycopg2-binary>=2.9.10
flask-sqlalchemy>=3.1.1
```

### 3. Deploy
```bash
# Adicionar tudo ao Git
git add .

# Commit
git commit -m "Fix Python version for Heroku deploy"

# Deploy (substitua meu-app pelo nome desejado)
heroku create meu-jusbrasil-clone
git push heroku main
```

### 4. Configurar Variáveis
```bash
heroku config:set SESSION_SECRET="$(date | md5sum | cut -c1-32)"
heroku config:set ALLPAY_API_TOKEN="j1IZn0g233LV9kca0xvo2szLN7DSEQfI3EqYBBFWWvPGZK3ZCrtkTncGfIac"
heroku config:set ALLPAY_PRODUCT_HASH="4grso93qjz"
heroku config:set ALLPAY_OFFER_HASH="cu1a6348wi"
heroku config:set IRONPAY_API_TOKEN="xYipgGdsLKk2779ZQHqpfm0TfZqJqJP8q5iRj272pogLoOhV5dJjY7jpftrD"
heroku config:set IRONPAY_PRODUCT_HASH="oq5y39ejpa"
heroku config:set IRONPAY_OFFER_HASH="ksrx34dlgv"
heroku config:set CPF_API_TOKEN="1285fe4s-e931-4071-a848-3fac8273c55a"
```

## 🎯 Checklist de Verificação

Antes do deploy, confirme:

- [ ] Arquivo `.python-version` existe e contém `3.13`
- [ ] Arquivo `requirements.txt` existe (não heroku_requirements.txt)
- [ ] Arquivo `Procfile` existe
- [ ] Está no diretório raiz do projeto
- [ ] Comandos git add/commit executados

## 🔍 Se Ainda Der Erro

Execute estes diagnósticos:

```bash
# Verificar estrutura
ls -la | grep -E "python|requirements|Procfile"

# Verificar conteúdo
echo "=== .python-version ==="
cat .python-version
echo "=== requirements.txt ==="
head -3 requirements.txt
echo "=== Procfile ==="
cat Procfile
```

## 📱 URLs para Testar Após Deploy

```
https://meu-jusbrasil-clone.herokuapp.com/01542521157
https://meu-jusbrasil-clone.herokuapp.com/checkout/01542521157
```

**Este deploy deve funcionar sem erros!**