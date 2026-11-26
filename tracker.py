import argparse
import json
import re
import sqlite3
from decimal import Decimal, InvalidOperation
from pathlib import Path
import pandas as pd

COLUMNS = ['transaction_id','transaction_date','type','category','amount','account','description']

def parse_amount(value):
    if not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", str(value)):
        return None
    try:
        paise = int(Decimal(value) * 100)
        return paise if 0 < paise <= 10**14 else None
    except (InvalidOperation, ValueError):
        return None

def build(source, destination):
    out = Path(destination)
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output folder is not empty. Choose a new --output folder to preserve old results.')
    raw = pd.read_csv(source, dtype='string', keep_default_na=False)
    raw.columns = raw.columns.str.strip().str.lower()
    if raw.columns.duplicated().any():
        raise ValueError('Duplicate normalized column names')
    missing = set(COLUMNS[:-1]) - set(raw.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    if 'description' not in raw:
        raw['description'] = ''
    df = raw[COLUMNS].copy()
    for col in COLUMNS:
        df[col] = df[col].str.strip()
    df['type'] = df['type'].str.lower()
    df['source_row'] = range(2, len(df)+2)
    dates = pd.to_datetime(df.transaction_date, format='%Y-%m-%d', errors='coerce')
    amounts = df.amount.map(parse_amount)
    reasons = pd.Series('', index=df.index, dtype='string')
    checks = {
        'missing_id': df.transaction_id.eq(''),
        'duplicate_id': df.transaction_id.ne('') & df.transaction_id.duplicated(keep=False),
        'invalid_date': dates.isna() | ~df.transaction_date.str.fullmatch(r'\d{4}-\d{2}-\d{2}'),
        'invalid_type': ~df.type.isin(['income','expense','refund','transfer']),
        'missing_category': df.category.eq(''),
        'missing_account': df.account.eq(''),
        'invalid_amount': amounts.isna()
    }
    for reason, mask in checks.items():
        reasons.loc[mask] += reason + ';'
    valid = reasons.eq('')
    clean = df.loc[valid].copy()
    clean['amount_paise'] = amounts.loc[valid].astype('int64')
    clean['transaction_date'] = dates.loc[valid].dt.strftime('%Y-%m-%d')
    rejected = df.loc[~valid].copy()
    rejected['rejection_reason'] = reasons.loc[~valid]
    out.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out/'clean_transactions.csv', index=False)
    rejected.to_csv(out/'rejected_transactions.csv', index=False)
    with sqlite3.connect(out/'expenses.db') as conn:
        conn.execute("""CREATE TABLE transactions (
transaction_id TEXT PRIMARY KEY NOT NULL,
transaction_date TEXT NOT NULL,
type TEXT NOT NULL CHECK(type IN ('income','expense','refund','transfer')),
category TEXT NOT NULL,
amount_paise INTEGER NOT NULL CHECK(typeof(amount_paise)='integer' AND amount_paise>0),
account TEXT NOT NULL,
description TEXT NOT NULL)""")
        cols = ['transaction_id','transaction_date','type','category','amount_paise','account','description']
        conn.executemany('INSERT INTO transactions VALUES (?,?,?,?,?,?,?)', clean[cols].itertuples(index=False,name=None))
        conn.execute('CREATE INDEX idx_date ON transactions(transaction_date)')
        count,total = conn.execute('SELECT COUNT(*),COALESCE(SUM(amount_paise),0) FROM transactions').fetchone()
        assert count == len(clean) and total == int(clean.amount_paise.sum())
        reports = out/'reports'
        reports.mkdir()
        for query in sorted((Path(__file__).parent/'sql').glob('*.sql')):
            pd.read_sql_query(query.read_text(), conn).to_csv(reports/(query.stem+'.csv'), index=False)
    assert len(raw) == len(clean)+len(rejected)
    quality = {'input_rows':len(raw),'accepted_rows':len(clean),'rejected_rows':len(rejected),
               'currency':'INR','storage':'integer paise','refund_policy':'recognized on receipt date',
               'duplicate_policy':'all rows sharing an ID rejected',
               'scope':'complete CSV snapshot; no append imports'}
    (out/'quality_report.json').write_text(json.dumps(quality,indent=2))
    print(json.dumps(quality,indent=2))
    return out

if __name__ == '__main__':
    p=argparse.ArgumentParser(description='Personal expense and savings tracker: CSV to SQLite and reports')
    p.add_argument('--input',required=True)
    p.add_argument('--output',default='artifacts')
    a=p.parse_args()
    build(a.input,a.output)
