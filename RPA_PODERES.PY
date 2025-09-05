import sys
import os
import re
import shutil  # Para copiar archivos
import fitz  # PyMuPDF para leer PDFs
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QTableWidget, QTableWidgetItem, 
                             QProgressBar, QTextEdit, QGroupBox, QFrame, QScrollArea,
                             QSplitter, QHeaderView, QApplication, QCheckBox)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

def extraer_cliente_fecha(nombre_archivo):
    # Busca patrón: _DNI_CLIENTE_FECHA.pdf
    # Ejemplo: CertificadoRegistro.pdf_05318950Q_JEAN_-_PIERRE_ALVARADO_ARIAS_2025-07-29_07:02:18.pdf
    patron = r'_(\w{7,9}[A-Z])_([A-ZÁÉÍÓÚÑa-záéíóúñ\-\s]+)_((?:\d{4}-\d{2}-\d{2})_\d{2}:\d{2}:\d{2})'
    m = re.search(patron, nombre_archivo)
    if m:
        cliente = m.group(2).replace('_', ' ').strip()
        fecha = m.group(3).replace('_', ' ')
        return cliente, fecha
    # Alternativa: buscar última fecha tipo yyyy-mm-dd en el nombre
    fecha_alt = re.findall(r'(\d{4}-\d{2}-\d{2})', nombre_archivo)
    fecha = fecha_alt[-1] if fecha_alt else ''
    return '', fecha

