# 📋 Quick Reference Card - Schema Form Builder

## 🚀 Getting Started (5 Steps)

```
1. Open Terminal/Command Prompt
2. Type: streamlit run dynamic_schema_form.py
3. Press Enter
4. Browser opens automatically
5. Start using your form!
```

---

## 🎯 Main Features At-a-Glance

| Action | Where | What It Does |
|--------|-------|--------------|
| **Select Schema** | Sidebar → Dropdown | Choose which form to use |
| **Upload Schema** | Sidebar → Upload button | Add a new form template |
| **Edit Schema** | Sidebar → Edit checkbox | Modify form fields live |
| **Fill Form** | Main area | Enter your data |
| **Validate** | Bottom → ✅ button | Check for errors |
| **Save Draft** | Bottom → 💾 button | Save without submitting |
| **Submit** | Bottom → 📤 button | Finalize and export |
| **Reset** | Sidebar → 🔄 button | Start over |

---

## 📝 Field Types Explained

| What You See | Schema Type | Purpose |
|--------------|-------------|---------|
| Text box | `string` | Names, descriptions, notes |
| Dropdown (pick one) | `enum` | Department, status, category |
| Multi-select (pick many) | `array` + `enum` | Countries, skills, permissions |
| Number box | `number` | Age, quantity, amount |
| Checkbox | `boolean` | Yes/No, agree/disagree |
| **Nested section** | `object` | Address, contact details |
| **Repeating items** ➕🗑️ | `array of objects` | Multiple employees, projects |

---

## ✏️ Editing Your Schema (Live Changes)

### Add a New Field

1. Click **🔧 Edit Schema** (sidebar)
2. Find `"properties": {`
3. Add your field:
```json
"fieldName": {
  "type": "string",
  "title": "What Users See",
  "description": "Help text here"
}
```
4. Click **💾 Save Schema**
5. New field appears!

### Make a Field Required

Find your field and add it to `required`:
```json
"required": ["existingField", "yourNewField"]
```

### Add a Dropdown

```json
"status": {
  "type": "string",
  "title": "Status",
  "enum": ["Active", "Inactive", "Pending"]
}
```

### Set Character Limits

```json
"comments": {
  "type": "string",
  "minLength": 10,
  "maxLength": 500
}
```

---

## ⚠️ Common Validation Rules

| Rule | What It Means |
|------|---------------|
| Field marked with `*` | Required - must fill out |
| `(Length: 2-20)` | Must be 2-20 characters |
| `❌ Minimum length is 5` | Type more characters |
| `❌ Invalid format` | Doesn't match pattern (e.g., email) |
| `❌ Required field` | Fill this before submitting |
| `❌ Items must be unique` | No duplicates allowed |

---

## 💾 File Types Generated

| File | When | Contains |
|------|------|----------|
| `draft_*.json` | Click "Save Draft" | Incomplete work |
| `submission_*.json` | Click "Submit" | Final validated data |
| `*.json` (in folder) | Your schemas | Form templates |

---

## 🔧 Quick Fixes

### "Schema file not found"
→ Put `.json` file in same folder as app

### Field won't update
→ Click **🔄 Reset Form** in sidebar

### Can't submit
→ Click **✅ Validate** to see errors  
→ Fix all fields with `❌`  
→ Try submit again

### Invalid JSON error when editing
→ Check for missing commas  
→ Check for extra/missing brackets `{ }`  
→ Use [JSONLint.com](https://jsonlint.com) to validate

---

## 🎨 Conditional Fields

**Show field ONLY when condition is met:**

```json
{
  "properties": {
    "country": {
      "enum": ["SG", "IN", "CN", "Others"]
    },
    "countryOther": {
      "type": "string",
      "title": "Specify Country"
    }
  },
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

**Result:** "Specify Country" field only appears when "Others" is selected!

---

## 📋 Copy-Paste Examples

### Simple Text Field
```json
"fullName": {
  "type": "string",
  "title": "Full Name",
  "minLength": 2,
  "maxLength": 100
}
```

### Email Field
```json
"email": {
  "type": "string",
  "title": "Email Address",
  "pattern": "^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
}
```

### Department Dropdown
```json
"department": {
  "type": "string",
  "title": "Department",
  "enum": ["Sales", "Engineering", "HR", "Finance", "Operations"]
}
```

### Multi-Select Countries
```json
"countries": {
  "type": "array",
  "title": "Select Countries",
  "items": {
    "type": "string",
    "enum": ["SG", "IN", "CN", "HK", "TW", "Others"]
  }
}
```

### Number with Range
```json
"age": {
  "type": "number",
  "title": "Age",
  "minimum": 18,
  "maximum": 120
}
```

### Yes/No Checkbox
```json
"agree": {
  "type": "boolean",
  "title": "I agree to the terms"
}
```

### Repeating Employees
```json
"employees": {
  "type": "array",
  "title": "Employees",
  "minItems": 1,
  "items": {
    "type": "object",
    "properties": {
      "employeeId": { "type": "string" },
      "name": { "type": "string" }
    },
    "required": ["employeeId"]
  }
}
```

---

## 🎯 Pro Tips

✅ **Test changes on a copy** - Duplicate your schema before editing  
✅ **Add one field at a time** - Easier to debug  
✅ **Use clear titles** - "Full Name" not "fName"  
✅ **Save drafts often** - Don't lose work  
✅ **Validate before editing schema** - See current state  
✅ **Keep backups** - Date your schema files  

---

## 🆘 Emergency Recovery

**Made a mistake editing schema?**
1. Click **❌ Cancel** (don't save)
2. Or restore from backup file
3. Or re-upload original schema

**Lost your work?**
- Check `draft_*.json` files
- They save automatically

**Form looks broken?**
1. **🔄 Reset Form** (sidebar)
2. Refresh browser (F5)
3. Restart app

---

## 📞 Support Checklist

Before asking for help, have ready:
- [ ] Schema file name
- [ ] What you were trying to do
- [ ] Error message (screenshot)
- [ ] Which field is causing issues

---

## 🎓 Remember

**This is YOUR form engine:**
- Change anything you want
- Add/remove fields anytime
- No coding knowledge needed
- Just edit the JSON schema

**Schema = Template**  
**Form Data = Your submission**  
**They're separate - edit schema freely!**

---

**Quick Start Command:**
```bash
streamlit run dynamic_schema_form.py
```

**That's it! Start building forms! 🚀**
