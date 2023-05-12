import tkinter as tk
from tkinter import Tk, messagebox, filedialog
import sqlite3
import matplotlib.pyplot as plt
import customtkinter as tkc
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import datetime
import calendar

# Conexão com o banco de dados
conn = sqlite3.connect('financas.db')
c = conn.cursor()

# Criação da tabela de transações
c.execute('''CREATE TABLE IF NOT EXISTS transacoes
             (id INTEGER PRIMARY KEY,
              categoria TEXT,
              valor REAL)''')
conn.commit()

tkc.set_appearance_mode("System")
tkc.set_default_color_theme("blue")
app = tkc.CTk()
app.geometry('500x770')
app.title('Gerenciador Finanças')

imagem = tkc.CTkImage(dark_image=Image.open('dinheiro.png'), size=(45, 45))
logo = tkc.CTkLabel(app, text="", height=10, image=imagem)
logo.place(x=50,y=12)

intro = tkc.CTkLabel(app, text="Gerenciador Financeiro", font=('Arial', 28, 'bold'),  height=10)
intro.place(x=120,y=18)

linha = tkc.CTkLabel(app, text="", width=750, height=1, font=('Arial', 1), fg_color=('#34b2e4'))
linha.place(x=0,y=70)

valor_var = tkc.DoubleVar()
categoria_var = tkc.StringVar()

categorias = ["Alimentação", "Carro", "Lazer", "Saúde", "Educação", "Luz", "Água", "Gás", "Moradia", "Doações", "Internet", "Outros"]
tkc.CTkLabel(app, text="Categoria", font=("Arial", 14, 'bold')).place(x=135,y=85)
categoria_combobox = tkc.CTkComboBox(app, variable=categoria_var, values=categorias, corner_radius=12)
categoria_combobox.place(x=100, y=115)

tkc.CTkLabel(app, text="Valor", font=("Arial", 14, 'bold')).place(x=320,y=85)
valor_entry = tkc.CTkEntry(app, textvariable=valor_var, corner_radius=12)
valor_entry.place(x=270, y=115)

total_label = tkc.CTkLabel(app, text="Total de Contas Pagas: 0  Ganhos totais: R$ 0.00", font=('Arial', 14, 'bold'))
total_label.place(x=65, y=727)
    
def adicionar_transacao():
    try:
        if valor_var.get() in (0.0, 0) or not valor_var.get() or categoria_var.get() == '':
            messagebox.showerror("Erro", "Todos os campos precisam ser preenchidos")
        
        else:
            valor = valor_var.get()
            categoria = categoria_var.get()
            c.execute('INSERT INTO transacoes (categoria, valor) VALUES (?, ?)', (categoria, valor))
            conn.commit()
            atualizar_lista()
            gerar_grafico()

    except ValueError:
        messagebox.showerror("Erro", "Todos os campos precisam ser preenchidos")

# Função para remover uma transação
def remover_transacao():
    id = lista.get(tk.ACTIVE).split(':')[0]
    c.execute('DELETE FROM transacoes WHERE id=?', (id,))
    conn.commit()
    atualizar_lista()
    gerar_grafico()

# Função para atualizar a lista de transações
def atualizar_lista():
    lista.delete(0, tk.END)
    c.execute('SELECT * FROM transacoes')
    transacoes = c.fetchall()
    total_transacoes = len(transacoes)
    valor_total = sum(transacao[2] for transacao in transacoes)
    total_label.configure(text=f"Total de Contas Pagas: {total_transacoes}  Ganhos Totais: R$ {3000-valor_total:.2f}")
    for id, categoria, valor in transacoes:
        lista.insert(tk.END, f" {id}: {categoria}: R$ {valor:.2f}")

