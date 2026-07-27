# Answer-oriented editorial contract

This directory defines content that can answer legitimate reader questions and
remain understandable when quoted outside the site. It does not authorize new
facts, estimates or promotional claims.

## Authority and boundaries

Profile facts continue to come from canonical front matter and Markdown under
`funds/` and `ecosystem/`. Editorial pages may explain the repository's method,
but cannot repair a missing profile fact or reinterpret a source.

The profile presentation contract in `profile-answer-contract.json` keeps six
concerns separate:

1. a concise localized summary;
2. normalized key facts;
3. a thesis explicitly declared by the entity;
4. signals observed in cited material;
5. sources;
6. the verification date.

`null`, `not_disclosed` and `NOT_DISCLOSED` are meaningful absence states. They
must not be replaced with estimates.

## Editorial page format

Every page under `editorial/<locale>/` uses JSON front matter validated by
`editorial-page.schema.json`. The body must:

- have one H1 matching the front matter title;
- answer the page's question in the first paragraph, in no more than 80 words;
- contain the required topic-specific sections;
- render every declared reference as a Markdown link;
- use descriptive link text;
- remain useful without navigation, structured data or JavaScript.

English is canonical. PT-BR and Spanish pages must point to the matching
English ID. Reference titles and URLs, dates, identifiers, code, numbers and
proper terms are protected exactly as defined by the profile translation
contract.

## Landing-page introductions

Country and category introductions use `templates/landing-page.en.md`.
Writers must describe only the entities actually represented by the filtered
catalog. Introductions cannot infer market size, quality, availability or
completeness. Two landing pages cannot reuse the same introduction merely with
a changed place or category name.

## Citation

The stable citation target is the repository and, after publication, the
versioned dataset export. A citation records:

- project name;
- repository or export URL;
- access date;
- commit SHA or release identifier when reproducibility matters.

A profile citation should also name the entity and link to its canonical
Markdown history. Citing the directory does not replace citing the underlying
source for a factual claim.

## Translation review

Automated translations are versioned content, never deploy-time output. Review
must compare each translation with its English canonical page and verify:

- the answer and every heading preserve meaning;
- distinctions between declared facts, observed signals and unavailable
  information remain explicit;
- reference titles and destinations are unchanged;
- names, identifiers, dates, values, currencies and code are unchanged;
- `translation_status` is updated only after review.

Corrections change the localized file and pass the same validator. They never
silently change canonical profile facts.

## Validation

```text
python tools/seo_geo/validate_editorial.py
python -m unittest discover -s tools/seo_geo/tests -p "test_editorial.py" -v
```
