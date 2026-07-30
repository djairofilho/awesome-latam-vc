# Contribution Guidelines

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms.

## How to contribute

You will need a [GitHub account](https://github.com/join).

### Adding a fund

1. Check that the fund is not already on the list.
2. Check that the fund qualifies as a Venture Capital firm investing in Latin America.
3. Create a detail page under the appropriate `funds/` directory.
4. Add the fund to the appropriate README section in alphabetical order.
5. Classify the fund by its primary investment type and geographic base.
6. Use the normalized stage values below:

Use one of these normalized fund types:

- `Venture capital`
- `Corporate venture capital`
- `Co-investment fund`
- `Fund investor and co-investor`
- `Fund investor and direct investor`
- `Venture studio and venture capital`
- `Venture builder and venture capital`
- `Accelerator and venture capital`
- `Not publicly disclosed`

Fund type and geography are separate classifications. Place a fund under the
country where it is based, under `regional/` when it is based in Latin America
and explicitly invests across the region, or under `multi-country/` when it is
based outside Latin America and has a regional investment presence. Do not
create geographic sections for investor types such as corporate venture capital
or fund of funds.

Keep an organization in `funds/` only when current official sources confirm that
it invests capital directly in startups through a recurring fund, corporate
venture program, co-investment vehicle, accelerator fund, or studio fund. Move
organizations that only connect investors and founders, invest only in other
funds, operate crowdfunding platforms, or provide public support programs to
`ecosystem/`.

For hybrid organizations, distinguish investment activity from acceleration,
company building, community, or advisory services. If direct startup investment
or access for external founders cannot be verified, use
`Not publicly disclosed` and record the missing evidence instead of inferring
an answer.

- `Pre-seed`
- `Seed`
- `Series A`
- `Series B`
- `Growth`
- `Multi-stage`

Combine values when the fund explicitly covers adjacent stages, for example
`Pre-seed, Seed, and Series A`. Use `Not publicly disclosed` only after checking
the fund's official sources. Use `Pending research` when the fund has not yet
been researched under the enriched profile standard.

### Fund detail page

Use this structure for every enriched profile:

```markdown
# Fund name

A short, factual description.

## Investment profile

- **Website:** https://example.com/
- **Fund type:** Venture capital
- **Direct startup investment:** Yes
- **Open to external founders:** Yes
- **Stage at entry:** Pre-seed and Seed
- **Follow-on stages:** Not publicly disclosed
- **Focus:** Concise description of the declared sector or thesis
- **Geography:** Countries or regions explicitly covered
- **Initial check:** Amount and currency, or `Not publicly disclosed`
- **Investment role:** Lead, co-investor, both, or `Not publicly disclosed`
- **Business models:** B2B, B2C, SaaS, deep tech, or another declared model
- **Portfolio size:** Number, methodology, and date context
- **Selected companies:** Three to five representative companies
- **Submit a startup:** Direct application URL or contact

## Declared thesis

A factual summary based on official sources.

## Portfolio signals

Observed portfolio patterns, clearly identified as observations rather than the
fund's official mandate.

## Sources

- [Descriptive source name](https://example.com/source)

**Last verified:** YYYY-MM-DD
```

The README row must use this format:

```markdown
| [Fund name](funds/region/fund-name.md) | Seed | Fintech | Latin America |
```

### Updating a fund

If a fund's information is outdated (website, name, focus), please submit a pull request with the correction.

### Canonical metadata and translations

New or migrated profiles use the
[SEO/GEO metadata contract](research/seo-geo/contract/README.md). The Markdown
file remains the auditable source; its front matter provides normalized data
for the site, filters, structured data and exports.

Use a JSON object between `---` delimiters. The complete schema, enums and
examples are versioned in `research/seo-geo/contract/`.

```markdown
---
{
  "schema_version": "1.0",
  "id": "fund:example-fund:en",
  "entity_id": "fund:example-fund",
  "slug": "example-fund",
  "name": "Example Fund",
  "entity_type": "fund",
  "locale": "en",
  "translation_of": null,
  "translation_status": "canonical"
}
---
```

The schema requires additional geography, stage, focus, URL, source and
verification fields; the shortened block above only illustrates identity.
Copy a complete valid example rather than filling fields from memory.

For translations:

- keep the same `entity_id`, `slug`, name, aliases and normalized facts;
- give each locale a unique `id`;
- point `translation_of` to the exact English canonical profile ID;
- localize the summary and Markdown prose;
- do not translate proper names, brands, URLs, identifiers, source titles,
  link destinations, code, numbers, values, currencies or dates;
- do not use automatic or deploy-time translation;
- use `needs_review` until a human review is complete.

Validate the full localized entity together so equivalence checks can compare
every translation with its canonical profile:

```text
python tools/seo_geo/validate_profiles.py path/to/localized/profile/directory
```

### Quality standards

- Only include funds that are active and investing in Latin America.
- Prefer current, official fund websites, thesis pages, FAQs, portfolio pages,
  and application forms.
- Provide accurate website and source links.
- Keep descriptions concise and factual.
- Classify fund type from current official sources. Do not infer it from the
  previous directory, the fund's name, or portfolio composition.
- Confirm direct startup investment and whether external founders can apply from
  current official sources. A portfolio alone does not establish the
  organization's current operating model.
- Do not infer a fund's official thesis, check size, stage, or lead preference
  from third-party databases or portfolio composition.
- Keep declared thesis information separate from observed portfolio patterns.
- Use the project's local portfolio dataset only as supporting analysis and
  label it clearly when cited.
- Record the date on which the profile was last verified.
- Follow alphabetical order within each section.

## Pull Request Process

1. Fork the repository.
2. Make your changes in a new branch.
3. Submit a pull request with a clear description of what you changed and why.
4. Ensure your changes follow the format guidelines above.
5. Link to the official sources that validate the entry. Use third-party sources
   only when no official source exists and identify them as secondary.

## Licensing contributions

By contributing original work, you agree that it will be made available under
the license that applies to its scope:

- catalog entries, profiles, translations, datasets, research records, and
  editorial content use CC0 1.0 Universal;
- site code, scripts, tests, automation, and tools use the MIT License.

See the [repository licensing policy](LICENSE) for the complete path and
material-type rules. Do not submit third-party material unless its terms permit
redistribution under the applicable project license.
