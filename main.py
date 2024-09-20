import sqlite3
import shutil
from pathlib import Path
import os
from datetime import datetime
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def criar_banco():
    Path('data').mkdir(parents=True, exist_ok=True)
    conexao = sqlite3.connect('data/livraria.db')
    conexao.close()

def criar_tabela():
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    conexao.commit()
    conexao.close()

def adicionar_livro(titulo, autor, ano_publicacao, preco):
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                   (titulo, autor, ano_publicacao, preco))
    conexao.commit()
    conexao.close()
    fazer_backup()

def exibir_livros():
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conexao.close()

    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
    else:
        print("Nenhum livro cadastrado.")

def atualizar_preco(titulo, novo_preco):
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('UPDATE livros SET preco = ? WHERE titulo = ?', (novo_preco, titulo))
    conexao.commit()
    conexao.close()
    fazer_backup()

def remover_livro(titulo):
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('DELETE FROM livros WHERE titulo = ?', (titulo,))
    conexao.commit()
    conexao.close()
    fazer_backup()

def buscar_livros_por_autor(autor):
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros WHERE autor = ?', (autor,))
    livros = cursor.fetchall()
    conexao.close()

    if livros:
        for livro in livros:
            print(f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
    else:
        print("Nenhum livro encontrado para esse autor.")


def exportar_csv():
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conexao.close()

    Path('exports').mkdir(parents=True, exist_ok=True)
    caminho_csv = 'exports/livros_exportados.csv'


    with open(caminho_csv, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        escritor.writerows(livros)
    print("Dados exportados com sucesso para livros_exportados.csv.")


def adicionar_livro_csv(id, titulo, autor, ano_publicacao, preco):
    caminho_csv = 'exports/livros_exportados.csv'


    with open(caminho_csv, mode='a', newline='', encoding='utf-8') as arquivo_csv:
        escritor = csv.writer(arquivo_csv)
        escritor.writerow([id, titulo, autor, ano_publicacao, preco])
    print("Novo livro adicionado ao CSV.")


def modificar_livro_csv(titulo_alvo, novo_preco):
    caminho_csv = 'exports/livros_exportados.csv'
    livros_modificados = []


    with open(caminho_csv, mode='r', newline='', encoding='utf-8') as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)
        for linha in leitor:
            if linha['Título'] == titulo_alvo:
                linha['Preço'] = f'{novo_preco:.2f}'  # Alterar o preço
            livros_modificados.append(linha)


    with open(caminho_csv, mode='w', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço']
        escritor = csv.DictWriter(arquivo_csv, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(livros_modificados)
    print(f"Preço do livro '{titulo_alvo}' atualizado.")

def importar_csv():
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()

    with open('exports/livros_importados.csv', mode='r', encoding='utf-8') as arquivo_csv:
        leitor = csv.reader(arquivo_csv)
        next(leitor)  # Pular cabeçalho
        for linha in leitor:
            cursor.execute('INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)',
                           (linha[1], linha[2], int(linha[3]), float(linha[4])))

    conexao.commit()
    conexao.close()
    fazer_backup()
    print("Dados importados com sucesso de livros_importados.csv.")

def fazer_backup():
    data_atual = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    origem = 'data/livraria.db'
    destino = f'backups/backup_livraria_{data_atual}.db'

    Path('backups').mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    print(f"Backup realizado: {destino}")
    limpar_backups_antigos()

def limpar_backups_antigos():
    backups = sorted(Path('backups').glob('*.db'), key=os.path.getmtime, reverse=True)
    if len(backups) > 5:
        for backup in backups[5:]:
            os.remove(backup)
            print(f"Backup removido: {backup}")

def validar_entrada(titulo, autor, ano_publicacao, preco):
    if not titulo.strip() or not autor.strip():
        print("Título e autor não podem estar vazios!")
        return False
    if not isinstance(ano_publicacao, int) or ano_publicacao <= 0:
        print("Ano de publicação inválido!")
        return False
    if not isinstance(preco, float) or preco <= 0:
        print("Preço deve ser um número positivo!")
        return False
    return True

def gerar_relatorio_pdf():
    conexao = sqlite3.connect('data/livraria.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    conexao.close()

    c = canvas.Canvas("exports/relatorio_livros.pdf", pagesize=letter)
    c.drawString(100, 750, "Relatório de Livros")
    y = 720

    for livro in livros:
        c.drawString(100, y, f"ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}")
        y -= 20

    c.save()
    print("Relatório requerido gerado com sucesso.")

def gerar_relatorio_html():
        conexao = sqlite3.connect('data/livraria.db')
        cursor = conexao.cursor()
        cursor.execute('SELECT * FROM livros')
        livros = cursor.fetchall()
        conexao.close()

        with open('exports/relatorio_livros.html', 'w') as arquivo_html:
            arquivo_html.write('<html><head><title>Relatório de Livros</title></head><body>')
            arquivo_html.write('<h1>Relatório de Livros</h1>')
            arquivo_html.write('<ul>')
            for livro in livros:
                arquivo_html.write(
                    f'<li>ID: {livro[0]}, Título: {livro[1]}, Autor: {livro[2]}, Ano: {livro[3]}, Preço: R$ {livro[4]:.2f}</li>')
            arquivo_html.write('</ul>')
            arquivo_html.write('</body></html>')

        print("Relatório HTML gerado com sucesso.")


def menu():
    while True:
        print('=============================')
        print("\n1. Adicionar novo livro")
        print("2. Exibir todos os livros")
        print("3. Atualizar preço de um livro")
        print("4. Remover um livro")
        print("5. Buscar livros por autor")
        print("6. Exportar dados para CSV")
        print("7. Importar dados de CSV")
        print("8. Fazer backup do banco de dados")
        print("9. Gerar relatório PDF")
        print("10. Gerar relatório HTML")
        print("11. Sair")
        print('=============================')


        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            titulo = input("Título: ")
            autor = input("Autor: ")
            ano_publicacao = int(input("Ano de publicação: "))
            preco = float(input("Preço: "))
            adicionar_livro(titulo, autor, ano_publicacao, preco)
        elif opcao == '2':
            exibir_livros()
        elif opcao == '3':
            exibir_livros()
            titulo = input("Título do livro para atualizar o valor: ")
            novo_preco = float(input("Novo valor: "))
            atualizar_preco(titulo, novo_preco)
        elif opcao == '4':
            titulo = input("Título do livro para remover: ")
            remover_livro(titulo)
        elif opcao == '5':
            autor = input("Nome do autor para buscar livros: ")
            buscar_livros_por_autor(autor)
        elif opcao == '6':
            print('Exportar dados para CSV')
            exportar_csv()
        elif opcao == '7':
            print('Importando dados de CSV')
            importar_csv()
        elif opcao == '8':
            print('Fazendo backup do banco de dados')
            fazer_backup()
        elif opcao == '9':
            gerar_relatorio_pdf()
        elif opcao == '10':
            gerar_relatorio_html()
        elif opcao == '11':
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

def app():
    criar_banco()
    criar_tabela()
    menu()

app()

#pip install reportlab instalar para rodar
