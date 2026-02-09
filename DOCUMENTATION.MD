# Form Builder - Technical Documentation

## Overview

A professional, schema-driven form engine for enterprise use. Clean interface, robust logging, and complete JSON Schema support.

---

## Installation

```bash
pip install streamlit
```

## Usage

```bash
streamlit run business_form_engine.py
```

Application opens automatically in browser at `http://localhost:8501`

---

## Features

### Core Functionality
- **Dynamic Field Generation** - Automatically creates form fields from any JSON Schema
- **Real-time Validation** - Validates input against schema constraints
- **Draft Management** - Save incomplete forms
- **Data Export** - Download submissions as JSON
- **Logging** - Complete audit trail in `form_engine.log`

### Supported Schema Features
- Basic types: string, number, boolean, array, object
- Enumerations (dropdowns and multi-select)
- Nested objects and arrays
- `$ref` resolution
- Conditional rendering (`if/then/else`)
- Validation: minLength, maxLength, pattern, minItems, maxItems, minimum, maximum
- Required fields
- Unique items

---

## File Structure

```
project/
├── business_form_engine.py    # Main application
├── schema.json                 # Your schema file(s)
├── form_engine.log            # Application logs
├── draft_*.json               # Saved drafts
└── submission_*.json          # Submitted forms
```

---

## Schema Format

### Basic Structure

```json
{
  "type": "object",
  "properties": {
    "fieldName": {
      "type": "string",
      "title": "Display Name",
      "description": "Help text",
      "minLength": 2,
      "maxLength": 50
    }
  },
  "required": ["fieldName"]
}
```

### Field Types

**Text Input**
```json
"fullName": {
  "type": "string",
  "title": "Full Name",
  "minLength": 2,
  "maxLength": 100
}
```

**Dropdown**
```json
"department": {
  "type": "string",
  "title": "Department",
  "enum": ["Sales", "Engineering", "HR"]
}
```

**Multi-Select**
```json
"skills": {
  "type": "array",
  "title": "Skills",
  "items": {
    "type": "string",
    "enum": ["Python", "Java", "JavaScript"]
  }
}
```

**Number**
```json
"age": {
  "type": "number",
  "title": "Age",
  "minimum": 18,
  "maximum": 120
}
```

**Checkbox**
```json
"agree": {
  "type": "boolean",
  "title": "I agree to terms"
}
```

**Nested Object**
```json
"address": {
  "type": "object",
  "title": "Address",
  "properties": {
    "street": {"type": "string"},
    "city": {"type": "string"},
    "zip": {"type": "string"}
  }
}
```

**Array of Objects**
```json
"contacts": {
  "type": "array",
  "title": "Emergency Contacts",
  "minItems": 1,
  "items": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "phone": {"type": "string"}
    },
    "required": ["name", "phone"]
  }
}
```

### Conditional Fields

```json
{
  "properties": {
    "hasOther": {
      "type": "boolean",
      "title": "Other category applies"
    },
    "otherDetails": {
      "type": "string",
      "title": "Specify other"
    }
  },
  "if": {
    "properties": {
      "hasOther": {"const": true}
    }
  },
  "then": {
    "required": ["otherDetails"]
  }
}
```

### Using References

```json
{
  "type": "object",
  "properties": {
    "employee": {"$ref": "#/definitions/person"}
  },
  "definitions": {
    "person": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "email": {"type": "string"}
      }
    }
  }
}
```

---

## Validation Rules

| Schema Property | Validation |
|----------------|------------|
| `required` | Field must be filled |
| `minLength` | Minimum character count |
| `maxLength` | Maximum character count |
| `pattern` | Regex pattern match |
| `minimum` | Minimum number value |
| `maximum` | Maximum number value |
| `minItems` | Minimum array items |
| `maxItems` | Maximum array items |
| `enum` | Must be one of listed values |

---

## Logging

All actions are logged to `form_engine.log`:

```
2026-02-09 10:30:45 - FormEngine - INFO - Application started
2026-02-09 10:30:46 - FormEngine - INFO - Loaded schema: employee_form.json
2026-02-09 10:31:02 - FormEngine - INFO - Validation successful
2026-02-09 10:31:15 - FormEngine - INFO - Form submitted: submission_20260209_103115.json
```

