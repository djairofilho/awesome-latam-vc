import importlib.util,json,unittest
from pathlib import Path
H=Path(__file__).parent; s=importlib.util.spec_from_file_location("b",H/"build_argentina.py"); b=importlib.util.module_from_spec(s); s.loader.exec_module(b)
class T(unittest.TestCase):
 def test_contract(self):
  r=json.loads(b.outputs()[H/"audit-report.json"]); self.assertEqual(1.0,r["sources"]["non_regulatory_share"]); self.assertEqual(0,r["regulatory"]["queries"]); self.assertEqual(4,r["publication"]["candidate_count"]); self.assertEqual("passed",r["review"]["independent_review"]); self.assertTrue(r["review"]["review_reconciled"])
 def test_sample(self):
  r=json.loads(b.outputs()[H/"audit-report.json"]); self.assertEqual(["fund-ar-galicia-ventures"],r["review"]["exclusion_sample_ids"]); self.assertIn("ceil(population/3)",r["review"]["exclusion_sample_rule"])
 def test_evidence(self):
  rows=[json.loads(x) for x in b.outputs()[H/"evidence.jsonl"].decode().splitlines()]; self.assertEqual(8,len(rows)); self.assertTrue(all(x["summary"] and x["claims"] for x in rows))
 def test_deterministic(self): self.assertEqual(b.outputs(),b.outputs())
if __name__=="__main__":unittest.main()
