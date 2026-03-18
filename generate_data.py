# save as: generate_data.py
# run: pip install faker pandas numpy
# then: python generate_data.py
# outputs: contacts.csv, deals.csv, invoices.csv, orders.csv, customers.csv

import pandas as pd
import numpy as np
from faker import Faker
import random
import uuid
from datetime import datetime, timedelta
import os

fake = Faker('en_IN')
random.seed(42)
np.random.seed(42)

OUT = "data"
os.makedirs(OUT, exist_ok=True)

# ── CONFIG ────────────────────────────────────────────────────────────────────
N_CONTACTS   = 300_000
N_DEALS      = 50_000
N_CUSTOMERS  = 12_000
N_INVOICES   = 45_000
N_ORDERS     = 30_000

INDUSTRIES   = ["SaaS","FinTech","HealthTech","E-commerce","Enterprise IT",
                 "EdTech","Logistics","Manufacturing","Retail","BFSI"]
REGIONS      = ["India - South","India - North","India - West","India - East",
                 "SEA","Middle East","ANZ","UK","Europe","North America"]
SEGMENTS     = ["SMB","Mid-Market","Enterprise"]
SEG_W        = [0.55, 0.30, 0.15]
SOURCES      = ["Outbound SDR","Inbound Demo","Partner Referral","Events",
                 "Paid Search","Organic SEO","Customer Referral","LinkedIn"]
STAGES       = ["Prospect","Qualified","Demo","Proposal","Negotiation",
                 "Closed Won","Closed Lost"]
STAGE_W      = [0.20,0.18,0.17,0.14,0.08,0.13,0.10]
PRODUCTS     = ["Core Platform","Analytics Add-on","Enterprise Suite",
                 "API Access","Professional Services"]
REPS         = [fake.name() for _ in range(20)]
LIFECYCLE    = ["Subscriber","Lead","MQL","SQL","Opportunity","Customer","Evangelist"]

def rand_date(start="2022-01-01", end="2024-12-31"):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end,   "%Y-%m-%d")
    return s + timedelta(days=random.randint(0, (e - s).days))

def weighted_choice(options, weights):
    return random.choices(options, weights=weights, k=1)[0]

# ── CONTACTS ──────────────────────────────────────────────────────────────────
print("Generating contacts...")
contacts = []
for i in range(N_CONTACTS):
    created = rand_date()
    seg     = weighted_choice(SEGMENTS, SEG_W)
    source  = random.choice(SOURCES)
    lc      = weighted_choice(LIFECYCLE, [0.10,0.20,0.15,0.15,0.15,0.20,0.05])
    contacts.append({
        "contact_id":       f"CON-{i+1:07d}",
        "first_name":       fake.first_name(),
        "last_name":        fake.last_name(),
        "email":            fake.unique.email(),
        "phone":            fake.phone_number(),
        "company":          fake.company(),
        "job_title":        random.choice(["CEO","CTO","VP Sales","Head of Ops",
                                           "Marketing Manager","RevOps Lead",
                                           "CFO","Director of Engineering"]),
        "industry":         random.choice(INDUSTRIES),
        "region":           random.choice(REGIONS),
        "segment":          seg,
        "source":           source,
        "lifecycle_stage":  lc,
        "owner_rep":        random.choice(REPS),
        "created_date":     created.date(),
        "last_activity_date": (created + timedelta(days=random.randint(0, 400))).date(),
        "email_opt_out":    random.choices([True, False], weights=[0.08, 0.92])[0],
        "data_complete_pct":random.randint(40, 100),
        "lead_score":       random.randint(0, 100),
        "country":          fake.country(),
    })
    if i % 50000 == 0:
        print(f"  contacts: {i:,}")

df_contacts = pd.DataFrame(contacts)
df_contacts.to_csv(f"{OUT}/contacts.csv", index=False)
print(f"  ✓ contacts.csv ({len(df_contacts):,} rows)")