# ---- Worker Thread para procesamiento en segundo plano ----
class ProcessingWorker(QThread):
    progress_update = pyqtSignal(int, str, dict)  # progreso, archivo actual, resultado
    finished = pyqtSignal(list)  # resultados finales
    error = pyqtSignal(str)  # errores
    
    def __init__(self, folder_path, export_folder=None):
        super().__init__()
        self.folder_path = folder_path
        self.export_folder = export_folder
        self.is_cancelled = False
    
    def cancel(self):
        self.is_cancelled = True
    
    def run(self):
        try:
            resultados_excel = []
            pdf_files = [f for f in os.listdir(self.folder_path) if f.lower().endswith(".pdf")]
            total_files = len(pdf_files)
            if total_files == 0:
                self.error.emit("No se encontraron archivos PDF en la carpeta seleccionada.")
                return
            for i, file in enumerate(pdf_files):
                if self.is_cancelled:
                    return
                try:
                    full_path = os.path.join(self.folder_path, file)
                    text, has_ocr = extract_text_from_pdf(full_path)
                    resultados = buscar_identificadores(text)
                    cliente, fecha = extraer_cliente_fecha(file)
                    if resultados:
                        tipo, secuencia, post = resultados[0]  # Solo primera coincidencia
                        nuevo_nombre = f"PODER_{secuencia}.pdf"
                        nuevo_path = os.path.join(self.folder_path, nuevo_nombre)
                        # Verificar si ya existe un archivo con ese nombre en la carpeta original
                        counter = 1
                        base_nuevo_nombre = nuevo_nombre
                        while os.path.exists(nuevo_path):
                            name, ext = os.path.splitext(base_nuevo_nombre)
                            nuevo_nombre = f"{name}_{counter}{ext}"
                            nuevo_path = os.path.join(self.folder_path, nuevo_nombre)
                            counter += 1
                        # Si hay carpeta de exportación, verificar si ya existe el archivo
                        export_path = ""
                        repetido_destino = False
                        if self.export_folder:
                            export_path = os.path.join(self.export_folder, nuevo_nombre)
                            if os.path.exists(export_path):
                                # No copiar ni renombrar, marcar como repetido
                                repetido_destino = True
                                estado = "Repetido en destino - No copiado"
                                resultado = {
                                    "archivo_original": file,
                                    "archivo_nuevo": nuevo_nombre,
                                    "tipo": tipo,
                                    "secuencia": secuencia,
                                    "secuencia_post": post,
                                    "estado": estado,
                                    "export_path": export_path,
                                    "tiene_ocr": "Sí" if has_ocr else "No",
                                    "cliente": cliente,
                                    "fecha": fecha
                                }
                                resultados_excel.append([file, nuevo_nombre, tipo, secuencia, post, estado, export_path, "Sí" if has_ocr else "No", cliente, fecha])
                                progress = int((i + 1) / total_files * 100)
                                self.progress_update.emit(progress, file, resultado)
                                continue
                        # Renombrar en la carpeta original
                        os.rename(full_path, nuevo_path)
                        if self.export_folder and not repetido_destino:
                            # Verificar duplicados en destino (por si el nombre cambia por sufijo)
                            export_path = os.path.join(self.export_folder, nuevo_nombre)
                            counter = 1
                            base_export_name = nuevo_nombre
                            while os.path.exists(export_path):
                                name, ext = os.path.splitext(base_export_name)
                                export_name = f"{name}_{counter}{ext}"
                                export_path = os.path.join(self.export_folder, export_name)
                                counter += 1
                            shutil.copy2(nuevo_path, export_path)
                        resultado = {
                            "archivo_original": file,
                            "archivo_nuevo": nuevo_nombre,
                            "tipo": tipo,
                            "secuencia": secuencia,
                            "secuencia_post": post,
                            "estado": "Procesado correctamente",
                            "export_path": export_path if self.export_folder else "No exportado",
                            "tiene_ocr": "Sí" if has_ocr else "No",
                            "cliente": cliente,
                            "fecha": fecha
                        }
                        resultados_excel.append([file, nuevo_nombre, tipo, secuencia, post, "Procesado", export_path if self.export_folder else "No exportado", "Sí" if has_ocr else "No", cliente, fecha])
                    else:
                        # No se encontraron identificadores - verificar OCR
                        estado_ocr = "Sí" if has_ocr else "No"
                        estado_procesamiento = "Sin identificadores" if has_ocr else "Sin identificadores - Sin OCR"
                        
                        # Si no se encontraron identificadores pero hay carpeta de exportación, copiar el archivo original
                        export_path = ""
                        if self.export_folder:
                            prefijo = "SIN_ID_" if has_ocr else "SIN_OCR_"
                            export_path = os.path.join(self.export_folder, f"{prefijo}{file}")
                            # Verificar duplicados
                            counter = 1
                            base_export_name = f"{prefijo}{file}"
                            while os.path.exists(export_path):
                                name, ext = os.path.splitext(base_export_name)
                                export_name = f"{name}_{counter}{ext}"
                                export_path = os.path.join(self.export_folder, export_name)
                                counter += 1
                            
                            shutil.copy2(full_path, export_path)
                        
                        resultado = {
                            "archivo_original": file,
                            "archivo_nuevo": file,
                            "tipo": "NO ENCONTRADO",
                            "secuencia": "",
                            "secuencia_post": "",
                            "estado": estado_procesamiento,
                            "export_path": export_path if self.export_folder else "No exportado",
                            "tiene_ocr": estado_ocr,
                            "cliente": cliente,
                            "fecha": fecha
                        }
                        resultados_excel.append([file, file, "NO ENCONTRADO", "", "", estado_procesamiento, export_path if self.export_folder else "No exportado", estado_ocr, cliente, fecha])
                    # Emitir progreso
                    progress = int((i + 1) / total_files * 100)
                    self.progress_update.emit(progress, file, resultado)
                except Exception as e:
                    # En caso de error, verificar si al menos tiene OCR
                    try:
                        has_ocr = verificar_ocr_pdf(os.path.join(self.folder_path, file))
                        estado_ocr = "Sí" if has_ocr else "No"
                    except:
                        estado_ocr = "No se pudo verificar"
                    cliente, fecha = extraer_cliente_fecha(file)
                    resultado = {
                        "archivo_original": file,
                        "archivo_nuevo": file,
                        "tipo": "ERROR",
                        "secuencia": "",
                        "secuencia_post": "",
                        "estado": f"Error: {str(e)}",
                        "export_path": "Error en exportación",
                        "tiene_ocr": estado_ocr,
                        "cliente": cliente,
                        "fecha": fecha
                    }
                    resultados_excel.append([file, file, "ERROR", "", "", f"Error: {str(e)}", "Error en exportación", estado_ocr, cliente, fecha])
                    progress = int((i + 1) / total_files * 100)
                    self.progress_update.emit(progress, file, resultado)
            self.finished.emit(resultados_excel)
        except Exception as e:
            self.error.emit(f"Error general en el procesamiento: {str(e)}")

