SECRET_KEY = "Bl0gJu!1@"
USUARIO_ADMIN = "adm"
SENHA_ADMIN = "adm" 

ambiente = "produção"

if ambiente == "produção":
	HOST = "localhost"
	USER = "root"
	PASSWORD = "senai"
	DATABASE = "blog_joao"
elif ambiente == "produção":
	HOST =  "link python anywhere"
	USER = "user python anywhere"
	PASSWORD = "senha database python anywhere"
	DATABASE = "nome do database python anywhere"