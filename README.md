The Complete Master Prompt (v4)
Role: You are an expert Python Streamlit developer.

Task: Build a strictly functional, highly structured UI skeleton (Proof of Concept) for "ALAN ADMIN PORTAL". Do not use emojis. The code must be concise, dependency-light (use ONLY native Streamlit and Pandas, absolutely no streamlit-aggrid), and feature a strict White and Red color theme designed for business users. Import time for small routing delays.

Context & Mock Data (State Management):
Initialize st.session_state with mock data. There is no backend yet.

Asset Types: usecase_schema, model_schema, experiment_schema, code_schema.

Tabular Data Mockup: Create a list of dictionaries for versions representing three strict states: active, archived, and draft.

Only ONE version per asset type can have is_active: True.

Include a rollback_id key. For the active version, set this to the version string of the prior active schema (e.g., if v4 is active, "rollback_id": "v2"). Do not display this column in the UI table.

Version-Specific Nested JSON: Embed a unique mock JSON payload inside each version dictionary. Ensure this JSON includes nested structures (like a dictionary of hyperparameters or an array of features).

App Structure & Routing:
Use st.session_state to manage routing between 3 screens: Main, Viewer, and Editor.

Component Requirements:

1. Sidebar:

Display static "Logged In User" details.

Dropdown menu to toggle between the 4 Asset Types. Changing this resets the app state to the Main Screen.

2. Main Screen (Tabular View, Clone & Rollback):

Display the currently active schema version prominently at the top.

Direct Clone Action: Next to the active version display, include a prominent "Clone Active Schema" button. When clicked, capture the active schema's payload, set editor_mode = "clone", and route immediately to the Editor Screen. This Clone button is ONLY for the active schema.

Rollback Logic: Place a "Rollback" button near the Active Version display. When clicked, open an st.dialog asking "Confirm Rollback to previous active version?". When confirmed, read the rollback_id, set that target version to active, and set the current active to archived. Show a success message, time.sleep(1.5), and st.rerun().

Display the version history using native Streamlit selection: st.dataframe(df, on_select="rerun", selection_mode="single-row").

Capture the user's selection directly from the dataframe state. Provide a "View Schema" button that updates st.session_state with the selected version and transitions to the Viewer Screen.

3. Viewer Screen (Strictly Read-Only Form View):

"Back to Main" button.

Display metadata (Uploaded by, Last Updated, State).

Form-Like View: Do NOT use st.json(). Instead, render the schema payload as a read-only form. You can achieve this by passing the JSON into st.data_editor(..., disabled=True) or by looping through the keys and using st.text_input(..., disabled=True). The user must see form fields, not raw JSON text.

Download: A "Download Schema" button (simulating /download) must be available for ALL versions.

State-Based Actions:

There is NO Clone button on this page.

If state == "draft": Show an "Edit Draft" button. Routes to Editor Screen with state flag editor_mode = "edit".

If state == "archived" or state == "active": Show NO editing buttons here.

4. Editor Screen (Clone vs. Edit Workflows):

"Cancel" button to return to the Main or Viewer screen.

Dynamic Editing: Pass the schema payload directly into st.data_editor (with num_rows="dynamic") so the user can edit the nested data directly in a pre-filled, interactive form.

Action Buttons: Display two primary buttons side-by-side: "Save" and "Submit".

"Save" Logic (Draft Update/Create - Simulates /save):

If editor_mode == "clone": Generates a new version increment (e.g., v4), saves the edited schema to the store with state: "draft" and is_active: False.

If editor_mode == "edit": Overwrites the current draft's schema payload in the store. State remains draft.

After saving, show a success toast/message, time.sleep(1.5), and route to Main.

"Submit" Logic (Promote to Active - Simulates /submit):

Opens an st.dialog for confirmation.

Upon confirmation, save the payload, change its state to active (is_active: True), set the previous active version to archived (is_active: False), update the new active version's rollback_id to point to the archived version, show st.balloons(), time.sleep(1.5), and route to Main.

"""Viewer screen: read-only schema display with metadata and download."""

import copy
import json
import time

import streamlit as st

from components.schema_form import render_schema_form
from state import _active_version, _go, _versions


def render_viewer_screen():
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

    st.markdown(
        f"## Viewer  --  "
        f"{st.session_state.asset_type.replace('_', ' ').title()} / {record['version']}"
    )

    # Metadata card
    st.markdown(
        f'<div class="meta-card">'
        f'<b>Uploaded by:</b> {record["uploaded_by"]} &nbsp;|&nbsp; '
        f'<b>Last Updated:</b> {record["last_updated"]} &nbsp;|&nbsp; '
        f'<b>State:</b> {record["state"]}</div>',
        unsafe_allow_html=True,
    )

    # ------------------------------------------------------------------
    # Action bar: buttons ABOVE the schema so they are always visible
    # ------------------------------------------------------------------

    # Submit dialog — defined at top level of function so Streamlit
    # registers it on every rerun regardless of state
    @st.dialog("Confirm Submit")
    def _viewer_submit_dialog():
        st.write(
            f"Promote **{record['version']}** to active? "
            "The current active version will be archived."
        )
        if st.button("Confirm Submit", key="viewer_submit_confirm"):
            versions = _versions()
            prev_active = _active_version()
            for v in versions:
                if v["version"] == record["version"]:
                    v["state"] = "active"
                    v["is_active"] = True
                    v["rollback_id"] = (
                        prev_active["version"] if prev_active else None
                    )
                    v["last_updated"] = time.strftime("%Y-%m-%d")
                    break
            # Ensure single active
            for v in versions:
                if v["is_active"] and v["version"] != record["version"]:
                    v["state"] = "archived"
                    v["is_active"] = False
            st.balloons()
            st.success("Version promoted to active.")
            time.sleep(1.5)
            _go("main")
            st.rerun()

    # Layout: Download always | Draft also gets Edit + Submit
    if record["state"] == "draft":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "Download Schema (JSON)",
                data=json.dumps(
                    {"version": record["version"], "payload": record["payload"]},
                    indent=2,
                ),
                file_name=f"{st.session_state.asset_type}_{record['version']}.json",
                mime="application/json",
                use_container_width=True,
            )
        with c2:
            if st.button("Edit Draft", use_container_width=True):
                _go(
                    "editor",
                    editor_mode="edit",
                    editor_payload=copy.deepcopy(record["payload"]),
                    editor_source_version=record["version"],
                )
                st.rerun()
        with c3:
            if st.button("Submit", use_container_width=True):
                _viewer_submit_dialog()
    else:
        # Active / Archived — download only
        st.download_button(
            "Download Schema (JSON)",
            data=json.dumps(
                {"version": record["version"], "payload": record["payload"]},
                indent=2,
            ),
            file_name=f"{st.session_state.asset_type}_{record['version']}.json",
            mime="application/json",
        )

    st.divider()

    # ------------------------------------------------------------------
    # Schema payload — read-only form, below the action bar
    # ------------------------------------------------------------------
    st.markdown("### Schema Payload")
    render_schema_form(record["payload"], editable=False, key_prefix="view")
