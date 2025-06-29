# Development Guide

## Platform-Specific Notes

### Windows PowerShell

**Command Chaining**: PowerShell uses semicolon (`;`) as command separator instead of `&&`:

```powershell
# ✅ Correct for PowerShell
sam build; sam local start-api --port 3001
npm install; npm run build
cd aws/lambdas; sam build; sam local start-api

# ❌ Incorrect (Bash/Unix syntax)
sam build && sam local start-api --port 3001
npm install && npm run build
```

**Background Processes**: For long-running processes in PowerShell:
```powershell
# Start API in background
Start-Job -ScriptBlock { sam local start-api --port 3001 }

# Check running jobs
Get-Job

# Stop background job
Stop-Job -Name "Job1"
```

### Unix/Linux/macOS

**Command Chaining**: Use `&&` for conditional execution:
```bash
# Commands run only if previous succeeds
sam build && sam local start-api --port 3001
npm install && npm run build

# Commands run regardless of previous result
sam build; sam local start-api --port 3001
```

## Development Workflow

### 1. Local Development Setup

```powershell
# Windows PowerShell
cd d:\proyectos\AWSLambdaHackathon\upnest
npm install; cd aws/lambdas; sam build
```

```bash
# Unix/Linux/macOS
cd /path/to/upnest
npm install && cd aws/lambdas && sam build
```

### 2. Start Local API

```powershell
# Windows PowerShell
sam local start-api --port 3001
```

```bash
# Unix/Linux/macOS
sam local start-api --port 3001
```

### 3. Testing

```powershell
# Windows PowerShell - Test specific function
sam local invoke ListBabiesFunction -e tests/test-event.json

# Chain multiple commands
sam build; sam local invoke CreateBabyFunction -e tests/test-event-create-baby.json
```

## Common Development Commands

### Build and Test
```powershell
# Windows PowerShell
sam build; sam local start-api --port 3001
```

```bash
# Unix/Linux/macOS
sam build && sam local start-api --port 3001
```

### Run Tests
```powershell
# Windows PowerShell
cd aws; python -m pytest tests/
```

```bash
# Unix/Linux/macOS
cd aws && python -m pytest tests/
```

### Check Logs
```powershell
# Windows PowerShell
sam logs -n YourFunctionName --stack-name your-stack
```

## Environment Variables

### Local Development
Create `.env` file in project root:
```env
AWS_REGION=us-east-1
DYNAMODB_ENDPOINT=http://localhost:8000
JWT_SECRET=your-test-secret
```

### SAM Local
Create `env.json` in `aws/lambdas/`:
```json
{
  "ListBabiesFunction": {
    "DYNAMODB_ENDPOINT": "http://localhost:8000",
    "JWT_SECRET": "your-test-secret"
  }
}
```

## Troubleshooting

### PowerShell Command Issues
- **Problem**: Commands not chaining properly
- **Solution**: Use `;` instead of `&&`

### SAM CLI Issues
- **Problem**: Functions not found
- **Solution**: Run `sam build` first

### DynamoDB Connection Issues
- **Problem**: Cannot connect to local DynamoDB
- **Solution**: Start DynamoDB local first:
  ```powershell
  docker run -p 8000:8000 amazon/dynamodb-local
  ```

## Best Practices

1. **Always build before testing**: `sam build` before `sam local start-api`
2. **Use environment-specific commands**: Check your shell before running commands
3. **Test locally first**: Validate functions locally before deployment
4. **Use proper separators**: `;` for PowerShell, `&&` for Unix shells
5. **Check logs**: Use `sam logs` for debugging deployed functions

---

*This guide ensures consistent development experience across different platforms and shells.*
