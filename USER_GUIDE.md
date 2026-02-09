# 📋 Dynamic Schema Form Builder

## Executive Summary

A **plug-and-play form engine** that automatically generates professional, editable forms from any JSON Schema file. Built for business users with zero coding required.

### Key Benefits
✅ **Universal** - Works with ANY JSON Schema file  
✅ **Dynamic** - Add/edit/remove fields directly from the UI  
✅ **Business-Ready** - Professional interface designed for non-technical users  
✅ **Validation** - Real-time validation with clear error messages  
✅ **Flexible** - Save drafts, edit schemas, export data  

---

## 🚀 Quick Start (For Business Users)

### Installation
```bash
# Install Streamlit (one-time setup)
pip install streamlit

# Run the application
streamlit run dynamic_schema_form.py
```

The form will open in your web browser automatically!

---

## 📖 User Guide

### 1️⃣ Loading a Schema

**Option A: Use Existing Schema**
- The app automatically detects `.json` files in your folder
- Select from the dropdown in the sidebar
- Form fields appear automatically

**Option B: Upload New Schema**
- Click "Upload JSON Schema" in sidebar
- Select your `.json` file
- Form generates instantly

### 2️⃣ Filling Out the Form

The form automatically creates the right input type for each field:

| Schema Type | UI Element | Example |
|------------|------------|---------|
| `string` | Text box | Name, description |
| `enum` | Dropdown | Country selection |
| `array + enum` | Multi-select | Select multiple countries |
| `number` | Number input | Age, quantity |
| `boolean` | Checkbox | Yes/No questions |
| `object` | Nested section | Address details |
| `array of objects` | Add/remove items | Multiple employees |

**Required Fields** are marked with `*`

### 3️⃣ Editing the Schema (Live!)

1. Click **"🔧 Edit Schema"** in sidebar
2. Modify the JSON directly
3. Click **"💾 Save Schema"**
4. Form updates automatically!

**What You Can Edit:**
- Add new fields
- Change field types (text → dropdown, etc.)
- Modify validation rules (min/max length)
- Add descriptions and help text
- Create conditional logic

### 4️⃣ Validating & Submitting

**Validate Button** ✅
- Checks all required fields
- Validates data formats
- Shows specific errors

**Save Draft Button** 💾
- Saves work-in-progress
- No validation required
- Can resume later

**Submit Button** 📤
- Validates first
- Saves final submission
- Downloads JSON file

---

## 🎨 Features Overview

### Dynamic Field Rendering

The engine intelligently creates form fields based on your schema:

```json
{
  "type": "string",
  "title": "Full Name",
  "minLength": 2,
  "maxLength": 50
}
```
↓ Automatically becomes ↓  
**Text input** with character limits and validation

```json
{
  "type": "array",
  "items": {
    "type": "string",
    "enum": ["SG", "IN", "CN", "HK"]
  }
}
```
↓ Automatically becomes ↓  
**Multi-select dropdown** with predefined options

### Conditional Logic Support

The engine handles `if/then/else` logic automatically:

```json
{
  "if": {
    "properties": {
      "country": { "const": "Others" }
    }
  },
  "then": {
    "required": ["countryOther"]
  }
}
```

**Result:** The "Country (Other)" field only appears and becomes required when "Others" is selected.

### Array Management

For array fields, the form provides:
- ➕ Add new items dynamically
- 🗑️ Remove items (respecting minimum requirements)
- Automatic numbering and organization
- Nested object support

### Real-Time Validation

As you type, the form validates:
- **Required fields** - Highlighted when empty
- **Length constraints** - Shows character count
- **Pattern matching** - Validates formats (email, phone, etc.)
- **Unique items** - Prevents duplicates in arrays
- **Min/Max values** - For numbers

---

## 🏢 Business Use Cases

### 1. Employee Onboarding Forms
- Personal information
- Emergency contacts
- Benefits selection
- Department assignment

