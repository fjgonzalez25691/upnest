# 🚀 **CASE STUDY: Critical Refactoring During Hackathon**
## **From 15 Lambda Functions to 3 in Record Time**

---

## 🚨 **THE PROBLEM: "Houston, we have a problem"**

### **Initial situation:**
- ⏰ **11 hours remaining** to deliver the hackathon
- 🔥 **Deployment error:** "Unzipped size must be smaller than 262144000 bytes"
- 📦 **Current size:** 1.45 GB (6x the Lambda limit!)
- 🐍 **15 Lambda functions** with massively duplicated code

### **The panic moment:**
```bash
# The deployment that didn't work
sam deploy --stack-name upnest-lambdas-hackathon
# ERROR: Function package size exceeded 250MB limit
```

---

## 🔍 **ANALYSIS: Identifying the "code smell"**

### **Detected code duplication:**

#### **1. Repeated imports (100% duplication):**
```python
# In EACH of the 15 files:
import json, logging, sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from dynamodb_client import get_dynamodb_client
from jwt_utils import get_jwt_validator, extract_token_from_event
from response_utils import success_response, unauthorized_response, ...
```

#### **2. JWT Authentication (100% duplication):**
```python
# In EACH function:
token = extract_token_from_event(event)
if not token:
    return unauthorized_response("Authorization token is required")
try:
    jwt_validator = get_jwt_validator()
    user_id = jwt_validator.extract_user_id(token)
except ValueError as e:
    return unauthorized_response(str(e))
```

#### **3. DynamoDB Setup (95% duplication):**
```python
# In EACH function:
dynamodb = get_dynamodb_client()
table_name = os.environ['BABIES_TABLE']
table = dynamodb.Table(table_name)
```

### **Problematic structure:**
```
📁 babies/
├── babies_create.py    # 117 lines + dependencies
├── babies_list.py      # 125 lines + dependencies  
├── babies_get.py       # 86 lines + dependencies
├── babies_update.py    # 152 lines + dependencies
├── babies_delete.py    # 112 lines + dependencies
├── create.py          # Duplicate?
├── delete.py          # Duplicate?
└── ... (more duplicates)

📁 growth-data/
├── growth_data_create.py
├── growth_data_list.py
└── ... (more duplication)

📁 advanced/
└── ... (even more functions)
```

---

## 💡 **THE SOLUTION: Unified Service Pattern**

### **New architecture principle:**
> **"One Service = One Complete Domain"**

Instead of:
- ❌ `create_baby.py`, `get_baby.py`, `update_baby.py`, `delete_baby.py`, `list_babies.py`

We implemented:
- ✅ `baby_service.py` → **Handles ALL baby operations**

### **Unified service structure:**
```python
class BabyService:
    def __init__(self, event, context):
        """Common setup executed ONLY once"""
        self.user_id = self._authenticate(event)  # Common JWT
        self.dynamodb = get_dynamodb_client()     # Common DB
        self.table = self.dynamodb.Table(os.environ['BABIES_TABLE'])
    
    def _authenticate(self, event):
        """Centralized authentication - No more duplication"""
        # Common JWT logic for all operations
```

---

## 📊 **RESULTS: The impact of refactoring**

### **Dramatic size reduction:**

| Metric | BEFORE | AFTER | Reduction |
|---------|--------|--------|-----------|
| **Lambda Functions** | 15+ | 3 | 80% |
| **Total Size** | 1.45 GB | ~120 MB | 92% |
| **Lines of Code** | ~2,000+ | ~800 | 60% |
| **Deploy Time** | FAILS | 2-3 minutes | ✅ |
| **Code Duplication** | ~75% | ~5% | 93% |

### **Unified services deployed:**

#### **1. Baby Service** (`baby_service.py`)
- **Routes:** `POST/GET/PUT/DELETE /babies`, `GET /babies/{babyId}`
- **Size:** ~20 MB
- **Functionality:** Complete baby CRUD with authentication

#### **2. Growth Data Service** (`growth_data_service.py`)  
- **Routes:** `POST/GET/PUT/DELETE /growth-data`, `GET /babies/{babyId}/growth`
- **Size:** ~20 MB
- **Functionality:** Growth data management linked to babies

#### **3. Percentiles Service** (`percentiles_service.py`)
- **Routes:** `POST /percentiles/calculate` 
- **Size:** ~85 MB (includes WHO/CDC Excel tables)
- **Functionality:** Percentile calculation using WHO/CDC standards
- **Included data:** 6 Excel tables (weight, height, head circumference) for boys/girls

### **Simplified template.yaml:**
```yaml
# BEFORE: 15+ Lambda resources
CreateBabyFunction: ...
ListBabiesFunction: ...
GetBabyFunction: ...
UpdateBabyFunction: ...
DeleteBabyFunction: ...
CreateGrowthDataFunction: ...
GetGrowthDataFunction: ...
# ... more functions ...
CalculatePercentilesFunction: ...

# AFTER: Only 3 resources
BabyServiceFunction: ...      # Handles ALL baby CRUD
GrowthDataServiceFunction: ... # Handles ALL growth-data CRUD  
PercentilesServiceFunction: ...# Handles percentile calculations
```

