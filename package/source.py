import pandas as pd
from datetime import datetime, timedelta, time
import pytz

a = None    
b = None    
c = None 
d = None    
e = None     
unique_donor = None
current_date = None
unique_hospital = None

async def load_data():
    global a, b, c, d, e, unique_donor, current_date, unique_hospital
    try:
        print("Loading...")
        data_g = "https://dub.sh/ds-data-granular"
        data_f = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_facility.csv"
        data_s = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/donations_state.csv"
        data_nf = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_facility.csv"
        data_ns = "https://raw.githubusercontent.com/MoH-Malaysia/data-darah-public/main/newdonors_state.csv"

        a = pd.read_parquet(data_g)
        b = pd.read_csv(data_f)
        c = pd.read_csv(data_s)
        d = pd.read_csv(data_nf)
        e = pd.read_csv(data_ns)

        unique_donor = a['donor_id'].nunique()
        current_date = a['visit_date'].max()
        unique_hospital = d['hospital'].nunique()

        print("Files reloaded at", datetime.now(pytz.timezone('Asia/Singapore')).strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as f:
        print("Error reloading data:", f)