import os
from app import app
import click

@app.cli.group()
def translate():
	#翻译和本地化命令
	pass

@translate.command()
def update():
	#更新所有语言
	if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
		raise RuntimeError('extract command failed')
	if os.system('pybabel update -i messages.pot -d app/translations'):
		raise RuntimeError('update command failed')
	os.remove('messages.pot')

@translate.command()
def compile():
	#编译所有语言
	if os.system('pybabel compile -d app/translations'):
		raise RuntimeError('compile command failed')

@translate.command()
@click.argument('lang')
def init(lang):
	#初始化一个新语言
	if os.system('pybabel extract -F babel.cfg -k _l -o messages.pot .'):
		raise RuntimeError('extract command failed')
	if os.system('pybabel init -i messages.pot -d app/translations -l ' +lang):
		raise RuntimeError('init command failed')
	os.remove('messages.pot')