### 2. Risk Assessment Forms
- Country selection
- Business unit classification
- Owner assignment
- Compliance checks

### 3. Customer Intake Forms
- Contact details
- Product preferences
- Custom requirements
- Document uploads

### 4. Project Approval Forms
- Project details
- Budget allocation
- Stakeholder approval
- Timeline specification

---

## 🔧 Technical Capabilities

### Supported JSON Schema Features

| Feature | Status | Notes |
|---------|--------|-------|
| Basic types (string, number, boolean) | ✅ Fully Supported | All standard types |
| Enums | ✅ Fully Supported | Renders as dropdowns |
| Arrays | ✅ Fully Supported | Multi-select or dynamic lists |
| Objects | ✅ Fully Supported | Nested sections |
| `$ref` references | ✅ Fully Supported | Resolves automatically |
| `required` fields | ✅ Fully Supported | Visual indicators |
| `minLength` / `maxLength` | ✅ Fully Supported | Real-time validation |
| `minimum` / `maximum` | ✅ Fully Supported | Number constraints |
| `pattern` (regex) | ✅ Fully Supported | Format validation |
| `minItems` / `maxItems` | ✅ Fully Supported | Array constraints |
| `uniqueItems` | ✅ Fully Supported | Duplicate prevention |
| `if/then/else` | ✅ Fully Supported | Conditional rendering |
| `allOf` | ✅ Fully Supported | Schema composition |
| Custom titles | ✅ Fully Supported | Field labels |
| Descriptions | ✅ Fully Supported | Help text |

### Schema Structure

Your JSON Schema should follow this structure:

```json
{
  "type": "object",
  "properties": {
    "fieldName": {
      "type": "string",
      "title": "Display Name",
      "description": "Help text for users",
      "minLength": 2,
      "maxLength": 50
    }
  },
  "required": ["fieldName"],
  "definitions": {
    // Reusable schema definitions
  }
}
```

---

## 📝 Workflow Examples

### Example 1: Creating a New Form

1. **Create Schema File** (`employee_form.json`):
```json
{
  "type": "object",
  "properties": {
    "fullName": {
      "type": "string",
      "title": "Full Name",
      "minLength": 2
    },
    "department": {
      "type": "string",
      "title": "Department",
      "enum": ["Sales", "Engineering", "HR", "Finance"]
    },
    "startDate": {
      "type": "string",
      "title": "Start Date",
      "format": "date"
    }
  },
  "required": ["fullName", "department"]
}
```

2. **Run Application**:
```bash
streamlit run dynamic_schema_form.py
```

3. **Select Schema**: Choose `employee_form.json` from dropdown

4. **Form Appears**: All fields rendered automatically!

### Example 2: Adding a Field

1. Click **"🔧 Edit Schema"** in sidebar
2. Add new field to JSON:
```json
"email": {
  "type": "string",
  "title": "Email Address",
  "pattern": "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
}
```
3. Click **"💾 Save Schema"**
4. Email field appears in form!

### Example 3: Conditional Field

Make "Other Department" appear only when "Other" is selected:

```json
{
  "properties": {
    "department": {
      "type": "string",
      "enum": ["Sales", "Engineering", "Other"]
    },
    "departmentOther": {
      "type": "string",
      "title": "Specify Department"
    }
  },
  "if": {
    "properties": {
      "department": { "const": "Other" }
    }
  },
  "then": {
    "required": ["departmentOther"]
  }
}
```

---

## 🎯 Best Practices

### For Business Users

✅ **Start Simple** - Begin with basic fields, add complexity gradually  
✅ **Use Clear Titles** - Make field names business-friendly  
✅ **Add Descriptions** - Provide context for each field  
✅ **Test Validation** - Try the form yourself before rolling out  
✅ **Save Drafts Often** - Don't lose your work  

### For Form Designers

✅ **Group Related Fields** - Use objects to organize sections  
✅ **Set Reasonable Limits** - Don't make fields too restrictive  
✅ **Provide Examples** - Use descriptions to show format  
✅ **Use Enums for Fixed Choices** - Better UX than free text  
✅ **Mark Required Fields** - But don't overuse  

