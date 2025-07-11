# Sistema DryWall - ERP Banking con Monitoreo de Humedad

Sistema distribuido de monitoreo de humedad para centros de datos bancarios usando SFTP y React Dashboard.

## 📁 Estructura del Proyecto

```
PARTE2_FINAL_ANALITICA/
├── 🖥️ server/                     # Servidor SFTP + Procesamiento
│   ├── sftp_server_integrated.py  # Servidor SFTP principal
│   ├── generate_test_csv.py       # Generador de datos de prueba
│   ├── logs/                      # Logs del servidor
│   ├── processed_data/            # Datos procesados (JSON)
│   └── sftp_uploads/              # Archivos recibidos vía SFTP
│
├── 📱 client/                     # Cliente IoT (Sensores)
│   ├── generate_humidity.py       # Generador de datos de sensores
│   ├── sftp_upload.py            # Cliente SFTP
│   ├── simple_upload.py          # Script todo-en-uno
│   ├── keys/                     # Claves SSH
│   └── data/                     # Datos generados localmente
│
├── 🌐 frontend/                   # Dashboard React (futuro)
│   └── (próximamente)
│
├── 📦 backup_old_files/          # Archivos de desarrollo
│   └── (archivos antiguos)
│
├── 🗂️ test_data/                 # Datos de prueba
│   ├── humidity_normal.csv
│   ├── humidity_large.csv
│   └── humidity_alerts.csv
│
└── 📋 docs/
    ├── README.md                 # Este archivo
    └── SISTEMA_COMPLETADO.md     # Documentación completa
```

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor SFTP

```bash
cd server
python sftp_server_integrated.py
```

### 2. Generar y Subir Datos (Cliente)

```bash
cd client
python simple_upload.py
```

## 🔧 Comandos Individuales

### Servidor

```bash
# Iniciar servidor SFTP con procesamiento automático
cd server
python sftp_server_integrated.py

# Generar datos de prueba
python generate_test_csv.py
```

### Cliente

```bash
cd client

# Generar datos de sensores
python generate_humidity.py -n 50 --format csv

# Subir archivo específico
python sftp_upload.py --host localhost --port 2222 --upload data/archivo.csv

# Todo en uno: generar + subir
python simple_upload.py
```

## 📊 Características

✅ **Servidor SFTP integrado** - Recibe archivos y procesa automáticamente  
✅ **Procesamiento CSV** - Convierte a JSON con estadísticas y alertas  
✅ **Logging completo** - Registra todas las operaciones  
✅ **Autenticación SSH** - Seguridad con claves públicas/privadas  
✅ **Alertas automáticas** - Detecta humedad alta/baja  
✅ **Generación realista** - Simula sensores IoT reales

## 🔐 Seguridad

- Autenticación por claves SSH (no contraseñas)
- Usuario específico: `drywall_user`
- Puerto no estándar: `2222`
- Claves en directorio protegido

## 📈 Flujo de Datos

1. **Cliente** genera datos CSV de sensores de humedad
2. **Cliente** sube via SFTP al servidor
3. **Servidor** procesa automáticamente el CSV
4. **Servidor** genera estadísticas y alertas en JSON
5. **Dashboard** (futuro) lee los datos procesados

## 🎯 Próximos Pasos

- [ ] Dashboard React para visualización
- [ ] API REST para consultas
- [ ] Base de datos para historiales
- [ ] Notificaciones en tiempo real
- [ ] Múltiples tipos de sensores

## 📞 Soporte

Para probar el sistema completo, ejecuta los comandos en el orden mostrado arriba.
Todos los logs y archivos procesados se guardan automáticamente.
