import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
from pathlib import Path

# Configuración de rutas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Archivos de datos
DATA_FILES = {
    'libros': DATA_DIR / 'libros.json',
    'prestamos': DATA_DIR / 'prestamos.json',
    'devoluciones': DATA_DIR / 'devoluciones.json',
    'usuarios': DATA_DIR / 'usuarios.json'
}

# Estilos y configuración visual
APP_STYLE = {
    'font': {'normal': ('Segoe UI', 12), 'heading': ('Segoe UI', 14, 'bold'), 'title': ('Segoe UI', 28, 'bold')},
    'colors': {'primary': '#007acc', 'secondary': '#005f99', 'background': '#f5f5f5', 'text': '#333'},
    'padding': {'small': 5, 'medium': 10, 'large': 20}
}

class DataManager:
    #Clase para manejar todas las operaciones de datos
    @staticmethod
    def cargar_datos(tipo):
        try:
            archivo = DATA_FILES[tipo]
            if not archivo.exists():
                with open(archivo, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4)
                return []

            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if not isinstance(datos, list):
                    raise ValueError(f"El archivo {archivo.name} no contiene una lista válida.")
                return datos

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar {tipo}: {str(e)}")
            return []

    @staticmethod
    def guardar_datos(tipo, datos):
        try:
            with open(DATA_FILES[tipo], 'w', encoding='utf-8') as f:
                json.dump(datos, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar {tipo}: {str(e)}")
            return False

class BaseView(ttk.Frame):
    """Clase base para todas las vistas"""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.configure_style()
        self.create_widgets()

    def configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=APP_STYLE['colors']['background'])
        style.configure("TLabel", background=APP_STYLE['colors']['background'], 
                    font=APP_STYLE['font']['normal'], foreground=APP_STYLE['colors']['text'])
        style.configure("TButton", font=APP_STYLE['font']['normal'], padding=6, 
                    background=APP_STYLE['colors']['primary'], foreground="white")
        style.map("TButton", background=[("active", APP_STYLE['colors']['secondary'])])
        style.configure("TEntry", font=APP_STYLE['font']['normal'])
        style.configure("TCombobox", font=APP_STYLE['font']['normal'])
        style.configure("Treeview", font=APP_STYLE['font']['normal'], rowheight=25)
        style.configure("Treeview.Heading", font=APP_STYLE['font']['heading'])

    def create_widgets(self):
        pass

class InicioView(BaseView):
    def create_widgets(self):
        ttk.Label(self, text="📖 Biblioteca Digital", 
                font=APP_STYLE['font']['title'], 
                foreground=APP_STYLE['colors']['primary']).pack(pady=50)

        opciones = [
            ("Buscar Libros", BuscarLibrosView),
            ("Realizar Préstamo", PrestamoView),
            ("Registrar Devolución", DevolucionView),
            ("Administrar Catálogo", AdministrarCatalogoView),
            ("Reportes y Estadísticas", ReportesView)
        ]

        for texto, vista in opciones:
            ttk.Button(self, text=texto, width=30, 
                    command=lambda v=vista: self.controller.mostrar_vista(v)).pack(pady=15)