# ---- Función para extraer texto del PDF ----
def extract_text_from_pdf(pdf_path):
    text = ""
    has_ocr = False
    
    with fitz.open(pdf_path) as doc:
        for page in doc:
            page_text = page.get_text()
            text += page_text
            
            # Verificar si la página tiene texto extraíble (OCR)
            if page_text.strip():
                has_ocr = True
    
    return text, has_ocr

# ---- Verificar si un PDF tiene OCR ----
def verificar_ocr_pdf(pdf_path):
    """Verificar si un PDF tiene texto extraíble (OCR)"""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                page_text = page.get_text().strip()
                if page_text:
                    return True
        return False
    except Exception:
        return False

# ---- Buscar DNI/NIF/NIE en texto ----
def buscar_identificadores(text):
    dni_nif_pattern = r"\b\d{7,8}[A-Z]\b"
    nie_pattern = r"\b[XYZ]\d{7}[A-Z]\b"
    
    resultados = []
    
    for match in re.finditer(f"{nie_pattern}|{dni_nif_pattern}", text):
        secuencia = match.group()
        tipo = "NIE" if re.match(nie_pattern, secuencia) else "DNI/NIF"
        
        # Buscar lo que viene después (10 caracteres siguientes como ejemplo)
        start_pos = match.end()
        secuencia_post = text[start_pos:start_pos+20].strip()
        resultados.append((tipo, secuencia, secuencia_post))
        
    return resultados