# Função para gerar o gráfico de despesas
def gerar_grafico():
    c.execute('SELECT categoria, SUM(valor) FROM transacoes GROUP BY categoria')
    dados = c.fetchall()
    categorias = [dado[0] for dado in dados]
    valores = [dado[1] for dado in dados]

    # Criação da figura do Matplotlib
    fig = plt.Figure(figsize=(4, 3), dpi=100, facecolor='#242424')
    ax = fig.add_subplot(111)
    pie = ax.pie(valores, labels=categorias, autopct='%1.1f%%')
    for text in pie[1]:
        text.set_color('white')
        text.set_font('Verdana')
    for text in pie[2]:
        text.set_color('white')
        text.set_weight('bold')
    ax.set_title('Distribuição de Despesas por Categorias', fontweight ="bold").set_color('white')
    

    # Criação do objeto FigureCanvasTkAgg e inserção na nova janela
    canvas = FigureCanvasTkAgg(fig, master=app)
    canvas.draw()
    canvas.get_tk_widget().place(x=52,y=430)

# Função para fazer o donwload do relatorio
def gerar_relatorio(resposta=''):
    hoje = datetime.date.today()
    ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
  
    if resposta =='': 
        if hoje.day == ultimo_dia:
            c.execute('SELECT * FROM transacoes')
            transacoes = c.fetchall()
            df = pd.DataFrame(transacoes, columns=['Id', 'Categoria', 'Valor'])
        
            total_transacoes = len(transacoes)
            valor_total = sum(transacao[2] for transacao in transacoes)
            
            df.loc[len(df)] = ['Número de despesas', total_transacoes, None]
            df.loc[len(df)] = ['Débito', valor_total, None]
            df.loc[len(df)] = ['Crédito', 3000 - valor_total, None]

            messagebox.showwarning("Relatório", "Chegou Final do Mês!!!\nEscolha uma pasta para colocar seu relatório.")

            folder_selected = filedialog.askdirectory()

            if folder_selected:
                nome_arquivo = f'{folder_selected}/relatorio_{hoje.month:02d}_{hoje.year}.xlsx'
                df.to_excel(nome_arquivo, index=False)
            else:
                messagebox.showerror("Erro", "Por favor, selecione uma pasta!!")
                gerar_relatorio()

    # Caso a resposta para gerar relatorio seja sim
    if resposta == 'yes':
        c.execute('SELECT * FROM transacoes')
        transacoes = c.fetchall()
        df = pd.DataFrame(transacoes, columns=['Id', 'Categoria', 'Valor'])
    
        total_transacoes = len(transacoes)
        valor_total = sum(transacao[2] for transacao in transacoes)
        
        df.loc[len(df)] = ['Número de despesas', total_transacoes, None]
        df.loc[len(df)] = ['Débito', valor_total, None]
        df.loc[len(df)] = ['Crédito', 3000 - valor_total, None]

        folder_selected = filedialog.askdirectory()

        if folder_selected:
            nome_arquivo = f'{folder_selected}/relatorio_{hoje.month:02d}_{hoje.year}.xlsx'
            df.to_excel(nome_arquivo, index=False)
        else:
            messagebox.showerror("Erro", "Por favor, selecione uma pasta!!")
            gerar_relatorio(resposta)

# Perguntar se quer gerar o relatório
def aviso():
    resposta = messagebox.askquestion("Relatório", "Um relatório será realizado no fim do mês.\nTem certeza que quer gerar um agora?")
    return resposta

# Criação da lista de transações
lista = tk.Listbox(app, bg='#343434', width=65, font=('Arial', 10, 'bold'), fg='white', highlightcolor='#34b2e4', highlightthickness=2, selectbackground='#34b2e4', relief="ridge")
lista.place(x=20, y=170)

adicionar_button = tkc.CTkButton(app, text="Adicionar", text_color='white', font=('Arial', 15, 'bold'), corner_radius=12, compound='top', fg_color=('#34b2e4'), command=adicionar_transacao)
adicionar_button.place(x=20, y=370)

remover_button = tkc.CTkButton(app, text="Remover", text_color='white', font=('Arial', 15, 'bold'), corner_radius=12, compound='top', fg_color=('#34b2e4'), command=remover_transacao)
remover_button.place(x=180, y=370)

remover_button = tkc.CTkButton(app, text="Gerar Relatório", text_color='white', font=('Arial', 15, 'bold'), corner_radius=12, compound='top', fg_color=('#34b2e4'), command=lambda:[gerar_relatorio(aviso())])
remover_button.place(x=340, y=370)

gerar_grafico()
atualizar_lista()
gerar_relatorio()
app.mainloop()

conn.close()

