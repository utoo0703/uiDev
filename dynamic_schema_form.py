import streamlit as st
import json
from typing import Dict, Any, List, Optional, Tuple
import re
from pathlib import Path
import copy
from datetime import datetime
import hashlib
import logging

# ==================== LOGGING CONFIGURATION ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schema_form_builder.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Schema Form Builder",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean business UI - Black/White/Red theme
st.markdown("""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');
    
    /* Global styles */
    .main {
        background: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .header-container {
        background: #1a1a1a;
        padding: 2rem 2rem;
        border-radius: 4px;
        margin-bottom: 2rem;
        border-left: 4px solid #dc2626;
    }
    
    .header-title {
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin: 0;
        letter-spacing: -0.3px;
    }
    
    .header-subtitle {
        color: #d1d5db;
        font-size: 0.95rem;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Card styling */
    .form-card {
        background: white;
        padding: 2rem;
        border-radius: 4px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    .section-header {
        color: #1a1a1a;
        font-size: 1.25rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid #1a1a1a;
    }
    
    /* Field styling */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stMultiSelect > div > div,
    .stTextArea > div > div > textarea {
        border: 1px solid #d1d5db;
        border-radius: 4px;
        padding: 0.5rem 0.75rem;
        font-size: 0.9rem;
        transition: border-color 0.2s;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #1a1a1a;
        outline: none;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 4px;
        padding: 0.5rem 1.25rem;
        font-weight: 500;
        font-size: 0.9rem;
        transition: all 0.2s;
        border: 1px solid #d1d5db;
    }
    
    .stButton > button[kind="primary"] {
        background: #dc2626;
        color: white;
        border: 1px solid #dc2626;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #b91c1c;
        border-color: #b91c1c;
    }
    
    .stButton > button[kind="secondary"] {
        background: #1a1a1a;
        color: white;
        border: 1px solid #1a1a1a;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #404040;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #f0fdf4;
        border-left: 4px solid #16a34a;
        border-radius: 4px;
        padding: 1rem;
        color: #166534;
    }
    
    .stError {
        background: #fef2f2;
        border-left: 4px solid #dc2626;
        border-radius: 4px;
        padding: 1rem;
        color: #991b1b;
    }
    
    .stWarning {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 4px;
        padding: 1rem;
        color: #92400e;
    }
    
    .stInfo {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        border-radius: 4px;
        padding: 1rem;
        color: #1e40af;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #f9fafb;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Info boxes */
    .info-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #1a1a1a;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
        font-size: 0.9rem;
    }
    
    /* Schema viewer */
    .schema-viewer {
        background: #1a1a1a;
        color: #e5e7eb;
        padding: 1.5rem;
        border-radius: 4px;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.85rem;
        overflow-x: auto;
    }
    
    /* Array item cards */
    .array-item {
        background: #f9fafb;
        padding: 1.25rem;
        border-radius: 4px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    
    /* Field labels */
    label {
        font-weight: 500 !important;
        color: #374151 !important;
        font-size: 0.875rem !important;
    }
    
    /* Required field indicator */
    .required-indicator {
        color: #dc2626;
        font-weight: 600;
        margin-left: 4px;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: white;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        color: #6b7280;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #1a1a1a;
        border-bottom-color: #dc2626;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        font-weight: 500;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)


# ==================== VERSION CONTROL MANAGER ====================
class VersionControlManager:
    """Manages schema versioning and change logs"""
    
    def __init__(self, schema_path: str):
        self.schema_path = schema_path
        self.base_name = Path(schema_path).stem
        self.versions_dir = Path("schema_versions") / self.base_name
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.changelog_file = self.versions_dir / "changelog.json"
        self._initialize_changelog()
        logger.info(f"Initialized version control for schema: {self.base_name}")
    
    def _initialize_changelog(self):
        """Initialize changelog file if it doesn't exist"""
        if not self.changelog_file.exists():
            changelog = {
                "schema_name": self.base_name,
                "versions": []
            }
            with open(self.changelog_file, 'w') as f:
                json.dump(changelog, f, indent=2)
            logger.info(f"Created new changelog file: {self.changelog_file}")
    
    def _get_schema_hash(self, schema: Dict) -> str:
        """Generate hash of schema for change detection"""
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()
    
    def save_version(self, schema: Dict, change_description: str, author: str = "User") -> Optional[str]:
        """Save a new version of the schema"""
        try:
            # Load changelog
            with open(self.changelog_file, 'r') as f:
                changelog = json.load(f)
            
            # Get current version number
            version_number = len(changelog['versions']) + 1
            timestamp = datetime.now().isoformat()
            schema_hash = self._get_schema_hash(schema)
            
            # Check if schema actually changed
            if changelog['versions']:
                last_hash = changelog['versions'][-1]['hash']
                if last_hash == schema_hash:
                    logger.info("No changes detected in schema")
                    return None
            
            # Create version entry
            version_entry = {
                "version": version_number,
                "timestamp": timestamp,
                "author": author,
                "description": change_description,
                "hash": schema_hash
            }
            
            # Save version file
            version_filename = f"v{version_number}_{timestamp.replace(':', '-').split('.')[0]}.json"
            version_path = self.versions_dir / version_filename
            
            with open(version_path, 'w') as f:
                json.dump(schema, f, indent=2)
            
            version_entry['file'] = str(version_path)
            
            # Update changelog
            changelog['versions'].append(version_entry)
            with open(self.changelog_file, 'w') as f:
                json.dump(changelog, f, indent=2)
            
            logger.info(f"Saved version {version_number}: {change_description} by {author}")
            return version_filename
        
        except Exception as e:
            logger.error(f"Error saving version: {str(e)}", exc_info=True)
            raise
    
    def get_changelog(self) -> Dict:
        """Get the full changelog"""
        try:
            if self.changelog_file.exists():
                with open(self.changelog_file, 'r') as f:
                    return json.load(f)
            return {"schema_name": self.base_name, "versions": []}
        except Exception as e:
            logger.error(f"Error reading changelog: {str(e)}", exc_info=True)
            return {"schema_name": self.base_name, "versions": []}
    
    def get_version(self, version_number: int) -> Optional[Dict]:
        """Retrieve a specific version of the schema"""
        try:
            changelog = self.get_changelog()
            
            for version in changelog['versions']:
                if version['version'] == version_number:
                    version_file = Path(version['file'])
                    if version_file.exists():
                        with open(version_file, 'r') as f:
                            logger.info(f"Retrieved version {version_number}")
                            return json.load(f)
            
            logger.warning(f"Version {version_number} not found")
            return None
        except Exception as e:
            logger.error(f"Error retrieving version {version_number}: {str(e)}", exc_info=True)
            return None
    
    def compare_versions(self, version1: int, version2: int) -> Dict:
        """Compare two versions and return differences"""
        try:
            schema1 = self.get_version(version1)
            schema2 = self.get_version(version2)
            
            if not schema1 or not schema2:
                return {"error": "Version not found"}
            
            differences = {
                "added_fields": [],
                "removed_fields": [],
                "modified_fields": []
            }
            
            # Compare properties
            props1 = set(schema1.get('properties', {}).keys())
            props2 = set(schema2.get('properties', {}).keys())
            
            differences['added_fields'] = list(props2 - props1)
            differences['removed_fields'] = list(props1 - props2)
            
            # Check modified fields
            for prop in props1.intersection(props2):
                if schema1['properties'][prop] != schema2['properties'][prop]:
                    differences['modified_fields'].append(prop)
            
            logger.info(f"Compared versions {version1} and {version2}")
            return differences
        
        except Exception as e:
            logger.error(f"Error comparing versions: {str(e)}", exc_info=True)
            return {"error": str(e)}
    
    def rollback_to_version(self, version_number: int, schema_path: str) -> bool:
        """Rollback schema to a specific version"""
        try:
            schema = self.get_version(version_number)
            if schema:
                with open(schema_path, 'w') as f:
                    json.dump(schema, f, indent=2)
                
                # Log the rollback as a new version
                self.save_version(
                    schema, 
                    f"Rolled back to version {version_number}",
                    "System"
                )
                logger.info(f"Successfully rolled back to version {version_number}")
                return True
            
            logger.warning(f"Could not rollback to version {version_number} - version not found")
            return False
        
        except Exception as e:
            logger.error(f"Error during rollback: {str(e)}", exc_info=True)
            return False


# ==================== SCHEMA RESOLVER ====================
class SchemaResolver:
    """Resolves $ref references in JSON Schema"""
    
    def __init__(self, schema: Dict):
        self.schema = schema
        self.definitions = schema.get('definitions', {})
        logger.debug("Initialized SchemaResolver")
    
    def resolve_ref(self, ref_path: str) -> Dict:
        """Resolve a $ref path like #/definitions/country"""
        if not ref_path.startswith('#/'):
            return {}
        
        path_parts = ref_path[2:].split('/')
        current = self.schema
        
        for part in path_parts:
            current = current.get(part, {})
        
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
        self.form_data = {}
        logger.debug("Initialized DynamicFormRenderer")
    
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
        
        label = f"{title} {'*' if required else ''}"
        indent = "　" * level if level > 0 else ""
        
        if field_type == 'enum':
            return self._render_enum(field_key, label, schema, description, indent)
        elif field_type == 'array_enum':
            return self._render_array_enum(field_key, label, schema, description, indent)
        elif field_type == 'array_object':
            return self._render_array_object(field_key, label, schema, description, level)
        elif field_type == 'array_simple':
            return self._render_array_simple(field_key, label, schema, description, indent)
        elif field_type == 'object':
            return self._render_object(field_key, label, schema, description, level)
        elif field_type == 'boolean':
            return self._render_boolean(field_key, label, description, indent)
        elif field_type == 'number':
            return self._render_number(field_key, label, schema, description, indent)
        else:
            return self._render_string(field_key, label, schema, description, indent, required)
    
    def _render_enum(self, key: str, label: str, schema: Dict, description: str, indent: str) -> Any:
        """Render enum as dropdown"""
        options = [''] + schema['enum']
        value = st.selectbox(
            f"{indent}{label}",
            options=options,
            key=key,
            help=description
        )
        return value if value else None
    
    def _render_array_enum(self, key: str, label: str, schema: Dict, description: str, indent: str) -> List:
        """Render array of enums as multiselect"""
        options = schema.get('items', {}).get('enum', [])
        values = st.multiselect(
            f"{indent}{label}",
            options=options,
            key=key,
            help=description
        )
        return values
    
    def _render_array_object(self, key: str, label: str, schema: Dict, description: str, level: int) -> List[Dict]:
        """Render array of objects with add/remove functionality"""
        st.markdown(f"##### {label}")
        if description:
            st.caption(description)
        
        if f"{key}_array" not in st.session_state:
            min_items = schema.get('minItems', 1)
            st.session_state[f"{key}_array"] = [{}] * min_items
        
        items_schema = self.resolver.resolve_schema(schema.get('items', {}))
        properties = items_schema.get('properties', {})
        required_fields = items_schema.get('required', [])
        
        array_values = []
        for idx, item_data in enumerate(st.session_state[f"{key}_array"]):
            with st.container():
                st.markdown(f'<div class="array-item">', unsafe_allow_html=True)
                
                cols = st.columns([4, 1])
                with cols[0]:
                    st.markdown(f"**Item {idx + 1}**")
                
                with cols[1]:
                    min_items = schema.get('minItems', 0)
                    if len(st.session_state[f"{key}_array"]) > max(min_items, 1):
                        if st.button("Remove", key=f"{key}_remove_{idx}", use_container_width=True):
                            st.session_state[f"{key}_array"].pop(idx)
                            logger.info(f"Removed array item {idx} from {key}")
                            st.rerun()
                
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
                
                array_values.append(item_value)
                st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button(f"Add {label}", key=f"{key}_add"):
            st.session_state[f"{key}_array"].append({})
            logger.info(f"Added new array item to {key}")
            st.rerun()
        
        return array_values
    
    def _render_array_simple(self, key: str, label: str, schema: Dict, description: str, indent: str) -> List:
        """Render simple array as comma-separated input"""
        value = st.text_input(
            f"{indent}{label}",
            key=key,
            help=f"{description} (Separate with commas)"
        )
        return [v.strip() for v in value.split(',') if v.strip()] if value else []
    
    def _render_object(self, key: str, label: str, schema: Dict, description: str, level: int) -> Dict:
        """Render object with nested fields"""
        if level == 0:
            st.markdown(f"### {label}")
        else:
            st.markdown(f"#### {label}")
        
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
        
        return obj_value
    
    def _render_boolean(self, key: str, label: str, description: str, indent: str) -> bool:
        """Render boolean as checkbox"""
        return st.checkbox(f"{indent}{label}", key=key, help=description)
    
    def _render_number(self, key: str, label: str, schema: Dict, description: str, indent: str) -> Optional[float]:
        """Render number input"""
        min_val = schema.get('minimum', None)
        max_val = schema.get('maximum', None)
        
        value = st.number_input(
            f"{indent}{label}",
            min_value=min_val,
            max_value=max_val,
            key=key,
            help=description
        )
        return value if value != 0 else None
    
    def _render_string(self, key: str, label: str, schema: Dict, description: str, 
                      indent: str, required: bool) -> Optional[str]:
        """Render string input with validation"""
        min_length = schema.get('minLength')
        max_length = schema.get('maxLength')
        pattern = schema.get('pattern')
        
        help_text = description
        if min_length or max_length:
            help_text += f" (Length: {min_length or 0}-{max_length or '∞'})"
        
        value = st.text_input(
            f"{indent}{label}",
            key=key,
            help=help_text,
            max_chars=max_length
        )
        
        if value:
            if min_length and len(value) < min_length:
                st.error(f"Minimum length: {min_length} characters")
            if max_length and len(value) > max_length:
                st.error(f"Maximum length: {max_length} characters")
            if pattern and not re.match(pattern, value):
                st.error(f"Invalid format")
        
        return value if value else None
    
    def _check_conditional_logic(self, schema: Dict, field_name: str, 
                                 current_values: Dict, parent_key: str) -> Tuple[bool, bool]:
        """Check if field should be rendered based on if/then/else logic"""
        
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
        """Evaluate a conditional schema"""
        properties = condition.get('properties', {})
        required = condition.get('required', [])
        
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
        
        for req_field in required:
            field_key = f"{parent_key}_{req_field}" if parent_key else req_field
            if not st.session_state.get(field_key):
                return False
        
        return True


# ==================== VALIDATION ENGINE ====================
class ValidationEngine:
    """Validates form data against JSON Schema"""
    
    def __init__(self, schema: Dict, resolver: SchemaResolver):
        self.schema = schema
        self.resolver = resolver
        logger.debug("Initialized ValidationEngine")
    
    def validate(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate data against schema"""
        errors = []
        
        properties = self.schema.get('properties', {})
        required_fields = self.schema.get('required', [])
        
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f"'{field}' is required")
                logger.warning(f"Validation failed: Required field '{field}' is missing")
        
        for field_name, field_value in data.items():
            if field_name in properties:
                field_schema = self.resolver.resolve_schema(properties[field_name])
                field_errors = self._validate_field(field_name, field_value, field_schema)
                errors.extend(field_errors)
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info("Form validation passed")
        else:
            logger.warning(f"Form validation failed with {len(errors)} errors")
        
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
                errors.append(f"{current_path}: Does not match required pattern")
            if 'enum' in schema and value not in schema['enum']:
                errors.append(f"{current_path}: Must be one of {schema['enum']}")
        
        elif field_type == 'array' and isinstance(value, list):
            if 'minItems' in schema and len(value) < schema['minItems']:
                errors.append(f"{current_path}: Minimum {schema['minItems']} items required")
            if 'maxItems' in schema and len(value) > schema['maxItems']:
                errors.append(f"{current_path}: Maximum {schema['maxItems']} items allowed")
            if schema.get('uniqueItems') and len(value) != len(set(map(str, value))):
                errors.append(f"{current_path}: Items must be unique")
            
            items_schema = schema.get('items', {})
            if items_schema.get('type') == 'object':
                for idx, item in enumerate(value):
                    item_errors = self._validate_object(f"{current_path}[{idx}]", item, items_schema)
                    errors.extend(item_errors)
        
        elif field_type == 'object' and isinstance(value, dict):
            errors.extend(self._validate_object(current_path, value, schema))
        
        return errors
    
    def _validate_object(self, path: str, obj: Dict, schema: Dict) -> List[str]:
        """Validate an object against its schema"""
        errors = []
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        for field in required_fields:
            if field not in obj or not obj[field]:
                errors.append(f"{path}.{field}: Required field")
        
        for prop_name, prop_value in obj.items():
            if prop_name in properties:
                prop_schema = self.resolver.resolve_schema(properties[prop_name])
                errors.extend(self._validate_field(prop_name, prop_value, prop_schema, path))
        
        return errors


# ==================== SCHEMA FORM EDITOR ====================
class SchemaFormEditor:
    """Visual form-based schema editor"""
    
    def __init__(self):
        self.field_types = [
            "string", "number", "integer", "boolean", 
            "array", "object", "enum"
        ]
        logger.debug("Initialized SchemaFormEditor")
    
    def render_property_editor(self, property_name: str, property_schema: Dict, 
                               parent_key: str = "") -> Optional[Dict]:
        """Render editor for a single property"""
        key_prefix = f"{parent_key}_{property_name}" if parent_key else property_name
        
        st.markdown(f"#### {property_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input(
                "Display Title",
                value=property_schema.get('title', property_name),
                key=f"{key_prefix}_title"
            )
            
            field_type = st.selectbox(
                "Field Type",
                options=self.field_types,
                index=self.field_types.index(property_schema.get('type', 'string')),
                key=f"{key_prefix}_type"
            )
        
        with col2:
            description = st.text_area(
                "Description",
                value=property_schema.get('description', ''),
                key=f"{key_prefix}_desc",
                height=100
            )
        
        updated_schema = {
            "type": field_type,
            "title": title
        }
        
        if description:
            updated_schema["description"] = description
        
        if field_type == "string":
            col1, col2, col3 = st.columns(3)
            with col1:
                min_length = st.number_input(
                    "Min Length",
                    min_value=0,
                    value=property_schema.get('minLength', 0),
                    key=f"{key_prefix}_minlen"
                )
            with col2:
                max_length = st.number_input(
                    "Max Length",
                    min_value=0,
                    value=property_schema.get('maxLength', 100),
                    key=f"{key_prefix}_maxlen"
                )
            with col3:
                pattern = st.text_input(
                    "Pattern (regex)",
                    value=property_schema.get('pattern', ''),
                    key=f"{key_prefix}_pattern"
                )
            
            if min_length > 0:
                updated_schema["minLength"] = min_length
            if max_length > 0:
                updated_schema["maxLength"] = max_length
            if pattern:
                updated_schema["pattern"] = pattern
        
        elif field_type == "enum":
            enum_values = st.text_area(
                "Enum Values (one per line)",
                value="\n".join(property_schema.get('enum', [])),
                key=f"{key_prefix}_enum"
            )
            if enum_values:
                updated_schema["enum"] = [v.strip() for v in enum_values.split('\n') if v.strip()]
        
        elif field_type == "array":
            col1, col2 = st.columns(2)
            with col1:
                min_items = st.number_input(
                    "Min Items",
                    min_value=0,
                    value=property_schema.get('minItems', 0),
                    key=f"{key_prefix}_minitems"
                )
            with col2:
                max_items = st.number_input(
                    "Max Items",
                    min_value=0,
                    value=property_schema.get('maxItems', 10),
                    key=f"{key_prefix}_maxitems"
                )
            
            unique_items = st.checkbox(
                "Unique Items",
                value=property_schema.get('uniqueItems', False),
                key=f"{key_prefix}_unique"
            )
            
            if min_items > 0:
                updated_schema["minItems"] = min_items
            if max_items > 0:
                updated_schema["maxItems"] = max_items
            if unique_items:
                updated_schema["uniqueItems"] = unique_items
            
            items_schema = property_schema.get('items', {'type': 'string'})
            item_type = st.selectbox(
                "Array Item Type",
                options=["string", "number", "integer", "object"],
                index=["string", "number", "integer", "object"].index(
                    items_schema.get('type', 'string')
                ),
                key=f"{key_prefix}_itemtype"
            )
            updated_schema["items"] = {"type": item_type}
        
        elif field_type in ["number", "integer"]:
            col1, col2 = st.columns(2)
            with col1:
                minimum = st.number_input(
                    "Minimum",
                    value=float(property_schema.get('minimum', 0)),
                    key=f"{key_prefix}_min"
                )
            with col2:
                maximum = st.number_input(
                    "Maximum",
                    value=float(property_schema.get('maximum', 100)),
                    key=f"{key_prefix}_max"
                )
            
            if minimum is not None:
                updated_schema["minimum"] = minimum
            if maximum is not None:
                updated_schema["maximum"] = maximum
        
        return updated_schema
    
    def render_schema_editor(self, schema: Dict) -> Dict:
        """Render full schema editor interface"""
        st.markdown("### Schema Structure Editor")
        
        with st.expander("Schema Metadata", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                schema_title = st.text_input(
                    "Schema Title",
                    value=schema.get('title', 'Untitled Schema'),
                    key="schema_title"
                )
            with col2:
                schema_desc = st.text_input(
                    "Schema Description",
                    value=schema.get('description', ''),
                    key="schema_desc"
                )
        
        st.markdown("### Properties")
        
        properties = schema.get('properties', {})
        updated_properties = {}
        
        for prop_name, prop_schema in properties.items():
            with st.expander(f"{prop_name}", expanded=False):
                updated_prop = self.render_property_editor(prop_name, prop_schema)
                if updated_prop:
                    updated_properties[prop_name] = updated_prop
                
                if st.button(f"Delete {prop_name}", key=f"delete_{prop_name}"):
                    st.session_state[f'delete_prop_{prop_name}'] = True
                    logger.info(f"Deleted property: {prop_name}")
                    st.rerun()
        
        for prop_name in list(updated_properties.keys()):
            if st.session_state.get(f'delete_prop_{prop_name}'):
                del updated_properties[prop_name]
                del st.session_state[f'delete_prop_{prop_name}']
        
        st.markdown("### Add New Property")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            new_prop_name = st.text_input(
                "Property Name",
                key="new_prop_name",
                placeholder="e.g., email, age, address"
            )
        
        with col2:
            new_prop_type = st.selectbox(
                "Type",
                options=self.field_types,
                key="new_prop_type"
            )
        
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Add Property", use_container_width=True):
                if new_prop_name and new_prop_name not in updated_properties:
                    updated_properties[new_prop_name] = {
                        "type": new_prop_type,
                        "title": new_prop_name.replace('_', ' ').title()
                    }
                    st.session_state.new_prop_name = ""
                    logger.info(f"Added new property: {new_prop_name}")
                    st.success(f"Added property: {new_prop_name}")
                    st.rerun()
                elif new_prop_name in updated_properties:
                    st.error("Property already exists")
        
        st.markdown("### Required Fields")
        current_required = schema.get('required', [])
        available_props = list(updated_properties.keys())
        
        required_fields = st.multiselect(
            "Select required fields",
            options=available_props,
            default=[f for f in current_required if f in available_props],
            key="required_fields"
        )
        
        updated_schema = {
            "type": "object",
            "properties": updated_properties
        }
        
        if schema_title:
            updated_schema["title"] = schema_title
        if schema_desc:
            updated_schema["description"] = schema_desc
        if required_fields:
            updated_schema["required"] = required_fields
        
        if 'definitions' in schema:
            updated_schema['definitions'] = schema['definitions']
        
        return updated_schema


# ==================== MAIN APPLICATION ====================
def main():
    logger.info("Application started")
    
    # Header
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Schema Form Builder</h1>
        <p class="header-subtitle">Professional form engine with version control</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Schema Management")
        
        schema_files = list(Path('.').glob('*.json'))
        
        if schema_files:
            selected_file = st.selectbox(
                "Select Schema File",
                options=[f.name for f in schema_files],
                key='schema_selector'
            )
            schema_path = selected_file
        else:
            st.warning("No .json schema files found")
            schema_path = st.text_input("Schema file name", value="schema.json")
        
        st.markdown("---")
        
        st.markdown("### Upload Schema")
        uploaded_file = st.file_uploader("Upload JSON Schema", type=['json'])
        
        if uploaded_file:
            try:
                new_schema = json.load(uploaded_file)
                with open(uploaded_file.name, 'w') as f:
                    json.dump(new_schema, f, indent=2)
                
                vc_manager = VersionControlManager(uploaded_file.name)
                vc_manager.save_version(new_schema, "Initial upload", "User")
                
                logger.info(f"Uploaded new schema: {uploaded_file.name}")
                st.success(f"Uploaded: {uploaded_file.name}")
                st.rerun()
            except Exception as e:
                logger.error(f"Error uploading file: {str(e)}", exc_info=True)
                st.error(f"Error: {str(e)}")
        
        st.markdown("---")
        
        mode = st.radio(
            "Mode",
            options=["Fill Form", "Edit Schema", "Version History"],
            key='mode_selector'
        )
        
        st.markdown("---")
        
        if st.button("Reset Form", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ['schema_selector', 'mode_selector']:
                    del st.session_state[key]
            logger.info("Form reset")
            st.success("Form reset")
            st.rerun()
    
    # Load schema
    try:
        with open(schema_path, 'r') as f:
            schema = json.load(f)
        logger.info(f"Loaded schema: {schema_path}")
    except FileNotFoundError:
        logger.error(f"Schema file not found: {schema_path}")
        st.error(f"Schema file '{schema_path}' not found")
        st.info("Please upload a JSON Schema file using the sidebar")
        return
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in schema file: {schema_path}")
        st.error("Invalid JSON in schema file")
        return
    
    vc_manager = VersionControlManager(schema_path)
    
    # ==================== EDIT SCHEMA MODE ====================
    if mode == "Edit Schema":
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Form Editor", "JSON Editor"])
        
        with tab1:
            editor = SchemaFormEditor()
            updated_schema = editor.render_schema_editor(schema)
            
            st.markdown("---")
            
            with st.expander("Preview Updated Schema"):
                st.json(updated_schema)
            
            st.markdown("### Save Changes")
            
            col1, col2 = st.columns([3, 1])
            with col1:
                change_description = st.text_input(
                    "Describe your changes",
                    placeholder="e.g., Added email field, Updated validation rules",
                    key="change_description"
                )
            
            with col2:
                author_name = st.text_input(
                    "Your Name",
                    value="User",
                    key="author_name"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Schema", use_container_width=True, type="primary"):
                    if not change_description:
                        st.error("Please describe your changes")
                    else:
                        try:
                            with open(schema_path, 'w') as f:
                                json.dump(updated_schema, f, indent=2)
                            
                            version_file = vc_manager.save_version(
                                updated_schema,
                                change_description,
                                author_name
                            )
                            
                            if version_file:
                                st.success(f"Schema saved - Version: {version_file}")
                            else:
                                st.info("No changes detected")
                            
                            st.rerun()
                        except Exception as e:
                            logger.error(f"Error saving schema: {str(e)}", exc_info=True)
                            st.error(f"Error saving: {str(e)}")
            
            with col2:
                if st.button("Cancel", use_container_width=True):
                    st.rerun()
        
        with tab2:
            st.caption("Edit your JSON Schema directly. Changes will be validated before saving.")
            
            edited_schema = st.text_area(
                "Schema JSON",
                value=json.dumps(schema, indent=2),
                height=500,
                key='schema_json_editor'
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                json_change_desc = st.text_input(
                    "Describe your changes",
                    placeholder="e.g., Manual JSON edits",
                    key="json_change_description"
                )
            
            with col2:
                json_author = st.text_input(
                    "Your Name",
                    value="User",
                    key="json_author_name"
                )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save JSON Schema", use_container_width=True, type="primary"):
                    if not json_change_desc:
                        st.error("Please describe your changes")
                    else:
                        try:
                            new_schema = json.loads(edited_schema)
                            
                            with open(schema_path, 'w') as f:
                                json.dump(new_schema, f, indent=2)
                            
                            version_file = vc_manager.save_version(
                                new_schema,
                                json_change_desc,
                                json_author
                            )
                            
                            if version_file:
                                st.success(f"Schema saved - Version: {version_file}")
                            else:
                                st.info("No changes detected")
                            
                            st.rerun()
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON: {str(e)}")
                            st.error(f"Invalid JSON: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error saving schema: {str(e)}", exc_info=True)
                            st.error(f"Error: {str(e)}")
            
            with col2:
                if st.button("Cancel JSON", use_container_width=True):
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # ==================== VERSION HISTORY MODE ====================
    elif mode == "Version History":
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.markdown("### Version History")
        
        changelog = vc_manager.get_changelog()
        versions = changelog.get('versions', [])
        
        if not versions:
            st.info("No version history available yet. Edit and save the schema to create versions.")
        else:
            st.markdown(f"**Total Versions:** {len(versions)}")
            
            for version in reversed(versions):
                with st.expander(
                    f"Version {version['version']} - {version['timestamp'][:10]} - {version['author']}"
                ):
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(f"**Description:** {version['description']}")
                        st.markdown(f"**Timestamp:** {version['timestamp']}")
                    
                    with col2:
                        st.markdown(f"**Author:** {version['author']}")
                        st.markdown(f"**Hash:** `{version['hash'][:12]}...`")
                    
                    with col3:
                        if st.button(
                            "Restore",
                            key=f"restore_v{version['version']}",
                            use_container_width=True
                        ):
                            if vc_manager.rollback_to_version(version['version'], schema_path):
                                st.success(f"Restored to version {version['version']}")
                                st.rerun()
                            else:
                                st.error("Failed to restore version")
                    
                    version_schema = vc_manager.get_version(version['version'])
                    if version_schema:
                        st.json(version_schema)
            
            st.markdown("---")
            st.markdown("### Compare Versions")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            version_numbers = [v['version'] for v in versions]
            
            with col1:
                compare_v1 = st.selectbox(
                    "Version 1",
                    options=version_numbers,
                    key="compare_v1"
                )
            
            with col2:
                compare_v2 = st.selectbox(
                    "Version 2",
                    options=version_numbers,
                    index=len(version_numbers)-1 if len(version_numbers) > 0 else 0,
                    key="compare_v2"
                )
            
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Compare", use_container_width=True):
                    if compare_v1 and compare_v2:
                        diff = vc_manager.compare_versions(compare_v1, compare_v2)
                        
                        if 'error' in diff:
                            st.error(diff['error'])
                        else:
                            st.markdown("#### Comparison Results")
                            
                            if diff['added_fields']:
                                st.success(f"**Added Fields:** {', '.join(diff['added_fields'])}")
                            
                            if diff['removed_fields']:
                                st.error(f"**Removed Fields:** {', '.join(diff['removed_fields'])}")
                            
                            if diff['modified_fields']:
                                st.warning(f"**Modified Fields:** {', '.join(diff['modified_fields'])}")
                            
                            if not any([diff['added_fields'], diff['removed_fields'], diff['modified_fields']]):
                                st.info("No differences found")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    # ==================== FILL FORM MODE ====================
    else:
        resolver = SchemaResolver(schema)
        renderer = DynamicFormRenderer(resolver)
        validator = ValidationEngine(schema, resolver)
        
        changelog = vc_manager.get_changelog()
        current_version = len(changelog.get('versions', []))
        
        st.markdown(f"""
        <div class="info-box">
            <strong>Schema Information</strong><br>
            <strong>File:</strong> {schema_path}<br>
            <strong>Fields:</strong> {len(schema.get('properties', {}))} top-level fields<br>
            <strong>Version:</strong> {current_version if current_version > 0 else 'No versions yet'}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        
        properties = schema.get('properties', {})
        required_fields = schema.get('required', [])
        
        if not properties:
            st.warning("No properties defined in schema")
            st.info("Switch to 'Edit Schema' mode to add properties")
            return
        
        form_data = {}
        for field_name, field_schema in properties.items():
            is_required = field_name in required_fields
            value = renderer.render_field(field_name, field_schema, required=is_required)
            
            if value is not None and value != "" and value != []:
                form_data[field_name] = value
            
            st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("### Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("Validate", use_container_width=True, type="secondary"):
                is_valid, errors = validator.validate(form_data)
                
                if is_valid:
                    st.success("Form validation passed")
                else:
                    st.error("Validation failed:")
                    for error in errors:
                        st.error(error)
        
        with col2:
            if st.button("Save Draft", use_container_width=True):
                draft_file = f"draft_{schema_path}"
                with open(draft_file, 'w') as f:
                    json.dump(form_data, f, indent=2)
                logger.info(f"Draft saved: {draft_file}")
                st.success(f"Draft saved to {draft_file}")
        
        with col3:
            if st.button("Submit", use_container_width=True, type="primary"):
                is_valid, errors = validator.validate(form_data)
                
                if is_valid:
                    submission_file = f"submission_{schema_path}"
                    with open(submission_file, 'w') as f:
                        json.dump(form_data, f, indent=2)
                    
                    logger.info(f"Form submitted: {submission_file}")
                    st.success("Form submitted successfully")
                    
                    st.download_button(
                        label="Download Submission",
                        data=json.dumps(form_data, indent=2),
                        file_name=submission_file,
                        mime="application/json"
                    )
                else:
                    st.error("Please fix validation errors:")
                    for error in errors:
                        st.error(error)
        
        with col4:
            if st.button("Preview Data", use_container_width=True):
                st.session_state.show_preview = not st.session_state.get('show_preview', False)
        
        if st.session_state.get('show_preview'):
            st.markdown("### Form Data Preview")
            st.json(form_data)


if __name__ == "__main__":
    main()