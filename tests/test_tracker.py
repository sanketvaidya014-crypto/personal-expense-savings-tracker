import tempfile
import unittest
from pathlib import Path
import sys
import sqlite3
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tracker import build, parse_amount

class TrackerTests(unittest.TestCase):
    def test_money(self):
        self.assertEqual(parse_amount('123.45'),12345)
        for bad in ['-1','0','1.234','1,000','NaN','inf','1e3']:
            self.assertIsNone(parse_amount(bad))

    def test_sample(self):
        root=Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as t:
            out=build(root/'data/sample_transactions.csv',Path(t)/'out')
            with sqlite3.connect(out/'expenses.db') as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],20)
                rows=conn.execute((root/'sql/01_monthly_savings.sql').read_text()).fetchall()
                self.assertEqual([r[3] for r in rows],[30500.0,39500.0,31200.0])
            self.assertEqual(len(list((out/'reports').glob('*.csv'))),6)
            with self.assertRaises(ValueError):
                build(root/'data/sample_transactions.csv',out)

    def test_duplicate_ids(self):
        with tempfile.TemporaryDirectory() as t:
            source=Path(t)/'input.csv'
            source.write_text('transaction_id,transaction_date,type,category,amount,account\nX,2026-01-01,income,Salary,1,Bank\nX,2026-01-01,income,Salary,1,Bank\n')
            out=build(source,Path(t)/'out')
            with sqlite3.connect(out/'expenses.db') as conn:
                self.assertEqual(conn.execute('SELECT COUNT(*) FROM transactions').fetchone()[0],0)

if __name__=='__main__':
    unittest.main()
