# 💰 Calculadora de Inversiones

**Simulador Financiero - UNT Finanzas Corporativas - Grupo 6**

Una aplicación web interactiva construida con Streamlit para calcular y analizar inversiones y valoración de bonos. Incluye análisis inteligente con IA (Gemini) y generación de reportes en PDF.

## 📋 Descripción

Esta aplicación permite a los usuarios:

- **📈 Módulo de Inversiones**: Calcular el crecimiento de carteras de inversión con aportes periódicos, considerando impuestos y diferentes escenarios de retiro
- **📊 Módulo de Bonos**: Valorar bonos y analizar su atractivo de inversión con cálculos de valor presente, cupones y sensibilidad

Ambos módulos incluyen:
- Visualizaciones interactivas con Plotly
- Análisis inteligente con Google Gemini AI
- Generación de reportes en PDF
- Envío de reportes por correo electrónico

## ✨ Características

### Módulo de Inversiones
- Cálculo de crecimiento de cartera con interés compuesto
- Aportes periódicos configurables (mensual, trimestral, semestral, anual)
- Consideración de impuestos (Bolsa Local 5% o Bolsa Extranjera 29.5%)
- Dos tipos de retiro: cobro total o pensión mensual
- Visualizaciones de crecimiento del capital
- Análisis de ROI y rentabilidad
- Comparación de escenarios
- Análisis de sensibilidad

### Módulo de Bonos
- Valoración de bonos con diferentes tasas de cupón
- Cálculo de valor presente y flujos de caja
- Identificación de bonos a descuento, prima o a la par
- Análisis de sensibilidad a cambios en tasas de interés
- Comparación de escenarios
- Visualizaciones de flujos de caja

### Funcionalidades Generales
- 🤖 Análisis inteligente con IA (Google Gemini)
- 📄 Generación de reportes PDF profesionales
- 📧 Envío de reportes por correo electrónico
- 📊 Gráficos interactivos con Plotly
- 🎨 Interfaz moderna y fácil de usar

## 🚀 Instalación

### Requisitos Previos
- Python 3.11 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd calculadora-inversiones
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.streamlit/secrets.toml` con las siguientes configuraciones:

```toml
# API Key de Google Gemini para análisis inteligente
GEMINI_API_KEY = "tu-api-key-de-gemini"

# Configuración de correo electrónico (Gmail)
EMAIL_SENDER = "tu-email@gmail.com"
EMAIL_PASSWORD = "tu-contraseña-de-aplicacion"
```

#### Obtener API Key de Gemini
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva API key
3. Copia la clave y agrégala a `secrets.toml`

#### Configurar Gmail para envío de correos
1. Habilita la verificación en 2 pasos en tu cuenta de Google
2. Genera una contraseña de aplicación:
   - Ve a [Cuenta de Google](https://myaccount.google.com/)
   - Seguridad → Verificación en 2 pasos → Contraseñas de aplicaciones
   - Genera una contraseña para "Correo"
3. Usa esta contraseña en `EMAIL_PASSWORD`

### Estructura de Carpetas

Asegúrate de que tu proyecto tenga la siguiente estructura:

```
calculadora-inversiones/
├── app.py
├── requirements.txt
├── .streamlit/
│   └── secrets.toml
├── ui/
│   ├── components/
│   │   ├── sidebar.py
│   │   └── footer.py
│   ├── forms/
│   │   ├── inversiones.py
│   │   └── bonos.py
│   └── results/
│       ├── res_inversiones.py
│       ├── res_mod_b.py
│       └── res_mod_c.py
└── utils/
    ├── utils.py
    ├── gemini.py
    └── email.py
