import os

import numpy as np
import pandas as pd


def analyze(df):
    srte = df.copy()

    tm = srte.columns[2:9]
    ta = srte.columns[9:14]
    cm = srte.columns[14:18]
    ifs = srte.columns[18:23]
    pta = srte.columns[23:25]

    tm = srte.drop(
        [
            "TA8",
            "TA9",
            "TA10",
            "TA11",
            "TA12",
            "CM13",
            "CM14",
            "CM15",
            "CM16",
            "IF17",
            "IF18",
            "IF19",
            "IF20",
            "IF21",
            "PTA22",
            "PTA23",
        ],
        axis="columns",
    )

    ta = srte.drop(
        [
            "TM1",
            "TM2",
            "TM3",
            "TM4",
            "TM5",
            "TM6",
            "TM7",
            "CM13",
            "CM14",
            "CM15",
            "CM16",
            "IF17",
            "IF18",
            "IF19",
            "IF20",
            "IF21",
            "PTA22",
            "PTA23",
        ],
        axis="columns",
    )

    cm = srte.drop(
        [
            "TM1",
            "TM2",
            "TM3",
            "TM4",
            "TM5",
            "TM6",
            "TM7",
            "TA8",
            "TA9",
            "TA10",
            "TA11",
            "TA12",
            "IF17",
            "IF18",
            "IF19",
            "IF20",
            "IF21",
            "PTA22",
            "PTA23",
        ],
        axis="columns",
    )

    ifs = srte.drop(
        [
            "TM1",
            "TM2",
            "TM3",
            "TM4",
            "TM5",
            "TM6",
            "TM7",
            "TA8",
            "TA9",
            "TA10",
            "TA11",
            "TA12",
            "CM13",
            "CM14",
            "CM15",
            "CM16",
            "PTA22",
            "PTA23",
        ],
        axis="columns",
    )

    pta = srte.drop(
        [
            "TM1",
            "TM2",
            "TM3",
            "TM4",
            "TM5",
            "TM6",
            "TM7",
            "TA8",
            "TA9",
            "TA10",
            "TA11",
            "TA12",
            "CM13",
            "CM14",
            "CM15",
            "CM16",
            "IF17",
            "IF18",
            "IF19",
            "IF20",
            "IF21",
        ],
        axis="columns",
    )

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

    # incomp = result.copy()
    # incomp = incomp[incomp['No'] <= 4]
    # result = result[result['No'] >= 5]

    def analyse_comp():
        results = {}

        sms = result[
            (result.index.str.startswith("ACCT"))
            | (result.index.str.startswith("BSAD"))
            | (result.index.str.startswith("BSTA"))
            | (result.index.str.startswith("BMTH"))
            | (result.index.str.startswith("FNCE"))
            | (result.index.str.startswith("IRMA"))
            | (result.index.str.startswith("MLIS"))
            | (result.index.str.startswith("MIHM"))
            | (result.index.str.startswith("BSAD/MKTG"))
            | (result.index.str.startswith("MBIM"))
            | (result.index.str.startswith("ECONS"))
            | (result.index.str.startswith("MKTG"))
        ]
        if len(sms.index) != 0:
            results["SMS"] = sms
            # if not os.path.exists('./Results/SMS'):
            #     os.makedirs('./Results/SMS')
            #     sms.to_excel('./Results/SMS/SMS.xlsx')
            # else:
            #     sms.to_excel('./Results/SMS/SMS.xlsx')

        vasss = result[
            (result.index.str.startswith("ECON"))
            | (result.index.str.startswith("MCOM"))
            | (result.index.str.startswith("MCBC"))
            | (result.index.str.startswith("MCJP"))
            | (result.index.str.startswith("MCPR"))
            | (result.index.str.startswith("PBAD"))
            | (result.index.str.startswith("PBMG"))
            | (result.index.str.startswith("PLSC"))
            | (result.index.str.startswith("IILDP"))
            | (result.index.str.startswith("ILDP"))
            | (result.index.str.startswith("PMBG"))
            | (result.index.str.startswith("SOWK"))
        ]
        if len(vasss.index) != 0:
            results["VASSS"] = vasss
            # if not os.path.exists('./Results/VASSS'):
            #     os.makedirs('./Results/VASSS')
            #     vasss.to_excel('./Results/VASSS/VASSS.xlsx')
            # else:
            #     vasss.to_excel('./Results/VASSS/VASSS.xlsx')

        cffs = result[
            (result.index.str.startswith("MAT"))
            | (result.index.str.startswith("LIT"))
            | (result.index.str.startswith("PHY"))
            | (result.index.str.startswith("CHE"))
            | (result.index.str.startswith("ECO"))
            | (result.index.str.startswith("BIO"))
            | (result.index.str.startswith("PPAD"))
            | (result.index.str.startswith("PILW"))
            | (result.index.str.startswith("CRS"))
            | (result.index.str.startswith("GOV"))
            | (result.index.str.startswith("ECN"))
            | (result.index.str.startswith("ACC"))
            | (result.index.str.startswith("BUS"))
            | (result.index.str.startswith("HIS"))
            | (result.index.str.startswith("AGR"))
        ]
        if len(cffs.index) != 0:
            results["CFFS"] = cffs
            # if not os.path.exists('./Results/CFFS'):
            #     os.makedirs('./Results/CFFS')
            #     cffs.to_excel('./Results/CFFS/CFFS.xlsx')
            # else:
            #     cffs.to_excel('./Results/CFFS/CFFS.xlsx')

        eah = result[
            (result.index.str.startswith("BEDU"))
            | (result.index.str.startswith("CRLS"))
            | (result.index.str.startswith("CRSL"))
            | (result.index.str.startswith("CHMN"))
            | (result.index.str.startswith("CHIS"))
            | (result.index.str.startswith("EDPA"))
            | (result.index.str.startswith("EDUC"))
            | (result.index.str.startswith("ENGL"))
            | (result.index.str.startswith("FRCH"))
            | (result.index.str.startswith("GCPY"))
            | (result.index.str.startswith("GEDS"))
	    | (result.index.str.startswith("BU/GST"))
            | (result.index.str.startswith("HIST"))
            | (result.index.str.startswith("MUSC"))
            | (result.index.str.startswith("RELS"))
            | (result.index.str.startswith("RELG"))
            | (result.index.str.startswith("EGLT"))
            | (result.index.str.startswith("BIBL"))
            | (result.index.str.startswith("NTST"))
            | (result.index.str.startswith("OTST"))
            | (result.index.str.startswith("THST"))
            | (result.index.str.startswith("FREN"))
        ]
        if len(eah.index) != 0:
            results["EAH"] = eah
            # if not os.path.exists('./Results/EAH'):
            #     os.makedirs('./Results/EAH')
            #     eah.to_excel('./Results/EAH/EAH.xlsx')
            # else:
            #     eah.to_excel('./Results/EAH/EAH.xlsx')

        pah = result[
            (result.index.str.startswith("MLSC"))
            | (result.index.str.startswith("PHSC"))
            | (result.index.str.startswith("MLSB"))
            | (result.index.str.startswith("MLSH"))
            | (result.index.str.startswith("MLSM"))
            | (result.index.str.startswith("MLSP"))
            | (result.index.str.startswith("PHFC"))
            | (result.index.str.startswith("PHMP"))
            | (result.index.str.startswith("PHEP"))
            | (result.index.str.startswith("PHNT"))
            | (result.index.str.startswith("PHPR"))
            | (result.index.str.startswith("PHEH"))
            | (result.index.str.startswith("ENGL/EGLT"))
        ]
        if len(pah.index) != 0:
            results["PAH"] = pah
            # if not os.path.exists('./Results/PAH'):
            #     os.makedirs('./Results/PAH')
            #     pah.to_excel('./Results/PAH/PAH.xlsx')
            # else:
            #     pah.to_excel('./Results/PAH/PAH.xlsx')

        nursing = result[(result.index.str.startswith("NRSG"))]
        if len(nursing.index) != 0:
            results["NURSING"] = nursing
            # if not os.path.exists('./Results/NURSING'):
            #     os.makedirs('./Results/NURSING')
            #     nursing.to_excel('./Results/NURSING/NURSING.xlsx')
            # else:
            #     nursing.to_excel('./Results/NURSING/NURSING.xlsx')

        ces = result[
            (result.index.str.startswith("COSC"))
            | (result.index.str.startswith("INSY"))
            | (result.index.str.startswith("ITGY"))
            | (result.index.str.startswith("ELCT"))
            | (result.index.str.startswith("SENG"))
	    | (result.index.str.startswith("BU/CPE"))
        ]
        if len(ces.index) != 0:
            results["CES"] = ces
            # if not os.path.exists('./Results/CES'):
            #     os.makedirs('./Results/CES')
            #     ces.to_excel('./Results/CES/CES.xlsx')
            # else:
            #     ces.to_excel('./Results/CES/CES.xlsx')

	se = result[
	    (result.index.str.startswith("BU/CPE"))
        ]
        if len(se.index) != 0:
            results["SENG"] = se
            # if not os.path.exists('./Results/SENG'):
            #     os.makedirs('./Results/SENG')
            #     ces.to_excel('./Results/CES/CES.xlsx')
            # else:
            #     ces.to_excel('./Results/CES/CES.xlsx')

        sat = result[
            (result.index.str.startswith("AGRE"))
            | (result.index.str.startswith("AGEM"))
            | (result.index.str.startswith("AGRY"))
            | (result.index.str.startswith("AGRI"))
            | (result.index.str.startswith("ANSC"))
            | (result.index.str.startswith("CRPT"))
            | (result.index.str.startswith("BIOL"))
            | (result.index.str.startswith("BOTA"))
            | (result.index.str.startswith("CHEM"))
            | (result.index.str.startswith("ICHEM"))
            | (result.index.str.startswith("ELCT"))
            | (result.index.str.startswith("MATH"))
            | (result.index.str.startswith("STAT"))
            | (result.index.str.startswith("MBIO"))
            | (result.index.str.startswith("NUDT"))
            | (result.index.str.startswith("ZOOL"))
            | (result.index.str.startswith("PHYS"))
        ]
        if len(sat.index) != 0:
            results["SAT"] = sat
            # if not os.path.exists('./Results/SAT'):
            #     os.makedirs('./Results/SAT')
            #     sat.to_excel('./Results/SAT/SAT.xlsx')
            # else:
            #     sat.to_excel('./Results/SAT/SAT.xlsx')

        bcsm = result[
            (result.index.str.startswith("ANAT"))
            | (result.index.str.startswith("BCHM"))
            | (result.index.str.startswith("MBBT"))
            | (result.index.str.startswith("PATH"))
            | (result.index.str.startswith("EPDM"))
            | (result.index.str.startswith("PHGY"))
            | (result.index.str.startswith("Internal"))
            | (result.index.str.startswith("Surgery"))
            | (result.index.str.startswith("Level"))
            | (result.index.str.startswith("OBGYN"))
            | (result.index.str.startswith("400"))
            | (result.index.str.startswith("Batch"))
        ]
        if len(bcsm.index) != 0:
            results["BCSM"] = bcsm
            # if not os.path.exists('./Results/BCSM'):
            #     os.makedirs('./Results/BCSM')
            #     bcsm.to_excel('./Results/BCSM/BCSM.xlsx')
            # else:
            #     bcsm.to_excel('./Results/BCSM/BCSM.xlsx')

        sbms = result[
            (result.index.str.startswith("COMH"))
            | (result.index.str.startswith("MBBS"))
        ]
        if len(sbms.index) != 0:
            results["SBMS"] = sbms
            # if not os.path.exists('./Results/SBMS'):
            #     os.makedirs('./Results/SBMS')
            #     sbms.to_excel('./Results/SBMS/SBMS.xlsx')
            # else:
            #     sbms.to_excel('./Results/SBMS/SBMS.xlsx')

        law = result[
            (result.index.str.startswith("LAWS"))
            | (result.index.str.startswith("DCSS"))
            | (result.index.str.startswith("LAW"))
            
        ]
        if len(law.index) != 0:
            results["LAW"] = law
            # if not os.path.exists('./Results/LAW'):
            #     os.makedirs('./Results/LAW')
            #     law.to_excel('./Results/LAW/LAW.xlsx')
            # else:
            #     law.to_excel('./Results/LAW/LAW.xlsx')

        sces = result[(result.index.str.startswith("Elct"))]
        if len(sces.index) != 0:
            results["SCES"] = sces
            # if not os.path.exists('./Results/SCES'):
            #     os.makedirs('./Results/SCES')
            #     sces.to_excel('./Results/SCES/SCES.xlsx')
            # else:
            #     sces.to_excel('./Results/SCES/SCES.xlsx')
        # print(type(results))
        return results

    return analyse_comp()

    # def analyse_incomp():
    #     if not os.path.exists('./Few_responses/SMS'):
    #         os.makedirs('./Few_responses/SMS')
    #         sms = incomp[(incomp.index.str.startswith('ACCT')) |
    #                      (incomp.index.str.startswith('BSAD')) |
    #                      (incomp.index.str.startswith('BSTA')) |
    #                      (incomp.index.str.startswith('FNCE')) |
    #                      (incomp.index.str.startswith('IRMA')) |
    #                      (incomp.index.str.startswith('MKTG'))
    #                      ]
    #         sms.to_excel('./Few_responses/SMS/SMS.xlsx')
    #     else:
    #         sms = incomp[(incomp.index.str.startswith('ACCT')) |
    #                      (incomp.index.str.startswith('BSAD')) |
    #                      (incomp.index.str.startswith('BSTA')) |
    #                      (incomp.index.str.startswith('FNCE')) |
    #                      (incomp.index.str.startswith('IRMA')) |
    #                      (incomp.index.str.startswith('MKTG'))
    #                      ]
    #         sms.to_excel('./Few_responses/SMS/SMS.xlsx')

    #     if not os.path.exists('./Few_responses/VASSS'):
    #         os.makedirs('./Few_responses/VASSS')
    #         vasss = incomp[(incomp.index.str.startswith('ECON')) |
    #                        (incomp.index.str.startswith('MCOM')) |
    #                        (incomp.index.str.startswith('PBAD')) |
    #                        (incomp.index.str.startswith('PLSC')) |
    #                        (incomp.index.str.startswith('IILDP')) |
    #                        (incomp.index.str.startswith('SOWK'))
    #                        ]
    #         vasss.to_excel('./Few_responses/VASSS/VASSS.xlsx')
    #     else:
    #         vasss = incomp[(incomp.index.str.startswith('ECON')) |
    #                        (incomp.index.str.startswith('MCOM')) |
    #                        (incomp.index.str.startswith('PBAD')) |
    #                        (incomp.index.str.startswith('PLSC')) |
    #                        (incomp.index.str.startswith('IILDP')) |
    #                        (incomp.index.str.startswith('SOWK'))
    #                        ]
    #         vasss.to_excel('./Few_responses/VASSS/VASSS.xlsx')

    #     if not os.path.exists('./Few_responses/EAH'):
    #         os.makedirs('./Few_responses/EAH')
    #         eah = incomp[(incomp.index.str.startswith('BEDU')) |
    #                      (incomp.index.str.startswith('CRLS')) |
    #                      (incomp.index.str.startswith('EDPA')) |
    #                      (incomp.index.str.startswith('EDUC')) |
    #                      (incomp.index.str.startswith('ENGL')) |
    #                      (incomp.index.str.startswith('FRCH')) |
    #                      (incomp.index.str.startswith('GCPY')) |
    #                      (incomp.index.str.startswith('GEDS')) |
    #                      (incomp.index.str.startswith('HIST')) |
    #                      (incomp.index.str.startswith('MUSC')) |
    #                      (incomp.index.str.startswith('RELS')) |
    #                      (incomp.index.str.startswith('FREN'))
    #                      ]
    #         eah.to_excel('./Few_responses/EAH/EAH.xlsx')
    #     else:
    #         eah = incomp[(incomp.index.str.startswith('BEDU')) |
    #                      (incomp.index.str.startswith('CRLS')) |
    #                      (incomp.index.str.startswith('EDPA')) |
    #                      (incomp.index.str.startswith('EDUC')) |
    #                      (incomp.index.str.startswith('ENGL')) |
    #                      (incomp.index.str.startswith('FRCH')) |
    #                      (incomp.index.str.startswith('GCPY')) |
    #                      (incomp.index.str.startswith('GEDS')) |
    #                      (incomp.index.str.startswith('HIST')) |
    #                      (incomp.index.str.startswith('MUSC')) |
    #                      (incomp.index.str.startswith('RELS')) |
    #                      (incomp.index.str.startswith('FREN'))
    #                      ]
    #         eah.to_excel('./Few_responses/EAH/EAH.xlsx')

    #     if not os.path.exists('./Few_responses/PAH'):
    #         os.makedirs('./Few_responses/PAH')
    #         pah = incomp[(incomp.index.str.startswith('MLSC')) |
    #                      (incomp.index.str.startswith('PHSC')) |
    #                      (incomp.index.str.startswith('PHFC'))
    #                      ]
    #         pah.to_excel('./Few_responses/PAH/PAH.xlsx')
    #     else:
    #         pah = incomp[(incomp.index.str.startswith('MLSC')) |
    #                      (incomp.index.str.startswith('PHSC')) |
    #                      (incomp.index.str.startswith('PHFC'))
    #                      ]
    #         pah.to_excel('./Few_responses/PAH/PAH.xlsx')

    #     if not os.path.exists('./Few_responses/NURSING'):
    #         os.makedirs('./Few_responses/NURSING')
    #         nursing = incomp[(incomp.index.str.startswith('NRSG'))]
    #         nursing.to_excel('./Few_responses/NURSING/NURSING.xlsx')
    #     else:
    #         nursing = incomp[(incomp.index.str.startswith('NRSG'))]
    #         nursing.to_excel('./Few_responses/NURSING/NURSING.xlsx')

    #     if not os.path.exists('./Few_responses/CES'):
    #         os.makedirs('./Few_responses/CES')
    #         ces = incomp[(incomp.index.str.startswith('COSC')) |
    #                      (incomp.index.str.startswith('INSY')) |
    #                      (incomp.index.str.startswith('ITGY')) |
    #                      (incomp.index.str.startswith('SENG'))
    #                      ]
    #         ces.to_excel('./Few_responses/CES/CES.xlsx')
    #     else:
    #         ces = incomp[(incomp.index.str.startswith('COSC')) |
    #                      (incomp.index.str.startswith('INSY')) |
    #                      (incomp.index.str.startswith('ITGY')) |
    #                      (incomp.index.str.startswith('SENG'))
    #                      ]
    #         ces.to_excel('./Few_responses/CES/CES.xlsx')

    #     if not os.path.exists('./Few_responses/SAT'):
    #         os.makedirs('./Few_responses/SAT')
    #         sat = incomp[(incomp.index.str.startswith('AGRE')) |
    #                      (incomp.index.str.startswith('AGRY')) |
    #                      (incomp.index.str.startswith('BIOL')) |
    #                      (incomp.index.str.startswith('BOTA')) |
    #                      (incomp.index.str.startswith('CHEM')) |
    #                      (incomp.index.str.startswith('ELCT')) |
    #                      (incomp.index.str.startswith('MATH')) |
    #                      (incomp.index.str.startswith('MBIO')) |
    #                      (incomp.index.str.startswith('NUDT')) |
    #                      (incomp.index.str.startswith('PHYS'))
    #                      ]
    #         sat.to_excel('./Few_responses/SAT/SAT.xlsx')
    #     else:
    #         sat = incomp[(incomp.index.str.startswith('AGRE')) |
    #                      (incomp.index.str.startswith('AGRY')) |
    #                      (incomp.index.str.startswith('BIOL')) |
    #                      (incomp.index.str.startswith('BOTA')) |
    #                      (incomp.index.str.startswith('CHEM')) |
    #                      (incomp.index.str.startswith('ELCT')) |
    #                      (incomp.index.str.startswith('MATH')) |
    #                      (incomp.index.str.startswith('MBIO')) |
    #                      (incomp.index.str.startswith('NUDT')) |
    #                      (incomp.index.str.startswith('PHYS'))
    #                      ]
    #         sat.to_excel('./Few_responses/SAT/SAT.xlsx')

    #     if not os.path.exists('./Few_responses/BCSM'):
    #         os.makedirs('./Few_responses/BCSM')
    #         bcsm = incomp[(incomp.index.str.startswith('ANAT')) |
    #                       (incomp.index.str.startswith('BCHM')) |
    #                       (incomp.index.str.startswith('PHGY'))
    #                       ]
    #         bcsm.to_excel('./Few_responses/BCSM/BCSM.xlsx')
    #     else:
    #         bcsm = incomp[(incomp.index.str.startswith('ANAT')) |
    #                       (incomp.index.str.startswith('BCHM')) |
    #                       (incomp.index.str.startswith('PHGY'))
    #                       ]
    #         bcsm.to_excel('./Few_responses/BCSM/BCSM.xlsx')

    #     if not os.path.exists('./Few_responses/LAW'):
    #         os.makedirs('./Few_responses/LAW')
    #         law = result[(result.index.str.startswith('LAWS'))]
    #         law.to_excel('./Few_responses/LAW/LAW.xlsx')
    #     else:
    #         law = result[(result.index.str.startswith('LAWS'))]
    #         law.to_excel('./Few_responses/LAW/LAW.xlsx')

    # if not os.path.exists('Results'):
    #     os.makedirs('Results')
    #     analyse_comp()
    # else:
    #     analyse_comp()

    # if not os.path.exists('Few_responses'):
    #     os.makedirs('Few_responses')
    #     analyse_incomp()
    # else:
    #     analyse_incomp()

    print("SRTE analysis completed successfully...")