# ---- Ventana principal mejorada ----
class RPAWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.setupStyles()
        self.folder = ""
        self.export_folder = ""
        self.worker = None
        self.resultados_procesamiento = []

    def setupUI(self):
        self.setWindowTitle("RPA Buscador DNI/NIF/NIE - Procesador de Poderes")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Header con título
        self.create_header(main_layout)
        
        # Splitter para dividir la interfaz
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Panel izquierdo - Controles
        self.create_control_panel(splitter)
        
        # Panel derecho - Resultados
        self.create_results_panel(splitter)
        
        # Footer con información
        self.create_footer(main_layout)
        
        # Configurar proporciones del splitter
        splitter.setSizes([450, 950])

    def create_header(self, layout):
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_layout = QVBoxLayout()
        header_frame.setLayout(header_layout)
        
        title_label = QLabel("RPA - Procesador Automático de Poderes")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Búsqueda, renombrado y exportación automática de archivos PDF por DNI/NIF/NIE")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)

    def create_control_panel(self, splitter):
        # Panel de controles
        control_frame = QFrame()
        control_frame.setObjectName("controlFrame")
        control_layout = QVBoxLayout()
        control_frame.setLayout(control_layout)
        
        # Grupo de selección de carpeta origen
        folder_group = QGroupBox("📁 Carpeta de Origen (PDFs)")
        folder_layout = QVBoxLayout()
        folder_group.setLayout(folder_layout)
        
        self.folder_label = QLabel("Ninguna carpeta seleccionada")
        self.folder_label.setObjectName("folderLabel")
        self.folder_label.setWordWrap(True)
        
        self.btn_select_folder = QPushButton("� Seleccionar Carpeta con PDFs")
        self.btn_select_folder.setObjectName("primaryButton")
        self.btn_select_folder.clicked.connect(self.select_folder)
        
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.btn_select_folder)
        
        # Grupo de exportación
        export_group = QGroupBox("📤 Exportación de Archivos")
        export_layout = QVBoxLayout()
        export_group.setLayout(export_layout)
        
        self.export_checkbox = QCheckBox("Exportar archivos procesados a otra carpeta")
        self.export_checkbox.setObjectName("exportCheckbox")
        self.export_checkbox.toggled.connect(self.toggle_export_options)
        
        self.export_folder_label = QLabel("Ninguna carpeta de exportación seleccionada")
        self.export_folder_label.setObjectName("exportFolderLabel")
        self.export_folder_label.setWordWrap(True)
        self.export_folder_label.setEnabled(False)
        
        self.btn_select_export_folder = QPushButton("📁 Seleccionar Carpeta de Destino")
        self.btn_select_export_folder.setObjectName("secondaryButton")
        self.btn_select_export_folder.clicked.connect(self.select_export_folder)
        self.btn_select_export_folder.setEnabled(False)
        
        export_layout.addWidget(self.export_checkbox)
        export_layout.addWidget(self.export_folder_label)
        export_layout.addWidget(self.btn_select_export_folder)
        
        # Grupo de procesamiento
        process_group = QGroupBox("⚙️ Procesamiento")
        process_layout = QVBoxLayout()
        process_group.setLayout(process_layout)
        
        self.btn_process = QPushButton("🚀 Iniciar Procesamiento")
        self.btn_process.setObjectName("primaryButton")
        self.btn_process.clicked.connect(self.process_files)
        self.btn_process.setEnabled(False)
        
        self.btn_cancel = QPushButton("⏹️ Cancelar Procesamiento")
        self.btn_cancel.setObjectName("secondaryButton")
        self.btn_cancel.clicked.connect(self.cancel_processing)
        self.btn_cancel.setEnabled(False)
        
        self.btn_export_excel = QPushButton("💾 Exportar Resultados a Excel")
        self.btn_export_excel.setObjectName("successButton")
        self.btn_export_excel.clicked.connect(self.export_to_excel)
        self.btn_export_excel.setEnabled(False)
        
        process_layout.addWidget(self.btn_process)
        process_layout.addWidget(self.btn_cancel)
        process_layout.addWidget(self.btn_export_excel)
        
        # Grupo de progreso
        progress_group = QGroupBox("📊 Progreso del Procesamiento")
        progress_layout = QVBoxLayout()
        progress_group.setLayout(progress_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        
        self.progress_label = QLabel("Listo para procesar")
        self.progress_label.setObjectName("progressLabel")
        
        self.current_file_label = QLabel("")
        self.current_file_label.setObjectName("currentFileLabel")
        self.current_file_label.setWordWrap(True)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.current_file_label)
        
        # Log de actividad
        log_group = QGroupBox("📋 Log de Actividad")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setObjectName("logText")
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        
        log_layout.addWidget(self.log_text)
        
        # Añadir grupos al layout de control
        control_layout.addWidget(folder_group)
        control_layout.addWidget(export_group)
        control_layout.addWidget(process_group)
        control_layout.addWidget(progress_group)
        control_layout.addWidget(log_group)
        control_layout.addStretch()
        
        splitter.addWidget(control_frame)

    def create_results_panel(self, splitter):
        # Panel de resultados
        results_frame = QFrame()
        results_frame.setObjectName("resultsFrame")
        results_layout = QVBoxLayout()
        results_frame.setLayout(results_layout)
        
        # Título de resultados
        results_title = QLabel("📈 Resultados del Procesamiento")
        results_title.setObjectName("sectionTitle")
        results_layout.addWidget(results_title)
        
        # Estadísticas
        stats_frame = QFrame()
        stats_frame.setObjectName("statsFrame")
        stats_layout = QHBoxLayout()
        stats_frame.setLayout(stats_layout)
        
        self.total_files_label = QLabel("Total: 0")
        self.processed_files_label = QLabel("Procesados: 0")
        self.error_files_label = QLabel("Errores: 0")
        self.exported_files_label = QLabel("Exportados: 0")
        self.no_ocr_files_label = QLabel("Sin OCR: 0")
        
        for label in [self.total_files_label, self.processed_files_label, self.error_files_label, self.exported_files_label, self.no_ocr_files_label]:
            label.setObjectName("statsLabel")
        
        stats_layout.addWidget(self.total_files_label)
        stats_layout.addWidget(self.processed_files_label)
        stats_layout.addWidget(self.error_files_label)
        stats_layout.addWidget(self.exported_files_label)
        stats_layout.addWidget(self.no_ocr_files_label)
        stats_layout.addStretch()
        
        results_layout.addWidget(stats_frame)
        
        # Tabla de resultados
        self.results_table = QTableWidget()
        self.results_table.setObjectName("resultsTable")
        self.results_table.setColumnCount(10)
        self.results_table.setHorizontalHeaderLabels([
            "Archivo Original", "Archivo Nuevo", "Tipo ID", "Identificador", "Texto Posterior", "Estado", "Ruta Exportación", "Tiene OCR", "Cliente", "Fecha"
        ])
        
        # Configurar tabla
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)
        
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_frame)

    def create_footer(self, layout):
        footer_frame = QFrame()
        footer_frame.setObjectName("footerFrame")
        footer_layout = QHBoxLayout()
        footer_frame.setLayout(footer_layout)

        footer_label = QLabel("© 2025 DANIEL GARCÍA CARABELOS. - Herramientas RPA para gestión de poderes")
        footer_label.setObjectName("footerLabel")
        
        footer_layout.addWidget(footer_label)
        footer_layout.addStretch()
        
        layout.addWidget(footer_frame)

    def setupStyles(self):
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        #headerFrame {
            background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                        stop: 0 #2c3e50, stop: 1 #3498db);
            color: white;
            padding: 20px;
            margin-bottom: 10px;
        }
        
        #titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: white;
        }
        
        #subtitleLabel {
            font-size: 14px;
            color: #ecf0f1;
        }
        
        #controlFrame {
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            margin: 5px;
        }
        
        #resultsFrame {
            background-color: white;
            border: 1px solid #bdc3c7;
            border-radius: 8px;
            margin: 5px;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
            color: #2c3e50;
        }
        
        #primaryButton {
            background-color: #3498db;
            border: none;
            color: white;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            margin: 5px;
        }
        
        #primaryButton:hover {
            background-color: #2980b9;
        }
        
        #primaryButton:pressed {
            background-color: #21618c;
        }
        
        #primaryButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        #secondaryButton {
            background-color: #e74c3c;
            border: none;
            color: white;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            margin: 5px;
        }
        
        #secondaryButton:hover {
            background-color: #c0392b;
        }
        
        #secondaryButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        #exportCheckbox {
            font-weight: bold;
            color: #2c3e50;
            padding: 5px;
        }
        
        #folderLabel, #exportFolderLabel {
            color: #7f8c8d;
            font-style: italic;
            padding: 10px;
            background-color: #ecf0f1;
            border-radius: 4px;
        }
        
        #successButton {
            background-color: #27ae60;
            border: none;
            color: white;
            padding: 12px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 6px;
            margin: 5px;
        }
        
        #successButton:hover {
            background-color: #229954;
        }
        
        #successButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        #progressBar {
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            text-align: center;
            background-color: #ecf0f1;
        }
        
        #progressBar::chunk {
            background-color: #3498db;
            border-radius: 6px;
        }
        
        #progressLabel {
            font-weight: bold;
            color: #2c3e50;
        }
        
        #currentFileLabel {
            color: #7f8c8d;
            font-size: 12px;
        }
        
        #logText {
            background-color: #2c3e50;
            color: #ecf0f1;
            border: none;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }
        
        #sectionTitle {
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        }
        
        #statsFrame {
            background-color: #ecf0f1;
            border-radius: 6px;
            padding: 10px;
            margin: 5px;
        }
        
        #statsLabel {
            font-weight: bold;
            color: #2c3e50;
            padding: 5px 15px;
            background-color: white;
            border-radius: 4px;
            margin: 0 5px;
        }
        
        #resultsTable {
            gridline-color: #bdc3c7;
            background-color: white;
            alternate-background-color: #f8f9fa;
            selection-background-color: #3498db;
        }
        
        #resultsTable::item {
            padding: 8px;
        }
        
        #footerFrame {
            background-color: #34495e;
            color: white;
            padding: 10px;
        }
        
        #footerLabel {
            color: #ecf0f1;
            font-size: 12px;
        }
        """
        self.setStyleSheet(style)

    def log_message(self, message):
        """Añadir mensaje al log con timestamp"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto scroll al final
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def update_stats(self):
        """Actualizar estadísticas en tiempo real"""
        total = len(self.resultados_procesamiento)
        procesados = sum(1 for r in self.resultados_procesamiento if r[5] == "Procesado")
        errores = sum(1 for r in self.resultados_procesamiento if "Error" in r[5])
        exportados = sum(1 for r in self.resultados_procesamiento if len(r) > 6 and r[6] != "No exportado" and r[6] != "Error en exportación")
        sin_ocr = sum(1 for r in self.resultados_procesamiento if len(r) > 7 and r[7] == "No")
        
        self.total_files_label.setText(f"Total: {total}")
        self.processed_files_label.setText(f"Procesados: {procesados}")
        self.error_files_label.setText(f"Errores: {errores}")
        self.exported_files_label.setText(f"Exportados: {exportados}")
        self.no_ocr_files_label.setText(f"Sin OCR: {sin_ocr}")

    def toggle_export_options(self, checked):
        """Habilitar/deshabilitar opciones de exportación"""
        self.export_folder_label.setEnabled(checked)
        self.btn_select_export_folder.setEnabled(checked)
        
        if not checked:
            self.export_folder = ""
            self.export_folder_label.setText("Ninguna carpeta de exportación seleccionada")
            self.log_message("Exportación deshabilitada")
        else:
            self.log_message("Exportación habilitada - selecciona carpeta de destino")

    def select_export_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de destino para exportación")
        if folder:
            self.export_folder = folder
            self.export_folder_label.setText(f"Carpeta de exportación:\n{folder}")
            self.log_message(f"Carpeta de exportación seleccionada: {folder}")

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta con PDFs")
        if folder:
            self.folder = folder
            self.folder_label.setText(f"Carpeta seleccionada:\n{folder}")
            self.btn_process.setEnabled(True)
            self.log_message(f"Carpeta origen seleccionada: {folder}")
            
            # Contar archivos PDF
            pdf_count = len([f for f in os.listdir(folder) if f.lower().endswith('.pdf')])
            self.log_message(f"Se encontraron {pdf_count} archivos PDF")

    def process_files(self):
        if not self.folder:
            QMessageBox.warning(self, "Error", "Selecciona una carpeta de origen primero")
            return
        
        if self.export_checkbox.isChecked() and not self.export_folder:
            QMessageBox.warning(self, "Error", "Selecciona una carpeta de exportación o desactiva la opción de exportar")
            return
        
        # Limpiar resultados previos
        self.resultados_procesamiento.clear()
        self.results_table.setRowCount(0)
        
        # Configurar UI para procesamiento
        self.btn_process.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_export_excel.setEnabled(False)
        self.progress_bar.setValue(0)
        
        # Determinar carpeta de exportación
        export_folder = self.export_folder if self.export_checkbox.isChecked() else None
        
        # Iniciar worker thread
        self.worker = ProcessingWorker(self.folder, export_folder)
        self.worker.progress_update.connect(self.on_progress_update)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.error.connect(self.on_processing_error)
        self.worker.start()
        
        if export_folder:
            self.log_message(f"Iniciando procesamiento con exportación a: {export_folder}")
        else:
            self.log_message("Iniciando procesamiento sin exportación")

    def cancel_processing(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.wait()
            self.log_message("Procesamiento cancelado por el usuario")
            self.reset_ui_after_processing()

    def on_progress_update(self, progress, current_file, resultado):
        """Actualizar UI con el progreso"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Progreso: {progress}%")
        self.current_file_label.setText(f"Procesando: {current_file}")
        
        # Añadir resultado a la tabla
        row_position = self.results_table.rowCount()
        self.results_table.insertRow(row_position)
        
        items = [
            resultado["archivo_original"],
            resultado["archivo_nuevo"],
            resultado["tipo"],
            resultado["secuencia"],
            resultado["secuencia_post"],
            resultado["estado"],
            resultado.get("export_path", "No exportado"),
            resultado.get("tiene_ocr", "No verificado"),
            resultado.get("cliente", ""),
            resultado.get("fecha", "")
        ]
        for col, item_text in enumerate(items):
            item = QTableWidgetItem(str(item_text))
            
            # Colorear según el estado
            if "Error" in resultado["estado"]:
                item.setBackground(QColor("#ffebee"))
            elif resultado["estado"] == "Procesado correctamente":
                item.setBackground(QColor("#e8f5e8"))
            elif "Sin identificadores" in resultado["estado"]:
                if "Sin OCR" in resultado["estado"]:
                    item.setBackground(QColor("#ffcdd2"))  # Rojo más claro para sin OCR
                else:
                    item.setBackground(QColor("#fff3e0"))  # Naranja para sin identificadores pero con OCR
            
            self.results_table.setItem(row_position, col, item)
        
        # Añadir a resultados
        self.resultados_procesamiento.append(items)
        
        # Actualizar estadísticas
        self.update_stats()
        
        # Log del archivo procesado
        if resultado["tipo"] != "ERROR":
            ocr_info = f" (OCR: {resultado.get('tiene_ocr', 'No verificado')})"
            if resultado.get("export_path", "No exportado") != "No exportado":
                self.log_message(f"Procesado y exportado: {current_file} -> {resultado['tipo']}: {resultado['secuencia']}{ocr_info}")
            else:
                if resultado["tipo"] == "NO ENCONTRADO":
                    self.log_message(f"Sin identificadores: {current_file}{ocr_info}")
                else:
                    self.log_message(f"Procesado: {current_file} -> {resultado['tipo']}: {resultado['secuencia']}{ocr_info}")
        else:
            self.log_message(f"Error en: {current_file} - {resultado['estado']}")

    def on_processing_finished(self, resultados):
        """Procesamiento completado"""
        self.log_message(f"Procesamiento completado. Total de archivos: {len(resultados)}")
        self.reset_ui_after_processing()
        self.btn_export_excel.setEnabled(True)
        
        # Mostrar resumen
        total = len(resultados)
        procesados = sum(1 for r in resultados if len(r) > 5 and r[5] == "Procesado")
        errores = sum(1 for r in resultados if len(r) > 5 and "Error" in r[5])
        sin_ocr = sum(1 for r in resultados if len(r) > 7 and r[7] == "No")
        exportados = sum(1 for r in resultados if len(r) > 6 and r[6] != "No exportado" and r[6] != "Error en exportación")
        
        mensaje_resumen = f"Procesamiento finalizado exitosamente.\n\n"
        mensaje_resumen += f"Total de archivos: {total}\n"
        mensaje_resumen += f"Procesados correctamente: {procesados}\n"
        mensaje_resumen += f"Errores: {errores}\n"
        mensaje_resumen += f"Documentos sin OCR: {sin_ocr}\n"
        
        if self.export_checkbox.isChecked():
            mensaje_resumen += f"Archivos exportados: {exportados}\n"
        
        mensaje_resumen += "\nLos resultados están disponibles en la tabla."
        
        QMessageBox.information(self, "Procesamiento Completado", mensaje_resumen)

    def on_processing_error(self, error_message):
        """Error en el procesamiento"""
        self.log_message(f"Error: {error_message}")
        QMessageBox.critical(self, "Error", f"Error durante el procesamiento:\n{error_message}")
        self.reset_ui_after_processing()

    def reset_ui_after_processing(self):
        """Resetear UI después del procesamiento"""
        self.btn_process.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.progress_label.setText("Procesamiento completado")
        self.current_file_label.setText("")

    def export_to_excel(self):
        """Exportar resultados a Excel"""
        if not self.resultados_procesamiento:
            QMessageBox.warning(self, "Error", "No hay resultados para exportar")
            return
        
        try:
            columns = ["Archivo Original", "Archivo Nuevo", "Tipo ID", "Identificador", "Texto Posterior", "Estado", "Ruta Exportación", "Tiene OCR", "Cliente", "Fecha"]
            df = pd.DataFrame(self.resultados_procesamiento, columns=columns)
            excel_path = os.path.join(self.folder, "resultado_rpa_detallado.xlsx")
            df.to_excel(excel_path, index=False)
            
            self.log_message(f"Resultados exportados a: {excel_path}")
            QMessageBox.information(
                self, 
                "Exportación Completada", 
                f"Los resultados se han exportado correctamente a:\n{excel_path}"
            )
        except Exception as e:
            error_msg = f"Error al exportar a Excel: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "Error de Exportación", error_msg)

    def closeEvent(self, event):
        """Manejar cierre de la aplicación"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, 
                'Confirmar Cierre', 
                'Hay un procesamiento en curso. ¿Desea cancelarlo y salir?',
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.worker.cancel()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

# ---- Ejecutar la aplicación ----
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Configurar estilo de aplicación
    app.setStyle('Fusion')
    
    # Configurar icono de la aplicación (opcional)
    # app.setWindowIcon(QIcon('icono.png'))
    
    window = RPAWindow()
    window.show()
    
    sys.exit(app.exec_())
