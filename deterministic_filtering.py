import pandas as pd
import numpy as np
import re
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("sampling_runtime.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class LookupSiteGroup():
    def __init__(self):
        self.std_excl = [self.r(9050, 9055), self.r(9140), self.r(9590, 9993)]
        self.rules = [
    # Oral Cavity and Pharynx
    {"group": "Lip", "recode": 20010, "site_type": "include", "site_ranges": [self.r(0,9)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Tongue", "recode": 20020, "site_type": "include", "site_ranges": [self.r(19,29)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Salivary Gland", "recode": 20030, "site_type": "include", "site_ranges": [self.r(79,89)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Floor of Mouth", "recode": 20040, "site_type": "include", "site_ranges": [self.r(40,49)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Gum and Other Mouth", "recode": 20050, "site_type": "include", "site_ranges": [self.r(30,39), self.r(50,59), self.r(60,69)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Nasopharynx", "recode": 20060, "site_type": "include", "site_ranges": [self.r(110,119)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Tonsil", "recode": 20070, "site_type": "include", "site_ranges": [self.r(90,99)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Oropharynx", "recode": 20080, "site_type": "include", "site_ranges": [self.r(100,109)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Hypopharynx", "recode": 20090, "site_type": "include", "site_ranges": [self.r(129), self.r(130,139)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Oral Cavity and Pharynx", "recode": 20100, "site_type": "include", "site_ranges": [self.r(140), self.r(142), self.r(148)], "hist_mode": "exclude", "hist_ranges": self.std_excl},

    # Digestive System
    {"group": "Esophagus", "recode": 21010, "site_type": "include", "site_ranges": [self.r(150,159)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Stomach", "recode": 21020, "site_type": "include", "site_ranges": [self.r(160,169)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Small Intestine", "recode": 21030, "site_type": "include", "site_ranges": [self.r(170,179)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Cecum", "recode": 21041, "site_type": "include", "site_ranges": [self.r(180)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Appendix", "recode": 21042, "site_type": "include", "site_ranges": [self.r(181)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Ascending Colon", "recode": 21043, "site_type": "include", "site_ranges": [self.r(182)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Hepatic Flexure", "recode": 21044, "site_type": "include", "site_ranges": [self.r(183)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Transverse Colon", "recode": 21045, "site_type": "include", "site_ranges": [self.r(184)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Splenic Flexure", "recode": 21046, "site_type": "include", "site_ranges": [self.r(185)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Descending Colon", "recode": 21047, "site_type": "include", "site_ranges": [self.r(186)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Sigmoid Colon", "recode": 21048, "site_type": "include", "site_ranges": [self.r(187)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Large Intestine, NOS", "recode": 21049, "site_type": "include", "site_ranges": [self.r(188,189), self.r(260)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Rectosigmoid Junction", "recode": 21051, "site_type": "include", "site_ranges": [self.r(199)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Rectum", "recode": 21052, "site_type": "include", "site_ranges": [self.r(209)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Anus, Anal Canal and Anorectum", "recode": 21060, "site_type": "include", "site_ranges": [self.r(210,212), self.r(218)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Liver", "recode": 21071, "site_type": "include", "site_ranges": [self.r(220)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Intrahepatic Bile Duct", "recode": 21072, "site_type": "include", "site_ranges": [self.r(221)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Gallbladder", "recode": 21080, "site_type": "include", "site_ranges": [self.r(239)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Biliary", "recode": 21090, "site_type": "include", "site_ranges": [self.r(240,249)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Pancreas", "recode": 21100, "site_type": "include", "site_ranges": [self.r(250,259)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Retroperitoneum", "recode": 21110, "site_type": "include", "site_ranges": [self.r(480)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Peritoneum, Omentum and Mesentery", "recode": 21120, "site_type": "include", "site_ranges": [self.r(481,482)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Digestive Organs", "recode": 21130, "site_type": "include", "site_ranges": [self.r(268,269), self.r(488)], "hist_mode": "exclude", "hist_ranges": self.std_excl},

    # Respiratory System
    {"group": "Nose, Nasal Cavity and Middle Ear", "recode": 22010, "site_type": "include", "site_ranges": [self.r(300,301), self.r(310,319)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Larynx", "recode": 22020, "site_type": "include", "site_ranges": [self.r(320,329)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Lung and Bronchus", "recode": 22030, "site_type": "include", "site_ranges": [self.r(340,349)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Pleura", "recode": 22050, "site_type": "include", "site_ranges": [self.r(384)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Trachea, Mediastinum and Other Respiratory Organs", "recode": 22060, "site_type": "include", "site_ranges": [self.r(339), self.r(381,383), self.r(388), self.r(390), self.r(398), self.r(399)], "hist_mode": "exclude", "hist_ranges": self.std_excl},

    # Bones, Soft Tissue, Skin
    {"group": "Bones and Joints", "recode": 23000, "site_type": "include", "site_ranges": [self.r(400,419)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Soft Tissue including Heart", "recode": 24000, "site_type": "include", "site_ranges": [self.r(380), self.r(470,479), self.r(490,499)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Melanoma of the Skin", "recode": 25010, "site_type": "include", "site_ranges": [self.r(440,449)], "hist_mode": "include", "hist_ranges": [self.r(8720,8790)]},
    {"group": "Other Non-Epithelial Skin", "recode": 25020, "site_type": "include", "site_ranges": [self.r(440,449)], "hist_mode": "exclude", "hist_ranges": [self.r(8000,8005), self.r(8010,8046), self.r(8050,8084), self.r(8090,8110), self.r(8720,8790)] + self.std_excl},

    # Breast and Reproductive
    {"group": "Breast", "recode": 26000, "site_type": "include", "site_ranges": [self.r(500,509)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Cervix Uteri", "recode": 27010, "site_type": "include", "site_ranges": [self.r(530,539)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Corpus Uteri", "recode": 27020, "site_type": "include", "site_ranges": [self.r(540,549)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Uterus, NOS", "recode": 27030, "site_type": "include", "site_ranges": [self.r(559)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Ovary", "recode": 27040, "site_type": "include", "site_ranges": [self.r(569)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Vagina", "recode": 27050, "site_type": "include", "site_ranges": [self.r(529)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Vulva", "recode": 27060, "site_type": "include", "site_ranges": [self.r(510,519)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Female Genital Organs", "recode": 27070, "site_type": "include", "site_ranges": [self.r(570,579), self.r(589)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Prostate", "recode": 28010, "site_type": "include", "site_ranges": [self.r(619)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Testis", "recode": 28020, "site_type": "include", "site_ranges": [self.r(620,629)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Penis", "recode": 28030, "site_type": "include", "site_ranges": [self.r(600,609)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Male Genital Organs", "recode": 28040, "site_type": "include", "site_ranges": [self.r(630,639)], "hist_mode": "exclude", "hist_ranges": self.std_excl},

    # Urinary and Nervous System
    {"group": "Urinary Bladder", "recode": 29010, "site_type": "include", "site_ranges": [self.r(670,679)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Kidney and Renal Pelvis", "recode": 29020, "site_type": "include", "site_ranges": [self.r(649), self.r(659)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Ureter", "recode": 29030, "site_type": "include", "site_ranges": [self.r(669)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Urinary Organs", "recode": 29040, "site_type": "include", "site_ranges": [self.r(680,689)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Eye and Orbit", "recode": 30000, "site_type": "include", "site_ranges": [self.r(690,699)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Brain", "recode": 31010, "site_type": "include", "site_ranges": [self.r(710,719)], "hist_mode": "exclude", "hist_ranges": [self.r(9530,9539)] + self.std_excl},
    {"group": "Cranial Nerves Other Nervous System", "recode": 31040, "site_type": "include", "site_ranges": [self.r(710,719)], "hist_mode": "include", "hist_ranges": [self.r(9530,9539)]},
    {"group": "Cranial Nerves Other Nervous System", "recode": 31040, "site_type": "include", "site_ranges": [self.r(700,709), self.r(720,729)], "hist_mode": "exclude", "hist_ranges": self.std_excl},

    # Endocrine
    {"group": "Thyroid", "recode": 32010, "site_type": "include", "site_ranges": [self.r(739)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
    {"group": "Other Endocrine including Thymus", "recode": 32020, "site_type": "include", "site_ranges": [self.r(379), self.r(740,749), self.r(750,759)], "hist_mode": "exclude", "hist_ranges": self.std_excl},

    # Lymphoma
    {"group": "Hodgkin - Nodal", "recode": 33011, "site_type": "include", "site_ranges": [self.r(24), self.r(98,99), self.r(111), self.r(142), self.r(379), self.r(422), self.r(770,779)], "hist_mode": "include", "hist_ranges": [self.r(9650,9667)]},
    {"group": "Hodgkin - Extranodal", "recode": 33012, "site_type": "all_other", "hist_mode": "include", "hist_ranges": [self.r(9650,9667)]},
    {"group": "NHL - Nodal", "recode": 33041, "site_type": "include", "site_ranges": [self.r(24), self.r(98), self.r(99), self.r(111), self.r(142), self.r(379), self.r(422), self.r(770,779)], "hist_mode": "include", "hist_ranges": [self.r(9590,9597), self.r(9670,9671), self.r(9673), self.r(9675), self.r(9678,9680), self.r(9684), self.r(9687,9691), self.r(9695), self.r(9698,9702), self.r(9705), self.r(9708,9709), self.r(9712), self.r(9714,9719), self.r(9724,9729), self.r(9735), self.r(9737,9738), self.r(9811,9818), self.r(9823), self.r(9827), self.r(9837)]},
    {"group": "NHL - Extranodal", "recode": 33042, "site_type": "all_except", "site_except": [self.r(24), self.r(98,99), self.r(111), self.r(142), self.r(379), self.r(422), self.r(770,779)], "hist_mode": "include", "hist_ranges": [self.r(9590,9597), self.r(9670,9671), self.r(9673), self.r(9675), self.r(9678,9680), self.r(9684), self.r(9687), self.r(9688), self.r(9689,9691), self.r(9695), self.r(9698,9702), self.r(9705), self.r(9708,9709), self.r(9712), self.r(9714,9719), self.r(9724,9729), self.r(9735), self.r(9737), self.r(9738)]},
    {"group": "NHL - Extranodal", "recode": 33042, "site_type": "all_except", "site_except": [self.r(24), self.r(98,99), self.r(111), self.r(142), self.r(379), self.r(420,422), self.r(424), self.r(770,779)], "hist_mode": "include", "hist_ranges": [self.r(9811,9819), self.r(9823), self.r(9827), self.r(9837)]},

    # Myeloma and Leukemia
    {"group": "Myeloma", "recode": 34000, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9731,9732), self.r(9734)]},
    {"group": "Acute Lymphocytic Leukemia", "recode": 35011, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9826), self.r(9835,9836)]},
    {"group": "Acute Lymphocytic Leukemia", "recode": 35011, "site_type": "include", "site_ranges": [self.r(420), self.r(421), self.r(424)], "hist_mode": "include", "hist_ranges": [self.r(9811,9819), self.r(9837)]},
    {"group": "Chronic Lymphocytic Leukemia", "recode": 35012, "site_type": "include", "site_ranges": [self.r(420), self.r(421), self.r(424)], "hist_mode": "include", "hist_ranges": [self.r(9823)]},
    {"group": "Other Lymphocytic Leukemia", "recode": 35013, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9820), self.r(9832,9834), self.r(9940)]},
    {"group": "Acute Myeloid Leukemia", "recode": 35021, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9840), self.r(9861), self.r(9865,9867), self.r(9869), self.r(9871,9874), self.r(9877,9879), self.r(9895,9897), self.r(9898), self.r(9910,9912), self.r(9920)]},
    {"group": "Acute Monocytic Leukemia", "recode": 35031, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9891)]},
    {"group": "Chronic Myeloid Leukemia", "recode": 35022, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9863), self.r(9875,9876), self.r(9945,9946)]},
    {"group": "Other Myeloid/Monocytic Leukemia", "recode": 35023, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9860), self.r(9930)]},
    {"group": "Other Acute Leukemia", "recode": 35041, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9801), self.r(9805,9809), self.r(9931)]},
    {"group": "Aleukemic, Subleukemic and NOS", "recode": 35043, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9733), self.r(9742), self.r(9800), self.r(9831), self.r(9870), self.r(9948), self.r(9963,9964)]},
    {"group": "Aleukemic, Subleukemic and NOS", "recode": 35043, "site_type": "include", "site_ranges": [self.r(420), self.r(421), self.r(424)], "hist_mode": "include", "hist_ranges": [self.r(9827)]},

    # Mesothelioma / Kaposi / Misc
    {"group": "Mesothelioma", "recode": 36010, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9050,9055)]},
    {"group": "Kaposi Sarcoma", "recode": 36020, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9140)]},
    {"group": "Miscellaneous", "recode": 37000, "site_type": "all", "hist_mode": "include", "hist_ranges": [self.r(9740,9741), self.r(9749,9769), self.r(9950), self.r(9960,9962), self.r(9965,9968), self.r(9970,9971), self.r(9975), self.r(9980), self.r(9982,9987), self.r(9989), self.r(9991,9993)]},
    {"group": "Miscellaneous", "recode": 37000, "site_type": "include", "site_ranges": [self.r(760,768), self.r(809), self.r(420,424), self.r(770,779)], "hist_mode": "exclude", "hist_ranges": self.std_excl},
]
    
    def r(self, lo, hi=None):
        if hi is None:
            hi = lo
        return (int(lo), int(hi))
    
    def norm_site_int(self, psite):
        if pd.isna(psite):
            return None
        s = str(psite).upper()
        match = re.search(r"C\s*(\d+)", s)
        if not match:
            return None
        return int(match.group(1))
    
    def norm_hist_int(self, hist):
        if pd.isna(hist):
            return None
        try:
            return int(str(hist).strip())
        except (ValueError, TypeError):
            return None
        
    def in_any_range(self, x, ranges):
        if x is None or not ranges:
            return False
        return any(lo <= x <= hi for lo, hi in ranges)
    
    def match_rule(self, site_i, hist_i, rule):
        if site_i is None or hist_i is None:
            return False

        # Site Matching Logic
        site_type = rule['site_type']
        if site_type == "all":
            site_ok = True
        elif site_type == "all_other":
            site_ok = True
        elif site_type == "include":
            site_ok = self.in_any_range(site_i, rule['site_ranges'])
        elif site_type == "all_except":
            site_ok = not self.in_any_range(site_i, rule['site_except'])
        else:
            site_ok = False

        if not site_ok:
            return False

        # Histology Matching Logic
        hist_mode = rule['hist_mode']
        if hist_mode == "any":
            hist_ok = True
        elif hist_mode == "include":
            hist_ok = self.in_any_range(hist_i, rule['hist_ranges'])
        elif hist_mode == "exclude":
            hist_ok = not self.in_any_range(hist_i, rule['hist_ranges'])
        else:
            hist_ok = False

        return hist_ok
    
    def lookup_site_group(self, psite, histology):
        
        s_int = self.norm_site_int(psite)
        h_int = self.norm_hist_int(histology)
        
        if s_int is None or h_int is None:
            return "Invalid", 99999
        
        for rule in self.rules:
            if self.match_rule(s_int, h_int, rule):
                return rule['group'], rule['recode']
                
        return "Invalid",  99999
    
    def manipulate_excel(self, path="Data/McElroy Breast Study 3.xlsx", new_path="Data/McElroy.xlsx"):
        df = pd.read_excel(path, sheet_name=0)
        results = df.apply(lambda row: self.lookup_site_group(row['PSite'],row['HistTypeICDO3']), axis=1)
        df[['SiteGroup', 'Recode']] = pd.DataFrame(results.tolist(), index=df.index)
        df.to_excel(new_path, index=False) 

    
    
class FetchData():
    def __init__(self, path="Data/McElroy.xlsx"):
        self.df = pd.read_excel(path)
        self.df = self.df.dropna(subset=["Phone"])
        code_cols = ["RepHosp", "Phone", "Recode"]

        for col in code_cols:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(self.int_to_str_if_not_empty)
        self.df['Race1'] = pd.to_numeric(self.df['Race1'], errors='coerce')
        self.df['DxCounty'] = pd.to_numeric(self.df['DxCounty'], errors='coerce')
        self.df['SS2018'] = pd.to_numeric(self.df['SS2018'], errors='coerce')
        self.df['DxDate'] = self.df['DxDate'].astype(str).str[:4]
        self.df['BirthDate'] = self.df['BirthDate'].astype(str).str[:4]
        bins = [24, 30, 40, 50, 60, 70, 80, 1000]
        labels = ['20s', '30s', '40s', '50s', '60s', '70s', '80+']
        self.df['AgeGroup'] = pd.cut(self.df['AgeDx'], bins=bins, labels=labels, right=False)

    def int_to_str_if_not_empty(self, x):
        if pd.isna(x):
            return pd.NA
        return str(int(float(x)))

    def get_stratified_sample(self, n, filters=None, random_state=42):
        start_time = time.perf_counter()
        logger.info("Sampling started")
        logger.info(f"Requested sample size: {n}")
        logger.info(f"Filters received: {filters}")

        temp_df = self.df.copy()
        logger.info(f"Initial dataframe size: {len(temp_df)}")
        # temp_df = temp_df[temp_df["Phone"].notna()]
        temp_df = temp_df.dropna(subset=["Phone", "DxCounty", "AgeGroup"])

        filter_start = time.perf_counter()
      
        if filters:
            for col, val in filters.items():
                if isinstance(val, list):
                    temp_df = temp_df[temp_df[col].isin(val)]
                else:
                    temp_df = temp_df[temp_df[col] == val]
        
        filter_end = time.perf_counter()
        
        if len(temp_df) == 0:
            total_time = time.perf_counter() - start_time
            logger.info(f"No records matched filters. Sampling ended in {total_time:.4f} seconds")
            return None
    
        
        logger.info(f"Filtering time: {filter_end - filter_start:.4f} seconds")
        
        # include atleast 20% of race==2
        total_race2_available = len(temp_df[temp_df['Race1'] == 2])
        natural_proportion = total_race2_available / len(temp_df)
        natural_count = int(np.round(n * natural_proportion))
        quota_count = int(np.round(n * 0.20))

        target_race2 = max(natural_count, quota_count)
        target_race2 = min(target_race2, total_race2_available)

        target_race1 = n-target_race2

        logger.info(f"Eligible records after filters: {len(temp_df)}")
        logger.info(f"Race2 available: {total_race2_available}")
        logger.info(f"Natural race2 proportion: {natural_proportion:.4f}")
        logger.info(f"Target race2 count: {target_race2}")
        logger.info(f"Target race1 count: {target_race1}")

        
        df_race2 = temp_df[temp_df['Race1'] == 2]
        df_race1 = temp_df[temp_df['Race1'] == 1]
        
        weights = ['DxCounty', 'AgeGroup', 'PSite']
        frac2 = target_race2/len(df_race2) if len(df_race2) > 0 else 0
        frac1 = target_race1/len(df_race1) if len(df_race1) > 0 else 0 

        
        # sampled_r2 = pd.DataFrame()
        # if not df_race2.empty and target_race2 > 0:
        #     sampled_r2 = df_race2.groupby(weights, group_keys=False, observed=False).apply(
        #         lambda x: x.sample(n=min(len(x), int(np.round(len(x) * frac2))))
        #     )

        # print(sampled_r2)
        # print("--------------------------------------")
        # sampled_r1 = pd.DataFrame()
        # if not df_race1.empty and target_race1 > 0:
        #     sampled_r1 = df_race1.groupby(weights, group_keys=False, observed=False).apply(
        #         lambda x: x.sample(n=min(len(x), int(np.round(len(x) * frac1))))
        #     )
        # print(sampled_r1)

        sampled_r2_list = []
        if not df_race2.empty and target_race2 > 0:
            for _, group in df_race2.groupby(weights, observed=True):
                sample_size = int(np.round(len(group) * frac2))
                sample_size = min(len(group), max(0, sample_size))
                if sample_size > 0:
                    sampled_r2_list.append(group.sample(n=sample_size, random_state=random_state))
        sampled_r2 = pd.concat(sampled_r2_list) if sampled_r2_list else pd.DataFrame()
        if len(sampled_r2) > target_race2:
            sampled_r2 = sampled_r2.sample(n=target_race2, random_state=random_state)

        elif len(sampled_r2) < target_race2:
            remaining_r2 = df_race2.drop(sampled_r2.index)
            extra_n = min(target_race2 - len(sampled_r2), len(remaining_r2))
            if extra_n > 0:
                sampled_r2 = pd.concat([sampled_r2,remaining_r2.sample(n=extra_n, random_state=random_state)])


        sampled_r1_list = []
        if not df_race1.empty and target_race1 > 0:
            for _, group in df_race1.groupby(weights, observed=True):
                sample_size = int(np.round(len(group) * frac1))
                sample_size = min(len(group), max(0, sample_size))
                if sample_size > 0:
                    sampled_r1_list.append(group.sample(n=sample_size, random_state=random_state))
        sampled_r1 = pd.concat(sampled_r1_list) if sampled_r1_list else pd.DataFrame()
        if len(sampled_r1) > target_race1:
            sampled_r1 = sampled_r1.sample(n=target_race1, random_state=random_state)

        elif len(sampled_r1) < target_race1:
            remaining_r1 = df_race1.drop(sampled_r1.index)
            extra_n = min(target_race1 - len(sampled_r1), len(remaining_r1))

            if extra_n > 0:
                sampled_r1 = pd.concat([sampled_r1,remaining_r1.sample(n=extra_n, random_state=random_state)])

        stratified_end = time.perf_counter()
        logger.info(f"Stratified sampling time: {stratified_end - start_time:.4f} seconds")

        sampled_df = pd.concat([sampled_r2, sampled_r1])
        if len(sampled_df) > n:
            sampled_df = sampled_df.sample(n=n, random_state=random_state)
        elif len(sampled_df) < n:
            remaining = temp_df.drop(sampled_df.index)
            extra_n = min(n - len(sampled_df), len(remaining))
            if extra_n > 0:
                extra = remaining.sample(n=extra_n, random_state=random_state)
                sampled_df = pd.concat([sampled_df, extra])
        


        return sampled_df.sample(frac=1, random_state=random_state).reset_index(drop=True)



