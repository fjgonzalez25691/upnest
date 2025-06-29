# AWS Lambda Compatibility Guide

## Problemas Comunes y Soluciones

### 1. Numpy/Pandas Compatibility Issues

**Problema**: `numpy` compiled with newer versions causing `GLIBC` errors in Lambda
**Solución**: Usar versiones específicas compatibles con Amazon Linux 2

```bash
# Versiones compatibles (ya configuradas en requirements.txt)
numpy==1.26.4
pandas==2.2.2
scipy==1.13.1
```

### 2. Build en Container para Compatibilidad

**Configuración SAM**: En `samconfig.toml` activar `use_container = true`

```toml
[default.build.parameters]
use_container = true
skip_pull_image = false
```

### 3. Comandos para Build Local Compatible

```powershell
# Build con container (recomendado para producción)
sam build --use-container

# Build rápido para desarrollo local
sam build --cached --parallel

# Start local API
sam local start-api --port 3001 --env-vars .env
```

### 4. Debugging Lambda Issues

#### Verificar compatibilidad de paquetes:
```powershell
# Test local con container
sam local invoke CreateBabyFunction --event tests/test-event-create-baby.json

# Ver logs en tiempo real
sam logs -n CreateBabyFunction --stack-name upnest-lambdas-dev --tail
```

#### Common Lambda Errors:

1. **ImportError**: Módulo no encontrado
   - **Causa**: Dependencia no incluida en requirements.txt
   - **Solución**: Agregar al requirements.txt del módulo específico

2. **GLIBC version mismatch**: 
   - **Causa**: Paquete compilado en arquitectura incompatible
   - **Solución**: Build con `--use-container`

3. **Module initialization timeout**:
   - **Causa**: Imports pesados o inicialización lenta
   - **Solución**: Lazy loading, optimizar imports

### 5. Estructura de Requirements por Módulo

Cada módulo Lambda tiene su propio `requirements.txt`:

- `babies/requirements.txt`: Dependencias básicas (boto3, PyJWT, etc.)
- `growth-data/requirements.txt`: Dependencias básicas
- `percentiles/requirements.txt`: Incluye numpy, pandas, scipy
- `advanced/requirements.txt`: Incluye numpy, pandas, scipy

### 6. Lambda Layer Optimization (Futuro)

Para optimizar cold starts y reducir tamaño de paquetes:

```yaml
# template.yaml - Layer para dependencias pesadas
PercentileCalculationLayer:
  Type: AWS::Serverless::LayerVersion
  Properties:
    LayerName: upnest-percentile-deps
    ContentUri: layers/percentile-deps/
    CompatibleRuntimes:
      - python3.11
```

### 7. Testing Pipeline

```powershell
# 1. Test unitarios
pytest aws/tests/

# 2. Test integración local
sam local start-api &
# Ejecutar tests contra localhost:3001

# 3. Test en AWS
sam deploy --guided
# Ejecutar tests contra endpoint real
```

### 8. Memory y Timeout Configuration

En `template.yaml` Globals:
```yaml
Globals:
  Function:
    Timeout: 30        # 30 segundos para percentiles
    MemorySize: 256    # 256MB suficiente para la mayoría
    # Para percentiles podría necesitar 512MB
```

### 9. Environment Variables Best Practices

- No hardcodear valores en código
- Usar CloudFormation ImportValue para ARNs de recursos
- Variables específicas por entorno en template.yaml

### 10. Cold Start Optimization

```python
# Importar dependencias pesadas fuera del handler
import pandas as pd
import numpy as np

# Cached data loading
_percentile_data = None

def lambda_handler(event, context):
    global _percentile_data
    if _percentile_data is None:
        _percentile_data = load_percentile_data()
    # ... rest of handler
```

## Next Steps

1. ✅ Configurar requirements.txt con versiones compatibles
2. ✅ Actualizar samconfig.toml con use_container
3. 🔄 Test build local con container
4. 📋 Implement growth-chart endpoint
5. 📋 Deploy y test en AWS
6. 📋 Optimizar con Lambda Layers si es necesario
