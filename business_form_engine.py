import streamlit as st
import json
from typing import Dict, Any, List, Optional, Tuple
import re
from pathlib import Path
from datetime import datetime
import logging

# ==================== LOGGING CONFIGURATION ====================
# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('form_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('FormEngine')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Form Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== PROFESSIONAL CSS STYLING ====================
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global overrides */
    * {
        font-family: 'IBM Plex Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main container */
    .main {
        background-color: #ffffff;
        padding: 2rem 4rem;
    }
    
    /* Remove Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header */
    .app-header {
        background-color: #1a1a1a;
        color: white;
        padding: 1.5rem 2rem;
        margin: -2rem -4rem 2rem -4rem;
        border-bottom: 3px solid #dc2626;
    }
    
    .app-title {
        font-size: 1.75rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .app-subtitle {
        font-size: 0.875rem;
        color: #d1d5db;
        margin-top: 0.25rem;
        font-weight: 300;
    }
    
    /* Section containers */
    .section-container {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .section-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0 0 1.25rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #e5e7eb;
    }
    
    /* Form controls */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
        padding: 0.625rem 0.75rem !important;
        font-size: 0.875rem !important;
        background: white !important;
        transition: border-color 0.15s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #1a1a1a !important;
        outline: none !important;
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Multi-select */
    .stMultiSelect > div > div {
        border: 1px solid #d1d5db !important;
        border-radius: 4px !important;
        background: white !important;
    }
    
    /* Labels */
    label {
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        color: #374151 !important;
        margin-bottom: 0.375rem !important;
    }
    
    .required-field::after {
        content: " *";
        color: #dc2626;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 4px !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.625rem 1.25rem !important;
        border: 1px solid #d1d5db !important;
        background: white !important;
        color: #1a1a1a !important;
        transition: all 0.15s ease !important;
    }
    
    .stButton > button:hover {
        background: #f9fafb !important;
        border-color: #1a1a1a !important;
    }
    
    .stButton > button[kind="primary"] {
        background: #1a1a1a !important;
        color: white !important;
        border-color: #1a1a1a !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #000000 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: #1a1a1a !important;
        border-color: #1a1a1a !important;
    }
    
    /* Array items */
    .array-item {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .array-item-header {
        font-size: 0.875rem;
        font-weight: 600;
        color: #1a1a1a;
        margin-bottom: 0.75rem;
    }
    
    /* Messages */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 4px !important;
        border-left: 4px solid !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.875rem !important;
    }
    
    .stSuccess {
        background-color: #f0fdf4 !important;
        border-left-color: #16a34a !important;
        color: #166534 !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border-left-color: #dc2626 !important;
        color: #991b1b !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border-left-color: #f59e0b !important;
        color: #92400e !important;
    }
    
    .stInfo {
        background-color: #eff6ff !important;
        border-left-color: #3b82f6 !important;
        color: #1e40af !important;
    }
    
    /* Help text */
    .stTextInput > label > div[data-testid="stMarkdownContainer"] > p,
    .stSelectbox > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 0.75rem !important;
        color: #6b7280 !important;
        font-weight: 400 !important;
    }
    
    /* Action bar */
    .action-bar {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 1.25rem;
        margin-top: 2rem;
    }
    
    /* Schema selector */
    .schema-selector {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #e5e7eb;
    }
    
    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Checkbox */
    .stCheckbox {
        font-size: 0.875rem !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: #dc2626 !important;
        color: white !important;
        border: none !important;
    }
    
    .stDownloadButton > button:hover {
        background: #b91c1c !important;
    }
</style>
""", unsafe_allow_html=True)


# ==================== SCHEMA RESOLVER ====================
class SchemaResolver:
    """Resolves $ref references in JSON Schema"""
    
    def __init__(self, schema: Dict):
        self.schema = schema
        self.definitions = schema.get('definitions', {})
        logger.info("Schema resolver initialized")
    
    def resolve_ref(self, ref_path: str) -> Dict:
        """Resolve a $ref path"""
        if not ref_path.startswith('#/'):
            logger.warning(f"Invalid ref path: {ref_path}")
            return {}
        
        path_parts = ref_path[2:].split('/')
        current = self.schema
        
        for part in path_parts:
            current = current.get(part, {})
        
        logger.debug(f"Resolved ref {ref_path}")
        return current
    
    def resolve_schema(self, schema: Dict) -> Dict:
        """Recursively resolve all $ref in a schema"""
        if '$ref' in schema:
            resolved = self.resolve_ref(schema['$ref'])
            schema_copy = {**resolved, **{k: v for k, v in schema.items() if k != '$ref'}}
            return self.resolve_schema(schema_copy)
        
        resolved = {}
        for key, value in schema.items():
            if isinstance(value, dict):
                resolved[key] = self.resolve_schema(value)
            elif isinstance(value, list):
                resolved[key] = [self.resolve_schema(item) if isinstance(item, dict) else item for item in value]
            else:
                resolved[key] = value
        
        return resolved


# ==================== DYNAMIC FIELD RENDERER ====================
class DynamicFormRenderer:
    """Dynamically renders form fields from JSON Schema"""
    
    def __init__(self, resolver: SchemaResolver):
        self.resolver = resolver
        logger.info("Form renderer initialized")
    
    def get_field_type(self, schema: Dict) -> str:
        """Determine the field type from schema"""
        field_type = schema.get('type', 'string')
        
        if 'enum' in schema:
            return 'enum'
        elif field_type == 'array':
            items_schema = schema.get('items', {})
            if items_schema.get('type') == 'object':
                return 'array_object'
            elif 'enum' in items_schema:
                return 'array_enum'
            else:
                return 'array_simple'
        elif field_type == 'object':
            return 'object'
        elif field_type == 'boolean':
            return 'boolean'
        elif field_type == 'number' or field_type == 'integer':
            return 'number'
        else:
            return 'string'
    
    def render_field(self, field_name: str, schema: Dict, parent_key: str = "", 
                     required: bool = False, level: int = 0) -> Any:
        """Render a single field based on its schema"""
        
        schema = self.resolver.resolve_schema(schema)
        field_key = f"{parent_key}_{field_name}" if parent_key else field_name
        
        title = schema.get('title', field_name.replace('_', ' ').title())
        description = schema.get('description', '')
        field_type = self.get_field_type(schema)
        
        # Add required class to label
        if required:
            label = f'<span class="required-field">{title}</span>'
        else:
            label = title
        
        logger.debug(f"Rendering field: {field_name} (type: {field_type})")
        
        if field_type == 'enum':
            return self._render_enum(field_key, label, schema, description)
        elif field_type == 'array_enum':
            return self._render_array_enum(field_key, label, schema, description)
        elif field_type == 'array_object':
            return self._render_array_object(field_key, title, schema, description, level)
        elif field_type == 'array_simple':
            return self._render_array_simple(field_key, label, schema, description)
        elif field_type == 'object':
            return self._render_object(field_key, title, schema, description, level)
        elif field_type == 'boolean':
            return self._render_boolean(field_key, label, description)
        elif field_type == 'number':
            return self._render_number(field_key, label, schema, description)
        else:
            return self._render_string(field_key, label, schema, description, required)
    
    def _render_enum(self, key: str, label: str, schema: Dict, description: str) -> Any:
        """Render enum as dropdown"""
        options = [''] + schema['enum']
        value = st.selectbox(
            label,
            options=options,
            key=key,
            help=description if description else None
        )
        return value if value else None
    
    def _render_array_enum(self, key: str, label: str, schema: Dict, description: str) -> List:
        """Render array of enums as multiselect"""
        options = schema.get('items', {}).get('enum', [])
        values = st.multiselect(
            label,
            options=options,
            key=key,
            help=description if description else None
        )
        return values
    
    def _render_array_object(self, key: str, label: str, schema: Dict, description: str, level: int) -> List[Dict]:
        """Render array of objects"""
        if level == 0:
            st.markdown(f'<div class="section-title">{label}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f"**{label}**")
        
        if description:
            st.caption(description)
        
        if f"{key}_array" not in st.session_state:
            min_items = schema.get('minItems', 1)
            st.session_state[f"{key}_array"] = [{}] * min_items
            logger.info(f"Initialized array {key} with {min_items} items")
        
        items_schema = self.resolver.resolve_schema(schema.get('items', {}))
        properties = items_schema.get('properties', {})
        required_fields = items_schema.get('required', [])
        
        array_values = []
        for idx, item_data in enumerate(st.session_state[f"{key}_array"]):
            st.markdown(f'<div class="array-item"><div class="array-item-header">Item {idx + 1}</div>', unsafe_allow_html=True)
            
            item_value = {}
            for prop_name, prop_schema in properties.items():
                is_required = prop_name in required_fields
                val = self.render_field(
                    prop_name, 
                    prop_schema, 
                    parent_key=f"{key}_item_{idx}",
                    required=is_required,
                    level=level + 1
                )
                if val is not None and val != "" and val != []:
                    item_value[prop_name] = val
            
            # Remove button
            min_items = schema.get('minItems', 0)
            if len(st.session_state[f"{key}_array"]) > max(min_items, 1):
                if st.button("Remove", key=f"{key}_remove_{idx}", type="secondary"):
                    st.session_state[f"{key}_array"].pop(idx)
                    logger.info(f"Removed item {idx} from {key}")
                    st.rerun()
            
            array_values.append(item_value)
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button(f"Add {label}", key=f"{key}_add", type="secondary"):
            st.session_state[f"{key}_array"].append({})
            logger.info(f"Added new item to {key}")
            st.rerun()
        
        return array_values
    
    def _render_array_simple(self, key: str, label: str, schema: Dict, description: str) -> List:
        """Render simple array"""
        help_text = description + " (Separate with commas)" if description else "Separate with commas"
        value = st.text_input(
            label,
            key=key,
            help=help_text
        )
        return [v.strip() for v in value.split(',') if v.strip()] if value else []
    
    def _render_object(self, key: str, label: str, schema: Dict, description: str, level: int) -> Dict:
        """Render object with nested fields"""
        if level == 0:
            st.markdown(f'<div class="section-container"><div class="section-title">{label}</div>', unsafe_allow_html=True)
            if description:
                st.caption(description)
        else:
            st.markdown(f"**{label}**")
            if description:
                st.caption(description)
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        obj_value = {}
        for prop_name, prop_schema in properties.items():
            is_required = prop_name in required_fields
            
            should_render, is_conditionally_required = self._check_conditional_logic(
                schema, prop_name, obj_value, key
            )
            
            if should_render:
                val = self.render_field(
                    prop_name, 
                    prop_schema, 
                    parent_key=key,
                    required=is_required or is_conditionally_required,
                    level=level + 1
                )
                if val is not None and val != "" and val != []:
                    obj_value[prop_name] = val
        
        if level == 0:
            st.markdown('</div>', unsafe_allow_html=True)
        
        return obj_value
    
    def _render_boolean(self, key: str, label: str, description: str) -> bool:
        """Render boolean as checkbox"""
        return st.checkbox(label, key=key, help=description if description else None)
    
    def _render_number(self, key: str, label: str, schema: Dict, description: str) -> Optional[float]:
        """Render number input"""
        min_val = schema.get('minimum', None)
        max_val = schema.get('maximum', None)
        
        value = st.number_input(
            label,
            min_value=min_val,
            max_value=max_val,
            key=key,
            help=description if description else None
        )
        return value if value != 0 else None
    
    def _render_string(self, key: str, label: str, schema: Dict, description: str, required: bool) -> Optional[str]:
        """Render string input"""
        min_length = schema.get('minLength')
        max_length = schema.get('maxLength')
        pattern = schema.get('pattern')
        
        help_text = description
        if min_length or max_length:
            length_info = f"Length: {min_length or 0}-{max_length or '∞'}"
            help_text = f"{description}. {length_info}" if description else length_info
        
        value = st.text_input(
            label,
            key=key,
            help=help_text if help_text else None,
            max_chars=max_length
        )
        
        if value:
            if min_length and len(value) < min_length:
                st.error(f"Minimum length: {min_length} characters")
            if pattern and not re.match(pattern, value):
                st.error(f"Invalid format")
        
        return value if value else None
    
    def _check_conditional_logic(self, schema: Dict, field_name: str, 
                                 current_values: Dict, parent_key: str) -> Tuple[bool, bool]:
        """Check conditional rendering logic"""
        all_of = schema.get('allOf', [])
        for condition in all_of:
            condition = self.resolver.resolve_schema(condition)
            
            if 'if' in condition:
                if_schema = self.resolver.resolve_schema(condition['if'])
                then_schema = self.resolver.resolve_schema(condition.get('then', {}))
                else_schema = self.resolver.resolve_schema(condition.get('else', {}))
                
                condition_met = self._evaluate_condition(if_schema, current_values, parent_key)
                
                if condition_met:
                    if field_name in then_schema.get('required', []):
                        return True, True
                else:
                    if 'not' in else_schema:
                        not_schema = else_schema['not']
                        if field_name in not_schema.get('required', []):
                            return False, False
        
        return True, False
    
    def _evaluate_condition(self, condition: Dict, current_values: Dict, parent_key: str) -> bool:
        """Evaluate conditional schema"""
        properties = condition.get('properties', {})
        
        for prop_name, prop_condition in properties.items():
            field_key = f"{parent_key}_{prop_name}" if parent_key else prop_name
            current_value = st.session_state.get(field_key)
            
            if 'const' in prop_condition:
                if current_value != prop_condition['const']:
                    return False
            
            if 'contains' in prop_condition:
                if not isinstance(current_value, list):
                    return False
                contains_value = prop_condition['contains'].get('const')
                if contains_value not in current_value:
                    return False
        
        return True


# ==================== VALIDATION ENGINE ====================
class ValidationEngine:
    """Validates form data against JSON Schema"""
    
    def __init__(self, schema: Dict, resolver: SchemaResolver):
        self.schema = schema
        self.resolver = resolver
        logger.info("Validation engine initialized")
    
    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate data against schema"""
        errors = []
        
        properties = self.schema.get('properties', {})
        required_fields = self.schema.get('required', [])
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"'{field}' is required")
                logger.warning(f"Validation error: {field} is required")
        
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = self.resolver.resolve_schema(properties[field_name])
                field_errors = self._validate_field(field_name, field_value, field_schema)
                errors.extend(field_errors)
        
        is_valid = len(errors) == 0
        logger.info(f"Validation result: {'PASSED' if is_valid else 'FAILED'} ({len(errors)} errors)")
        return is_valid, errors
    
    def _validate_field(self, field_name: str, value: Any, schema: Dict, path: str = "") -> List[str]:
        """Validate a single field"""
        errors = []
        current_path = f"{path}.{field_name}" if path else field_name
        
        field_type = schema.get('type')
        
        if field_type == 'string' and isinstance(value, str):
            if 'minLength' in schema and len(value) < schema['minLength']:
                errors.append(f"{current_path}: Minimum length is {schema['minLength']}")
            if 'maxLength' in schema and len(value) > schema['maxLength']:
                errors.append(f"{current_path}: Maximum length is {schema['maxLength']}")
            if 'pattern' in schema and not re.match(schema['pattern'], value):
                errors.append(f"{current_path}: Invalid format")
        
        elif field_type == 'array' and isinstance(value, list):
            if 'minItems' in schema and len(value) < schema['minItems']:
                errors.append(f"{current_path}: Minimum {schema['minItems']} items required")
            if 'maxItems' in schema and len(value) > schema['maxItems']:
                errors.append(f"{current_path}: Maximum {schema['maxItems']} items allowed")
            
            items_schema = schema.get('items', {})
            if items_schema.get('type') == 'object':
                for idx, item in enumerate(value):
                    item_errors = self._validate_object(f"{current_path}[{idx}]", item, items_schema)
                    errors.extend(item_errors)
        
        elif field_type == 'object' and isinstance(value, dict):
            errors.extend(self._validate_object(current_path, value, schema))
        
        return errors
    
    def _validate_object(self, path: str, obj: Dict, schema: Dict) -> List[str]:
        """Validate object"""
        errors = []
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        for field in required_fields:
            if field not in obj or not obj[field]:
                errors.append(f"{path}.{field}: Required")
        
        for prop_name, prop_value in obj.items():
            if prop_name in properties:
                prop_schema = self.resolver.resolve_schema(properties[prop_name])
                errors.extend(self._validate_field(prop_name, prop_value, prop_schema, path))
        
        return errors


