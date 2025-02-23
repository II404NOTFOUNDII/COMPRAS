import tkinter as tk
from tkinter import messagebox
import subprocess
import os
from functions import leer_saludo,mostrar_saludo,Start_ComArt


# Crear la ventana principal
root = tk.Tk()
root.title("INICIO")
root.geometry("400x400")  # Establece tamaño inicial
root.state("normal")       # Asegura que no inicie maximizada


# Botón para mostrar el saludo
btn_saludo = tk.Button(root, text="Mostrar Saludo", command=mostrar_saludo)
btn_saludo.pack(pady=10)
btn_saludo.place(x=50, y=150, width=200, height=100)

# Botón para abrir compras
btn_abrir = tk.Button(root, text="Abrir Compras por articulo", command=Start_ComArt)
btn_abrir.pack(side="left",pady=10)
btn_abrir.place(width=200, height=100)


# Ejecutar la ventana
root.mainloop()