```

## 🎯 Uso

### Ejecutar la Aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Usar el Módulo de Inversiones

1. Ingresa tu nombre y correo electrónico en la barra lateral
2. Selecciona "📈 Inversiones"
3. Completa los parámetros:
   - Edad actual
   - Monto inicial en USD
   - Tipo de impuesto (Bolsa Local o Extranjera)
   - Aporte periódico (opcional)
   - Tasa Efectiva Anual (TEA)
   - Frecuencia de aportes
   - Tiempo de retiro o edad de jubilación
   - Tipo de retiro (cobro total o pensión mensual)
4. Haz clic en "Calcular" para ver los resultados
5. Explora las visualizaciones y análisis
6. Genera y descarga el reporte PDF
7. Opcionalmente, envía el reporte por correo

### Usar el Módulo de Bonos

1. Ingresa tu nombre y correo electrónico en la barra lateral
2. Selecciona "📊 Bonos"
3. Completa los parámetros del bono:
   - Valor nominal
   - Tasa cupón (% TEA)
   - Frecuencia de pago
   - Plazo en años
   - Tasa de retorno esperada (% TEA)
4. Haz clic en "Calcular" para ver la valoración
5. Revisa el análisis de atractivo del bono
6. Explora los gráficos de flujos y sensibilidad
7. Genera y descarga el reporte PDF
8. Opcionalmente, envía el reporte por correo

## 📦 Dependencias Principales

- **streamlit** (>=1.28.0): Framework para la interfaz web
- **pandas** (>=2.0.3): Manipulación de datos
- **numpy** (>=1.26.4): Cálculos numéricos
- **plotly** (>=5.15.0): Gráficos interactivos
- **google-generativeai**: Integración con Gemini AI
- **reportlab**: Generación de PDFs
- **fpdf2** (>=2.7.0): Generación alternativa de PDFs
- **python-dotenv** (>=1.0.0): Gestión de variables de entorno

Ver `requirements.txt` para la lista completa de dependencias.

## 🏗️ Estructura del Proyecto

```
calculadora-inversiones/
├── app.py                      # Aplicación principal Streamlit
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Este archivo
├── .devcontainer/              # Configuración de Dev Container
│   └── devcontainer.json
├── .streamlit/                 # Configuración de Streamlit
│   └── secrets.toml            # Variables de entorno (crear)
├── ui/                         # Interfaz de usuario
│   ├── components/             # Componentes reutilizables
│   │   ├── sidebar.py         # Barra lateral de navegación
│   │   └── footer.py          # Pie de página
│   ├── forms/                  # Formularios de entrada
│   │   ├── inversiones.py     # Formulario de inversiones
│   │   └── bonos.py           # Formulario de bonos
│   └── results/                # Visualización de resultados
│       ├── res_inversiones.py # Resultados de inversiones
│       ├── res_mod_b.py       # Resultados módulo B
│       └── res_mod_c.py       # Resultados módulo C (bonos)
└── utils/                      # Utilidades
    ├── utils.py               # Funciones auxiliares
    ├── gemini.py              # Integración con Gemini AI
    └── email.py               # Funcionalidad de correo
```

## 🔧 Desarrollo

### Usar Dev Container

El proyecto incluye configuración para Dev Containers. Si usas VS Code con la extensión Dev Containers:

1. Abre el proyecto en VS Code
2. Presiona `F1` y selecciona "Dev Containers: Reopen in Container"
3. El contenedor se configurará automáticamente y la aplicación se iniciará

### Ejecutar en Modo Desarrollo

```bash
streamlit run app.py --server.headless true
```

## 📝 Notas Importantes

- Los cálculos financieros son aproximaciones y no constituyen asesoramiento financiero profesional
- Las tasas de interés y rendimientos son estimaciones basadas en los parámetros ingresados
- Los análisis generados por IA son sugerencias y deben ser revisados por un profesional financiero
- Asegúrate de mantener seguras tus API keys y no compartirlas públicamente

## 🤝 Contribuciones

Este proyecto fue desarrollado para el curso de Finanzas Corporativas de la UNT - Grupo 6.

## 📄 Licencia

Este proyecto es de uso educativo.

## 👥 Autores

- **[Marck]** - [@usuario-github1](https://github.com/marck-h-cmd)
- **[Felix]** - [@usuario-github2](https://github.com/Felixby2004)
- **[Dan]** - [@usuario-github3](https://github.com/Dan101111111)
- **[Villa]** - [@usuario-github4](https://github.com/DrkonVilla)
- **[Geri]** - [@usuario-github4](https://github.com/YeriBoooo)

---

## 🆘 Soporte

Si encuentras algún problema o tienes preguntas:

1. Revisa que todas las dependencias estén instaladas correctamente
2. Verifica que el archivo `secrets.toml` esté configurado correctamente
3. Asegúrate de tener conexión a internet para usar la API de Gemini
4. Revisa los logs de Streamlit para identificar errores

---

**¡Disfruta calculando tus inversiones! 💰📈**