### **Impact comparison:**

#### **Before refactoring:**
- ❌ Deploy failed constantly
- ❌ Impossible to test individual functions
- ❌ Unmaintainable code
- ❌ No time for frontend

#### **After refactoring:**
- ✅ Successful deploy in 2 minutes
- ✅ Simplified testing
- ✅ Clean and maintainable code
- ✅ Time recovered for frontend

---

## 🔧 **TECHNICAL IMPLEMENTATION**

### **Final structure:**
```
📁 babies/
├── baby_service.py      # Unified handler (complete CRUD)
├── requirements.txt     # Basic dependencies
└── __init__.py

📁 growth-data/
├── growth_data_service.py  # Unified handler (CRUD + queries)
├── requirements.txt        # Basic dependencies  
└── __init__.py

📁 percentiles/
├── percentiles_service.py  # Handler for WHO/CDC calculations
├── requirements.txt        # pandas, scipy, openpyxl
├── data/                   # WHO/CDC tables (1.17MB)
│   ├── weight/
│   │   ├── wfa-boys-zscore-expanded-tables.xlsx
│   │   └── wfa-girls-zscore-expanded-tables.xlsx
│   ├── height/
│   │   ├── lhfa-boys-zscore-expanded-tables.xlsx
│   │   └── lhfa-girls-zscore-expanded-tables.xlsx
│   └── head-circumference/
│       ├── hcfa-boys-zscore-expanded-tables.xlsx
│       └── hcfa-girls-zscore-expanded-tables.xlsx
└── __init__.py

📁 shared/
├── jwt_utils.py         # Shared utilities (fallback included)
├── dynamodb_client.py
├── response_utils.py
└── validation_utils.py
```

### **Final template.yaml:**
```yaml
Resources:
  # Baby Service - Unified CRUD
  BabyServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: babies/
      Handler: baby_service.lambda_handler
      Events:
        BabiesApi:
          Type: Api
          Properties:
            Path: /babies
            Method: ANY
        BabiesIdApi:
          Type: Api
          Properties:
            Path: /babies/{babyId}
            Method: ANY

  # Growth Data Service - Unified CRUD  
  GrowthDataServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: growth-data/
      Handler: growth_data_service.lambda_handler
      Events:
        GrowthDataApi:
          Type: Api
          Properties:
            Path: /growth-data
            Method: ANY
        GrowthDataIdApi:
          Type: Api
          Properties:
            Path: /growth-data/{dataId}
            Method: ANY
        BabyGrowthApi:
          Type: Api
          Properties:
            Path: /babies/{babyId}/growth
            Method: GET

  # Percentiles Service - WHO/CDC Calculations
  PercentilesServiceFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: percentiles/
      Handler: percentiles_service.lambda_handler
      Timeout: 60        # Longer for data processing
      MemorySize: 512    # More memory for pandas/scipy
      Events:
        PercentilesApi:
          Type: Api
          Properties:
            Path: /percentiles/calculate
            Method: POST
```

### **Deployed endpoints:**
**Base URL:** `https://8l68gypmvb.execute-api.eu-south-2.amazonaws.com/Prod/`

**Babies:** `POST/GET/PUT/DELETE /babies`, `GET /babies/{babyId}`
**Growth Data:** `POST/GET/PUT/DELETE /growth-data`, `GET /babies/{babyId}/growth`  
**Percentiles:** `POST /percentiles/calculate` (with WHO/CDC tables included)

---

## 🎯 **LESSONS LEARNED**

### **Applied principles:**
1. **DRY (Don't Repeat Yourself):** Elimination of massive code duplication
2. **Single Responsibility:** One service = One complete domain  
3. **Fallback Pattern:** Resilience in imports for development/production
4. **Embedded Data:** Include static data (WHO/CDC) in package for zero latency
5. **Unified Handlers:** One handler per domain with internal routing

### **Key technical decisions:**
- **Local package vs S3:** For WHO/CDC data, we chose local package (1.17MB) for speed
- **Fallback imports:** Enable local development without complex shared dependencies  
- **Unified routing:** One handler manages multiple HTTP operations
- **Memory/Timeout:** Adjusted per service (percentiles needs more resources)

### **Total refactoring time:** ⏱️ **< 1 hour**
- **Baby Service:** 15 minutes
- **Growth Data Service:** 10 minutes (pattern already established)
- **Percentiles Service:** 20 minutes (including Excel data handling)
- **Deploy and testing:** 10 minutes

---

**📝 Note:** This case demonstrates that in high-pressure development, code quality and simple architecture can be the difference between project success and failure.

**🏆 Result:** Project saved, hackathon successfully completed, and a great refactoring story to tell.