# ── CUSTOMERS ─────────────────────────────────────────────────────────────────
print("Generating customers...")
customer_contact_ids = random.sample(df_contacts["contact_id"].tolist(), N_CUSTOMERS)
customers = []
for cid in customer_contact_ids:
    row = df_contacts[df_contacts.contact_id == cid].iloc[0]
    acq = rand_date()
    seg = row["segment"]
    acv = {"SMB": random.randint(5,40), "Mid-Market": random.randint(30,150),
            "Enterprise": random.randint(100,500)}[seg] * 1000
    is_churned = random.random() < 0.12
    customers.append({
        "customer_id":       f"CUS-{len(customers)+1:06d}",
        "contact_id":        cid,
        "company":           row["company"],
        "segment":           seg,
        "industry":          row["industry"],
        "region":            row["region"],
        "acquisition_date":  acq.date(),
        "churn_date":        (acq + timedelta(days=random.randint(60,730))).date() if is_churned else None,
        "is_churned":        is_churned,
        "acv":               acv,
        "product":           random.choice(PRODUCTS),
        "owner_rep":         row["owner_rep"],
        "nps_score":         random.randint(0, 10),
        "health_score":      random.randint(20, 100),
    })

df_customers = pd.DataFrame(customers)
df_customers.to_csv(f"{OUT}/customers.csv", index=False)
print(f"  ✓ customers.csv ({len(df_customers):,} rows)")

# ── DEALS ─────────────────────────────────────────────────────────────────────
print("Generating deals...")
IND_BASE = {"SaaS":45,"FinTech":120,"HealthTech":85,"E-commerce":35,
            "Enterprise IT":200,"EdTech":25,"Logistics":65,"Manufacturing":90,
            "Retail":30,"BFSI":110}
PROBS    = {"Prospect":8,"Qualified":22,"Demo":38,"Proposal":58,"Negotiation":76,
            "Closed Won":100,"Closed Lost":0}
LOSS_REASONS = ["Price","Competitor","No Budget","No Decision","Timing","Product Fit"]
WIN_REASONS  = ["ROI","Relationships","Product","Pricing","Support","Speed"]

deals = []
# 80% deals linked to contacts, 20% orphan
linked_ids   = random.choices(df_contacts["contact_id"].tolist(), k=int(N_DEALS * 0.80))
orphan_count = N_DEALS - len(linked_ids)

for i in range(N_DEALS):
    cid   = linked_ids[i] if i < len(linked_ids) else None
    if cid:
        crow = df_contacts[df_contacts.contact_id == cid].iloc[0]
        ind  = crow["industry"]
        seg  = crow["segment"]
        reg  = crow["region"]
        rep  = crow["owner_rep"]
        src  = crow["source"]
    else:
        ind  = random.choice(INDUSTRIES)
        seg  = weighted_choice(SEGMENTS, SEG_W)
        reg  = random.choice(REGIONS)
        rep  = random.choice(REPS)
        src  = random.choice(SOURCES)

    stage   = weighted_choice(STAGES, STAGE_W)
    base    = IND_BASE.get(ind, 50)
    amt     = round(base * random.uniform(0.4, 2.5)) * 1000
    created = rand_date()
    cycle   = random.randint(7, 180)
    closed  = (created + timedelta(days=cycle)).date() if stage in ["Closed Won","Closed Lost"] else None
    acts    = random.randint(2, 60)

    deals.append({
        "deal_id":           f"DEAL-{i+1:06d}",
        "contact_id":        cid,
        "deal_name":         f"{fake.company()} - {random.choice(PRODUCTS)}",
        "stage":             stage,
        "amount":            amt,
        "probability":       PROBS[stage],
        "industry":          ind,
        "segment":           seg,
        "region":            reg,
        "source":            src,
        "product":           random.choice(PRODUCTS),
        "owner_rep":         rep,
        "created_date":      created.date(),
        "close_date":        closed,
        "sales_cycle_days":  cycle if closed else None,
        "activity_count":    acts,
        "win_reason":        random.choice(WIN_REASONS) if stage == "Closed Won" else None,
        "loss_reason":       random.choice(LOSS_REASONS) if stage == "Closed Lost" else None,
        "forecast_category": random.choice(["Commit","Best Case","Pipeline","Omitted"]),
        "is_upsell":         random.random() < 0.15,
    })
    if i % 10000 == 0:
        print(f"  deals: {i:,}")

