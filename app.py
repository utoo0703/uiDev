import streamlit as st
import pandas as pd
from datetime import datetime
import copy
import time

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="ALAN ADMIN PORTAL", layout="wide")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background:#ffffff; }
    [data-testid="stSidebar"] { background:#f9f9f9; border-right:2px solid #cc0000; }
    .stButton > button { background:#cc0000 !important; color:#fff !important;
        border:none !important; border-radius:4px !important; font-weight:600 !important; }
    .stButton > button:hover { background:#990000 !important; }
    h1, h2, h3 { color:#cc0000 !important; }
    .active-badge { background:#cc0000; color:#fff; padding:2px 10px;
        border-radius:12px; font-size:0.78rem; font-weight:700; }
    .meta-block { background:#fafafa; border-left:3px solid #cc0000;
        padding:10px 16px; border-radius:0 6px 6px 0; margin-bottom:12px; }
    .meta-row { display:flex; gap:40px; flex-wrap:wrap; }
    .meta-item { display:flex; flex-direction:column; }
    .meta-label { font-size:0.72rem; font-weight:700; color:#999;
        text-transform:uppercase; letter-spacing:0.04em; }
    .meta-value { font-size:0.9rem; font-weight:600; color:#222; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
ASSET_TYPES = ["usecase_schema", "model_schema", "experiment_schema", "code_schema"]

INITIAL_VERSIONS = [
    {
        "version": "v1", "state": "archived", "is_active": False,
        "uploaded_by": "j.smith",
        "last_uploaded": "2024-11-01", "last_updated_timestamp": "2024-11-02 10:00",
        "schema": {
            "name": "alan_model_v1",
            "version": 1,
            "enabled": False,
            "threshold": 0.75,
            "hyperparameters": {"learning_rate": 0.001, "epochs": 50, "batch_size": 32},
            "features": ["age", "income", "tenure"],
            "metadata": {"created_by": "j.smith", "reviewed": False},
        },
    },
    {
        "version": "v2", "state": "active", "is_active": True,
        "uploaded_by": "a.patel",
        "last_uploaded": "2025-01-15", "last_updated_timestamp": "2025-01-16 09:30",
        "schema": {
            "name": "alan_model_v2",
            "version": 2,
            "enabled": True,
            "threshold": 0.85,
            "hyperparameters": {"learning_rate": 0.0005, "epochs": 100, "batch_size": 64},
            "features": ["age", "income", "tenure", "churn_score"],
            "metadata": {"created_by": "a.patel", "reviewed": True},
        },
    },
    {
        "version": "v3", "state": "draft", "is_active": False,
        "uploaded_by": "r.chen",
        "last_uploaded": "2025-03-01", "last_updated_timestamp": "2025-03-02 14:20",
        "schema": {
            "name": "alan_model_v3",
            "version": 3,
            "enabled": False,
            "threshold": 0.90,
            "hyperparameters": {"learning_rate": 0.0003, "epochs": 150, "batch_size": 128},
            "features": ["age", "income", "tenure", "churn_score", "nps_index"],
            "metadata": {"created_by": "r.chen", "reviewed": False},
        },
    },
]

# ── Session state init ────────────────────────────────────────────────────────
def _init():
    defaults = {
        "screen": "main",
        "asset_type": ASSET_TYPES[0],
        "selected_row": None,
        "validated": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if "version_store" not in st.session_state:
        st.session_state.version_store = {}
    for at in ASSET_TYPES:
        if at not in st.session_state.version_store:
            st.session_state.version_store[at] = copy.deepcopy(INITIAL_VERSIONS)

_init()

# ── Helpers ───────────────────────────────────────────────────────────────────
def go(screen, row=None):
    st.session_state.screen = screen
    st.session_state.validated = False
    if row is not None:
        st.session_state.selected_row = row
    st.rerun()

def current_versions():
    return st.session_state.version_store[st.session_state.asset_type]

def next_version_tag(versions):
    nums = [int(v["version"].lstrip("v")) for v in versions if v["version"].startswith("v")]
    return f"v{max(nums) + 1}"

def table_rows(versions):
    """Return display-safe rows (drop the nested schema dict)."""
    return [
        {k: v for k, v in ver.items() if k != "schema"}
        for ver in versions
    ]

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ALAN ADMIN PORTAL")
    st.divider()
    st.markdown("**Logged In User**")
    st.markdown("Name: `admin.user`")
    st.markdown("Role: `Administrator`")
    st.markdown("Org:  `ALAN Platform`")
    st.divider()
    chosen = st.selectbox(
        "Asset Type", ASSET_TYPES,
        index=ASSET_TYPES.index(st.session_state.asset_type),
    )
    if chosen != st.session_state.asset_type:
        st.session_state.asset_type = chosen
        st.session_state.screen = "main"
        st.session_state.selected_row = None
        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN: MAIN
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.screen == "main":
    st.title("Asset Version Manager")
    st.markdown(f"**Asset Type:** `{st.session_state.asset_type}`")

    versions = current_versions()
    active = next((r for r in versions if r["is_active"]), None)
    if active:
        st.markdown(
            f"Active Version: &nbsp;<span class='active-badge'>{active['version']}</span>",
            unsafe_allow_html=True,
        )
    st.divider()

    df = pd.DataFrame(table_rows(versions))

    # Native dataframe with single-row selection
    table_state = st.dataframe(
        df,
        on_select="rerun",
        selection_mode="single-row",
        use_container_width=True,
        hide_index=True,
        height=220,
    )

    sel_indices = table_state.selection.get("rows", [])
    if sel_indices:
        chosen_idx = sel_indices[0]
        chosen_version = versions[chosen_idx]
        st.caption(f"Selected: **{chosen_version['version']}** — {chosen_version['state']}")
        if st.button("View Schema"):
            go("viewer", chosen_version)
    else:
        st.info("Click a row to select it, then click View Schema.")

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN: VIEWER
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.screen == "viewer":
    row = st.session_state.selected_row

    st.title(f"Schema Viewer  —  {row['version']}")

    # Action bar
    col_back, col_dl, col_rb, _ = st.columns([1, 1, 1, 3])
    with col_back:
        if st.button("Back to Main"):
            go("main")
    with col_dl:
        if st.button("Download Schema"):
            st.toast("Download initiated (mock).")
    with col_rb:
        if st.button("Rollback"):
            st.toast(f"Rollback to {row['version']} simulated (mock).")

    st.divider()

    # ── Metadata block ────────────────────────────────────────────────────────
    state_color = "#cc0000" if row["state"] == "active" else "#888"
    st.markdown(
        f"""
        <div class="meta-block">
          <div class="meta-row">
            <div class="meta-item">
              <span class="meta-label">Version</span>
              <span class="meta-value">{row['version']}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">State</span>
              <span class="meta-value" style="color:{state_color};text-transform:capitalize">
                {row['state']}
              </span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Active</span>
              <span class="meta-value">{'Yes' if row['is_active'] else 'No'}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Uploaded By</span>
              <span class="meta-value">{row.get('uploaded_by', '—')}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Last Uploaded</span>
              <span class="meta-value">{row['last_uploaded']}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Last Updated</span>
              <span class="meta-value">{row['last_updated_timestamp']}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Schema JSON ───────────────────────────────────────────────────────────
    st.json(row.get("schema", {}))
    st.divider()

    is_active = bool(row.get("is_active", False))
    if is_active:
        if st.button("Edit / Clone Schema"):
            go("editor")
    else:
        st.warning("Viewing a historical version. Only the active schema can be edited.")

# ─────────────────────────────────────────────────────────────────────────────
# SCREEN: EDITOR
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.screen == "editor":
    row = st.session_state.selected_row
    versions = current_versions()
    next_tag = next_version_tag(versions)

    st.title(f"Schema Editor  —  New Version {next_tag}")
    st.markdown(
        f"Cloning **{row['version']}** — submitting will create **{next_tag}** "
        f"and promote it to active."
    )

    if st.button("Cancel"):
        go("viewer")

    st.divider()

    # ── st.data_editor on a deep clone of the version-specific schema ─────────
    schema_clone = copy.deepcopy(row.get("schema", {}))

    st.markdown("#### Edit Schema")
    st.caption(
        "Nested objects and arrays are editable inline. "
        "Add or remove rows with the controls at the bottom of the table."
    )

    edited_schema = st.data_editor(
        schema_clone,
        num_rows="dynamic",
        use_container_width=True,
        key="schema_editor",
    )

    st.divider()

    # ── Validate → reveal Submit ──────────────────────────────────────────────
    if st.button("Validate Schema"):
        if edited_schema:
            st.session_state.validated = True
            st.success("Schema validated successfully. Review the preview below before submitting.")
        else:
            st.error("Schema appears empty. Please check your edits.")

    if st.session_state.validated:
        st.markdown("#### Preview — Final Payload")
        st.json(edited_schema)

        # ── Confirmation dialog ───────────────────────────────────────────────
        @st.dialog("Confirm Promotion")
        def confirm_dialog():
            st.warning(
                f"Are you sure you want to promote **{next_tag}** to active? "
                f"The current active version (**{row['version']}**) will be archived."
            )
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes, promote it", key="confirm_yes"):
                    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                    today  = datetime.now().strftime("%Y-%m-%d")
                    for v in versions:
                        v["is_active"] = False
                        if v["state"] == "active":
                            v["state"] = "archived"
                    versions.append({
                        "version": next_tag,
                        "state": "active",
                        "is_active": True,
                        "uploaded_by": "admin.user",
                        "last_uploaded": today,
                        "last_updated_timestamp": now_ts,
                        "schema": copy.deepcopy(edited_schema),
                    })
                    st.session_state.version_store[st.session_state.asset_type] = versions
                    st.session_state.validated = False
                    st.rerun()
            with col_no:
                if st.button("Cancel", key="confirm_no"):
                    st.rerun()

        st.divider()
        if st.button("Submit as New Version"):
            confirm_dialog()

        # ── Post-dialog routing: if new version was just saved, go to main ────
        updated = current_versions()
        if any(v["version"] == next_tag for v in updated):
            st.success(f"Version **{next_tag}** saved and set as active.")
            st.balloons()
            time.sleep(1.5)
            go("main")