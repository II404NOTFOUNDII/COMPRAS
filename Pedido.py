from config import *
from functions import * # Importa la función para leer el código del config.ini
from CONSULTA_SQL import *
# Conexión a la base de datos SQL Server
def conectar_db():
    try:
        config = obtener_configuracion()  # Suponiendo que tienes la función para obtener la configuración
        conn = pyodbc.connect(f"DRIVER={{SQL Server}};"
                              f"SERVER={config['server']};"
                              f"DATABASE={config['database']};"
                              f"UID={config['username']};"
                              f"PWD={config['password']};")
        return conn
    except Exception as e:
        messagebox.showerror("Error de Conexión", str(e))
        return None

# Función para buscar unidades y almacenes usando CLIPBOARD
def buscar_codigo():
    codigo = leer_clipboard()  # Obtiene el código de config.ini

    if not codigo:
        messagebox.showwarning("Advertencia", "No hay código en CLIPBOARD.")
        return

    conn = conectar_db()
    if conn is None:
        return  # Si no pudo conectarse, termina la función

    cursor = conn.cursor()

    # Consulta de unidades y factores
    cursor.execute("""
        SELECT b.Unidad, au.Factor,a.articulo
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))
    unidades = cursor.fetchall()

    cursor.execute("""
        SELECT a.articulo
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))
    articulo = cursor.fetchone()
    articulo = articulo[0] if articulo else ''

     
    cursor.execute(proveedores_con_actividad)
    proveedor = [row[0] for row in cursor.fetchall()]
    print(proveedor)
    # Consulta de almacenes
    cursor.execute("SELECT DISTINCT almacen FROM ArtAlm")
    almacenes = [row[0] for row in cursor.fetchall()]
    print(unidades)
    print(articulo)
    conn.close()

    if not unidades:
        messagebox.showwarning("Advertencia", "No se encontraron unidades para el código en CLIPBOARD.")
        return

    # Crear ventana principal
    ventana = tk.Tk()
    ventana.title("Seleccionar Pedido")

    # Etiqueta y entrada de cantidad
    tk.Label(ventana, text="Cantidad:").grid(row=0, column=0, padx=5, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.grid(row=0, column=1, padx=5, pady=5)

    # ComboBox de unidades
    tk.Label(ventana, text="Unidad:").grid(row=1, column=0, padx=5, pady=5)
    unidad_var = tk.StringVar()
    combo_unidad = ttk.Combobox(ventana, textvariable=unidad_var, state="readonly")
    combo_unidad["values"] = [f"{u[0]} (Factor: {u[1]})" for u in unidades]
    combo_unidad.grid(row=1, column=1, padx=5, pady=5)


    # ComboBox de proveedor
    tk.Label(ventana, text="Proveedor:").grid(row=2, column=0, padx=5, pady=5)
    proveedor_var = tk.StringVar()
    combo_proveedor = ttk.Combobox(ventana, textvariable=proveedor_var, state="readonly")
    combo_proveedor["values"] = proveedor
    combo_proveedor.grid(row=2, column=1, padx=5, pady=5)


    # ComboBox de almacenes
    tk.Label(ventana, text="Almacén:").grid(row=3, column=0, padx=5, pady=5)
    almacen_var = tk.StringVar()
    combo_almacen = ttk.Combobox(ventana, textvariable=almacen_var, state="readonly")
    combo_almacen["values"] = almacenes
    combo_almacen.grid(row=3, column=1, padx=5, pady=5)

    # Función para guardar el pedido
    def guardar_pedido():
        proveedor = proveedor_var.get().strip()
        cantidad = entry_cantidad.get().strip()
        unidad = unidad_var.get().split(" ")[0]  # Solo la unidad sin el factor
        almacen = almacen_var.get().strip()

        if not cantidad or not unidad or not almacen:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        guardar_en_config(codigo,articulo,unidad, almacen,cantidad,proveedor)
        messagebox.showinfo("Éxito", "Pedido guardado correctamente.")
        ventana.destroy()

    # Botón para guardar el pedido
    tk.Button(ventana, text="Guardar", command=guardar_pedido).grid(row=4, column=0, columnspan=2, pady=10)

    # Iniciar la ventana principal
    ventana.mainloop()

# Guardar en archivo config.ini

def guardar_en_config(codigo, articulo, unidad, almacen, cantidad,proveedor):
    # Definir el archivo destino
    archivo_pedido = "Pedido.ini"
    
    # Construir la línea a guardar
    linea = f"{proveedor}\t{articulo}\t{unidad}\t{almacen}\t{cantidad}\n"

    # Abrir el archivo en modo append para agregar nuevas líneas
    with open(archivo_pedido, "a") as configfile:
        configfile.write(linea)





# Llamar a buscar_codigo automáticamente al abrir
buscar_codigo()
