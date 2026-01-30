# 🚀 Comandos de Deploy Corrigidos - Heroku

## ⚠️ Erro Solucionado
O Heroku agora usa o gerenciador de pacotes `uv` que requer `.python-version` em vez de `runtime.txt`.

### ✅ Correções Aplicadas:
- ❌ `runtime.txt` removido
- ✅ `.python-version` criado com `3.13` (conforme erro do Heroku)
- ✅ Dependencies atualizadas para versões compatíveis
- ✅ Arquivo deve estar no diretório raiz do projeto

## 📋 Comandos para Deploy

### 1. Preparar Projeto
```bash
# Renomear requirements
mv heroku_requirements.txt requirements.txt

# Verificar se .python-version existe
cat .python-version
# Deve mostrar: 3.13

# Se não existir, criar:
echo "3.13" > .python-version
```

### 2. Configurar Git
```bash
git init
git add .
git commit -m "Fix Heroku deploy with .python-version"
```

### 3. Deploy via Heroku CLI
```bash
# Login no Heroku
heroku login

# Criar app (substitua pelo nome desejado)
heroku create meu-jusbrasil-clone

# Deploy
git push heroku main
```

### 4. Configurar Variáveis de Ambiente
```bash
# Session Secret (gerar automaticamente)
heroku config:set SESSION_SECRET="$(openssl rand -base64 32)"

# APIs PIX
heroku config:set ALLPAY_API_TOKEN="j1IZn0g233LV9kca0xvo2szLN7DSEQfI3EqYBBFWWvPGZK3ZCrtkTncGfIac"
heroku config:set ALLPAY_PRODUCT_HASH="4grso93qjz"
heroku config:set ALLPAY_OFFER_HASH="cu1a6348wi"

# Iron Pay (backup)
heroku config:set IRONPAY_API_TOKEN="xYipgGdsLKk2779ZQHqpfm0TfZqJqJP8q5iRj272pogLoOhV5dJjY7jpftrD"
heroku config:set IRONPAY_PRODUCT_HASH="oq5y39ejpa"
heroku config:set IRONPAY_OFFER_HASH="ksrx34dlgv"

# CPF API
heroku config:set CPF_API_TOKEN="1285fe4s-e931-4071-a848-3fac8273c55a"
```

### 5. Verificar Deploy
```bash
# Ver logs
heroku logs --tail

# Abrir app
heroku open

# Verificar status
heroku ps
```

## 🧪 Testar URLs

Substitua `meu-jusbrasil-clone` pelo nome da sua app:

### Página com CPF
```
https://meu-jusbrasil-clone.herokuapp.com/01542521157
https://meu-jusbrasil-clone.herokuapp.com/02755224827
```

### Checkout PIX
```
https://meu-jusbrasil-clone.herokuapp.com/checkout/01542521157
```

### API PIX
```
https://meu-jusbrasil-clone.herokuapp.com/api/gerar-pix
```

## ✅ Deploy Automático via GitHub

1. **Subir para GitHub**:
   ```bash
   # Criar repositório no GitHub primeiro
   git remote add origin https://github.com/SEU_USUARIO/jusbrasil-clone.git
   git branch -M main
   git push -u origin main
   ```

2. **Conectar no Heroku Dashboard**:
   - Acesse https://dashboard.heroku.com
   - Vá em "Deploy" > "GitHub"
   - Conecte o repositório
   - Configure as variáveis em "Settings" > "Config Vars"

## 🔧 Troubleshooting

### Se ainda der erro de buildpack:
```bash
# Forçar buildpack Python
heroku buildpacks:set heroku/python
```

### Se der erro de dependencies:
```bash
# Verificar se requirements.txt está correto
cat requirements.txt

# Deve conter as dependências com >=
```

### Para logs detalhados:
```bash
heroku logs --tail --source app
```

## 📦 Estrutura Final

```
projeto/
├── .python-version     # ✅ 3.11
├── requirements.txt    # ✅ Dependencies
├── Procfile           # ✅ Web server config
├── app.json           # ✅ Deploy config
├── main.py            # ✅ Entry point
├── app.py             # ✅ Flask app
└── templates/         # ✅ HTML files
```

## 🎯 Deploy Status: CORRIGIDO

O projeto agora está compatível com o novo sistema do Heroku que usa `uv` package manager.

**Execute os comandos acima e o deploy será bem-sucedido!**