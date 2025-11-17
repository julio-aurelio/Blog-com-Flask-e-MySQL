from flask import Flask, render_template, request, redirect, flash, session
import mysql.connector
from db import *
from dotenv import load_dotenv
import os
from werkzeug.security import generate_password_hash, check_password_hash

#carregar esse arquivo para o Python
load_dotenv()

#Acessar as variaveis
secret_key = os.getenv("SECRET_KEY")
usuario_admin = os.getenv("USUARIO_ADMIN")
senha_admin = os.getenv("SENHA_ADMIN")

#essa linha cria o um app web usando Flask
app = Flask(__name__)
app.secret_key = secret_key #chave secreta

#rota inicial do seu site
@app.route('/')
def index():
    postagens = listar_post()
    return render_template('index.html', postagens = postagens)

#rota do form de postagem
@app.route('/novopost', methods=['GET','POST'])
def novopost():
    if request.method == 'GET':
        return redirect ('/')
    if 'idUsuario' not in session:
        flash("Você precisa estar logado para postar!")
        return redirect('/login')
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()
        idUsuario = session['idUsuario']

        if not titulo or not conteudo:
            flash("Preencha todos os campos")
            return redirect('/')
        
        post = adicionar_post(titulo, conteudo, idUsuario)
        if post:
            flash ("Post realizado com sucesso")
            return redirect ('/')
        else:
            flash  ("ERRO! Falha ao postar!")
            postagens = listar_post()
            return render_template('index.html', postagens=postagens)

@app.route('/deletarpost/<int:idPost>', methods=['GET','POST'])
def deletarpost(idPost):
    if 'idUsuario' not in session and not session.get('admin'):
        print("Usuário não autorizado acessando rota excluir.")
        flash("Você precisa estar logado para excluir posts!")
        return redirect('/')

    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            if not session.get('admin'):
                cursor.execute("SELECT idUsuario FROM post WHERE idPost = %s", (idPost,))
                autor_post = cursor.fetchone()

                if not autor_post or autor_post['idUsuario'] != session.get('idUsuario'):
                    print("Tentativa de exclusão inválida!")
                    flash("Você não pode excluir posts de outros usuários!")
                    return redirect('/')
            cursor.execute("DELETE FROM post WHERE idPost = %s", (idPost,))
            conexao.commit()
            flash("Post excluído com sucesso!")
            print(f"Post {idPost} excluído com sucesso!")

            if 'admin' in session:
                return redirect('/dashboard')
            else:
                return redirect('/')

    except mysql.connector.Error as erro:
        print(f"ERRO DE BD! Erro: {erro}")
        flash("Ops! Tente mais tarde!")
        return redirect('/')
    
@app.route('/editarpost/<int:idPost>', methods=['GET','POST'])
def editarpost(idPost):
    if 'user' not in session or 'admin' in session:
        return redirect('/')

    # Verifica se o post pertence ao usuário
    with conectar() as conexao:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT idUsuario FROM post WHERE idPost = %s", (idPost,))
        autor = cursor.fetchone()

        if not autor:
            flash("Post não encontrado!")
            return redirect('/')

        if autor['idUsuario'] != session['idUsuario']:
            print("Tentativa de acesso inválida")
            return redirect('/')

    if request.method == "GET":
        try:
            with conectar() as conexao:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT * FROM post WHERE idPost = %s", (idPost,))
                post = cursor.fetchone()
                postagens = listar_post()
                return render_template('index.html', postagens=postagens, post=post)

        except mysql.connector.Error as erro:
            print(f"ERRO DE DB!ERRO:{erro}")
            flash("Houve um erro! Tente mais tarde!")
            return redirect ('/')

    if request.method == "POST":
        titulo = request.form['titulo'].strip()
        conteudo = request.form['conteudo'].strip()

        if not titulo or not conteudo:
            flash("Preencha todos os campos!")
            return redirect(f'/editarpost/{idPost}')

        sucesso = atualizar_post(titulo, conteudo, idPost)
            
        if sucesso:    
            flash("Post alterado com sucesso")
        else:
            flash("Falha ao alterar o post! Tente mais tarde")
        return redirect('/')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template('/login.html')
    elif request.method == "POST":
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()
        if not usuario or not senha:
            flash("Preencha todos os campos")
            return redirect('/')
        if not usuario or not senha:
            flash("Preencha todos os campos")
            return redirect('/login')
        if usuario == usuario_admin and senha == senha_admin:
            session['admin'] = True
            return redirect('/dashboard')
        resultado, usuario_encontrado = verificar_usuario(usuario, senha)
        if resultado:
            if usuario_encontrado['ativo'] == 0:
                flash("Usuario bloqueado, fale com o ADM")
                return redirect('/login')

            if usuario_encontrado['senha'] == '1234':
                session['idUsuario'] = usuario_encontrado['idUsuario']
                return render_template("nova_senha.html")

            session['idUsuario'] = usuario_encontrado['idUsuario']
            session['user'] = usuario_encontrado['user']
            return redirect('/')
        else:
            flash("Credenciais inválidas!")
            return render_template('/login.html')
        


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if not session or not session.get('admin'):
        return redirect('/')

    usuarios = listar_usuarios()
    posts = listar_post()
    return render_template('dashboard.html', posts=posts, usuarios=usuarios)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('cadastro.html')
    elif request.method == 'POST':
        nome = request.form['nome'].strip()
        usuario = request.form['user'].lower().strip()
        senha = request.form['senha'].strip()
        if not nome or not usuario or not senha:
            flash('Preencha todos os campos!Ligero você fio😠')
            return redirect('/register')
        
        senha_hash =  generate_password_hash(senha)

        resultado, erro = adicionar_usuario(nome, usuario, senha_hash)

        if resultado:
            flash("usuario cadastrado com sucesso!")
            return redirect('/login')
        else:
            if erro.errno == 1062:
                flash("Esse nome de usuario já foi cadastrado! tente outro!")
            else:
                flash("Erro ao cadastro! procuro o suporte")
            return redirect('/register')
        
@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('erro404.html')

@app.errorhandler(500)
def pagina_nao_encontrada(error):
    return render_template('erro500.html')

@app.route('/usuario/status/<int:idUsuario>')
def status_usuario(idUsuario):
    if not session:
        return redirect('/')
    
    sucesso = alterar_status(idUsuario)

    if sucesso:
        flash('Status alterado com sucesso!')
    else:
        flash("Erro na alteração so status!")

    return redirect('/dashboard')

@app.route('/usuario/excluir/<int:idUsuario>') 
def excluir_usuario(idUsuario):
    if 'admin' not in session:
        return redirect('/')
    
    sucesso = delete_usuario(idUsuario)

    if sucesso:
        flash("Usuario excluido com sucesso")
    else:
        flash("Erro na exclusão do usuario")
    
    return redirect('/dashboard')


@app.route('/usuario/reset/<int:idUsuario>')
def reset(idUsuario):
    if 'admin' not in session:
        return redirect('/')
    sucesso = reset_senha(idUsuario)
    if sucesso:
        flash("Senha restada com sucesso!")
    else: 
        flash("Falha ao resetar a senha!")
    return redirect('/dashboard')
#executar codigo
if __name__ == "__main__":
    app.run(debug=True)