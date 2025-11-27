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

app.config['UPLOAD_FOLDER'] = "static/uploads"


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
            return redirect('/login')
        
        if usuario == usuario_admin and senha == senha_admin:
            session['admin'] = True
            return redirect('/dashboard')
        
        # CORREÇÃO: Verificar se a função retornou algo válido
        resultado = verificar_usuario(usuario, senha)
        
        if resultado is None:
            flash("Usuario não encontrado. Tente novamente!")
            return render_template('/login.html')
        
        # Agora faz o unpacking
        sucesso, usuario_encontrado = resultado
        
        if sucesso:
            if usuario_encontrado['ativo'] == 0:
                flash("Usuário bloqueado, fale com o ADM")
                return redirect('/login')

            if usuario_encontrado['senha'] == '1234':
                session['idUsuario'] = usuario_encontrado['idUsuario']
                return render_template("nova_senha.html")

            session['idUsuario'] = usuario_encontrado['idUsuario']
            session['user'] = usuario_encontrado['user']
            session['foto'] = usuario_encontrado['foto']
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

        foto = "placeholder.jpg"

        resultado, erro = adicionar_usuario(nome, usuario, senha_hash, foto)

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

@app.route('/usuario/novasenha', methods =['POST','GET'])
def novasenha():
    if 'idUsuario' not in session:
        return redirect('/')
    if request.method == 'POST':
        senha = request.form['senha']
        confirmacao = request.form['confirmacao']

        if not senha or not confirmacao:
            flash('Preencha corretamente as senhas!')
            return render_template ('nova_senha.html')
        if senha != confirmacao:
            flash('As senhas estão diferentes!')
            return render_template('nova_senha.html')
        if senha == '1234':
            flash('A senha não pode ser a mesma!')
            return render_template('nova_senha.html')
        
        senha_hash = generate_password_hash(senha)
        idUsuario = session['idUsuario']
        sucesso = alterar_senha(senha_hash, idUsuario)
        if sucesso:
            flash("senha alterada com sucesso!")
            return redirect('/login')
        else:
            flash("Erro no cadastro da nova senha!")
            return render_template('nova_senha.html')


@app.route('/perfil', methods = ['GET', 'POST'])
def perfil():
    if 'user' not in session:
        return redirect('/')
    
    if request.method == 'GET':
        lista_usuarios = listar_usuarios()
        usuario = None
        for u in lista_usuarios:
            if u['idUsuario'] == session['idUsuario']:
                usuario = u
                break
        
        # VERIFICAÇÃO CRÍTICA - se usuário não foi encontrado
        if not usuario:
            flash("Erro: usuário não encontrado no banco de dados!")
            return redirect('/')
        
        return render_template('perfil.html', nome=usuario['nome'], user=usuario['user'], foto=usuario['foto'])

    if request.method == 'POST':
        nome = request.form['nome'].strip()
        user = request.form['user'].strip()
        foto = request.files['foto']
        idUsuario = session['idUsuario']
        nome_foto = ""

        if not nome or not user:
            flash("Os campos Nome e User não podem estar vazios!")
            return redirect('/perfil')
        
        if foto:
            if foto.filename == '':
                flash("Arquivo inválido!")
                return redirect('/perfil')
            
            extensao = foto.filename.rsplit('.',1)[-1].lower()
            if extensao not in ('png','jpg','webp'):
                flash("Extensão inválida!")
                return redirect('/perfil')
            
            if len(foto.read()) > 2 * 1024 * 1024:
                flash("Arquivo acima de 2MB não é aceito!")
                return redirect('/perfil')
            
            foto.seek(0)
            nome_foto = f"{idUsuario}.{extensao}"
    
        sucesso = editar_perfil(nome, user, nome_foto, idUsuario)
        if sucesso:
            if foto:
                foto.save(f"static/uploads/{nome_foto}")
            flash("Parabéns pela alteração, cada dia mais próximo de virar um piblle 100%😼","success")
        else:
            flash("Erro ao alterar seus dados, mas não desista ainda, você pode tentar denovo ou pedir ajuda para o piblle supremo (ADM)")

        return redirect('/perfil')

if __name__ == "__main__":
    app.run(debug=True)