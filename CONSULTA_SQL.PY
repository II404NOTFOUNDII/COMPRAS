

# Obtener datos de la consulta SQ

consulta_para_pedido_multiple = """

    
        SELECT au.factor,au.unidad
        FROM cb b
        LEFT JOIN ArtUnidad au ON au.Articulo = b.Cuenta AND au.Unidad = b.Unidad
        LEFT JOIN art a ON b.Cuenta = a.Articulo
        WHERE b.Cuenta IN (SELECT CUENTA FROM CB WHERE CB.Codigo = ?)
        """

proveedores_con_actividad = "SELECT DISTINCT NOMBRE FROM Prov WHERE Proveedor IN (SELECT PROVEEDOR FROM COMPRA WHERE mov ='Entrada Compra' and Estatus = 'CONCLUIDO')"