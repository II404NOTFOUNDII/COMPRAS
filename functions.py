
# COMPRAS.py

from config import *

from CONSULTA_SQL import *

# Ahora puedes usar todas las librerías importadas en config.py directamente.

consulta_almacen = "SELECT DISTINCT ALMACEN FROM Alm"

config_path = os.path.join(os.path.dirname(__file__), "config.ini")

anchos_columnas = {
    "Articulos": 150,
    "Almacen": 50,
    "Cantidad": 20
    }

# A

def leer_saludo():
    """Lee el saludo desde el archivo config.ini"""
    config = configparser.ConfigParser()
    config.read("config.ini", encoding="utf-8")  
    return config["INICIO"].get("saludo", "¡Hola!")

def mostrar_saludo():
    """Muestra un cuadro de diálogo con un saludo"""
    saludo = leer_saludo()
    messagebox.showinfo("INICIO", saludo)

def Start_ComArt():
    """Abre el programa compras.exe desde la carpeta dist"""
    ruta_programa = os.path.join(os.getcwd(), "dist", "compras.exe")
    try:
        subprocess.Popen([ruta_programa], shell=True)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta_programa}")

def Start_ComFab():
    """Abre el programa compras.exe desde la carpeta dist"""
    ruta_programa = os.path.join(os.getcwd(), "dist", "FabrExpl.exe")
    try:
        subprocess.Popen([ruta_programa], shell=True)
    except FileNotFoundError:
        messagebox.showerror("Error", f"No se encontró el archivo:\n{ruta_programa}")

def cerrar_instancias_duplicadas():
    """Cierra otras instancias del programa si ya está en ejecución."""
    # Obtener el nombre del archivo actual (puede ser .exe o .py)
    nombre_programa = "compras.exe"  # Reemplaza con el nombre de tu programa
    
    # Iterar a través de los procesos en ejecución
    for proc in psutil.process_iter(attrs=['pid', 'name', 'exe']):
        try:
            # Verifica si es una instancia del programa y no la actual
            if proc.info['exe'] and nombre_programa in proc.info['exe']:
                if proc.info['pid'] != os.getpid():  # Comparar con el PID actual
                    proc.terminate()  # Termina el proceso duplicado
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass  # Omitir procesos que ya no existen o no se pueden acceder

def iniciar_programa():
    """Inicia el programa y cierra otras instancias si las hay."""
    cerrar_instancias_duplicadas()


# Función para obtener informacion de configuracion
def obtener_configuracion_LOCAL():
    config = configparser.ConfigParser()
    config.read(config_path)

    if "CONECTION" not in config:
        raise KeyError("La sección [CONECTION] no se encontró en config.ini")

    return {
        "server": config["CONECTION"].get("SERVER", ""),
        "databaseLOCAL": config["CONECTION"].get("DATABASE", ""),
        "username": config["CONECTION"].get("USERNAME", ""),
        "password": config["CONECTION"].get("PASSWORD", "")
        }


# Función para obtener informacion de configuracion
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

# Función para obtener la lista de proveedores
def obtener_Proveedores():
    try:
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT NOMBRE FROM Prov WHERE Proveedor IN (SELECT PROVEEDOR FROM COMPRA WHERE mov ='Entrada Compra' and Estatus = 'CONCLUIDO')")

        proveedores = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return proveedores
    except Exception as e:
        messagebox.showerror("Error al obtener Proveedores", str(e))
        return []





# Función para obtener la lista de almacenes
def obtener_almacenes():
    try:
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        cursor.execute(consulta_almacen)

        almacenes = [row[0] for row in cursor.fetchall()]
        almacenes.insert(0, "(TODOS)")  # Agregar opción "TODOS"

        cursor.close()
        conn.close()

        return almacenes
    except Exception as e:
        messagebox.showerror("Error al obtener almacenes", str(e))
        return ["(TODOS)"]



def connect_server(config):
    return(
            f"DRIVER={{SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
        )


def buscar_ARTVSPROV(combo_proveedor, tabla):
    proveedor_seleccionado = combo_proveedor.get()

    try:
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))

        cursor = conn.cursor()

        filtro_proveedor = ""
        if proveedor_seleccionado and proveedor_seleccionado != "(TODOS)":
            filtro_proveedor = f"AND P.Nombre = '{proveedor_seleccionado}' GROUP BY  A.Descripcion1,C.Almacen"

        query = f"""
        SELECT 
            A.Descripcion1 AS Articulos,
            C.Almacen AS Almacen,
            sum(CD.CantidadInventario) aS CANTIDAD
        FROM
            comprad CD
        LEFT JOIN
            compra C ON CD.ID = C.ID
        LEFT JOIN
            art A ON CD.Articulo = A.Articulo
        LEFT JOIN 
            prov P ON C.Proveedor = P.Proveedor 
        WHERE
            C.Mov='Entrada Compra'
        AND
            C.Estatus = 'CONCLUIDO'
        {filtro_proveedor}
        """

        print("Consulta generada:", query)  # Para depuración
        cursor.execute(query)
        resultados = cursor.fetchall()

        # Limpiar la tabla antes de insertar nuevos resultados
        for row in tabla.get_children():
            tabla.delete(row)

        # Insertar los nuevos resultados en la tabla con valores limpios
        for row in resultados:
            valores_limpios = [str(valor).strip() if isinstance(valor, str) else valor for valor in row]
            tabla.insert("", "end", values=valores_limpios)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        cursor.close()
        conn.close()





