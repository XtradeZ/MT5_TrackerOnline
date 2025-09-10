# 🚀 Registrador de Operaciones MT5

Esta aplicación de escritorio permite a los traders conectar con su cuenta de MetaTrader 5, visualizar su historial de operaciones y exportarlo a archivos CSV y Excel para un análisis más detallado.

## 📸 Capturas de Pantalla

![Captura de pantalla de la aplicación MT5 Tracker](assets/images/Captura%20de%20pantalla%20de%20la%20aplicación%20MT5%20Tracker.JPG)

## ✨ Características

- **Conexión Segura a MT5**: Conecta directamente a tu cuenta de MetaTrader 5.
- **Visualización de Operaciones**: Carga y muestra tu historial de operaciones en una tabla interactiva.
- **Coloreado por Resultados**: Las filas de la tabla se colorean de verde (ganancias) o rojo (pérdidas) para una fácil visualización.
- **Edición de Comentarios**: Añade o edita comentarios directamente en la tabla y se guardarán para futuros usos.
- **Exportación de Datos**: Exporta tu historial de operaciones a formatos `.csv` y `.xlsx`.
- **Manejo Incremental**: Al exportar, la aplicación solo añade las operaciones nuevas, evitando duplicados y actualizando comentarios.
- **Interfaz Gráfica Intuitiva**: Desarrollada con PyQt5 para una experiencia de usuario fluida.
- **Configurable**: Ajusta la configuración de la aplicación a través de un archivo `config_simple.json`.

## 📁 Estructura del Proyecto

```
demo/
├── mt5_tracker/         # Módulo principal de la aplicación
│   ├── app.py           # Punto de entrada y configuración de la app
│   ├── ui.py            # Lógica de la interfaz gráfica (PyQt5)
│   ├── connector.py     # Maneja la conexión con MetaTrader 5
│   ├── tracker.py       # Procesa los datos de las operaciones
│   ├── file_manager.py  # Gestiona la exportación de archivos
│   └── comments_manager.py # Maneja los comentarios de las operaciones
├── assets/              # Recursos como imágenes y logos
├── output/              # Carpeta por defecto para los archivos exportados
├── main.py              # Script principal para ejecutar la aplicación
├── config_simple.json   # Archivo de configuración
└── requirements.txt     # Dependencias del proyecto
```

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner en marcha la aplicación.

### 1. Prerrequisitos

- Python 3.x
- Una cuenta de MetaTrader 5

### 2. Clonar el Repositorio

```bash
git clone <URL-DEL-REPOSITORIO>
cd demo
```

### 3. Crear un Entorno Virtual (Recomendado)

```bash
python -m venv venv
```
**Windows:**
```bash
venv\Scripts\activate
```
**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar Dependencias

Asegúrate de tener tu entorno virtual activado e instala las librerías necesarias:
```bash
pip install -r requirements.txt
```

### 5. Configurar la Aplicación

Antes de lanzar la aplicación, puedes personalizar su comportamiento editando el archivo `config_simple.json`:

```json
{
    "app_settings": {
        "window_size": [1400, 900],
        "window_title": "Registrador de Operaciones MT5"
    },
    "export_settings": {
        "output_folder": "output",
        "columns": ["Ticket", "Símbolo", "Tipo", "Volumen", "Precio", "Beneficio", "Fecha Apertura", "Fecha Cierre", "Comentario"]
    }
}
```

- **`window_size`**: Ancho y alto de la ventana de la aplicación.
- **`window_title`**: Título que aparecerá en la ventana.
- **`output_folder`**: Carpeta donde se guardarán los archivos CSV/Excel.
- **`columns`**: Las columnas que se incluirán en los archivos exportados.

## ▶️ Cómo Ejecutar la Aplicación

Con tu entorno virtual activado y las dependencias instaladas, ejecuta el siguiente comando desde la carpeta `demo`:

```bash
python main.py
```

Al abrirse la aplicación:
1.  Introduce tus credenciales de MetaTrader 5 (login, contraseña y servidor).
2.  Haz clic en **"Conectar MT5"**.
3.  Una vez conectado, haz clic en **"Cargar Todas las Operaciones"**.
4.  Tu historial de operaciones aparecerá en la tabla.
5.  Usa los botones de exportación para guardar los datos.

---

**¡Disfruta de un registro de trading más organizado!** 🚀 
