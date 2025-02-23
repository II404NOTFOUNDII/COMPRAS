# Función para obtener el listado de codigos de Barra
def obtener_barcodes():
    try:

        config = obtener_configuracion()

        conn = pyodbc.connect(f"DRIVER={{SQL Server}};"
                              f"SERVER={config['server']};"
                              f"DATABASE={config['database']};"
                              f"UID={config['username']};"
                              f"PWD={config['password']};")
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