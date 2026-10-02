# 📝 Blog com Flask e MySQL

Blog completo com cadastro de usuários, login, posts e painel de administração, feito durante o curso com **Python (Flask)** e **MySQL**.

![Logo do blog](static/img/logo.png)

## Funcionalidades

**Usuários**
- Cadastro e login com senha criptografada (hash com Werkzeug)
- Criar, editar e excluir os próprios posts
- Página de perfil com troca de nome, usuário e foto
- Troca de senha

**Administrador**
- Dashboard com a lista de usuários e posts
- Ativar e desativar usuários
- Excluir usuários (os posts deles são apagados junto)
- Resetar a senha de um usuário

**Extras**
- Páginas personalizadas de erro 404 e 500
- Upload de foto de perfil

## Tecnologias

- **Python + Flask**: rotas, sessões e templates (Jinja2)
- **MySQL** com `mysql-connector-python`
- **Werkzeug**: hash de senhas
- HTML, CSS e JavaScript

## Estrutura

```
├── app.py           # rotas do Flask
├── db.py            # funções que acessam o banco
├── config.py        # chave secreta, admin e dados de conexão
├── scriptbd.sql     # criação do banco e das tabelas
├── templates/       # páginas HTML (login, cadastro, dashboard, perfil...)
└── static/          # CSS, JS, imagens e uploads
```

## Banco de dados

Duas tabelas, criadas pelo `scriptbd.sql`:

- **usuario**: id, nome, user, senha (hash), foto, data de cadastro e status (ativo ou não)
- **post**: id, título, conteúdo, data e o usuário que escreveu (excluído em cascata junto com o usuário)

## Como rodar localmente

1. Clone o repositório
   ```bash
   git clone https://github.com/julio-aurelio/blog.git
   cd blog
   ```
2. Instale as dependências
   ```bash
   pip install flask mysql-connector-python
   ```
3. Rode o `scriptbd.sql` no MySQL para criar o banco e as tabelas.
4. No `config.py`, coloque o usuário e a senha do seu MySQL e o nome do banco que o script criou (`blog_julio`).
5. Inicie o servidor
   ```bash
   python app.py
   ```
6. Abra `http://127.0.0.1:5000` no navegador.

---

Feito por **Julio Aurelio Souza** 😼
