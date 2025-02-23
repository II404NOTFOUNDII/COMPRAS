from config import *

from functions import obtener_barcodes,Barcode_a_clipborad

# Función para actualizar la lista en base a la búsqueda
def carga_inicial_barcodes(event=None):
    filtro = entry_busqueda.get().lower()
    lista.delete(*lista.get_children())  # Limpiar lista
    for codigo, unidad, descripcion in datos:
        if filtro in codigo.lower() or filtro in descripcion.lower():
            lista.insert("", "end", values=(codigo, unidad, descripcion))

# Obtener la ruta del archivo de configuración
config_path = os.path.join(os.path.dirname(__file__), "config.ini")

# Función que inicializa la interfaz
def iniciar_buscador():
    root = tk.Tk()
    root.title("Buscador de Códigos de Barras")
    root.geometry("600x300")
    root.resizable(True, True)

    # Caja de búsqueda
    global entry_busqueda
    entry_busqueda = tk.Entry(root, font=("Arial", 12))
    entry_busqueda.pack(pady=5, fill="x", padx=10)
    entry_busqueda.bind("<KeyRelease>", carga_inicial_barcodes)

    # Lista de resultados
    global lista
    columnas = ("Código", "Unidad", "Descripción")
    lista = ttk.Treeview(root, columns=columnas, show="headings", height=10)
    for col in columnas:
        lista.heading(col, text=col)
        lista.column(col, width=100)

    lista.pack(padx=10, pady=5, fill="both", expand=True)

    # Botón para copiar y cerrar
    btn_copiar = tk.Button(root, text="Copiar Código y Cerrar", command=Barcode_a_clipborad, font=("Arial", 12))
    btn_copiar.pack(pady=5)

    # Atajo de teclado Ctrl + C
    root.bind("<Control-c>", Barcode_a_clipborad)

    # Cargar datos iniciales
    global datos
    datos = obtener_barcodes()
    carga_inicial_barcodes()

    root.mainloop()

# Llamar a la función para iniciar la interfaz
