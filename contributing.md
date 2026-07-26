# Contribution Guidelines

Please note that this project is released with a [Contributor Code of Conduct](code-of-conduct.md). By participating in this project you agree to abide by its terms.

## How to contribute

You will need a [GitHub account](https://github.com/join).

### Adding a fund

1. Check that the fund is not already on the list.
2. Check that the fund qualifies as a Venture Capital firm investing in Latin America.
3. Create a detail page under the appropriate `funds/` directory.
4. Add the fund to the appropriate README section in alphabetical order.
5. Use the normalized stage values below:

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

### Quality standards

- Only include funds that are active and investing in Latin America.
- Prefer current, official fund websites, thesis pages, FAQs, portfolio pages,
  and application forms.
- Provide accurate website and source links.
- Keep descriptions concise and factual.
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