# ==================== MAIN APPLICATION ====================
def main():
    # Header
    st.markdown("""
    <div class="app-header">
        <div class="app-title">Form Builder</div>
        <div class="app-subtitle">Dynamic schema-driven forms</div>
    </div>
    """, unsafe_allow_html=True)
    
    logger.info("Application started")
    
    # Schema selector
    st.markdown('<div class="schema-selector">', unsafe_allow_html=True)
    
    schema_files = list(Path('.').glob('*.json'))
    
    if not schema_files:
        st.error("No JSON schema files found in the current directory.")
        logger.error("No schema files found")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        selected_file = st.selectbox(
            "Schema File",
            options=[f.name for f in schema_files],
            key='schema_selector',
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("Reset Form", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'schema_selector':
                    del st.session_state[key]
            logger.info("Form reset")
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load schema
    try:
        with open(selected_file, 'r') as f:
            schema = json.load(f)
        logger.info(f"Loaded schema: {selected_file}")
    except Exception as e:
        st.error(f"Error loading schema: {str(e)}")
        logger.error(f"Schema load error: {str(e)}")
        return
    
    # Initialize components
    resolver = SchemaResolver(schema)
    renderer = DynamicFormRenderer(resolver)
    validator = ValidationEngine(schema, resolver)
    
    # Render form
    properties = schema.get('properties', {})
    required_fields = schema.get('required', [])
    
    if not properties:
        st.warning("No properties defined in schema.")
        return
    
    form_data = {}
    for field_name, field_schema in properties.items():
        is_required = field_name in required_fields
        value = renderer.render_field(field_name, field_schema, required=is_required)
        
        if value is not None and value != "" and value != []:
            form_data[field_name] = value
    
    # Action bar
    st.markdown('<div class="action-bar">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Validate", use_container_width=True, type="secondary"):
            is_valid, errors = validator.validate(form_data)
            
            if is_valid:
                st.success("Validation passed")
                logger.info("Validation successful")
            else:
                st.error("Validation failed")
                for error in errors:
                    st.error(error)
                logger.warning(f"Validation failed with {len(errors)} errors")
    
    with col2:
        if st.button("Save Draft", use_container_width=True, type="secondary"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_file = f"draft_{timestamp}.json"
            with open(draft_file, 'w') as f:
                json.dump(form_data, f, indent=2)
            st.success(f"Draft saved: {draft_file}")
            logger.info(f"Draft saved: {draft_file}")
    
    with col3:
        if st.button("Submit", use_container_width=True, type="primary"):
            is_valid, errors = validator.validate(form_data)
            
            if is_valid:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                submission_file = f"submission_{timestamp}.json"
                
                with open(submission_file, 'w') as f:
                    json.dump(form_data, f, indent=2)
                
                st.success(f"Submitted successfully: {submission_file}")
                logger.info(f"Form submitted: {submission_file}")
                
                st.download_button(
                    label="Download Submission",
                    data=json.dumps(form_data, indent=2),
                    file_name=submission_file,
                    mime="application/json",
                    use_container_width=True
                )
            else:
                st.error("Please fix validation errors before submitting")
                for error in errors:
                    st.error(error)
                logger.warning(f"Submit failed - validation errors: {len(errors)}")
    
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()