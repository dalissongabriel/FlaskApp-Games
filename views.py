from flask import render_template, request, redirect, flash,session, url_for, send_from_directory
from models import Jogo, Usuario
from dao import UsuarioDao, JogoDao
from jogateca import app, db
from helpers import deleta_arquivo, recupera_imagem
import os
import time

jogo_DAO = JogoDao(db)
usuario_DAO = UsuarioDao(db)

@app.route('/')
def index():
  if('usuario_logado' not in session or session['usuario_logado']  == None):
    return redirect(url_for('login',proxima='/'))
  lista = jogo_DAO.listar()
  return render_template('index.html', jogos=lista, titulo = 'Lista de jogos')

@app.route('/jogo/formulario' )
def show_form_new_game():

  if('usuario_logado' not in session or session['usuario_logado']  == None ):
    return redirect(url_for('login', proxima='/jogo/formulario'))

  titulo = "Criar novo jogo"
  return render_template('formulario_novo_jogo.html', titulo = titulo)

@app.route('/jogo/editar/<int:id>' )
def show_form_edit_game(id):

  if('usuario_logado' not in session or session['usuario_logado']  == None ):
    return redirect(url_for('login', proxima='/jogo/editar'))
  jogo = jogo_DAO.busca_por_id(id)
  titulo = "Editar jogo"
  nome_imagem = recupera_imagem(id)

  return render_template('formulario_editar_jogo.html', titulo=titulo, jogo = jogo, capa_jogo=nome_imagem)



@app.route('/jogo/excluir/<int:id>')
def delete(id):
  jogo_DAO.deletar(id)
  flash('Jogo excluído com sucesso')   
  return redirect(url_for('index'))


@app.route('/jogo/editar', methods=['POST'])
def update():
  
  nome = request.form['nome']
  categoria = request.form['categoria']
  console = request.form['console']
  id = request.form['id']
  jogo = Jogo(nome,categoria,console,id)

  arquivo = request.files['arquivo']
  upload_path = app.config['UPLOAD_PATH']
  timestamp = time.time()
  deleta_arquivo(jogo.id)
  arquivo.save(f'{upload_path}/capa_{jogo.id}-{timestamp}.jpg')

  jogo_DAO.salvar(jogo)
  return redirect(url_for('index'))

@app.route('/jogo/criar', methods=['POST'])
def create():
  if('usuario_logado' not in session or session['usuario_logado'] == None):
    return redirect(url_for('login',proxima='/jogo/formulario'))

  nome = request.form['nome']
  categoria = request.form['categoria']
  console = request.form['console']
  jogo = Jogo(nome,categoria, console)
  jogo_DAO.salvar(jogo)

  timestamp = time.time()
  arquivo = request.files['arquivo']
  upload_path = app.config['UPLOAD_PATH']
  arquivo.save(f'{upload_path}/capa_{jogo.id}-{timestamp}.jpg')
  return redirect(url_for('index'))

@app.route('/login')
def login():
  proxima = request.args.get('proxima') or '/'
  return render_template('formulario_login.html', titulo="Login na Jogoteca", proxima=proxima)

@app.route('/autenticar', methods=['POST'])
def authentication():
  usuario_login = request.form['usuario']
  senha_login = request.form['senha']
  proxima_pagina =  request.form['proxima']
  usuario = usuario_DAO.buscar_por_id(usuario_login)
  if usuario:
    print(usuario)
    if usuario.senha == senha_login: 
      session['usuario_logado'] = usuario_login
      flash(usuario_login+' logou com sucesso')   
      return redirect(proxima_pagina)    

  flash('Credencias erradas')
  return redirect(url_for('login',proxima=proxima_pagina))
  
@app.route("/logout")
def logout():

  session['usuario_logado'] = None
  flash('deslogou com sucesso')
  
  return redirect('/login')

@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)