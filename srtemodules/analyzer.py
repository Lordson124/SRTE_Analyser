import os
import numpy as np
import pandas as pd
from srtemodules.data_standardizer import standardize_lecturer_data # Import the new function

def analyze(df):
    """
    Performs SRTE analysis, including lecturer data standardization and categorization
    by school.

    Args:
        df (pd.DataFrame): The raw input DataFrame containing SRTE data.

    Returns:
        dict: A dictionary where keys are school names (e.g., "SMS", "VASSS")
              and values are DataFrames containing the analyzed results for that school.
    """
    # --- STEP 1: Standardize Lecturer Data ---
    # Call the standardization function first.
    # It will use 'Lecturer database.xlsx - Sheet1.csv' internally.
    # Pass a copy of the DataFrame to avoid modifying the original 'df' outside this function's scope
    # if 'df' is used elsewhere before 'analyze'.
    print("Standardizing lecturer names and affiliations...")
    standardized_df, unmatched_lecturers = standardize_lecturer_data(df.copy())

    if unmatched_lecturers:
        print("\n--- WARNING: UNMATCHED LECTURERS FOUND ---")
        print("The following lecturer names from the raw data were not found in the lecturer database:")
        for name in sorted(unmatched_lecturers):
            print(f"- {name}")
        print("Please consider adding them or their aliases to your 'Lecturer database.xlsx - Sheet1.csv' file.")
        print("-------------------------------------------\n")
    else:
        print("All lecturer names standardized successfully or no new names found.")


    # --- STEP 2: Continue with existing SRTE analysis using the standardized DataFrame ---
    srte = standardized_df.copy() # Use the standardized DataFrame for all subsequent operations

    # Your existing column definitions and drops:
    # These sections will now operate on the DataFrame where 'Lecturer Name',
    # 'Department', and 'School' (if present in original 'df') have been standardized.

    tm = srte.columns[2:9]
    ta = srte.columns[9:14]
    cm = srte.columns[14:18]
    ifs = srte.columns[18:23]
    pta = srte.columns[23:25]

    tm = srte.drop(
        [
            "TA8", "TA9", "TA10", "TA11", "TA12", "CM13", "CM14", "CM15", "CM16",
            "IF17", "IF18", "IF19", "IF20", "IF21", "PTA22", "PTA23",
        ],
        axis="columns",
    )

    ta = srte.drop(
        [
            "TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7", "CM13", "CM14", "CM15", "CM16",
            "IF17", "IF18", "IF19", "IF20", "IF21", "PTA22", "PTA23",
        ],
        axis="columns",
    )

    cm = srte.drop(
        [
            "TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7", "TA8", "TA9", "TA10", "TA11", "TA12",
            "IF17", "IF18", "IF19", "IF20", "IF21", "PTA22", "PTA23",
        ],
        axis="columns",
    )

    ifs = srte.drop(
        [
            "TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7", "TA8", "TA9", "TA10", "TA11", "TA12",
            "CM13", "CM14", "CM15", "CM16", "PTA22", "PTA23",
        ],
        axis="columns",
    )

    pta = srte.drop(
        [
            "TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7", "TA8", "TA9", "TA10", "TA11", "TA12",
            "CM13", "CM14", "CM15", "CM16", "IF17", "IF18", "IF19", "IF20", "IF21",
        ],
        axis="columns",
    )

    # These groupings will now use the standardized 'Lecturer Name'
    tm = tm.groupby(["Course Title", "Lecturer Name"]).mean()
    tm["TM Overall"] = tm.apply(np.mean, axis=1)
    tm["TM Overall"] = tm["TM Overall"].round(2)
    tm["TM %"] = (tm["TM Overall"] / 5) * 100
    tm["TM %"] = tm["TM %"].round(1)
    tm = tm.drop(["TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7"], axis="columns")

    ta = ta.groupby(["Course Title", "Lecturer Name"]).mean()
    ta["TA Overall"] = ta.apply(np.mean, axis=1)
    ta["TA Overall"] = ta["TA Overall"].round(2)
    ta["TA %"] = (ta["TA Overall"] / 5) * 100
    ta["TA %"] = ta["TA %"].round(1)
    ta = ta.drop(["TA8", "TA9", "TA10", "TA11", "TA12"], axis="columns")

    cm = cm.groupby(["Course Title", "Lecturer Name"]).mean()
    cm["CM Overall"] = cm.apply(np.mean, axis=1)
    cm["CM Overall"] = cm["CM Overall"].round(2)
    cm["CM %"] = (cm["CM Overall"] / 5) * 100
    cm["CM %"] = cm["CM %"].round(1)
    cm = cm.drop(["CM13", "CM14", "CM15", "CM16"], axis="columns")

    ifs = ifs.groupby(["Course Title", "Lecturer Name"]).mean()
    ifs["IF Overall"] = ifs.apply(np.mean, axis=1)
    ifs["IF Overall"] = ifs["IF Overall"].round(2)
    ifs["IF %"] = (ifs["IF Overall"] / 5) * 100
    ifs["IF %"] = ifs["IF %"].round(1)
    ifs = ifs.drop(["IF17", "IF18", "IF19", "IF20", "IF21"], axis="columns")

    pta = pta.groupby(["Course Title", "Lecturer Name"]).mean()
    pta["PTA Overall"] = (pta.apply(np.mean, axis=1) / 100) * 5
    pta["PTA Overall"] = pta["PTA Overall"].round(2)
    pta["PTA %"] = (pta["PTA Overall"] / 5) * 100
    pta["PTA %"] = pta["PTA %"].round(1)
    pta = pta.drop(["PTA22", "PTA23"], axis="columns")

    ts = (
        tm["TM Overall"]
        + ta["TA Overall"]
        + cm["CM Overall"]
        + ifs["IF Overall"]
        + pta["PTA Overall"]
    ) / 5
    tsp = (ts / 5) * 100
    pta["ES Overall"] = ts
    pta["ES Overall"] = pta["ES Overall"].round(2)
    pta["ES %"] = tsp
    pta["ES %"] = pta["ES %"].round(1)

    srt = srte.groupby(["Course Title", "Lecturer Name"]).count()
    pta["No"] = srt["TM1"]

    frame = [tm, ta, cm, ifs, pta]

    result = pd.concat(frame, axis=1, join="inner", sort=False)

    result = result.reset_index("Lecturer Name")

    # The 'School' and 'Department' columns will now be updated in 'result'
    # due to the standardization, assuming they were part of the initial 'df'
    # or you add them as part of the analysis process after standardization.
    # If not present in the original 'df', you might need to merge them back
    # into 'result' from 'standardized_df' based on 'Lecturer Name' and 'Course Title'.
    # For now, I'll assume they are handled by the initial standardization.

    def analyse_comp():
        results = {}

        # The filtering logic here will operate on the 'Course Title' index
        # This remains unchanged, as lecturer standardization doesn't directly
        # impact course titles.
        sms = result[
            (result.index.str.startswith("ACCT")) | (result.index.str.startswith("BSAD")) |
            (result.index.str.startswith("BSTA")) | (result.index.str.startswith("BMTH")) |
            (result.index.str.startswith("FNCE")) | (result.index.str.startswith("IRMA")) |
            (result.index.str.startswith("MLIS")) | (result.index.str.startswith("MIHM")) |
            (result.index.str.startswith("BSAD/MKTG")) | (result.index.str.startswith("MBIM")) |
            (result.index.str.startswith("ECONS")) | (result.index.str.startswith("MKTG")) |
            (result.index.str.startswith("AMS")) | (result.index.str.startswith("'BU-ACC")) |
            (result.index.str.startswith("BUA")) | (result.index.str.startswith("BU-BSD")) |
            (result.index.str.startswith("MCON")) | (result.index.str.startswith("MHIM")) |
            (result.index.str.startswith("BU-IRM")) | (result.index.str.startswith("BU-IRMA")) |
            (result.index.str.startswith("BU-MKT")) | (result.index.str.startswith("BU-BSD")) |
            (result.index.str.startswith("MKT")) | (result.index.str.startswith("IRM")) |
            (result.index.str.startswith("ENT")) | (result.index.str.startswith("BU-BUA")) |
            (result.index.str.startswith("BSD")) | (result.index.str.startswith("BU-FIN")) |
            (result.index.str.startswith("FIN")) | (result.index.str.startswith("IIRM"))
        ]
        if len(sms.index) != 0:
            results["SMS"] = sms

        vasss = result[
            (result.index.str.startswith("ECON")) | (result.index.str.startswith("MCOM")) |
            (result.index.str.startswith("MCBC")) | (result.index.str.startswith("MCJP")) |
            (result.index.str.startswith("MCPR")) | (result.index.str.startswith("PBAD")) |
            (result.index.str.startswith("PBMG")) | (result.index.str.startswith("PLSC")) |
            (result.index.str.startswith("IILDP")) | (result.index.str.startswith("ILDP")) |
            (result.index.str.startswith("PMBG")) | (result.index.str.startswith("SOWK")) |
            (result.index.str.startswith("CMS")) | (result.index.str.startswith("MCM")) |
            (result.index.str.startswith("BU-ILD")) | (result.index.str.startswith("BU-POL")) |
            (result.index.str.startswith("POL")) | (result.index.str.startswith("BU-ECO")) |
            (result.index.str.startswith("BU-SWK")) | (result.index.str.startswith("BU-PAD")) |
            (result.index.str.startswith("BU-CMS")) | (result.index.str.startswith("BU-MCM")) |
            (result.index.str.startswith("BU-POL")) | (result.index.str.startswith("ILD-POL")) |
            (result.index.str.startswith("BU-ILDP")) | (result.index.str.startswith("SWK")) |
            (result.index.str.startswith("SOC")) | (result.index.str.startswith("SWMP")) |
            (result.index.str.startswith("SWFC")) | (result.index.str.startswith("SWSA")) |
            (result.index.str.startswith("PBMR")) | (result.index.str.startswith("PAD")) |
            (result.index.str.startswith("BU-SOWK"))
        ]
        if len(vasss.index) != 0:
            results["VASSS"] = vasss

        cffs = result[
            (result.index.str.startswith("MAT")) | (result.index.str.startswith("LIT")) |
            (result.index.str.startswith("PHY")) | (result.index.str.startswith("CHE")) |
            (result.index.str.startswith("ECO")) | (result.index.str.startswith("BIO")) |
            (result.index.str.startswith("PPAD")) | (result.index.str.startswith("PILW")) |
            (result.index.str.startswith("CRS")) | (result.index.str.startswith("GOV")) |
            (result.index.str.startswith("ECN")) | (result.index.str.startswith("ACC")) |
            (result.index.str.startswith("BUS")) | (result.index.str.startswith("HIS")) |
            (result.index.str.startswith("AGR"))
        ]
        if len(cffs.index) != 0:
            results["CFFS"] = cffs

        eah = result[
            (result.index.str.startswith("BEDU")) | (result.index.str.startswith("CRLS")) |
            (result.index.str.startswith("CRSL")) | (result.index.str.startswith("CHMN")) |
            (result.index.str.startswith("CHIS")) | (result.index.str.startswith("EDPA")) |
            (result.index.str.startswith("EDUC")) | (result.index.str.startswith("ENGL")) |
            (result.index.str.startswith("FRCH")) | (result.index.str.startswith("GCPY")) |
            (result.index.str.startswith("GEDS")) | (result.index.str.startswith("HIST")) |
            (result.index.str.startswith("MUSC")) | (result.index.str.startswith("RELS")) |
            (result.index.str.startswith("RELG")) | (result.index.str.startswith("EGLT")) |
            (result.index.str.startswith("BIBL")) | (result.index.str.startswith("NTST")) |
            (result.index.str.startswith("OTST")) | (result.index.str.startswith("THST")) |
            (result.index.str.startswith("FREN")) | (result.index.str.startswith("BU/GST")) |
            (result.index.str.startswith("BU-GST")) | (result.index.str.startswith("BU-CRS")) |
            (result.index.str.startswith("BU-GEDS")) | (result.index.str.startswith("PRDE")) |
            (result.index.str.startswith("GES")) | (result.index.str.startswith("GST")) |
            (result.index.str.startswith("GET")) | (result.index.str.startswith("BU-HIS")) |
            (result.index.str.startswith("MUS")) | (result.index.str.startswith("PSY")) |
            (result.index.str.startswith("BU-LIT")) | (result.index.str.startswith("BU-MUS")) |
            (result.index.str.startswith("FAC")) | (result.index.str.startswith("BU-GST")) |
            (result.index.str.startswith("CGPY")) | (result.index.str.startswith("RELG"))
        ]
        if len(eah.index) != 0:
            results["EAH"] = eah

        pah = result[
            (result.index.str.startswith("MLSC")) | (result.index.str.startswith("PHSC")) |
            (result.index.str.startswith("MLSB")) | (result.index.str.startswith("MLSH")) |
            (result.index.str.startswith("MLSM")) | (result.index.str.startswith("MLSP")) |
            (result.index.str.startswith("PHFC")) | (result.index.str.startswith("PHMP")) |
            (result.index.str.startswith("PHEP")) | (result.index.str.startswith("PHNT")) |
            (result.index.str.startswith("PHPR")) | (result.index.str.startswith("PHEH")) |
            (result.index.str.startswith("ENGL/EGLT")) | (result.index.str.startswith("PHHP")) |
            (result.index.str.startswith("MLS")) | (result.index.str.startswith("BU-MLS"))
        ]
        if len(pah.index) != 0:
            results["PAH"] = pah

        nursing = result[
            (result.index.str.startswith("NRSG")) | (result.index.str.startswith("COS")) |
            (result.index.str.startswith("NSC")) | (result.index.str.startswith("BU-NSC")) |
            (result.index.str.startswith("RSG"))
        ]
        if len(nursing.index) != 0:
            results["NURSING"] = nursing

        ces = result[
            (result.index.str.startswith("COSC")) | (result.index.str.startswith("INSY")) |
            (result.index.str.startswith("ITGY")) | (result.index.str.startswith("ELCT")) |
            (result.index.str.startswith("SENG")) | (result.index.str.startswith("IFT")) |
            (result.index.str.startswith("SEN")) | (result.index.str.startswith("BU-CSC")) |
            (result.index.str.startswith("BU-SEN")) | (result.index.str.startswith("INS")) |
            (result.index.str.startswith("BU-IFT")) | (result.index.str.startswith("CYB")) |
            (result.index.str.startswith("BU-ENG")) | (result.index.str.startswith("BU-CSC")) |
            (result.index.str.startswith("BU-SEN"))
        ]
        if len(ces.index) != 0:
            results["CES"] = ces

        sat = result[
            (result.index.str.startswith("AGRE")) | (result.index.str.startswith("AGEM")) |
            (result.index.str.startswith("AGRY")) | (result.index.str.startswith("AGRI")) |
            (result.index.str.startswith("ANSC")) | (result.index.str.startswith("CRPT")) |
            (result.index.str.startswith("BIOL")) | (result.index.str.startswith("BOTA")) |
            (result.index.str.startswith("CHEM")) | (result.index.str.startswith("ICHEM")) |
            (result.index.str.startswith("ELCT")) | (result.index.str.startswith("MATH")) |
            (result.index.str.startswith("STAT")) | (result.index.str.startswith("MBIO")) |
            (result.index.str.startswith("NUDT")) | (result.index.str.startswith("ZOOL")) |
            (result.index.str.startswith("ZOO")) | (result.index.str.startswith("PHYS")) |
            (result.index.str.startswith("BU-CHM")) | (result.index.str.startswith("BU-BIO")) |
            (result.index.str.startswith("EVMT")) | (result.index.str.startswith("BU-AGG")) |
            (result.index.str.startswith("STA/STAT")) | (result.index.str.startswith("BU-AGR")) |
            (result.index.str.startswith("BOT")) | (result.index.str.startswith("BU-BIO")) |
            (result.index.str.startswith("BU-BTG")) | (result.index.str.startswith("BU-CHM")) |
            (result.index.str.startswith("CSC")) | (result.index.str.startswith("STA")) |
            (result.index.str.startswith("BU-MCB")) | (result.index.str.startswith("MCB")) |
            (result.index.str.startswith("AGG"))
        ]
        if len(sat.index) != 0:
            results["SAT"] = sat

        bcsm = result[
            (result.index.str.startswith("ANAT")) | (result.index.str.startswith("BCHM")) |
            (result.index.str.startswith("MBBT")) | (result.index.str.startswith("PATH")) |
            (result.index.str.startswith("EPDM")) | (result.index.str.startswith("PHGY")) |
            (result.index.str.startswith("Internal")) | (result.index.str.startswith("Surgery")) |
            (result.index.str.startswith("Level")) | (result.index.str.startswith("OBGYN")) |
            (result.index.str.startswith("400")) | (result.index.str.startswith("Batch")) |
            (result.index.str.startswith("SURG")) | (result.index.str.startswith("PAED")) | 
            (result.index.str.startswith("Junior")) 
        ]
        if len(bcsm.index) != 0:
            results["BCSM"] = bcsm

        sbms = result[
            (result.index.str.startswith("COMH")) | (result.index.str.startswith("MBBS")) |
            (result.index.str.startswith("CHM")) | (result.index.str.startswith("NUT")) |
            (result.index.str.startswith("BU-NUT")) | (result.index.str.startswith("ANA")) |
            (result.index.str.startswith("BCH")) | (result.index.str.startswith("PHS")) |
            (result.index.str.startswith("BU-PIO")) | (result.index.str.startswith("PIO")) |
            (result.index.str.startswith("BU-ANA")) | (result.index.str.startswith("BU-BCH"))
        ]
        if len(sbms.index) != 0:
            results["SBMS"] = sbms

        law = result[
            (result.index.str.startswith("LAWS")) | (result.index.str.startswith("DCSS")) |
            (result.index.str.startswith("LAW")) | (result.index.str.startswith("BU-PUL")) |
            (result.index.str.startswith("CIL")) | (result.index.str.startswith("PHL")) |
            (result.index.str.startswith("PUL")) | (result.index.str.startswith("BU-CIL"))
        ]
        if len(law.index) != 0:
            results["LAW"] = law

        sces = result[
            (result.index.str.startswith("Elct")) | (result.index.str.startswith("MTH")) |
            (result.index.str.startswith("BU/CPE")) | (result.index.str.startswith("MEE")) |
            (result.index.str.startswith("CEE")) | (result.index.str.startswith("BU-CPE")) |
            (result.index.str.startswith("INGY"))
        ]
        if len(sces.index) != 0:
            results["SCES"] = sces

        return results

    # The rest of your analyzer.py (analyse_comp function and its calls)
    # remains largely the same, but it will now operate on the `srte` DataFrame
    # which has been standardized.

    return analyse_comp()

    # The commented out sections for saving to Excel in analyser.py
    # would also use the standardized data if uncommented.

    # print("SRTE analysis completed successfully...")

