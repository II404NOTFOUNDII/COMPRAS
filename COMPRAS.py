# COMPRAS.py

from config import *

from functions import iniciar_programa,actualizar_clipboard
from FabrExpl import iniciar_interfaz
from buscador import iniciar_buscador
from Pedido2 import iniciar_interfaz_Pedido


# Obtener la ruta del archivo de configuración
config_path = os.path.join(os.path.dirname(__file__), "config.ini")

# Función para leer la configuración desde config.ini
def obtener_configuracion():
    config = configparser.ConfigParser()
    config.read(config_path)

    if "CONECTION" not in config:
        raise KeyError("La sección [CONECTION] no se encontró en config.ini")

    return {
        "server": config["CONECTION"].get("SERVER", ""),
        "database": config["CONECTION"].get("DATABASE", ""),
        "username": config["CONECTION"].get("USERNAME", ""),
        "password": config["CONECTION"].get("PASSWORD", "")
    }



# Función para obtener la lista de almacenes
def obtener_almacenes():
    try:
        config = obtener_configuracion()

        conn = pyodbc.connect(f"DRIVER={{SQL Server}};"
                              f"SERVER={config['server']};"
                              f"DATABASE={config['database']};"
                              f"UID={config['username']};"
                              f"PWD={config['password']};")
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ALMACEN FROM Alm")

        almacenes = [row[0] for row in cursor.fetchall()]
        almacenes.insert(0, "(TODOS)")  # Agregar opción "TODOS"

        cursor.close()
        conn.close()

        return almacenes
    except Exception as e:
        messagebox.showerror("Error al obtener almacenes", str(e))
        return ["(TODOS)"]
# Función para abrir Buscador.exe

# Función para ejecutar la consulta SQL con filtros de fecha
def buscar_codigo():
    codigo_barras = entry_codigo.get().strip()
    almacen_seleccionado = combo_almacen.get()
    fecha_inicio = entry_fecha_inicio.get_date()  # Obtener la fecha seleccionada
    fecha_fin = entry_fecha_fin.get_date()  # Obtener la fecha seleccionada


    if not fecha_inicio or not fecha_fin:
        messagebox.showwarning("Advertencia", "Por favor, ingresa un rango de fechas.")
        return

    try:
        # Validar que las fechas estén en el formato correcto
        # Formatear la fecha de inicio y fin al formato necesario (YYYY-MM-DD HH:mm:ss.000)
        fecha_inicio_sql = fecha_inicio.strftime("%Y-%m-%dT%H:%M:%S.000")
        fecha_fin_sql = fecha_fin.strftime("%Y-%m-%dT%H:%M:%S.000")

        config = obtener_configuracion()

        conn = pyodbc.connect(f"DRIVER={{SQL Server}};"
                              f"SERVER={config['server']};"
                              f"DATABASE={config['database']};"
                              f"UID={config['username']};"
                              f"PWD={config['password']};")

        cursor = conn.cursor()

# Construcción del filtro dinámico del almacén
        filtro_almacen = ""
        if almacen_seleccionado and almacen_seleccionado != "(TODOS)":
            filtro_almacen = f"AND CD.Almacen = '{almacen_seleccionado}'"

