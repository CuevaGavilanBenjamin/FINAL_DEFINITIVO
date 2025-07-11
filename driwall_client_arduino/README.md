# 🏗️ Sistema DryWall - Cliente de Sensores IoT

Cliente para generar datos simulados de sensores de humedad y enviarlos via SFTP a un backend bancario.

## 📋 Componentes

- **Cliente DryWall** (`client/`) - Simulador de sensores IoT y cliente SFTP
- **Backend Bancario** (tu proyecto separado) - Receptor SFTP y API REST
- **Dashboard React** (tu frontend bancario) - Visualización de datos

## 🏗️ Arquitectura Separada

El sistema está diseñado con **separación física real** para demostrar integración entre sistemas independientes:

```
📁 PARTE2_FINAL_ANALITICA/    (Cliente + Frontend)
├── drywall_client/           # Simulador Arduino
└── project/                  # Dashboard React

📁 bank_server/              # Servidor ERP SEPARADO
├── bank_backend.py          # Backend independiente
├── authorized_keys/         # Autenticación SSH
└── upload/                  # Datos recibidos
```

## 🚀 Configuración Inicial

### 1. Dependencias Python

```bash
pip install paramiko pandas fastapi uvicorn
```

### 2. Dependencias Node.js (para el dashboard)

```bash
cd project
npm install
```

### 3. Configurar Servidor Bancario

El servidor bancario ya está configurado en `../bank_server/` con:

- ✅ Backend Python (`bank_backend.py`)
- ✅ Llaves SSH autorizadas
- ✅ Directorio de subida configurado
- ✅ Dependencias en `requirements.txt`

### 4. Verificar Configuración

Las llaves SSH ya están sincronizadas entre cliente y servidor.

## 🎯 Ejecución

### 1. Servidor Bancario (ERP) - Terminal 1

```bash
cd ..\bank_server
python bank_backend.py
```

Inicia en:

- SFTP Server: puerto 2222
- API REST: http://localhost:8000

### 2. Dashboard React - Terminal 2

```bash
cd project
npm start
```

- Dashboard: http://localhost:3000

### 3. Cliente DryWall (Sensores) - Terminal 3

```bash
cd drywall_client
python demo_auto.py        # Demo cada 30 segundos
python auto_sensor_system.py  # Intervalos configurables
```

## 📡 Flujo de Datos

1. **Generación**: `generate_humidity.py` crea datos CSV simulados
2. **Envío SFTP**: Datos enviados de forma segura con llaves SSH
3. **Procesamiento**: Backend procesa CSV y expone API REST
4. **Visualización**: Dashboard React muestra datos en tiempo real

## 🔐 Seguridad

- Autenticación SSH con llaves RSA 2048-bit
- Protocolo SFTP para transferencia segura
- CORS configurado para desarrollo local
- Logs detallados de todas las operaciones

## 📊 Endpoints API

- `GET /api/drywall/status` - Estado del sistema
- `GET /api/drywall/sensor-summary` - Resumen ejecutivo
- `GET /api/drywall/sensor-data` - Datos detallados
- `GET /health` - Health check

## 🛠️ Comandos Útiles

```bash
# Generar datos únicos
python generate_humidity.py

# Subir archivo específico via SFTP
python sftp_upload.py --upload data/archivo.csv

# Verificar estado del sistema
python check_status.py

# Ver logs
tail -f bank_backend.log
tail -f sftp_client.log
```

## 📁 Estructura de Archivos

```
PARTE2_FINAL_ANALITICA/
├── .gitignore                 # Exclusiones de Git
├── drywall_client/           # Cliente IoT simulado
│   ├── keys/                 # Llaves SSH (no subir a Git)
│   ├── data/                 # Datos CSV generados (no subir)
│   ├── *.log                 # Logs (no subir)
│   └── *.py                  # Scripts del cliente
└── project/                  # Sistema bancario
    ├── backend/              # API + SFTP Server
    │   ├── upload/           # Archivos recibidos (no subir)
    │   ├── authorized_keys/  # Llaves SSH (no subir)
    │   └── *.py             # Código del backend
    ├── src/                  # Frontend React
    └── package.json          # Dependencias Node.js
```

## ⚠️ Notas Importantes

- Las llaves SSH se generan localmente (no incluidas en Git)
- Los archivos CSV son temporales (no incluidos en Git)
- Los logs contienen información sensible (no incluidos en Git)
- `node_modules/` se regenera con `npm install`

## 🔧 Troubleshooting

### Error CORS

- Verificar que backend esté en puerto 8000
- Verificar que React esté en puerto 3000

### Error SFTP

- Verificar llaves SSH generadas correctamente
- Verificar backend corriendo en puerto 2222
- Usar `simple_auto.py` como alternativa

### Error de Dependencias

```bash
# Python
pip install -r requirements.txt

# Node.js
rm -rf node_modules package-lock.json
npm install
```
