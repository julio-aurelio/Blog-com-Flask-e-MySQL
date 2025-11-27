import mysql.connector
from werkzeug.security import check_password_hash

def conectar():
    conexao = mysql.connector.connect(
        host= "localhost",
        user="root",
        password = "senai",
        database="blog_julio"
    )

    if conexao.is_connected():
        print("conexão com BD OK!")
    
    return conexao

def listar_post():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT p.*,u.user, u.foto FROM post p INNER JOIN usuario u ON u.idUsuario = p.idUsuario WHERE u.ativo = 1 ORDER BY idPost DESC")
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB!ERRO:{erro}")
        return []

def listar_usuarios():
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuario")
            return cursor.fetchall()
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB!ERRO:{erro}")
        return []

def adicionar_post(titulo, conteudo, idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO post(titulo, conteudo, idUsuario) VALUES (%s, %s, %s)"
            cursor.execute(sql, (titulo, conteudo, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False

#CADASTRA PESSOAS
def adicionar_usuario(nome, usuario, senha, foto):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "INSERT INTO usuario(nome, user, senha, foto) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (nome, usuario, senha, foto))
            conexao.commit()
            return True, "ok"
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB!ERRO:{erro}")
        return False, erro
    
def verificar_usuario(usuario, senha):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT * FROM usuario WHERE user = %s"
            cursor.execute(sql, (usuario,))
            usuario_encontrado = cursor.fetchone()
            if usuario_encontrado:
                if usuario_encontrado['senha'] == '1234'and senha == '1234' :
                    return True, usuario_encontrado
                
                if check_password_hash(usuario_encontrado['senha'], senha):
                    return True, usuario_encontrado
                return False, None
            conexao.commit()
    except mysql.connector.Error as erro:
        print(f"ERRO DE DB!ERRO:{erro}")
        return False, None
    
def alterar_status(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "SELECT ativo FROM usuario WHERE idUsuario = %s;"
            cursor.execute(sql,(idUsuario,))
            status = cursor.fetchone()

            if status['ativo']:
                sql = "UPDATE usuario SET ativo = 0 WHERE idUsuario = %s"
            else:
                sql = "UPDATE usuario SET ativo = 1 WHERE idUsuario = %s"

            cursor.execute(sql,(idUsuario,))
            conexao.commit()
            return True

    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False, None
    

def delete_usuario(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "DELETE FROM usuario WHERE idUsuario = %s"
            cursor.execute(sql,(idUsuario,))
            status = cursor.fetchone()
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False, None
    
def atualizar_post(titulo,conteudo,idPost):    
    try:
        with conectar() as conexao:
            cursor = conexao.cursor()
            sql = "UPDATE post SET titulo=%s, conteudo=%s WHERE idPost = %s"
            cursor.execute(sql, (titulo,conteudo,idPost))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False
    
def reset_senha(idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "UPDATE usuario SET senha = '1234' WHERE idUsuario = %s"
            cursor.execute(sql, (idUsuario,))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False
    

def alterar_senha(senha_hash,idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            sql = "UPDATE usuario SET senha = %s WHERE idUsuario = %s"
            cursor.execute(sql, (senha_hash, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False
    

def editar_perfil(nome,user,nome_foto,idUsuario):
    try:
        with conectar() as conexao:
            cursor = conexao.cursor(dictionary=True)
            if nome_foto:
                sql = "UPDATE usuario SET nome = %s, user = %s, foto = %s WHERE idUsuario = %s"
                cursor.execute(sql, (nome, user,nome_foto, idUsuario))
            else:
                sql = "UPDATE usuario SET nome = %s, user = %s WHERE idUsuario = %s"
                cursor.execute(sql, (nome, user, idUsuario))
            conexao.commit()
            return True
    except mysql.connector.Error as erro:
        conexao.rollback()
        print(f"ERRO DE DB!ERRO:{erro}")
        return False