class BuscarLibrosView(BaseView):
    def create_widgets(self):
        # Encabezado
        ttk.Label(self, text="🔍 Buscar Libros", 
                font=APP_STYLE['font']['title'], 
                foreground=APP_STYLE['colors']['primary']).pack(pady=20)

        # Controles de búsqueda
        frame_filtros = ttk.Frame(self)
        frame_filtros.pack(pady=20)

        self.filtro = tk.StringVar()
        self.entrada = tk.StringVar()

        ttk.Combobox(frame_filtros, textvariable=self.filtro, 
                    values=["Título", "Autor", "Género", "Todos"], 
                    state="readonly", width=15).grid(row=0, column=0, padx=10)
        ttk.Entry(frame_filtros, textvariable=self.entrada, width=30).grid(row=0, column=1, padx=10)
        ttk.Button(frame_filtros, text="Buscar", command=self.buscar_libros).grid(row=0, column=2, padx=10)

        # Resultados
        self.create_results_table()
        ttk.Button(self, text="Volver", command=lambda: self.controller.mostrar_vista(InicioView)).pack(pady=20)

    def create_results_table(self):
        columns = ("Título", "Autor", "Género", "Disponible")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="w")
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(pady=20, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def buscar_libros(self):
        libros = DataManager.cargar_datos('libros')
        prestamos = DataManager.cargar_datos('prestamos')
        criterio = self.filtro.get().lower()
        texto = self.entrada.get().lower()

        libros_prestados = [p['libro'] for p in prestamos]
        self.tree.delete(*self.tree.get_children())
        
        for libro in libros:
            disponible = "Sí" if libro['titulo'] not in libros_prestados else "No"
            
            if not criterio or criterio == "todos":
                if any(texto in libro[field].lower() for field in ['titulo', 'autor', 'genero']):
                    self.add_book_to_tree(libro, disponible)
            else:
                campo = {"título": "titulo", "autor": "autor", "género": "genero"}.get(criterio, "titulo")
                if texto in libro[campo].lower():
                    self.add_book_to_tree(libro, disponible)

    def add_book_to_tree(self, libro, disponible):
        self.tree.insert("", "end", values=(
            libro['titulo'],
            libro['autor'],
            libro['genero'],
            disponible
        ))

class PrestamoView(BaseView):
    def create_widgets(self):
        ttk.Label(self, text="📑 Registrar Préstamo", 
                font=APP_STYLE['font']['title'], 
                foreground=APP_STYLE['colors']['primary']).pack(pady=20)

        frame_prestamo = ttk.Frame(self)
        frame_prestamo.pack(pady=20)

        # Libros disponibles
        ttk.Label(frame_prestamo, text="Libro:").grid(row=0, column=0, padx=10, pady=10)
        self.libro = tk.StringVar()
        self.cb_libros = ttk.Combobox(frame_prestamo, textvariable=self.libro, width=40)
        self.cb_libros.grid(row=0, column=1, padx=10)
        
        # Usuarios
        ttk.Label(frame_prestamo, text="Usuario:").grid(row=1, column=0, padx=10, pady=10)
        self.usuario = tk.StringVar()
        self.cb_usuarios = ttk.Combobox(frame_prestamo, textvariable=self.usuario, width=40)
        self.cb_usuarios.grid(row=1, column=1, padx=10)
        
        self.actualizar_listas()

        ttk.Button(self, text="Registrar Préstamo", command=self.registrar_prestamo).pack(pady=25)
        self.resultado = ttk.Label(self, text="", font=APP_STYLE['font']['normal'])
        self.resultado.pack(pady=5)

        ttk.Button(self, text="Volver", command=lambda: self.controller.mostrar_vista(InicioView)).pack(pady=20)

    def actualizar_listas(self):
        libros = DataManager.cargar_datos('libros')
        prestamos = DataManager.cargar_datos('prestamos')
        libros_prestados = [p['libro'] for p in prestamos]
        
        self.cb_libros['values'] = [
            libro['titulo'] for libro in libros 
            if libro['titulo'] not in libros_prestados
        ]
        
        usuarios = DataManager.cargar_datos('usuarios')
        self.cb_usuarios['values'] = [u['nombre'] for u in usuarios] if usuarios else []

    def registrar_prestamo(self):
        libro = self.libro.get()
        usuario = self.usuario.get()
        
        if not libro or not usuario:
            messagebox.showwarning("Campos incompletos", "Completa todos los campos.")
            return

        if not self.verificar_usuario(usuario):
            return

        fecha_prestamo = datetime.now()
        fecha_devolucion = fecha_prestamo + timedelta(days=14)

        prestamo = {
            "libro": libro,
            "usuario": usuario,
            "fecha_prestamo": fecha_prestamo.strftime("%Y-%m-%d"),
            "fecha_devolucion": fecha_devolucion.strftime("%Y-%m-%d")
        }

        if DataManager.guardar_datos('prestamos', DataManager.cargar_datos('prestamos') + [prestamo]):
            self.resultado.config(
                text=f"Préstamo registrado. Fecha de devolución: {fecha_devolucion.strftime('%Y-%m-%d')}", 
                foreground="green"
            )
            self.libro.set("")
            self.usuario.set("")
            self.actualizar_listas()

    def verificar_usuario(self, usuario):
        usuarios = DataManager.cargar_datos('usuarios')
        if any(u['nombre'] == usuario for u in usuarios):
            return True
            
        if messagebox.askyesno("Usuario no registrado", "¿Desea registrar este usuario ahora?"):
            nuevo_usuario = {
                "nombre": usuario,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d")
            }
            return DataManager.guardar_datos('usuarios', usuarios + [nuevo_usuario])
        return False

class DevolucionView(BaseView):
    def create_widgets(self):
        ttk.Label(self, text="📚 Registrar Devolución", 
                font=APP_STYLE['font']['title']).pack(pady=20)
        
        columns = ("ID", "Libro", "Usuario", "Préstamo", "Devolución")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="w")
        
        self.tree.column("ID", width=50)
        self.tree.column("Libro", width=200)
        
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(pady=10, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        frame_botones = ttk.Frame(self)
        frame_botones.pack(pady=10)
        
        ttk.Button(frame_botones, text="Registrar Devolución", 
                command=self.registrar_devolucion).pack(side="left", padx=10)
        ttk.Button(frame_botones, text="Actualizar Lista", 
                command=self.actualizar_lista_prestamos).pack(side="left", padx=10)
        ttk.Button(frame_botones, text="Volver", 
                command=lambda: self.controller.mostrar_vista(InicioView)).pack(side="left", padx=10)
        
        self.actualizar_lista_prestamos()
    
    def actualizar_lista_prestamos(self):
        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(DataManager.cargar_datos('prestamos'), 1):
            self.tree.insert("", "end", values=(
                i,
                p['libro'],
                p['usuario'],
                p['fecha_prestamo'],
                p['fecha_devolucion']
            ))
    
    def registrar_devolucion(self):
        if not (item := self.tree.focus()):
            messagebox.showwarning("Error", "Selecciona un préstamo de la lista")
            return
        
        datos = self.tree.item(item)['values']
        libro, usuario, fecha_prestamo = datos[1], datos[2], datos[3]
        
        devolucion = self.crear_registro_devolucion(datos)
        if not DataManager.guardar_datos('devoluciones', DataManager.cargar_datos('devoluciones') + [devolucion]):
            return

        self.eliminar_prestamo(libro, usuario, fecha_prestamo)
        self.mostrar_resumen(devolucion)
        self.actualizar_lista_prestamos()

    def crear_registro_devolucion(self, datos):
        fecha_devolucion_real = datetime.now()
        fecha_devolucion_prevista = datetime.strptime(datos[4], "%Y-%m-%d")
        dias_retraso = max(0, (fecha_devolucion_real - fecha_devolucion_prevista).days)
        
        return {
            "libro": datos[1],
            "usuario": datos[2],
            "fecha_prestamo": datos[3],
            "fecha_devolucion_prevista": datos[4],
            "fecha_devolucion_real": fecha_devolucion_real.strftime("%Y-%m-%d"),
            "dias_retraso": dias_retraso,
            "multa": dias_retraso * 1.5
        }

    def eliminar_prestamo(self, libro, usuario, fecha_prestamo):
        prestamos = [
            p for p in DataManager.cargar_datos('prestamos') 
            if not (p['libro'] == libro and p['usuario'] == usuario and p['fecha_prestamo'] == fecha_prestamo)
        ]
        DataManager.guardar_datos('prestamos', prestamos)

    def mostrar_resumen(self, devolucion):
        mensaje = f"Devolución registrada:\n\nLibro: {devolucion['libro']}\nUsuario: {devolucion['usuario']}"
        if devolucion['dias_retraso'] > 0:
            mensaje += f"\n\n¡Atención! Retraso de {devolucion['dias_retraso']} días.\nMulta aplicada: ${devolucion['multa']:.2f}"
        messagebox.showinfo("Éxito", mensaje)

class AdministrarCatalogoView(BaseView):
    def create_widgets(self):
        ttk.Label(self, text="📋 Administrar Catálogo", 
                font=APP_STYLE['font']['title'], 
                foreground=APP_STYLE['colors']['primary']).pack(pady=20)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.crear_pestana_agregar(notebook)
        self.crear_pestana_lista(notebook)
        self.crear_pestana_penalizaciones(notebook)
        
        ttk.Button(self, text="Volver", command=lambda: self.controller.mostrar_vista(InicioView)).pack(pady=10)

    def crear_pestana_agregar(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Agregar Libros")
        
        campos = [
            ("Título:", "titulo"),
            ("Autor:", "autor"),
            ("Género:", "genero")
        ]
        
        self.vars = {}
        for i, (texto, nombre) in enumerate(campos):
            ttk.Label(frame, text=texto).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            self.vars[nombre] = tk.StringVar()
            ttk.Entry(frame, textvariable=self.vars[nombre], width=40).grid(
                row=i, column=1, padx=10, pady=10, sticky="w")
        
        ttk.Button(frame, text="Agregar Libro", command=self.agregar_libro).grid(
            row=len(campos), column=1, pady=20, sticky="e")

    def crear_pestana_lista(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Lista de Libros")
        
        columns = ("Título", "Autor", "Género")
        self.tree_libros = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree_libros.heading(col, text=col)
            self.tree_libros.column(col, width=200, anchor="w")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree_libros.yview)
        self.tree_libros.configure(yscrollcommand=scrollbar.set)
        
        self.tree_libros.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.actualizar_lista_libros()

    def crear_pestana_penalizaciones(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Penalizaciones")
        ttk.Button(frame, text="Ver Penalizaciones", command=self.ver_penalizaciones).pack(pady=20)

    def agregar_libro(self):
        datos = {k: v.get().strip() for k, v in self.vars.items()}
        
        if not all(datos.values()):
            messagebox.showwarning("Campos incompletos", "Completa todos los campos.")
            return

        libros = DataManager.cargar_datos('libros')
        if any(libro['titulo'].lower() == datos['titulo'].lower() for libro in libros):
            messagebox.showwarning("Libro existente", "Este libro ya está en el catálogo.")
            return
            
        if DataManager.guardar_datos('libros', libros + [datos]):
            messagebox.showinfo("Éxito", f"'{datos['titulo']}' agregado al catálogo.")
            for var in self.vars.values():
                var.set("")
            self.actualizar_lista_libros()
    
    def actualizar_lista_libros(self):
        self.tree_libros.delete(*self.tree_libros.get_children())
        for libro in DataManager.cargar_datos('libros'):
            self.tree_libros.insert("", "end", values=(
                libro['titulo'],
                libro['autor'],
                libro['genero']
            ))

    def ver_penalizaciones(self):
        ventana = tk.Toplevel()
        ventana.title("Reporte de Penalizaciones")
        ventana.geometry("800x500")
        
        columns = ("Usuario", "Libro", "Fecha Devolución", "Días Retraso", "Multa")
        tree = ttk.Treeview(ventana, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")
        
        tree.column("Usuario", width=120)
        tree.column("Libro", width=200)
        
        scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        hoy = datetime.now()
        for p in DataManager.cargar_datos('prestamos'):
            devolucion = datetime.strptime(p['fecha_devolucion'], "%Y-%m-%d")
            if hoy > devolucion:
                dias_retraso = (hoy - devolucion).days
                tree.insert("", "end", values=(
                    p['usuario'],
                    p['libro'],
                    p['fecha_devolucion'],
                    dias_retraso,
                    f"${dias_retraso * 1.5:.2f}"
                ))

class ReportesView(BaseView):
    def create_widgets(self):
        ttk.Label(self, text="📊 Reportes y Estadísticas", 
                font=APP_STYLE['font']['title']).pack(pady=20)
        
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.crear_pestana_estadisticas(notebook)
        self.crear_pestana_libros(notebook)
        self.crear_pestana_usuarios(notebook)
        
        ttk.Button(self, text="Actualizar Reportes", command=self.actualizar_reportes).pack(pady=10)
        ttk.Button(self, text="Volver", command=lambda: self.controller.mostrar_vista(InicioView)).pack(pady=10)
        
        self.actualizar_reportes()
    
    def crear_pestana_estadisticas(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Estadísticas Generales")
        
        etiquetas = [
            ("Total de libros en catálogo:", "valor_total_libros"),
            ("Libros actualmente prestados:", "valor_libros_prestados"),
            ("Total de usuarios registrados:", "valor_total_usuarios"),
            ("Multas pendientes de pago:", "valor_multas_pendientes")
        ]
        
        for i, (texto, nombre) in enumerate(etiquetas):
            ttk.Label(frame, text=texto, font=APP_STYLE['font']['normal']).grid(
                row=i, column=0, padx=10, pady=10, sticky="e")
            setattr(self, nombre, ttk.Label(frame, text="0", font=APP_STYLE['font']['heading']))
            getattr(self, nombre).grid(row=i, column=1, padx=10, pady=10, sticky="w")
        
        self.valor_multas_pendientes.config(text="$0.00")

    def crear_pestana_libros(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Libros Más Prestados")
        
        self.tree_libros = self.crear_tabla(frame, ("Libro", "Veces Prestado"))

    def crear_pestana_usuarios(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Usuarios Más Activos")
        
        self.tree_usuarios = self.crear_tabla(frame, ("Usuario", "Préstamos", "Multas Acumuladas"))

    def crear_tabla(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return tree
    
    def actualizar_reportes(self):
        data = {
            'libros': DataManager.cargar_datos('libros'),
            'prestamos': DataManager.cargar_datos('prestamos'),
            'usuarios': DataManager.cargar_datos('usuarios'),
            'devoluciones': DataManager.cargar_datos('devoluciones')
        }
        
        # Estadísticas generales
        self.valor_total_libros.config(text=str(len(data['libros'])))
        self.valor_libros_prestados.config(text=str(len(data['prestamos'])))
        self.valor_total_usuarios.config(text=str(len(data['usuarios'])))
        
        hoy = datetime.now()
        multas_pendientes = sum(
            (hoy - datetime.strptime(p['fecha_devolucion'], "%Y-%m-%d")).days * 1.5
            for p in data['prestamos']
            if hoy > datetime.strptime(p['fecha_devolucion'], "%Y-%m-%d")
        )
        self.valor_multas_pendientes.config(text=f"${multas_pendientes:.2f}")
        
        # Libros más prestados
        conteo_libros = self.contar_ocurrencias(data['prestamos'] + data['devoluciones'], 'libro')
        self.actualizar_tabla(self.tree_libros, conteo_libros)
        
        # Usuarios más activos
        conteo_usuarios = self.contar_ocurrencias(data['prestamos'] + data['devoluciones'], 'usuario')
        multas_usuarios = self.sumar_multas_por_usuario(data['devoluciones'])
        self.actualizar_tabla_usuarios(conteo_usuarios, multas_usuarios)

    def contar_ocurrencias(self, datos, campo):
        conteo = {}
        for item in datos:
            conteo[item[campo]] = conteo.get(item[campo], 0) + 1
        return sorted(conteo.items(), key=lambda x: x[1], reverse=True)

    def sumar_multas_por_usuario(self, devoluciones):
        return {d['usuario']: sum(m['multa'] for m in devoluciones if m['usuario'] == d['usuario']) 
                for d in devoluciones}

    def actualizar_tabla(self, tree, datos):
        tree.delete(*tree.get_children())
        for item, count in datos:
            tree.insert("", "end", values=(item, count))

    def actualizar_tabla_usuarios(self, conteo, multas):
        self.tree_usuarios.delete(*self.tree_usuarios.get_children())
        for usuario, count in conteo:
            self.tree_usuarios.insert("", "end", values=(
                usuario, 
                count, 
                f"${multas.get(usuario, 0):.2f}"
            ))

class BibliotecaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 Biblioteca Digital")
        self.geometry("1000x700")
        self.resizable(True, True)
        self.configure(bg=APP_STYLE['colors']['background'])

        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}
        for vista in (InicioView, BuscarLibrosView, PrestamoView, 
                    AdministrarCatalogoView, DevolucionView, ReportesView):
            self.frames[vista] = vista(parent=container, controller=self)
            self.frames[vista].grid(row=0, column=0, sticky="nsew")

        self.mostrar_vista(InicioView)

    def mostrar_vista(self, cont):
        self.frames[cont].tkraise()

if __name__ == "__main__":
    # Inicializar archivos si no existen
    for archivo in DATA_FILES.values():
        if not archivo.exists():
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=4)
    
    app = BibliotecaApp()
    app.mainloop()