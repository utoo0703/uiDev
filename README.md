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

https://legendary-broccoli-7x5pr499pxjhp65v-8000.app.github.dev/
