import streamlit as st
import pandas as pd
import os

st.title("📚 Library Management - Accession Number Search")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your dataset (CSV, Excel, TSV, etc.)", 
    type=["csv", "xlsx", "xls", "tsv"]
)

if uploaded_file:
    # Read file depending on type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith(".tsv"):
        df = pd.read_csv(uploaded_file, sep="\t")
    else:
        st.error("Unsupported file format.")
        st.stop()

    st.success("✅ File loaded successfully!")
    st.write("### Preview of Data", df.head())

    # Standardize column names (remove spaces, lowercase for safety)
    df.columns = df.columns.str.strip().str.replace(" ", "_").str.replace(".", "")

    # Input accession number
    accession_no_input = st.text_input("Enter Accession Number:")

    if accession_no_input:
        # Make it always 6 digits
        if len(accession_no_input) == 5:
            accession_no = "0" + accession_no_input
        elif len(accession_no_input) == 4:
            accession_no = "00" + accession_no_input
        elif len(accession_no_input) == 3:
            accession_no = "000" + accession_no_input
        else:
            accession_no = accession_no_input  # already 6 digits
        result = df[df["Acc_No"].astype(str) == accession_no]

        if not result.empty:
            st.subheader("Book Details Found:")
            st.write(result)

            # Get Title and count copies
            title = result["Ttitle"].values[0]  # assuming typo Ttitle
            total_copies = df[df["Ttitle"] == title].shape[0]

            # Add no_of_copies column
            result = result.copy()
            result["no_of_copies"] = total_copies

            st.info(f"📖 The book '{title}' has **{total_copies} copies** in the library.")
            st.write(result)

            # Extra fields
            rack_location = st.text_input("Enter Rack Location:")
            student_rating = st.number_input("Enter Student Rating (1-5)", min_value=1, max_value=5, step=1)
            teacher_rating = st.number_input("Enter Teacher Rating (1-5)", min_value=1, max_value=5, step=1)

            if st.button("Save Record"):
                updated_row = result.copy()
                updated_row["RackLocation"] = rack_location
                updated_row["StudentRating"] = student_rating
                updated_row["TeacherRating"] = teacher_rating

                # Save into new CSV
                OUTPUT_FILE = "library_records_updated.csv"
                if not os.path.exists(OUTPUT_FILE):
                    updated_row.to_csv(OUTPUT_FILE, index=False)
                else:
                    updated_row.to_csv(OUTPUT_FILE, mode="a", header=False, index=False)

                st.success(f"✅ Record saved to {OUTPUT_FILE}")

                # Reload updated CSV
                updated_df = pd.read_csv(OUTPUT_FILE)

                # Download button
                st.download_button(
                    label="📥 Download Updated CSV",
                    data=updated_df.to_csv(index=False).encode("utf-8"),
                    file_name="library_records_updated.csv",
                    mime="text/csv"
                )

        else:
            st.error("❌ No record found for this accession number.")
