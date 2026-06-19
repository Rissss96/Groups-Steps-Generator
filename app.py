import streamlit as st
import pandas as pd
from io import BytesIO


st.set_page_config(page_title="Groups Steps Generator", layout="wide")
st.title("Groups Steps Generator")
st.caption("Generate New_Group_Definitions.xlsx and New_Group_Assignments.xlsx from your staged construction inputs.")


with st.sidebar:
    st.header("Inputs")
    case_file = st.file_uploader("Case - Static 6 - Nonlinear Stage Data.xlsx", type=["xlsx"])
    def_file = st.file_uploader("Groups 1 - Definitions.xlsx", type=["xlsx"])
    asg_file = st.file_uploader("Groups 2 - Assignments.xlsx", type=["xlsx"])

st.subheader("Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    default_case = "CSA_MS_v14"
    staged_construction_case = st.text_input("Staged construction case", value=default_case)

with col2:
    step_start = st.number_input("Step start", min_value=1, value=1, step=1)

with col3:
    step_end = st.number_input("Step end", min_value=1, value=74, step=1)

color_name = st.text_input("Output color (exact name used by your model)", value="DarkMagenta")



def build_outputs(df_static_6, df_group_def, df_group_assignments, staged_case, steps, color):
    # ---- 1) Build df_steps_and_groups ----
    rows = []
    for step in steps:
        added_groups = df_static_6.loc[
            (df_static_6.index == staged_case)
            & (df_static_6["Stage"] <= step)
            & (df_static_6["Operation"] == "Add Structure")
        ]["ObjName"].dropna().unique().tolist()

        removed_groups = df_static_6.loc[
            (df_static_6.index == staged_case)
            & (df_static_6["Stage"] <= step)
            & (df_static_6["Operation"] == "Remove Structure")
        ]["ObjName"].dropna().unique().tolist()

        existing_groups = [g for g in added_groups if g not in removed_groups]

        rows.append({"Step": f"W_Step_{step}", "Groups": existing_groups})

    df_steps_and_groups = pd.DataFrame(rows)

    # ---- 2) Build New_Group_Definitions ----
    if "All" not in df_group_def.index:
        raise ValueError("Template row 'All' not found in Groups 1 - Definitions.xlsx")

    base_row = df_group_def.loc["All"].copy()
    new_rows = {}

    for step in steps:
        group_name = f"W_Step_{step}"
        new_row = base_row.copy()
        new_row["Color"] = color
        new_rows[group_name] = new_row

    df_new_groups = pd.DataFrame.from_dict(new_rows, orient="index")
    df_new_groups.index.name = "GroupName"

    # ---- 3) Build New_Group_Assignments ----
    df_expanded = df_steps_and_groups.explode("Groups").rename(columns={"Groups": "GroupName"})

    df_group = df_group_assignments.reset_index()
    result = df_expanded.merge(df_group, on="GroupName", how="left")
    result = result[["Step", "ObjectType", "ObjectLabel"]]

    return df_steps_and_groups, df_new_groups, result


if st.button("Generate", type="primary"):
    if not (case_file and def_file and asg_file):
        st.error("Please upload all three Excel files first.")
    elif step_end < step_start:
        st.error("Step end must be greater than or equal to Step start.")
    else:
        try:
            # Read exactly as in notebook
            df_static_6 = pd.read_excel(case_file, header=1, index_col=0)
            df_group_def = pd.read_excel(def_file, header=1, index_col=0)
            df_group_assignments = pd.read_excel(asg_file, header=1, index_col=0)

            if staged_construction_case not in df_static_6.index:
                st.error(
                    f"Case '{staged_construction_case}' not found. "
                    f"Available examples: {', '.join(map(str, pd.Series(df_static_6.index).dropna().unique()[:10]))}"
                )
            else:
                staged_construction_steps = list(range(int(step_start), int(step_end) + 1))

                df_steps_and_groups, df_new_groups, result = build_outputs(
                    df_static_6,
                    df_group_def,
                    df_group_assignments,
                    staged_construction_case,
                    staged_construction_steps,
                    color_name,
                )

                st.success("Done.")

                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Generated steps", len(df_steps_and_groups))
                    st.metric("Definitions rows", len(df_new_groups))
                with c2:
                    st.metric("Assignments rows", len(result))

                st.subheader("Preview: Steps and Groups")
                st.dataframe(df_steps_and_groups, use_container_width=True, height=260)

                st.subheader("Preview: New Group Definitions")
                st.dataframe(df_new_groups, use_container_width=True, height=260)

                st.subheader("Preview: New Group Assignments")
                st.dataframe(result, use_container_width=True, height=260)

                # In-memory Excel for download
                buf_defs = BytesIO()
                with pd.ExcelWriter(buf_defs, engine="openpyxl") as writer:
                    df_new_groups.to_excel(writer, sheet_name="Sheet1")
                buf_defs.seek(0)

                buf_asg = BytesIO()
                with pd.ExcelWriter(buf_asg, engine="openpyxl") as writer:
                    result.to_excel(writer, index=False, sheet_name="Sheet1")
                buf_asg.seek(0)

                d1, d2 = st.columns(2)
                with d1:
                    st.download_button(
                        "Download New_Group_Definitions.xlsx",
                        data=buf_defs,
                        file_name="New_Group_Definitions.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                with d2:
                    st.download_button(
                        "Download New_Group_Assignments.xlsx",
                        data=buf_asg,
                        file_name="New_Group_Assignments.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )

        except Exception as e:
            st.exception(e)


st.markdown("---")
st.markdown(
    """
**Instructions**

* Upload the required Excel files.
* Group definitions are generated based on the group named **"All"**. This group must exist in the model. 
* The **`W_Step_n`** groups are automatically generated from the **Add Structure** and **Remove Structure** operations defined in the **"Case - Static 6 - Nonlinear Stage Data"** Excel sheet.
* After the process is completed, download the generated **Group Definitions** and **Group Assignments** files shown below.
* Import these files into SAP2000 using the **Interactive Database Editing** feature.

"""
)
