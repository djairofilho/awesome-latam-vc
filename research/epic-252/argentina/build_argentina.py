#!/usr/bin/env python3
"""Build the deterministic Argentina fund re-audit and publication."""
from __future__ import annotations
import argparse, importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("mx",ROOT/"research/epic-249/mexico/build_mexico.py"); assert spec and spec.loader
mx=importlib.util.module_from_spec(spec); spec.loader.exec_module(mx)
SOURCES=[
("ar-arcap","maps","https://arcap.org/","ARCAP"),("ar-byma","launches","https://www.byma.com.ar/newsroom/byma-relanza-su-fondo-de-cvc-bajo-el-nombre-byma-ventures","BYMA Ventures"),
("ar-byma-report","allocators","https://data-widgets.byma.com.ar/wp-content/uploads/2025/03/MEMORIA-2024-INGLES-EEFF-2_compressed.pdf","BYMA 2024 report"),
("ar-embarca","regional_sources","https://www.embarca.tech/inicio/","Embarca"),("ar-embarca-portfolio","official_portfolios","https://www.embarca.tech/portfolio/","Embarca portfolio"),
("ar-sancor","official_portfolios","https://sancorsegurosventures.com/en/","Sancor Seguros Ventures"),
("ar-shefa","official_portfolios","https://shefa.vc/","SHEFA Holding"),("ar-irsa","allocators","https://www.irsa.com.ar/wp-content/uploads/2024/08/MemoriaIRSAFY23.pdf","IRSA report"),
("ar-galicia","historical_delta","https://galicia-ventures.ar/","Galicia Ventures"),("ar-kamay","events","https://kamayventures.com/","Kamay Ventures"),
("ar-incutex","blind_search","https://incutex.com.ar/","Incutex"),("ar-overboost","blind_search","https://overboost.vc/","Overboost")]
CANDIDATES=[
("fund-ar-byma-ventures","BYMA Ventures","eligible","funds/argentina/byma-ventures.md",["ar-byma","ar-byma-report"]),
("fund-ar-embarca-ventures","Embarca Ventures","eligible","funds/argentina/embarca-ventures.md",["ar-embarca","ar-embarca-portfolio"]),
("fund-ar-sancor-seguros-ventures","Sancor Seguros Ventures","eligible","funds/argentina/sancor-seguros-ventures.md",["ar-sancor"]),
("fund-ar-shefa-holding","SHEFA Holding","eligible","funds/argentina/shefa-holding.md",["ar-shefa","ar-irsa"]),
("fund-ar-galicia-ventures","Galicia Ventures","duplicate","funds/regional/galicia-ventures.md",["ar-galicia"]),
("fund-ar-kamay-ventures","Kamay Ventures","duplicate","funds/regional/kamay-ventures.md",["ar-kamay"]),
("fund-ar-overboost","Overboost","insufficient_evidence",None,["ar-overboost"]),
("fund-ar-incutex","Incutex","routed_accelerators","epic-62-accelerators",["ar-incutex"])]
REASONS={
"fund-ar-byma-ventures":"The official relaunch and annual report confirm a CVC vehicle with seven startup investments and current activity.",
"fund-ar-embarca-ventures":"The official site reports 17 startups backed by Fund F1 and the formation of Fund F2.",
"fund-ar-sancor-seguros-ventures":"The official site confirms a CVC thesis, direct investment, a current portfolio, and an open application route.",
"fund-ar-shefa-holding":"The current official site identifies SHEFA Holding as an investment holding with a recurring direct venture portfolio; it is included as an equivalent vehicle, not as a traditional fund.",
"fund-ar-galicia-ventures":"The entity already has a current canonical profile at funds/regional/galicia-ventures.md.",
"fund-ar-kamay-ventures":"The entity already has a current canonical profile at funds/regional/kamay-ventures.md.",
"fund-ar-overboost":"No sufficiently current official evidence was found to confirm active recurring investment by the cutoff date.",
"fund-ar-incutex":"The official site identifies an accelerator, so the candidate is routed to the accelerator inventory in epic #62."
}
def P(dest,name,summary,site,sources,focuses,signal):
 return {"destination":dest,"name":name,"summary":{"en":summary,"es":summary,"pt-BR":summary},"base":{"kind":"country","code":"AR"},"countries":["AR","LATAM"],"stages":["not_disclosed"],"focuses":focuses,"website":site,"route":site,"sources":sources,"signal":{"en":signal,"es":signal,"pt-BR":signal}}
