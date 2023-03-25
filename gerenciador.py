import tkinter as tk
import sqlite3
import matplotlib.pyplot as plt
import customtkinter as tkc
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Conexão com o banco de dados
conn = sqlite3.connect('financas.db')
c = conn.cursor()

# Criação da tabela de transações
c.execute('''CREATE TABLE IF NOT EXISTS transacoes
             (id INTEGER PRIMARY KEY,
              nome TEXT,
              valor REAL,
              categoria TEXT)''')
conn.commit()

tkc.set_appearance_mode("System")
tkc.set_default_color_theme("blue")
app = tkc.CTk()
app.geometry('500x770')
app.title('Gerenciador Finanças')

#logo
imagem = tkc.CTkImage(dark_image=Image.open('dinheiro.png'), size=(45, 45))
logo = tkc.CTkLabel(app, text="", height=10, image=imagem)
logo.place(x=50,y=12)

#texto intro
intro = tkc.CTkLabel(app, text="Gerenciador Financeiro", font=('Arial', 28, 'bold'),  height=10)
intro.place(x=120,y=18)

linha = tkc.CTkLabel(app, text="", width=750, height=1, font=('Arial', 1), fg_color=('#34b2e4'))
linha.place(x=0,y=70)

# Criação dos campos de entrada para nome, valor e categoria
nome_var = tkc.StringVar()
valor_var = tkc.DoubleVar()
categoria_var = tkc.StringVar()

tkc.CTkLabel(app, text="Nome", font=("Arial", 14, 'bold')).place(x=70,y=85)
nome_entry = tkc.CTkEntry(app, textvariable=nome_var)
nome_entry.place(x=20, y=115)

tkc.CTkLabel(app, text="Valor", font=("Arial", 14, 'bold')).place(x=230,y=85)
valor_entry = tkc.CTkEntry(app, textvariable=valor_var)
valor_entry.place(x=180, y=115)

tkc.CTkLabel(app, text="Categoria", font=("Arial", 14, 'bold')).place(x=380,y=85)
categoria_entry = tkc.CTkEntry(app, textvariable=categoria_var)
categoria_entry.place(x=340, y=115)

# Criação do label para exibir o total de transações e o valor total
total_label = tkc.CTkLabel(app, text="Total de pagamentos: 0  Valor total: R$ 0.00", font=('Arial', 14, 'bold'))
total_label.place(x=85, y=727)

# Função para adicionar uma transação
def adicionar_transacao():
    nome = nome_var.get()
    valor = valor_var.get()
    categoria = categoria_var.get()
    c.execute('INSERT INTO transacoes (nome, valor, categoria) VALUES (?, ?, ?)', (nome, valor, categoria))
    conn.commit()
    atualizar_lista()
    gerar_grafico()

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
    total_label.configure(text=f"Total de pagamentos: {total_transacoes}  Valor total: R$ {2400-valor_total:.2f}")
    for id, nome, valor, categoria in transacoes:
        lista.insert(tk.END, f"{id}: {nome}: R$ {valor:.2f}: {categoria}")

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

# Criação da lista de transações
lista = tk.Listbox(app, bg='#343434', width=60, font=('Arial', 10, 'bold'), fg='white', highlightcolor='#34b2e4', highlightthickness=2, selectbackground='#34b2e4')
lista.place(x=40, y=170)

# Criação dos botões
adicionar_button = tkc.CTkButton(app, text="Adicionar", text_color='white', font=('Arial', 15, 'bold'), corner_radius=10, compound='top', fg_color=('#34b2e4'), command=adicionar_transacao)
adicionar_button.place(x=100, y=370)

remover_button = tkc.CTkButton(app, text="Remover", text_color='white', font=('Arial', 15, 'bold'), corner_radius=10, compound='top', fg_color=('#34b2e4'), command=remover_transacao)
remover_button.place(x=270, y=370)

gerar_grafico()
atualizar_lista()
app.mainloop()

# Fechamento do banco de dados
conn.close()

