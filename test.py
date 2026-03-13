import streamlit as st
import pandas as pd
import json
import time
import copy

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="ALAN ADMIN PORTAL", layout="wide")

# ---------------------------------------------------------------------------
# CSS  (strict White & Red theme, kept under 20 lines)
# ---------------------------------------------------------------------------
st.markdown("""
<style>
:root{--red:#C0392B;--red-light:#E74C3C;--grey:#F8F9FA;}
header[data-testid="stHeader"]{background:#fff;border-bottom:2px solid var(--red);}
[data-testid="stSidebar"]{background:#fff;border-right:2px solid var(--red);}
h1,h2,h3{color:var(--red)!important;}
div.stButton>button{background:var(--red);color:#fff;border:none;border-radius:4px;padding:.45rem 1.1rem;}
div.stButton>button:hover{background:var(--red-light);color:#fff;}
div[data-testid="stDialog"] button{background:var(--red);color:#fff;border:none;}
.active-banner{background:var(--grey);border-left:4px solid var(--red);padding:12px 18px;margin-bottom:10px;border-radius:4px;}
.active-banner h3{margin:0;font-size:1.05rem;}
.meta-card{background:var(--grey);padding:14px 18px;border-radius:6px;margin-bottom:6px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Mock data factory
# ---------------------------------------------------------------------------
def _build_store():
    payloads = {
        "usecase_schema": [
            {"name": "Fraud Detection", "domain": "finance",
             "features": ["txn_amount", "merchant_id", "ip_geo"],
             "config": {"threshold": 0.85, "ensemble": True, "fallback": "rule_engine"}},
            {"name": "Fraud Detection", "domain": "finance",
             "features": ["txn_amount", "merchant_id"],
             "config": {"threshold": 0.80, "ensemble": False, "fallback": "manual_review"}},
            {"name": "Fraud Detection v3", "domain": "finance",
             "features": ["txn_amount", "merchant_id", "ip_geo", "device_fp"],
             "config": {"threshold": 0.90, "ensemble": True, "fallback": "rule_engine", "retries": 3}},
        ],
        "model_schema": [
            {"model_name": "XGBoost-v1", "framework": "xgboost",
             "hyperparams": {"n_estimators": 200, "max_depth": 6, "learning_rate": 0.1},
             "metrics": {"auc": 0.91, "f1": 0.87}},
            {"model_name": "XGBoost-v2", "framework": "xgboost",
             "hyperparams": {"n_estimators": 300, "max_depth": 8, "learning_rate": 0.05},
             "metrics": {"auc": 0.93, "f1": 0.89}},
            {"model_name": "XGBoost-v3", "framework": "xgboost",
             "hyperparams": {"n_estimators": 350, "max_depth": 8, "learning_rate": 0.03, "subsample": 0.9},
             "metrics": {"auc": 0.94, "f1": 0.90}},
        ],
        "experiment_schema": [
            {"experiment": "AB-Test-Checkout", "variant_count": 2,
             "variants": [{"id": "A", "weight": 0.5}, {"id": "B", "weight": 0.5}],
             "kpis": {"conversion": 0.032, "revenue_lift": 0.0}},
            {"experiment": "AB-Test-Checkout", "variant_count": 3,
             "variants": [{"id": "A", "weight": 0.34}, {"id": "B", "weight": 0.33}, {"id": "C", "weight": 0.33}],
             "kpis": {"conversion": 0.041, "revenue_lift": 1.8}},
            {"experiment": "AB-Test-Checkout-v3", "variant_count": 3,
             "variants": [{"id": "A", "weight": 0.5}, {"id": "B", "weight": 0.25}, {"id": "C", "weight": 0.25}],
             "kpis": {"conversion": 0.045, "revenue_lift": 2.3, "p_value": 0.04}},
        ],
        "code_schema": [
            {"module": "preprocessor", "language": "python",
             "entrypoint": "run()",
             "dependencies": ["pandas", "numpy"],
             "settings": {"timeout_s": 120, "retry": False}},
            {"module": "preprocessor", "language": "python",
             "entrypoint": "run()",
             "dependencies": ["pandas", "numpy", "scipy"],
             "settings": {"timeout_s": 180, "retry": True, "max_retries": 3}},
            {"module": "preprocessor-v3", "language": "python",
             "entrypoint": "run()",
             "dependencies": ["pandas", "numpy", "scipy", "pyarrow"],
             "settings": {"timeout_s": 240, "retry": True, "max_retries": 5, "log_level": "DEBUG"}},
        ],
    }

    store = {}
    states_map = [
        ("v1", "archived", False, None),
        ("v2", "archived", False, "v1"),
        ("v3", "draft",    False, None),
    ]
    for asset, plist in payloads.items():
        versions = []
        for idx, (ver, state, is_active, rb) in enumerate(states_map):
            versions.append({
                "version": ver,
                "state": state,
                "is_active": is_active,
                "uploaded_by": "admin@alan.io",
                "last_updated": f"2025-06-{10+idx:02d}",
                "rollback_id": rb,
                "payload": plist[idx],
            })
        # promote v2 to active for all asset types
        versions[1]["state"] = "active"
        versions[1]["is_active"] = True
        versions[1]["rollback_id"] = "v1"
        store[asset] = versions
    return store

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "store" not in st.session_state:
    st.session_state.store = _build_store()
if "screen" not in st.session_state:
    st.session_state.screen = "main"
if "asset_type" not in st.session_state:
    st.session_state.asset_type = "usecase_schema"
if "selected_version" not in st.session_state:
    st.session_state.selected_version = None
if "editor_mode" not in st.session_state:
    st.session_state.editor_mode = None
if "editor_payload" not in st.session_state:
    st.session_state.editor_payload = None
if "editor_source_version" not in st.session_state:
    st.session_state.editor_source_version = None

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _versions(asset=None):
    return st.session_state.store[asset or st.session_state.asset_type]

def _active_version(asset=None):
    for v in _versions(asset):
        if v["is_active"]:
            return v
    return None

def _next_version_tag(asset=None):
    nums = [int(v["version"].replace("v","")) for v in _versions(asset)]
    return f"v{max(nums)+1}"

def _go(screen, **kwargs):
    st.session_state.screen = screen
    for k, v in kwargs.items():
        st.session_state[k] = v

def _flatten_payload(payload):
    """Convert a nested dict/list payload into a list of (key, value_str) rows for form display."""
    rows = []
    for k, v in payload.items():
        if isinstance(v, (dict, list)):
            rows.append((k, json.dumps(v, indent=2)))
        else:
            rows.append((k, str(v)))
    return rows

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ALAN ADMIN PORTAL")
    st.divider()
    st.markdown("**Logged In User**")
    st.text("admin@alan.io")
    st.text("Role: Super Admin")
    st.divider()

    prev = st.session_state.asset_type
    asset = st.selectbox("Asset Type", [
        "usecase_schema", "model_schema", "experiment_schema", "code_schema"
    ], index=["usecase_schema","model_schema","experiment_schema","code_schema"].index(prev))
    if asset != prev:
        st.session_state.asset_type = asset
        _go("main", selected_version=None, editor_mode=None, editor_payload=None)
        st.rerun()

# ---------------------------------------------------------------------------
# MAIN SCREEN
# ---------------------------------------------------------------------------
if st.session_state.screen == "main":
    st.markdown(f"## {st.session_state.asset_type.replace('_',' ').title()}")

    active = _active_version()

    # Active version banner + Clone + Rollback
    if active:
        st.markdown(
            f'<div class="active-banner"><h3>Active Version: {active["version"]}'
            f' &mdash; last updated {active["last_updated"]}</h3></div>',
            unsafe_allow_html=True,
        )

        # Rollback dialog (must be defined before the button that calls it)
        @st.dialog("Confirm Rollback")
        def _rollback_dialog():
            if not active.get("rollback_id"):
                st.warning("No previous active version to rollback to.")
                return
            st.write(f"Rollback active from **{active['version']}** to **{active['rollback_id']}**?")
            if st.button("Confirm Rollback", key="rb_confirm"):
                target_id = active["rollback_id"]
                for v in _versions():
                    if v["version"] == target_id:
                        v["state"] = "active"
                        v["is_active"] = True
                    if v["version"] == active["version"]:
                        v["state"] = "archived"
                        v["is_active"] = False
                st.success("Rollback successful.")
                time.sleep(1.5)
                st.rerun()

        c1, c2, c3 = st.columns([1, 1, 4])
        with c1:
            if st.button("Clone Active Schema"):
                _go("editor", editor_mode="clone",
                     editor_payload=copy.deepcopy(active["payload"]),
                     editor_source_version=active["version"])
                st.rerun()
        with c2:
            if st.button("Rollback"):
                _rollback_dialog()

    # --- Version History Table ---
    st.markdown("### Version History")
    versions = _versions()
    display = []
    for v in versions:
        display.append({
            "Version": v["version"],
            "State": v["state"],
            "Active": v["is_active"],
            "Uploaded By": v["uploaded_by"],
            "Last Updated": v["last_updated"],
        })
    df = pd.DataFrame(display)
    event = st.dataframe(df, on_select="rerun", selection_mode="single-row",
                         use_container_width=True, hide_index=True)

    sel_rows = event.selection.rows if event.selection else []

    if sel_rows:
        chosen_idx = sel_rows[0]
        chosen = versions[chosen_idx]
        st.info(f"Selected: **{chosen['version']}** ({chosen['state']})")
        if st.button("View Schema"):
            _go("viewer", selected_version=chosen["version"])
            st.rerun()


# ---------------------------------------------------------------------------
# VIEWER SCREEN
# ---------------------------------------------------------------------------
elif st.session_state.screen == "viewer":
    ver_id = st.session_state.selected_version
    record = None
    for v in _versions():
        if v["version"] == ver_id:
            record = v
            break
    if not record:
        st.error("Version not found.")
        if st.button("Back to Main"):
            _go("main")
            st.rerun()
        st.stop()

    if st.button("Back to Main"):
        _go("main")
        st.rerun()

    st.markdown(f"## Viewer  --  {st.session_state.asset_type.replace('_',' ').title()} / {record['version']}")

    # Metadata card
    st.markdown(
        f'<div class="meta-card">'
        f'<b>Uploaded by:</b> {record["uploaded_by"]} &nbsp;|&nbsp; '
        f'<b>Last Updated:</b> {record["last_updated"]} &nbsp;|&nbsp; '
        f'<b>State:</b> {record["state"]}</div>',
        unsafe_allow_html=True,
    )

    # Form-like read-only view (no st.json)
    st.markdown("### Schema Payload")
    payload = record["payload"]
    for key, val in payload.items():
        if isinstance(val, (dict, list)):
            # Render nested structures as disabled data_editor tables
            st.markdown(f"**{key}**")
            if isinstance(val, dict):
                nested_df = pd.DataFrame([val])
            else:  # list
                if val and isinstance(val[0], dict):
                    nested_df = pd.DataFrame(val)
                else:
                    nested_df = pd.DataFrame({"values": val})
            st.data_editor(nested_df, disabled=True, use_container_width=True,
                           hide_index=True, key=f"view_{key}")
        else:
            st.text_input(key, value=str(val), disabled=True, key=f"view_{key}")

    # Download
    st.download_button(
        "Download Schema (JSON)",
        data=json.dumps({"version": record["version"], "payload": record["payload"]}, indent=2),
        file_name=f"{st.session_state.asset_type}_{record['version']}.json",
        mime="application/json",
    )

    # State-based actions
    if record["state"] == "draft":
        if st.button("Edit Draft"):
            _go("editor", editor_mode="edit",
                 editor_payload=copy.deepcopy(record["payload"]),
                 editor_source_version=record["version"])
            st.rerun()

# ---------------------------------------------------------------------------
# EDITOR SCREEN
# ---------------------------------------------------------------------------
elif st.session_state.screen == "editor":
    mode = st.session_state.editor_mode  # "clone" or "edit"
    payload = st.session_state.editor_payload
    source_ver = st.session_state.editor_source_version

    if st.button("Cancel"):
        _go("main" if mode == "clone" else "viewer")
        st.rerun()

    label = "Clone from Active" if mode == "clone" else f"Edit Draft {source_ver}"
    st.markdown(f"## Editor  --  {label}")

    # Editable form using data_editor per payload key
    edited_payload = {}
    for key, val in payload.items():
        st.markdown(f"**{key}**")
        if isinstance(val, dict):
            nested_df = pd.DataFrame([val])
            edited_df = st.data_editor(nested_df, num_rows="dynamic",
                                       use_container_width=True, hide_index=True,
                                       key=f"edit_{key}")
            # Convert back to dict (first row)
            if len(edited_df) > 0:
                edited_payload[key] = edited_df.iloc[0].to_dict()
            else:
                edited_payload[key] = {}
        elif isinstance(val, list):
            if val and isinstance(val[0], dict):
                nested_df = pd.DataFrame(val)
            else:
                nested_df = pd.DataFrame({"values": val})
            edited_df = st.data_editor(nested_df, num_rows="dynamic",
                                       use_container_width=True, hide_index=True,
                                       key=f"edit_{key}")
            if val and isinstance(val[0], dict):
                edited_payload[key] = edited_df.to_dict(orient="records")
            else:
                edited_payload[key] = edited_df["values"].tolist()
        else:
            new_val = st.text_input(key, value=str(val), key=f"edit_{key}")
            # Attempt to preserve type
            if isinstance(val, (int, float)):
                try:
                    new_val = type(val)(new_val)
                except ValueError:
                    pass
            edited_payload[key] = new_val

    st.divider()

    # --- Submit dialog ---
    @st.dialog("Confirm Submit")
    def _submit_dialog():
        st.write("Promote this version to **active**? The current active version will be archived.")
        if st.button("Confirm Submit", key="submit_confirm"):
            versions = _versions()
            prev_active = _active_version()
            if mode == "clone":
                new_tag = _next_version_tag()
                new_rec = {
                    "version": new_tag,
                    "state": "active",
                    "is_active": True,
                    "uploaded_by": "admin@alan.io",
                    "last_updated": "2025-06-15",
                    "rollback_id": prev_active["version"] if prev_active else None,
                    "payload": edited_payload,
                }
                versions.append(new_rec)
            else:
                # edit mode — promote existing draft
                for v in versions:
                    if v["version"] == source_ver:
                        v["payload"] = edited_payload
                        v["state"] = "active"
                        v["is_active"] = True
                        v["rollback_id"] = prev_active["version"] if prev_active else None
                        break
            # Archive previous active
            if prev_active:
                for v in versions:
                    if v["version"] == prev_active["version"] and v["version"] != (source_ver if mode == "edit" else ""):
                        v["state"] = "archived"
                        v["is_active"] = False
            st.balloons()
            st.success("Version promoted to active.")
            time.sleep(1.5)
            _go("main", editor_mode=None, editor_payload=None)
            st.rerun()

    # Action buttons
    b1, b2 = st.columns(2)
    with b1:
        if st.button("Save", use_container_width=True):
            versions = _versions()
            if mode == "clone":
                new_tag = _next_version_tag()
                versions.append({
                    "version": new_tag,
                    "state": "draft",
                    "is_active": False,
                    "uploaded_by": "admin@alan.io",
                    "last_updated": "2025-06-15",
                    "rollback_id": None,
                    "payload": edited_payload,
                })
                st.success(f"Saved as new draft {new_tag}.")
            else:
                for v in versions:
                    if v["version"] == source_ver:
                        v["payload"] = edited_payload
                        break
                st.success(f"Draft {source_ver} updated.")
            time.sleep(1.5)
            _go("main", editor_mode=None, editor_payload=None)
            st.rerun()
    with b2:
        if st.button("Submit", use_container_width=True):
            _submit_dialog()