# Consulta SQL con filtro de fechas
        query = f"""
        SELECT
         CASE 
           WHEN CD.Almacen = 'ALMVGPE' THEN 'LIZ'
           WHEN CD.Almacen = 'ALMPALM' THEN 'PALMAS'
           WHEN CD.Almacen = 'ALMTESTE' THEN 'TESTERAZO'
           WHEN CD.Almacen = 'ALMMAYO' THEN 'MAYOREO'
           ELSE CD.Almacen
         END AS Sucursal,
         P.NOMBRE,
         C.FechaEmision,
         CD.Cantidad,
         CD.Unidad,
         CD.Factor AS Equivalencia,
         CD.CantidadInventario,
         CD.Costo,
         CD.Impuesto1 AS IVA,
         CD.Impuesto2 AS IEPS,
         FORMAT((CD.DescuentoImporte / NULLIF(CD.COSTO * CD.Cantidad, 0)) * 100, 'N2') AS PorcentajeDescuento,
         ROUND((CD.COSTO * (1 + (ISNULL(CD.Impuesto2, 0) / 100))) * (1 + (ISNULL(CD.Impuesto1, 0) / 100)), 2) AS CostoTotal,

         A.Descripcion1  -- Se agrega la descripción del artículo
        FROM CompraD CD
        LEFT JOIN ART A ON A.Articulo = CD.Articulo
        LEFT JOIN Compra C ON CD.ID = C.ID
        LEFT JOIN PROV P ON P.Proveedor = C.Proveedor
        WHERE CD.ARTICULO IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
        AND C.ESTATUS = 'CONCLUIDO'
        AND C.MOV = 'entrada compra'
        AND C.FechaEmision BETWEEN ? AND ?
        {filtro_almacen}
        """

        cursor.execute(query, (codigo_barras, fecha_inicio_sql, fecha_fin_sql))
        resultados = cursor.fetchall()

# Limpiar la tabla antes de insertar nuevos resultados
        for row in tabla.get_children():
            tabla.delete(row)

# Variables para acumular los totales
        total_cantidad = 0
        total_cantidad_inventario = 0
        total_costo = 0
        total_costo_total = 0

# Insertar resultados en la tabla y calcular totales
        for row in resultados:
            valores = list(row)
            valores_limpios = []

            for i, valor in enumerate(valores):
                if i in [3, 6, 7, 11]:  # Índices de las columnas que sumamos
                    valores_limpios.append(float(valor) if valor else 0)
                else:
                    valores_limpios.append(valor)

            total_cantidad += valores_limpios[3]
            total_cantidad_inventario += valores_limpios[6]
            total_costo += valores_limpios[7]
            total_costo_total += valores_limpios[11]

            tabla.insert("", "end", values=valores_limpios)

            # Actualizar etiquetas de totales
        label_total_cantidad.config(text=f"{total_cantidad:,.2f}")
        label_total_cantidad_inventario.config(text=f"{total_cantidad_inventario:,.2f}")
        label_total_costo.config(text=f"${total_costo:,.2f}")
        label_total_costo_total.config(text=f"${total_costo_total:,.2f}")

        cursor.close()
        conn.close()
        

            # Actualizar la caja de texto con la descripción
        if resultados:
            descripcion_var.set(resultados[0][-1])  # Última columna de la consulta (Descripción1)
        else:
            descripcion_var.set("")  # Si no hay resultados, limpiar la caja

        if not resultados:
            messagebox.showinfo("Sin resultados", "No se encontraron datos para el código ingresado.")

    except Exception as e:
        messagebox.showerror("Error inesperado", f"Ocurrió un error: {e}")



# Crear ventana principal
root = tk.Tk()
root.title("Historial Compra Cesar Guardado")
root.state("zoomed")


if __name__ == "__main__":
    iniciar_programa()

# Frame para la entrada de datos
frame_top = tk.Frame(root, padx=1, pady=1)
frame_top.pack(fill="x")


tk.Label(frame_top, text="Código de Barras:").pack(side="left")


entry_codigo = tk.Entry(frame_top, width=20)
entry_codigo.pack(side="left", padx=5)

entry_codigo.bind("<Return>", lambda event: (buscar_codigo(), actualizar_clipboard(entry_codigo)))


tk.Label(frame_top, text="Almacén:").pack(side="left", padx=5)

# Crear widgets para las fechas de inicio y fin

entry_fecha_fin = DateEntry(frame_top, date_pattern='yyyy-mm-dd')
entry_fecha_fin.pack(side="right",padx=5, pady=1)

entry_fecha_inicio = DateEntry(frame_top, date_pattern='yyyy-mm-dd')
entry_fecha_inicio.pack(side="right",padx=5, pady=1)


# Lista desplegable con almacenes
almacenes_disponibles = obtener_almacenes()
combo_almacen = ttk.Combobox(frame_top, values=almacenes_disponibles, state="readonly")
combo_almacen.current(0)  # Selecciona "(TODOS)" por defecto
combo_almacen.pack(side="left", padx=1)

