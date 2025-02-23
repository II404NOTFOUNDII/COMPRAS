from config import *
from functions import *

# Guardar los datos seleccionados en la base de datos
def guardar_seleccion():
    conn = conectar_bd()
    cursor = conn.cursor()
    for i, var in enumerate(check_vars):
        if var.get():  # Si el checkbox está marcado
            id_producto = productos[i][0]
            cantidad = cantidad_vars[i].get()
            if cantidad.isdigit() and int(cantidad) > 0:
                cursor.execute("INSERT INTO seleccionados (producto_id, cantidad) VALUES (?, ?)", (id_producto, cantidad))
            else:
                messagebox.showwarning("Error", f"Cantidad inválida para {productos[i][1]}")
    conn.commit()
    conn.close()
    messagebox.showinfo("Éxito", "Datos guardados correctamente")

# Crear la ventana
root = tk.Tk()
root.title("Seleccionar Productos")

productos = datos_pedido_3()  # Lista de productos de la consulta
check_vars = []  # Lista para almacenar variables de los checkboxes
cantidad_vars = []  # Lista para almacenar variables de cantidad

# Crear los elementos de la interfaz
for i, (id_producto, nombre) in enumerate(productos):
    var = tk.BooleanVar()
    check = tk.Checkbutton(root, text=nombre, variable=var)
    check.grid(row=i, column=0, sticky="w")
    check_vars.append(var)

    cantidad_var = tk.StringVar()
    cantidad_entry = tk.Entry(root, textvariable=cantidad_var, width=5)
    cantidad_entry.grid(row=i, column=1)
    cantidad_vars.append(cantidad_var)

# Botón para guardar
btn_guardar = tk.Button(root, text="Guardar", command=guardar_seleccion)
btn_guardar.grid(row=len(productos), column=0, columnspan=2)

root.mainloop()
