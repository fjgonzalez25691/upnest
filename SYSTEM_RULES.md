# SYSTEM RULES FOR AI ASSISTANT

## CRITICAL PLATFORM RULES

### CURRENT ENVIRONMENT: Windows PowerShell
- **ALWAYS use semicolon (`;`) as command separator**
- **NEVER use `&&` in PowerShell commands**
- **User has specified this multiple times - DO NOT FORGET**

### Command Examples:
```powershell
# ✅ CORRECT - Use semicolon
sam build; sam local start-api --port 3001
cd aws/lambdas; sam build; sam local invoke FunctionName

# ❌ WRONG - Do not use &&
sam build && sam local start-api --port 3001
```

### When using run_in_terminal tool:
1. Check: Is this Windows PowerShell? (YES - according to environment_info)
2. Use: Semicolon (`;`) as command separator
3. Never: Use `&&` syntax

---
**REMEMBER**: The user is working in Windows PowerShell and has reminded about this rule multiple times.
**ACTION**: Always check this file before generating terminal commands.
**IMPORTANCE**: Critical for proper command execution in user's environment.