df_deals = pd.DataFrame(deals)
df_deals.to_csv(f"{OUT}/deals.csv", index=False)
print(f"  ✓ deals.csv ({len(df_deals):,} rows)")

# ── INVOICES ─────────────────────────────────────────────────────────────────
print("Generating invoices...")
won_deals = df_deals[df_deals.stage == "Closed Won"]["deal_id"].tolist()

invoices = []
for i in range(N_INVOICES):
    deal_id  = random.choice(won_deals) if random.random() < 0.85 else None
    issued   = rand_date()
    due      = issued + timedelta(days=30)
    is_paid  = random.random() < 0.82
    paid_on  = (issued + timedelta(days=random.randint(1, 60))).date() if is_paid else None
    amount   = random.randint(5, 500) * 1000
    discount = round(random.uniform(0, 0.25), 2) if random.random() < 0.3 else 0
    invoices.append({
        "invoice_id":     f"INV-{i+1:06d}",
        "deal_id":        deal_id,
        "issued_date":    issued.date(),
        "due_date":       due.date(),
        "paid_date":      paid_on,
        "is_paid":        is_paid,
        "amount":         amount,
        "discount_pct":   discount,
        "net_amount":     round(amount * (1 - discount)),
        "is_overdue":     not is_paid and datetime(2025, 1, 1) > due,
        "days_to_pay":    (paid_on - issued.date()).days if paid_on else None,
        "currency":       "INR",
        "status":         "Paid" if is_paid else ("Overdue" if datetime(2025,1,1).date() > due.date() else "Pending"),
    })

df_invoices = pd.DataFrame(invoices)
df_invoices.to_csv(f"{OUT}/invoices.csv", index=False)
print(f"  ✓ invoices.csv ({len(df_invoices):,} rows)")

# ── ORDERS / BOOKINGS ─────────────────────────────────────────────────────────
print("Generating orders...")
orders = []
for i in range(N_ORDERS):
    cust     = random.choice(df_customers["customer_id"].tolist())
    crow     = df_customers[df_customers.customer_id == cust].iloc[0]
    ordered  = rand_date()
    delivered= (ordered + timedelta(days=random.randint(1, 45))).date()
    orders.append({
        "order_id":       f"ORD-{i+1:06d}",
        "customer_id":    cust,
        "product":        random.choice(PRODUCTS),
        "segment":        crow["segment"],
        "region":         crow["region"],
        "industry":       crow["industry"],
        "order_date":     ordered.date(),
        "delivery_date":  delivered,
        "amount":         random.randint(10, 300) * 1000,
        "status":         random.choice(["Delivered","Processing","Cancelled","Refunded"]),
        "payment_method": random.choice(["Bank Transfer","Credit Card","UPI","Cheque"]),
        "rep":            crow["owner_rep"],
        "is_renewal":     random.random() < 0.35,
    })

df_orders = pd.DataFrame(orders)
df_orders.to_csv(f"{OUT}/orders.csv", index=False)
print(f"  ✓ orders.csv ({len(df_orders):,} rows)")

print("\n✅ Done. Files in ./data/")
print(f"   contacts.csv  → {len(df_contacts):,} rows")
print(f"   deals.csv     → {len(df_deals):,} rows")
print(f"   customers.csv → {len(df_customers):,} rows")
print(f"   invoices.csv  → {len(df_invoices):,} rows")
print(f"   orders.csv    → {len(df_orders):,} rows")