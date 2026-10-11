
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from threading import Thread
from markitdown import MarkItDown

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

archivos = []
destino = None

app = ctk.CTk()
app.title("MarkItDown - Conversor de archivos")
app.geometry("720x520")
app.minsize(600, 450)

titulo = ctk.CTkLabel(
    app,
    text="MarkItDown",
    font=("Arial", 30, "bold")
)
titulo.pack(pady=(25, 5))

subtitulo = ctk.CTkLabel(
    app,
    text="Convierte tus documentos a Markdown",
    text_color="gray"
)
subtitulo.pack(pady=(0, 20))

lista = ctk.CTkTextbox(app, height=175, width=620)
lista.pack(padx=25, pady=10)
lista.configure(state="disabled")


def actualizar_lista():
    lista.configure(state="normal")
    lista.delete("1.0", "end")
    for archivo in archivos:
        lista.insert("end", f"• {Path(archivo).name}\n")
    lista.configure(state="disabled")


def seleccionar_archivos():
    nuevos = filedialog.askopenfilenames(
        title="Seleccionar documentos",
        filetypes=[
            ("Documentos", "*.pdf *.docx *.pptx *.xlsx *.xls"),
            ("Todos los archivos", "*.*")
        ]
    )
    for archivo in nuevos:
        if archivo not in archivos:
            archivos.append(archivo)
    actualizar_lista()


def limpiar():
    archivos.clear()
    actualizar_lista()
    estado.configure(text="Selecciona archivos para comenzar")


def seleccionar_destino():
    global destino
    carpeta = filedialog.askdirectory(
        title="Seleccionar carpeta de destino"
    )
    if carpeta:
        destino = carpeta
        etiqueta_destino.configure(
            text=f"Destino: {carpeta}"
        )


def finalizar(exitos, errores):
    boton_convertir.configure(state="normal")
    estado.configure(
        text=f"Finalizado: {exitos} archivos convertidos"
    )
    if errores:
        messagebox.showwarning(
            "Conversión finalizada con errores",
            "\n".join(errores[:8])
        )
    else:
        messagebox.showinfo(
            "Conversión completada",
            f"Se convirtieron {exitos} archivos correctamente."
        )


def convertir():
    if not archivos:
        messagebox.showwarning(
            "Sin archivos", "Primero selecciona documentos."
        )
        return

    seleccionados = archivos.copy()
    carpeta_destino = destino

    boton_convertir.configure(state="disabled")
    estado.configure(text="Convirtiendo archivos...")

    def tarea():
        exitos = 0
        errores = []
        md = MarkItDown(enable_plugins=False)

        for archivo in seleccionados:
            try:
                ruta = Path(archivo)
                carpeta = (
                    Path(carpeta_destino)
                    if carpeta_destino else ruta.parent
                )
                salida = carpeta / f"{ruta.stem}.md"

                resultado = md.convert(str(ruta))
                salida.write_text(
                    resultado.markdown, encoding="utf-8"
                )
                exitos += 1

            except Exception as e:
                errores.append(
                    f"{Path(archivo).name}: {str(e)}"
                )

        app.after(0, finalizar, exitos, errores)

    Thread(target=tarea, daemon=True).start()


botones = ctk.CTkFrame(app, fg_color="transparent")
botones.pack(pady=8)

ctk.CTkButton(
    botones,
    text="Agregar archivos",
    command=seleccionar_archivos
).pack(side="left", padx=6)

ctk.CTkButton(
    botones,
    text="Limpiar lista",
    fg_color="#555555",
    command=limpiar
).pack(side="left", padx=6)

ctk.CTkButton(
    botones,
    text="Elegir destino",
    command=seleccionar_destino
).pack(side="left", padx=6)

etiqueta_destino = ctk.CTkLabel(
    app,
    text="Destino: misma carpeta de los archivos originales",
    wraplength=600
)
etiqueta_destino.pack(pady=8)

boton_convertir = ctk.CTkButton(
    app,
    text="Convertir a Markdown",
    height=45,
    width=280,
    font=("Arial", 16, "bold"),
    command=convertir
)
boton_convertir.pack(pady=12)

estado = ctk.CTkLabel(
    app, text="Selecciona archivos para comenzar"
)
estado.pack(pady=5)

app.mainloop()