PROFILES={
"byma-ventures":P("funds/argentina/byma-ventures.md","BYMA Ventures","BYMA Ventures is the Argentine exchange group's corporate venture capital fund for early-stage Latin American startups.","https://www.byma.com.ar/",[{"title":"BYMA relaunches its CVC fund","url":SOURCES[1][2],"kind":"official_activity"},{"title":"BYMA 2024 annual report","url":SOURCES[2][2],"kind":"official_activity"}],["fintech","market_infrastructure","cybersecurity"],"BYMA reported seven startup investments and an active portfolio strategy in its 2024 reporting."),
"embarca-ventures":P("funds/argentina/embarca-ventures.md","Embarca Ventures","Embarca Ventures is a Mendoza-based venture capital fund investing in technology startups across Argentina and Latin America.","https://www.embarca.tech/inicio/",[{"title":"Embarca Ventures","url":SOURCES[3][2],"kind":"official_thesis"},{"title":"Portfolio","url":SOURCES[4][2],"kind":"official_portfolio"}],["technology"],"The official site reports 17 startups backed by its first fund and formation of Fund F2."),
"sancor-seguros-ventures":P("funds/argentina/sancor-seguros-ventures.md","Sancor Seguros Ventures","Sancor Seguros Ventures is Sancor Seguros Group's Argentine corporate venture capital fund for scalable technology startups.","https://sancorsegurosventures.com/en/",[{"title":"Sancor Seguros Ventures","url":SOURCES[5][2],"kind":"official_portfolio"}],["insurtech","technology"],"The current official portfolio and open application route confirm recurring direct investment."),
"shefa-holding":P("funds/argentina/shefa-holding.md","SHEFA Holding","SHEFA Holding is an Argentine investment holding with a recurring direct venture portfolio; it is listed as an equivalent vehicle rather than a traditional fund.","https://shefa.vc/",[{"title":"SHEFA Holding portfolio","url":SOURCES[6][2],"kind":"official_portfolio"},{"title":"IRSA annual report","url":SOURCES[7][2],"kind":"official_activity"}],["real_estate_technology","agtech"],"The current site presents the SHEFA Holding identity and portfolio, while IRSA reporting documents the earlier Shefa Ventures corporate venture operation.")}
LOCALIZED={
"byma-ventures":{"es":("BYMA Ventures es el fondo de capital de riesgo corporativo del grupo bursátil argentino para startups latinoamericanas en etapa temprana.","BYMA informó siete inversiones en startups y una estrategia activa de portafolio en su reporte de 2024."),"pt-BR":("A BYMA Ventures é o fundo de venture capital corporativo do grupo da bolsa argentina para startups latino-americanas em estágio inicial.","A BYMA informou sete investimentos em startups e uma estratégia ativa de portfólio em seu relatório de 2024.")},
"embarca-ventures":{"es":("Embarca Ventures es un fondo de capital de riesgo de Mendoza que invierte en startups de tecnología de Argentina y América Latina.","El sitio oficial informa 17 startups respaldadas por su primer fondo y la formación del Fondo F2."),"pt-BR":("A Embarca Ventures é um fundo de venture capital de Mendoza que investe em startups de tecnologia na Argentina e na América Latina.","O site oficial informa 17 startups apoiadas por seu primeiro fundo e a formação do Fundo F2.")},
"sancor-seguros-ventures":{"es":("Sancor Seguros Ventures es el fondo de capital de riesgo corporativo argentino del Grupo Sancor Seguros para startups tecnológicas escalables.","El portafolio oficial atual y la convocatoria abierta confirman la inversión directa recurrente."),"pt-BR":("A Sancor Seguros Ventures é o fundo argentino de venture capital corporativo do Grupo Sancor Seguros para startups de tecnologia escaláveis.","O portfólio oficial atual e o canal aberto para inscrições confirmam o investimento direto recorrente.")},
"shefa-holding":{"es":("SHEFA Holding es un holding de inversión argentino con un portafolio recurrente de inversiones directas en startups; se incluye como vehículo equivalente y no como fondo tradicional.","El sitio actual presenta la identidad y el portafolio de SHEFA Holding, mientras que los reportes de IRSA documentan la operación corporativa anterior, Shefa Ventures."),"pt-BR":("A SHEFA Holding é uma holding de investimentos argentina com um portfólio recorrente de investimentos diretos em startups; está listada como veículo equivalente, não como fundo tradicional.","O site atual apresenta a identidade e o portfólio da SHEFA Holding, enquanto os relatórios da IRSA documentam a operação corporativa anterior, Shefa Ventures.")}
}
def outputs():
 src=[{"schema_version":"1.0","source_id":a,"source_family":b,"initial_url":c,"source":d,"research_channel":"non_regulatory","is_regulatory":False,"discovery_allowed":True,"accessed_on":mx.CUTOFF,"result":"complete"} for a,b,c,d in SOURCES]
 cand=[{"schema_version":"1.0","candidate_id":a,"name":b,"aliases":["Shefa Ventures"] if a=="fund-ar-shefa-holding" else [],"decision":c,"destination":d,"discovery_source_ids":e,"official_evidence_ids":["ev-"+a],"reason":REASONS[a],"status":"decided","cutoff_date":mx.CUTOFF} for a,b,c,d,e in CANDIDATES]
 evidence=[{"schema_version":"1.0","evidence_id":"ev-"+a,"candidate_id":a,"source_ids":e,"accessed_on":mx.CUTOFF,"decision":c,"claims":[{"field":"identity","result":"confirmed"},{"field":"terminal_decision","result":c}],"summary":REASONS[a]} for a,b,c,d,e in CANDIDATES]
 counts={}; [counts.__setitem__(x[2],counts.get(x[2],0)+1) for x in CANDIDATES]
 eligible=[x for x in CANDIDATES if x[2]=="eligible"]
 exclusion_population=sorted(x[0] for x in CANDIDATES if x[2] in {"duplicate","insufficient_evidence"})
 exclusion_sample=exclusion_population[:1]
 report={"schema_version":"1.0","epic":252,"issues":[274,275,276,277,278],"market":"Argentina","cutoff_date":mx.CUTOFF,"status":"passed","sources":{"planned":len(src),"non_regulatory_share":1.0},"candidates":{"rows":len(cand),"decision_counts":counts},"regulatory":{"name":"Comisión Nacional de Valores de Argentina","queries":0,"eligibility_use":False},"review":{"eligible_reviewed":4,"routed_reviewed":1,"exclusion_population":len(exclusion_population),"exclusion_sample_reviewed":len(exclusion_sample),"exclusion_sample_rule":"sort candidate_id ascending and take ceil(population/3)","exclusion_sample_source":"candidates.jsonl decisions duplicate or insufficient_evidence","exclusion_sample_ids":exclusion_sample,"blind_new_candidates":2,"blind_new_eligible":0,"independent_review":"passed","reviewer":"integrator","reviewed_on":"2026-07-30","review_reconciled":True,"critical_findings":0,"high_findings":0},"publication":{"batch_count":1,"candidate_count":4,"profile_file_count":12},"limitations":["Cobertura auditada; não representa totalidade do mercado argentino."]}
 freeze={**report,"status":"frozen","publication":{"batch_count":1,"batch_size_limit":10,"candidates":[{"candidate_id":x[0],"destination":x[3]} for x in eligible]}}
 readme=f"# Reauditoria de fundos — Argentina\n\nData de corte: `{mx.CUTOFF}`. Cobertura auditada, sem alegar totalidade.\n\n- {len(src)} fontes não regulatórias;\n- 8 candidatos: 4 elegíveis, 2 duplicatas, 1 insuficiente e 1 encaminhado;\n- zero consultas à Comisión Nacional de Valores de Argentina;\n- amostra determinística de exclusões: ordenar `candidate_id` e revisar o primeiro `ceil(n/3)` de `candidates.jsonl` com decisões `duplicate` ou `insufficient_evidence` ({', '.join(exclusion_sample)});\n- revisão independente de #277 aprovada por `integrator` em 2026-07-30, sem achados críticos ou altos.\n"
 out={HERE/"source-inventory.jsonl":mx.jsonl_bytes(src),HERE/"candidates.jsonl":mx.jsonl_bytes(cand),HERE/"evidence.jsonl":mx.jsonl_bytes(evidence),HERE/"audit-report.json":mx.json_bytes(report),HERE/"freeze-manifest.json":mx.json_bytes(freeze),HERE/"README.md":readme.encode()}
 for slug,p in PROFILES.items():
  for loc in ("en","es","pt-BR"):
   path=ROOT/p["destination"] if loc=="en" else ROOT/"translations"/loc/p["destination"]
   p_loc={**p,"summary":dict(p["summary"]),"signal":dict(p["signal"])}
   if loc!="en": p_loc["summary"][loc],p_loc["signal"][loc]=LOCALIZED[slug][loc]
   body=mx.markdown(slug,p_loc,loc)
   if slug=="shefa-holding": body=body.replace(b'"aliases": []',b'"aliases": ["Shefa Ventures"]',1)
   out[path]=body
 return out
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--check",action="store_true"); args=ap.parse_args(); out=outputs()
 if args.check:
  bad=[p for p,b in out.items() if not p.is_file() or p.read_bytes()!=b]
  if bad: raise SystemExit("Divergent: "+", ".join(map(str,bad)))
 else:
  for p,b in out.items(): p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b)
 print("Argentina re-audit verified." if args.check else "Argentina re-audit generated.")
if __name__=="__main__": main()