btn_buscar = tk.Button(frame_top, text="Buscar", command=buscar_codigo)
btn_buscar.pack(side="left", padx=5)

# Etiqueta para la descripción
#tk.Label(frame_top, text="Descripción:").pack(side="right", padx=5)

# Caja de texto no editable para la descripción
descripcion_var = tk.StringVar()
entry_descripcion = tk.Entry(frame_top, textvariable=descripcion_var, state="readonly", width=50)
entry_descripcion.pack(side="right", padx=1)

btn_abrir = tk.Button(frame_top, text="Registra Pedido", command=iniciar_interfaz_Pedido, font=("Arial", 10))
btn_abrir.pack(side="right", pady=5)


# Botón para ejecutar la función de FabrExpl
btn_abrir = tk.Button(frame_top, text="Buscador", command=iniciar_buscador, font=("Arial", 10))
btn_abrir.pack(side="right", pady=5)

# Botón para ejecutar la función de FabrExpl
btn_abrir = tk.Button(frame_top, text="Arts del Proveedor", command=iniciar_interfaz, font=("Arial", 10))
btn_abrir.pack(side="right", pady=5)

# Frame para la tabla de resultados
Frame_body = tk.Frame(root, padx=1, pady=1)
Frame_body.pack(fill="both", expand=True)

columnas = ["Sucursal", "Nombre", "Fecha Emisión", "Cantidad", "Unidad", "Equivalencia", "Cantidad Inventario", 
            "Costo", "IVA", "IEPS", "Porcentaje Descuento", "Costo Total"]

tabla = ttk.Treeview(Frame_body, columns=columnas, show="headings")

for col in columnas:
    tabla.heading(col, text=col)
    tabla.column(col, anchor="center", width=100)

scroll_y = ttk.Scrollbar(Frame_body, orient="vertical", command=tabla.yview)
scroll_y.pack(side="right", fill="y")
tabla.configure(yscrollcommand=scroll_y.set)

tabla.pack(fill="both", expand=True)

scroll_x = ttk.Scrollbar(Frame_body, orient="horizontal", command=tabla.xview)
scroll_x.pack(side="bottom", fill="x")
tabla.configure(xscrollcommand=scroll_x.set)

tabla.pack(fill="both", expand=True)

# Sección de totales
frame_totales = tk.Frame(root, padx=10, pady=30, relief="ridge", borderwidth=2)
frame_totales.pack(fill="x")

# Etiqueta y total de Cantidad
tk.Label(frame_totales, text="Total Cantidad:", font=("Arial", 15, "bold")).pack(side="left", padx=5)
label_total_cantidad = tk.Label(frame_totales, text="0.00", font=("Arial", ))
label_total_cantidad.pack(side="left", padx=20)

# Etiqueta y total de Cantidad Inventario
tk.Label(frame_totales, text="Total Cantidad Inventario:", font=("Arial", 15, "bold")).pack(side="left", padx=5)
label_total_cantidad_inventario = tk.Label(frame_totales, text="0.00", font=("Arial", 15))
label_total_cantidad_inventario.pack(side="left", padx=20)

# Etiqueta y total de Costo
tk.Label(frame_totales, text="Total Costo:", font=("Arial", 15, "bold")).pack(side="left", padx=5)
label_total_costo = tk.Label(frame_totales, text="$0.00", font=("Arial", 15))
label_total_costo.pack(side="left", padx=20)

# Etiqueta y total de Costo Total
tk.Label(frame_totales, text="Total Costo Total:", font=("Arial", 15, "bold")).pack(side="left", padx=5)
label_total_costo_total = tk.Label(frame_totales, text="$0.00", font=("Arial", 15))
label_total_costo_total.pack(side="left", padx=20)


# Frame para la tabla de resultados
#Frame_footer = tk.Frame(root, padx=1, pady=1)
#Frame_footer.pack(fill="both", expand=True)

# Ejecutar aplicación
root.mainloop()