### Log Levels
- **INFO** - Normal operations (schema load, validation, submission)
- **WARNING** - Validation failures, missing data
- **ERROR** - Schema errors, file I/O issues
- **DEBUG** - Field rendering, ref resolution (when enabled)

---

## Workflow

### 1. Select Schema
- Application automatically detects `.json` files
- Choose from dropdown
- Form renders immediately

### 2. Fill Form
- Required fields marked with *
- Help text displayed below fields
- Real-time format validation

### 3. Validate
- Click "Validate" to check all fields
- Errors displayed inline
- Must pass before submission

### 4. Save Draft
- Click "Save Draft" to preserve work
- Timestamped file created
- Can resume later

### 5. Submit
- Click "Submit" after validation passes
- Creates timestamped submission file
- Download button appears

---

## Data Format

### Input: JSON Schema
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"}
  }
}
```

### Output: Form Data
```json
{
  "name": "John Doe"
}
```

Files are saved as:
- `draft_YYYYMMDD_HHMMSS.json`
- `submission_YYYYMMDD_HHMMSS.json`

---

## Integration

### Database Integration
The output JSON can be directly inserted into document stores (MongoDB, PostgreSQL JSON columns):

```python
import json
with open('submission_20260209_103115.json') as f:
    data = json.load(f)
    db.collection.insert_one(data)
```

### API Integration
Use as request body for REST APIs:

```python
import requests
import json

with open('submission_20260209_103115.json') as f:
    data = json.load(f)
    response = requests.post('https://api.example.com/submit', json=data)
```

### CSV Export
Convert to tabular format:

```python
import pandas as pd
import json

with open('submission_20260209_103115.json') as f:
    data = json.load(f)
    df = pd.json_normalize(data)
    df.to_csv('output.csv', index=False)
```

---

## Troubleshooting

### Schema Not Loading
**Error**: "Error loading schema"
**Solution**: 
- Validate JSON syntax at jsonlint.com
- Check file exists in same directory
- Verify file permissions

### Validation Fails
**Error**: "Validation failed"
**Solution**:
- Check all required fields (marked with *)
- Verify field formats (email, phone, etc.)
- Review character limits
- Check log file for specific errors

### Field Not Appearing
**Cause**: Conditional logic
**Solution**:
- Check `if/then/else` conditions in schema
- Verify parent field values
- Review schema definition

### Form State Issues
**Solution**:
- Click "Reset Form"
- Refresh browser
- Check session state in logs

---

## Performance

- Handles schemas with 100+ fields
- Sub-second validation for typical forms
- Minimal memory footprint
- Logs rotated automatically

---

## Security Considerations

- All data stored locally
- No external API calls
- File permissions respect OS settings
- Input sanitization via schema validation
- Pattern matching prevents injection

---

## Customization

### Modify Theme
Edit CSS in `business_form_engine.py`:
```python
# Change primary color (currently black)
background: #1a1a1a !important;

# Change accent color (currently red)
border-left-color: #dc2626 !important;
```

### Add Custom Validation
Extend `ValidationEngine._validate_field()`:
```python
# Add custom business logic
if field_name == 'email' and not value.endswith('@company.com'):
    errors.append(f"{field_name}: Must be company email")
```

### Modify Logging
Change log level in configuration:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG for verbose
    ...
)
```

---

## Best Practices

### Schema Design
- Use clear, descriptive titles
- Add helpful descriptions
- Set reasonable min/max constraints
- Group related fields in objects
- Use enums for fixed choices
- Mark only essential fields as required

### Form Usage
- Validate before saving drafts
- Keep schema files version controlled
- Archive old submissions
- Review logs regularly
- Test schema changes incrementally

### Production Deployment
- Set up log rotation
- Configure backup for submissions
- Implement access controls
- Monitor disk space
- Document schema changes

---

## Support

### Log Analysis
Check `form_engine.log` for:
- Schema loading issues
- Validation failures
- Field rendering problems
- Submission errors

### Common Issues

**High log file size**
- Implement log rotation
- Reduce log level to INFO

**Slow performance**
- Reduce schema complexity
- Minimize nested objects
- Limit array items

**Memory usage**
- Large schemas load into memory
- Consider chunking for huge forms

---

## Version History

### Current Version
- Clean black/white/red theme
- Professional typography (IBM Plex Sans)
- Comprehensive logging
- Minimal UI elements
- Production-ready

---

## License

Enterprise use permitted. Customize as needed.