### Schema Design Tips

✅ **Reuse Definitions** - Use `$ref` for repeated structures  
✅ **Validate Incrementally** - Test schema changes one at a time  
✅ **Document Changes** - Keep notes on why fields were added  
✅ **Version Your Schemas** - Save dated backups  

---

## 🔒 Data & Privacy

- **Local Storage**: All data stays on your computer
- **No Cloud Uploads**: Nothing sent to external servers
- **JSON Output**: Standard format, easy to process
- **Draft Saves**: Stored locally for privacy

---

## 🆘 Troubleshooting

### Form Doesn't Load
**Problem**: "Schema file not found"  
**Solution**: Ensure `.json` file is in same folder as `dynamic_schema_form.py`

### Field Not Appearing
**Problem**: New field doesn't show up  
**Solution**: 
1. Check JSON syntax (use a validator)
2. Click "🔄 Reset Form" in sidebar
3. Refresh browser page

### Validation Errors Persist
**Problem**: Form won't submit  
**Solution**: 
1. Click "✅ Validate" to see specific errors
2. Check all fields marked with `*`
3. Verify character limits and formats

### Schema Edit Fails
**Problem**: "Invalid JSON" error  
**Solution**: 
1. Copy your JSON to [JSONLint](https://jsonlint.com/)
2. Fix syntax errors
3. Paste corrected JSON back
4. Save again

---

## 📊 Output Format

### Submission Files

When you click **Submit**, the app creates:

**File**: `submission_<schema_name>.json`  
**Format**: Clean JSON ready for processing

Example output:
```json
{
  "fullName": "John Doe",
  "department": "Engineering",
  "email": "john.doe@company.com",
  "startDate": "2026-03-01",
  "projects": [
    {
      "projectName": "Project Alpha",
      "role": "Lead Engineer"
    }
  ]
}
```

### Draft Files

**File**: `draft_<schema_name>.json`  
**Use**: Resume incomplete forms  
**Contains**: All filled fields, even if incomplete

---

## 🔄 Migration from Other Tools

### From Excel Forms
1. Map Excel columns to JSON schema properties
2. Use dropdowns → `enum` fields
3. Use data validation → `pattern` or `min/max`

### From Google Forms
1. Export existing questions
2. Convert to JSON schema format
3. Map question types:
   - Short answer → `string`
   - Multiple choice → `enum`
   - Checkboxes → `array` with `enum` items

### From React JSON Schema Form
✅ This tool is **100% compatible** with existing schemas!  
✅ No migration needed - just load your schema  
✅ Same validation rules apply  

---

## 💼 Enterprise Features

### Multi-Schema Support
- Store multiple schemas in one folder
- Switch between forms using dropdown
- Each schema independent

### Audit Trail
- Submission files timestamped
- Draft versions saved
- Schema changes versioned

### Integration Ready
- JSON output integrates with any system
- REST API compatible
- Database-ready format

---

## 📞 Support & Feedback

### Getting Help
1. Check Troubleshooting section above
2. Review Schema documentation
3. Test with simpler schema first

### Providing Feedback
- Note which schema file caused issues
- Share validation error messages
- Describe expected vs actual behavior

---

## 🎓 Learning Resources

### JSON Schema Basics
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)
- [Schema Validator](https://www.jsonschemavalidator.net/)

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io/)
- [Streamlit Gallery](https://streamlit.io/gallery)

---

## 📄 License

This form builder is provided for business use. Customize and extend as needed for your organization.

---

## ✨ Summary

This is a **true plug-and-play form engine**:
- Drop in any JSON Schema → Get a working form
- Edit schemas live → See changes instantly  
- Business-friendly UI → Non-technical users can use it
- Enterprise-ready → Validation, drafts, submissions

**No coding required. Just add your schema and go!** 🚀
