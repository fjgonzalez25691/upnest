# Lambda Test Events

Esta carpeta contiene eventos de prueba para testing local con SAM CLI.

## Archivos de test disponibles:

### `test-event.json`
- **Descripción**: Evento básico GET para listar bebés
- **Método**: GET
- **Ruta**: `/babies`
- **Autenticación**: Incluye token de prueba
- **Uso**: `sam local invoke ListBabiesFunction -e tests/test-event.json`

### `test-event-no-auth.json`
- **Descripción**: Evento GET sin autenticación (para probar manejo de errores)
- **Método**: GET
- **Ruta**: `/babies`
- **Autenticación**: Sin token (debe retornar 401)
- **Uso**: `sam local invoke ListBabiesFunction -e tests/test-event-no-auth.json`

### `test-event-create-baby.json`
- **Descripción**: Evento POST para crear un bebé
- **Método**: POST
- **Ruta**: `/babies`
- **Body**: JSON con datos de bebé de prueba
- **Uso**: `sam local invoke CreateBabyFunction -e tests/test-event-create-baby.json`

## Uso con SAM CLI

```bash
# Desde la carpeta aws/lambdas/
sam local invoke FunctionName -e tests/test-event.json
sam local invoke FunctionName -e tests/test-event.json --env-vars env.json
```

## Estructura de eventos

Los eventos siguen la estructura estándar de AWS API Gateway:
- `httpMethod`: Método HTTP
- `path`: Ruta de la petición
- `headers`: Headers HTTP (incluyendo Authorization)
- `queryStringParameters`: Parámetros de query
- `body`: Cuerpo de la petición (JSON string)
