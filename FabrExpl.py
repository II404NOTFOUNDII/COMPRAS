# COMPRAS.py

from config import *

from functions import obtener_Proveedores,obtener_configuracion, buscar_ARTVSPROV,anchos_columnas


# Obtener la ruta del archivo de configuración
config_path = os.path.join(os.path.dirname(__file__), "config.ini")

# Función que inicializa la interfaz
def iniciar_interfaz():
    root = tk.Tk()
    root.title("Artículos de proveedor")
    
    # Obtener el tamaño de la pantalla
    pantalla_ancho = root.winfo_screenwidth()
    pantalla_alto = root.winfo_screenheight()

    # Calcular el tamaño de la ventana (50% de la pantalla)
    ancho_ventana = int(pantalla_ancho * 0.5)
    alto_ventana = int(pantalla_alto * 0.5)

    # Calcular la posición para centrar la ventana
    pos_x = int((pantalla_ancho - ancho_ventana) / 2)
    pos_y = int((pantalla_alto - alto_ventana) / 2)

    # Establecer la geometría con el tamaño y la posición calculados
    root.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")

    root.state("normal")

    # Frame para la entrada de datos
    frame_top = tk.Frame(root, padx=1, pady=1)
    frame_top.pack(fill="x")

    # Lista desplegable con proveedores
    proveedores_disponibles = obtener_Proveedores()
    combo_proveedor = ttk.Combobox(frame_top, values=proveedores_disponibles, state="readonly", width=50)
    combo_proveedor.pack(side="left", padx=1)

    # Aquí se usa lambda correctamente para pasar el argumento
    btn_buscar = tk.Button(frame_top, text="Buscar", command=lambda: buscar_ARTVSPROV(combo_proveedor, tabla))
    btn_buscar.pack(side="left", padx=5)

    # Frame para la tabla de resultados
    frame_bottom = tk.Frame(root, padx=1, pady=1)
    frame_bottom.pack(fill="both", expand=True)

    columnas = ["Articulos", "Almacen", "Cantidad"]

    tabla = ttk.Treeview(frame_bottom, columns=columnas, show="headings")

    for col in columnas:
        tabla.heading(col, text=col)
        tabla.column(col, anchor="center", width=anchos_columnas.get(col, 100))

    scroll_y = ttk.Scrollbar(frame_bottom, orient="vertical", command=tabla.yview)
    scroll_y.pack(side="right", fill="y")
    tabla.configure(yscrollcommand=scroll_y.set)

    tabla.pack(fill="both", expand=True)

    scroll_x = ttk.Scrollbar(frame_bottom, orient="horizontal", command=tabla.xview)
    scroll_x.pack(side="bottom", fill="x")
    tabla.configure(xscrollcommand=scroll_x.set)

    tabla.pack(fill="both", expand=True)

    # Ejecutar aplicación
    root.mainloop()
