from config import *
from functions import *
from CONSULTA_SQL import *

def ejecutar_pedido():
    def conectar_db():
        try:
            config = obtener_configuracion()
            conn = pyodbc.connect(f"DRIVER={{SQL Server}};"
                                  f"SERVER={config['server']};"
                                  f"DATABASE={config['database']};"
                                  f"UID={config['username']};"
                                  f"PWD={config['password']};")
            return conn
        except Exception as e:
            messagebox.showerror("Error de Conexión", str(e))
            return None

    def guardar_en_config(codigo, articulo, unidad, almacen, cantidad, proveedor):
        archivo_pedido = "Pedido.ini"
        linea = f"{proveedor}\t{articulo}\t{unidad}\t{almacen}\t{cantidad}\n"
        with open(archivo_pedido, "a") as configfile:
            configfile.write(linea)

    codigo = leer_clipboard()

    if not codigo:
        messagebox.showwarning("Advertencia", "No hay código en CLIPBOARD.")
        return

    conn = conectar_db()
    if conn is None:
        return

    cursor = conn.cursor()

    cursor.execute("""
        SELECT b.Unidad, au.Factor, a.articulo
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

    cursor.execute("SELECT DISTINCT almacen FROM ArtAlm")
    almacenes = [row[0] for row in cursor.fetchall()]

    conn.close()

    if not unidades:
        messagebox.showwarning("Advertencia", "No se encontraron unidades para el código en CLIPBOARD.")
        return

    ventana = tk.Tk()
    ventana.title("Seleccionar Pedido")

    tk.Label(ventana, text="Cantidad:").grid(row=0, column=0, padx=5, pady=5)
    entry_cantidad = tk.Entry(ventana)
    entry_cantidad.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Unidad:").grid(row=1, column=0, padx=5, pady=5)
    unidad_var = tk.StringVar()
    combo_unidad = ttk.Combobox(ventana, textvariable=unidad_var, state="readonly")
    combo_unidad["values"] = [f"{u[0]} (Factor: {u[1]})" for u in unidades]
    combo_unidad.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Proveedor:").grid(row=2, column=0, padx=5, pady=5)
    proveedor_var = tk.StringVar()
    combo_proveedor = ttk.Combobox(ventana, textvariable=proveedor_var, state="readonly")
    combo_proveedor["values"] = proveedor
    combo_proveedor.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(ventana, text="Almacén:").grid(row=3, column=0, padx=5, pady=5)
    almacen_var = tk.StringVar()
    combo_almacen = ttk.Combobox(ventana, textvariable=almacen_var, state="readonly")
    combo_almacen["values"] = almacenes
    combo_almacen.grid(row=3, column=1, padx=5, pady=5)

    def guardar_pedido():
        proveedor_seleccionado = proveedor_var.get().strip()
        cantidad = entry_cantidad.get().strip()
        unidad = unidad_var.get().split(" ")[0]
        almacen = almacen_var.get().strip()

        if not cantidad or not unidad or not almacen:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        guardar_en_config(codigo, articulo, unidad, almacen, cantidad, proveedor_seleccionado)
        messagebox.showinfo("Éxito", "Pedido guardado correctamente.")
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar_pedido).grid(row=4, column=0, columnspan=2, pady=10)
    ventana.mainloop()