# Función para obtener el listado de codigos de Barra
def obtener_barcodes():
    try:

        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        query = """
        SELECT CB.Codigo, CB.Unidad, ART.Descripcion1
        FROM CB
        LEFT JOIN ART ON CB.Cuenta = ART.Articulo
        WHERE CB.UNIDAD IS NOT NULL
        AND Descripcion1 IS NOT NULL
        """
        cursor.execute(query)
        datos = cursor.fetchall()
        conn.close()
        return [(row[0], row[1], row[2]) for row in datos]  # Lista de tuplas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la base de datos.\n{e}")
        return []


# Función para copiar el código seleccionado y cerrar
def Barcode_a_clipborad(event=None):
    seleccionado = lista.selection()
    if seleccionado:
        codigo = lista.item(seleccionado, "values")[0]
        pyperclip.copy(codigo)  # Copiar al portapapeles
        root.destroy()
    else:
        messagebox.showwarning("Aviso", "Selecciona un código primero.")

# Función para actualizar el código en config.ini en la sección [CLIPBOARD]
import configparser

def actualizar_clipboard(entry_codigo):
    codigo = entry_codigo.get().strip()
    if not codigo:
        return

    config = configparser.ConfigParser()
    config.read("config.ini")

    if "CLIPBOARD" not in config:
        config["CLIPBOARD"] = {}

    config["CLIPBOARD"]["Barcode"] = codigo

    with open("config.ini", "w") as configfile:
        config.write(configfile)


def leer_clipboard():
    config = configparser.ConfigParser()
    config.read("config.ini")

    return config.get("CLIPBOARD", "Barcode", fallback="")  # Devuelve el código o una cadena vacía

def conectar_db():
    try:
        config = obtener_configuracion()  # Suponiendo que tienes la función para obtener la configuración
        conn = pyodbc.connect(connect_server(config))
        return conn
    except Exception as e:
        messagebox.showerror("Error de Conexión", str(e))
        return None

# Función para buscar unidades y almacenes usando CLIPBOARD
def buscar_codigo_en_clipboard():
    codigo = leer_clipboard()  # Obtiene el código de config.ini

    if not codigo:
        messagebox.showwarning("Advertencia", "No hay código en CLIPBOARD.")
        return

    conn = pyodbc.connect(connect_server(config))
    if conn is None:
        return  # Si no pudo conectarse, termina la función

    cursor = conn.cursor()

    # Consulta de unidades
    cursor.execute("""
        SELECT b.Unidad
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))
    unidades = cursor.fetchall()

    # Consulta de almacenes
    cursor.execute(consulta_almacen)
    almacenes = [row[0] for row in cursor.fetchall()]

    conn.close()

    if not unidades:
        messagebox.showwarning("Advertencia", "No se encontraron unidades para el código en CLIPBOARD.")
        return

# Función para guardar el pedido
def guardar_pedido(entry_cantidad,combo_unidades):
        cantidad = entry_cantidad.get().strip()
        unidad = unidad_var.get().split(" ")[0]  # Solo la unidad sin el factor
        almacen = almacen_var.get().strip()

        if not cantidad or not unidad or not almacen:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

def guardar_en_config(codigo, unidad, almacen, cantidad):
    config = configparser.ConfigParser()
    config.read("config.ini")

    if "PEDIDO" not in config:
        config["PEDIDO"] = {}

    config["PEDIDO"][codigo] = f"{unidad}\t{almacen}\t{cantidad}"

    with open("config.ini", "w") as configfile:
        config.write(configfile)

# Función para buscar unidades y almacenes usando CLIPBOARD
def obtener_unidades():
    try:
        codigo = leer_clipboard()
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.Unidad,au.factor
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))

        factor_var = [row[0] for row in cursor.fetchall()]
        unidad_var = [row[1] for row in cursor.fetchall()]

        cursor.close()
        conn.close()
        print(factor_var,unidad_var)
        return factor_var, unidad_var
    except Exception as e:
        messagebox.showerror("Error al obtener Proveedores", str(e))
        return []

# Función para buscar unidades y almacenes usando CLIPBOARD
def obtener_factores():
    try:
        codigo = leer_clipboard()
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        cursor.execute("""
        SELECT au.factor
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))

        proveedores = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return proveedores
    except Exception as e:
        messagebox.showerror("Error al obtener Proveedores", str(e))
        return []

# Función para buscar unidades y almacenes usando CLIPBOARD
def obtener_sucursales():
    try:
        codigo = leer_clipboard()
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        cursor.execute("""
        SELECT au.factor
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))

        proveedores = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return proveedores
        cursor.close()
    except Exception as e:
        messagebox.showerror("Error al obtener Proveedores", str(e))
        return []
# Función para buscar unidades y almacenes usando CLIPBOARD
def hacer_pedido():
    try:
        codigo = leer_clipboard()
        config = obtener_configuracion()

        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()
        cursor.execute("""
        SELECT au.factor
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
    """, (codigo,))

        proveedores = [row[0] for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return proveedores
    except Exception as e:
        messagebox.showerror("Error al obtener Proveedores", str(e))
        return []

# Obtener datos de la consulta SQL
def datos_pedido_3():
    try:
        config = obtener_configuracion()
        conn = pyodbc.connect(connect_server(config))
        cursor = conn.cursor()

        query = consulta_para_pedido_multiple  # Asegúrate de que esto esté definido
        cursor.execute(query)

        datos = cursor.fetchall()
        print(datos)  # Verificar datos obtenidos
        return datos

    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return []

    finally:
        if 'conn' in locals():
            conn.close()
