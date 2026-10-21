
from datetime import datetime, timedelta
import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk


class SistemaBibliotecaApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Sistema de Biblioteca")
    self.root.geometry("700x550")

    # Arquivo para persistência de dados
    self.arquivo_dados = "dados_biblioteca.json"

    # Bancos de dados (carregados do arquivo ou vazios)
    self.livros = []
    self.emprestimos = []
    self.id_contador = 1

    self.carregar_dados()

    # Sistema de Abas (Notebook)
    self.notebook = ttk.Notebook(root)
    self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

    # Criação das Abas
    self.aba_livros = ttk.Frame(self.notebook)
    self.aba_emprestimos = ttk.Frame(self.notebook)

    self.notebook.add(self.aba_livros, text="Gerenciar Acervo")
    self.notebook.add(self.aba_emprestimos, text="Gerenciar Empréstimos")

    # Monta o conteúdo de cada aba
    self.criar_interface_livros()
    self.criar_interface_emprestimos()

    # Atualiza as tabelas logo na inicialização com os dados carregados
    self.atualizar_tabelas()

  # ==========================================
  # PERSISTÊNCIA DE DADOS (JSON)
  # ==========================================
  def salvar_dados(self):
    # Prepara os empréstimos convertendo a data para string antes de salvar
    emprestimos_para_salvar = []
    for emp in self.emprestimos:
      emp_copia = emp.copy()
      emp_copia["data_limite"] = emp["data_limite"].strftime("%Y-%m-%d")
      emprestimos_para_salvar.append(emp_copia)

    dados = {
        "id_contador": self.id_contador,
        "livros": self.livros,
        "emprestimos": emprestimos_para_salvar,
    }

    try:
      with open(self.arquivo_dados, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    except Exception as e:
      messagebox.showerror(
          "Erro", f"Não foi possível salvar os dados no arquivo: {e}"
      )

  def carregar_dados(self):
    if os.path.exists(self.arquivo_dados):
      try:
        with open(self.arquivo_dados, "r", encoding="utf-8") as f:
          dados = json.load(f)
          self.id_contador = dados.get("id_contador", 1)
          self.livros = dados.get("livros", [])

          # Converte a string de data de volta para o objeto datetime
          emprestimos_carregados = dados.get("emprestimos", [])
          self.emprestimos = []
          for emp in emprestimos_carregados:
            emp["data_limite"] = datetime.strptime(
                emp["data_limite"], "%Y-%m-%d"
            )
            self.emprestimos.append(emp)
      except Exception as e:
        messagebox.showerror(
            "Erro", f"Não foi possível carregar os dados salvos: {e}"
        )

  # ==========================================
  # ABA 1: GERENCIAMENTO DE LIVROS (ACERVO)
  # ==========================================
  def criar_interface_livros(self):
    frame_cad = tk.LabelFrame(
        self.aba_livros, text=" Cadastrar Novo Livro ", padx=10, pady=10
    )
    frame_cad.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_cad, text="Título do Livro:").grid(
        row=0, column=0, sticky="w", pady=2
    )
    self.entry_livro = tk.Entry(frame_cad, width=35)
    self.entry_livro.grid(row=0, column=1, pady=2)

    btn_cad_livro = tk.Button(
        frame_cad,
        text="Cadastrar Livro",
        bg="#4CAF50",
        fg="white",
        command=self.cadastrar_livro,
    )
    btn_cad_livro.grid(row=1, column=0, columnspan=2, pady=8)

    frame_list = tk.LabelFrame(
        self.aba_livros, text=" Livros no Acervo ", padx=10, pady=10
    )
    frame_list.pack(fill="both", expand=True, padx=10, pady=5)

    self.tabela_livros = ttk.Treeview(
        frame_list, columns=("ID", "Título", "Status"), show="headings"
    )
    self.tabela_livros.heading("ID", text="ID")
    self.tabela_livros.heading("Título", text="Título do Livro")
    self.tabela_livros.heading("Status", text="Status")
    self.tabela_livros.pack(fill="both", expand=True)

  def cadastrar_livro(self):
    titulo = self.entry_livro.get().strip()

    if not titulo:
      messagebox.showerror(
          "Erro", "O título do livro não pode estar vazio!"
      )
      return

    for livro in self.livros:
      if livro["titulo"].lower() == titulo.lower():
        messagebox.showerror("Erro", "Este livro já está cadastrado no acervo!")
        return

    self.livros.append(
        {"id": self.id_contador, "titulo": titulo, "disponivel": True}
    )
    self.id_contador += 1

    self.entry_livro.delete(0, tk.END)
    self.salvar_dados()
    self.atualizar_tabelas()
    messagebox.showinfo("Sucesso", "Livro cadastrado com sucesso!")

  # ==========================================
  # ABA 2: GERENCIAMENTO DE EMPRÉSTIMOS
  # ==========================================
  def criar_interface_emprestimos(self):
    frame_emp = tk.LabelFrame(
        self.aba_emprestimos, text=" Realizar Empréstimo ", padx=10, pady=10
    )
    frame_emp.pack(fill="x", padx=10, pady=10)

    tk.Label(frame_emp, text="Selecionar Livro:").grid(
        row=0, column=0, sticky="w", pady=2
    )
    self.combo_livros = ttk.Combobox(frame_emp, state="readonly", width=33)
    self.combo_livros.grid(row=0, column=1, pady=2)

    tk.Label(frame_emp, text="Nome do Usuário:").grid(
        row=1, column=0, sticky="w", pady=2
    )
    self.entry_usuario = tk.Entry(frame_emp, width=35)
    self.entry_usuario.grid(row=1, column=1, pady=2)

    tk.Label(
        frame_emp, text="Dias de Empréstimo (Prazo):"
    ).grid(row=2, column=0, sticky="w", pady=2)
    self.entry_prazo = tk.Entry(frame_emp, width=35)
    self.entry_prazo.insert(0, "7")
    self.entry_prazo.grid(row=2, column=1, pady=2)

    btn_realizar_emp = tk.Button(
        frame_emp,
        text="Realizar Empréstimo",
        bg="#2196F3",
        fg="white",
        command=self.realizar_emprestimo,
    )
    btn_realizar_emp.grid(row=3, column=0, columnspan=2, pady=8)

    frame_list_emp = tk.LabelFrame(
        self.aba_emprestimos, text=" Histórico de Empréstimos ", padx=10, pady=10
    )
    frame_list_emp.pack(fill="both", expand=True, padx=10, pady=5)

    btn_devolver = tk.Button(
        frame_list_emp,
        text="Devolver Livro Selecionado",
        bg="#FF9800",
        fg="white",
        command=self.devolver_emprestimo,
    )
    btn_devolver.pack(side="right", padx=5, anchor="n")

    self.tabela_emprestimos = ttk.Treeview(
        frame_list_emp,
        columns=("Livro", "Usuário", "Data Limite", "Status", "Multa"),
        show="headings",
    )
    self.tabela_emprestimos.heading("Livro", text="Livro")
    self.tabela_emprestimos.heading("Usuário", text="Usuário")
    self.tabela_emprestimos.heading("Data Limite", text="Data Limite")
    self.tabela_emprestimos.heading("Status", text="Status")
    self.tabela_emprestimos.heading("Multa", text="Multa (R$)")

    self.tabela_emprestimos.column("Livro", width=120)
    self.tabela_emprestimos.column("Usuário", width=100)
    self.tabela_emprestimos.column("Data Limite", width=80, anchor="center")
    self.tabela_emprestimos.column("Status", width=90, anchor="center")
    self.tabela_emprestimos.column("Multa", width=80, anchor="center")

    self.tabela_emprestimos.pack(fill="both", expand=True, side="left")

  def realizar_emprestimo(self):
    livro_selecionado = self.combo_livros.get()
    usuario = self.entry_usuario.get().strip()
    prazo_str = self.entry_prazo.get().strip()

    if not livro_selecionado or livro_selecionado == "Nenhum livro disponível":
      messagebox.showerror("Erro", "Selecione um livro válido para empréstimo!")
      return

    if not usuario:
      messagebox.showerror("Erro", "O nome do usuário não pode estar vazio!")
      return

    try:
      dias_prazo = int(prazo_str)
      if dias_prazo <= 0:
        raise ValueError
    except ValueError:
      messagebox.showerror("Erro", "O prazo deve ser um número inteiro positivo!")
      return

    data_emprestimo = datetime.now()
    data_limite = data_emprestimo + timedelta(days=dias_prazo)

    for livro in self.livros:
      if livro["titulo"] == livro_selecionado and livro["disponivel"]:
        livro["disponivel"] = False
        self.emprestimos.append({
            "livro": livro_selecionado,
            "usuario": usuario,
            "data_limite": data_limite,
            "status": "Ativo",
            "multa": "R$ 0,00",
        })
        break

    self.entry_usuario.delete(0, tk.END)
    self.salvar_dados()
    self.atualizar_tabelas()
    messagebox.showinfo("Sucesso", "Empréstimo realizado com sucesso!")

  def devolver_emprestimo(self):
    selected_item = self.tabela_emprestimos.selection()
    if not selected_item:
      messagebox.showwarning(
          "Aviso", "Selecione um empréstimo ativo na tabela para devolver!"
      )
      return

    item_dados = self.tabela_emprestimos.item(selected_item)
    livro_titulo = item_dados["values"][0]
    status_atual = item_dados["values"][3]

    if status_atual == "Devolvido":
      messagebox.showerror("Erro", "Este livro já foi devolvido anteriormente!")
      return

    data_str_simulada = simpledialog.askstring(
        "Simular Data de Devolução",
        "Digite a data de devolução (DD/MM/AAAA):\n(Deixe em branco para usar a data de hoje)",
    )

    if data_str_simulada is None:
      return

    data_devolucao_real = datetime.now()
    if data_str_simulada.strip() != "":
      try:
        data_devolucao_real = datetime.strptime(
            data_str_simulada.strip(), "%d/%m/%Y"
        )
      except ValueError:
        messagebox.showerror(
            "Erro", "Formato de data inválido! Use o formato DD/MM/AAAA."
        )
        return

    emprestimo_alvo = None
    for emp in self.emprestimos:
      if emp["livro"] == livro_titulo and emp["status"] == "Ativo":
        emprestimo_alvo = emp
        break

    if not emprestimo_alvo:
      return

    data_limite = emprestimo_alvo["data_limite"]

    multa_total = 0.00
    if data_devolucao_real > data_limite:
      dias_atraso = (data_devolucao_real - data_limite).days
      if dias_atraso == 0:
        dias_atraso = 1
      multa_total = dias_atraso * 2.00

    emprestimo_alvo["status"] = "Devolvido"
    emprestimo_alvo["multa"] = f"R$ {multa_total:.2f}".replace(".", ",")

    for livro in self.livros:
      if livro["titulo"] == livro_titulo:
        livro["disponivel"] = True
        break

    self.salvar_dados()
    self.atualizar_tabelas()

    if multa_total > 0:
      messagebox.showwarning(
          "Atenção - Atraso Detectado",
          f"Devolução simulada com atraso!\nMulta aplicada: R$ {multa_total:.2f}",
      )
    else:
      messagebox.showinfo(
          "Sucesso", "Livro devolvido dentro do prazo sem multas!"
      )

  # ==========================================
  # ATUALIZAÇÃO VISUAL DE TODAS AS TABELAS
  # ==========================================
  def atualizar_tabelas(self):
    for row in self.tabela_livros.get_children():
      self.tabela_livros.delete(row)

    livros_disponiveis_para_combo = []
    for livro in self.livros:
      status_str = "Disponível" if livro["disponivel"] else "Emprestado"
      self.tabela_livros.insert(
          "", tk.END, values=(livro["id"], livro["titulo"], status_str)
      )
      if livro["disponivel"]:
        livros_disponiveis_para_combo.append(livro["titulo"])

    self.combo_livros["values"] = livros_disponiveis_para_combo
    if livros_disponiveis_para_combo:
      self.combo_livros.set("")
    else:
      self.combo_livros.set("Nenhum livro disponível")

    for row in self.tabela_emprestimos.get_children():
      self.tabela_emprestimos.delete(row)

    for emp in self.emprestimos:
      data_limite_fmt = emp["data_limite"].strftime("%d/%m/%Y")
      self.tabela_emprestimos.insert(
          "",
          tk.END,
          values=(
              emp["livro"],
              emp["usuario"],
              data_limite_fmt,
              emp["status"],
              emp["multa"],
          ),
      )


if __name__ == "__main__":
  root = tk.Tk()
  app = SistemaBibliotecaApp(root)
  root.mainloop()
