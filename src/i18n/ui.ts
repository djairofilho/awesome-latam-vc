import type { Category } from "../lib/catalog";

export const ui = {
  en: {
    languageName: "English",
    languageNavigation: "Choose language",
    skipLink: "Skip to content",
    home: "Overview",
    catalog: "Catalog",
    editorial: "Methodology",
    editorialNavigation: "Editorial pages",
    lastReviewed: "Last reviewed",
    viewSource: "View Markdown source",
    translationNotice: "This page includes machine-translated content that was reviewed before publication.",
    suggestCorrection: "Suggest a correction.",
    breadcrumbNavigation: "Breadcrumb",
    primaryNavigation: "Primary navigation",
    githubLabel: "GitHub",
    sourceFooter: "Open data, official sources and an auditable history on",
    staticFooter: "Built as static HTML. No runtime server.",
    homeTitle: "Awesome LatAm VC · The open funding directory",
    homeDescription:
      "An open, source-backed directory of venture funds and startup funding programs across Latin America.",
    heroKicker: "Open funding intelligence for Latin America",
    heroTitle: "Find the capital paths that are actually documented.",
    heroBody:
      "Venture funds, accelerators, angel networks, funding platforms and public programs. Every entry stays connected to its Markdown source, official evidence and Git history.",
    browseCatalog: "Browse the catalog",
    inspectSource: "Inspect the source",
    snapshot: "Current snapshot",
    canonicalProfiles: "canonical profiles",
    geographies: "Geographies",
    categories: "Categories",
    categoryHeading: "One catalog, five routes to funding",
    categoryBody:
      "Counts come from the canonical files at build time. New accepted profiles appear automatically without copying content into the site.",
    principlesHeading: "Built for verification, not hype",
    principles: [
      ["Canonical Markdown", "The repository remains the source of truth."],
      [
        "Structured evidence",
        "Official links and verification dates travel with profiles.",
      ],
      ["Static by default", "Every published page works without a runtime server."],
    ],
    catalogTitle: "Latin American funding catalog · Awesome LatAm VC",
    catalogDescription:
      "Browse the canonical Awesome LatAm VC funding catalog by entity type.",
    catalogKicker: "Canonical catalog",
    profileCount: (count: number) =>
      `${count} profiles, directly from the repository.`,
    catalogIntro:
      "Browse every canonical entry by entity type. Localized profile bodies arrive in reviewed translation batches; identity and source links remain stable.",
    jumpNavigation: "Jump to a catalog category",
    profilePlural: "profiles",
    sourceLabel: "View canonical Markdown",
    directoryHeading: "Search and filter",
    searchLabel: "Search profiles",
    searchPlaceholder: "Name, focus, stage or geography",
    clearFilters: "Clear search and filters",
    submitSearch: "Search",
    facetLabels: {
      entity_type: "Entity type",
      geography: "Geography",
      stage: "Stage",
      focus: "Focus",
    },
    resultCount: "{count} profiles",
    loadingResults: "Searching profiles…",
    noResults: "No profiles match this search and filter combination.",
    searchError:
      "Search is temporarily unavailable. Showing local filter results.",
    noScript:
      "All profile links remain available below. Search and combined filters require JavaScript.",
    browseCategories: "Browse categories",
    browseCountries: "Browse countries",
    profileSource: "Canonical source",
    profileHistory: "File history",
    officialWebsite: "Official website",
    founderRoute: "Founder route",
    verifiedOn: "Verified on",
    coverage: "Coverage",
    stages: "Stages",
    focuses: "Focuses",
    categoryLandingTitle: (label: string) => label,
    categoryLandingDescription: (label: string) =>
      `Browse ${label.toLocaleLowerCase()} in the Awesome LatAm VC catalog.`,
    countryLandingTitle: (country: string) => `Funding directory for ${country}`,
    countryLandingDescription: (country: string) =>
      `Browse documented funding entities connected to ${country}.`,
    categoryLabels: {
      fund: "Venture funds",
      accelerator: "Accelerators",
      angel_network: "Angel networks",
      funding_platform: "Funding platforms",
      public_program: "Public programs",
    } satisfies Record<Category, string>,
  },
  "pt-BR": {
    languageName: "Português (Brasil)",
    languageNavigation: "Escolher idioma",
    skipLink: "Pular para o conteúdo",
    home: "Visão geral",
    catalog: "Catálogo",
    editorial: "Metodologia",
    editorialNavigation: "Páginas editoriais",
    lastReviewed: "Última revisão",
    viewSource: "Ver fonte em Markdown",
    translationNotice:
      "Esta página inclui conteúdo traduzido automaticamente e revisado antes da publicação.",
    suggestCorrection: "Sugira uma correção.",
    breadcrumbNavigation: "Trilha de navegação",
    primaryNavigation: "Navegação principal",
    githubLabel: "GitHub",
    sourceFooter: "Dados abertos, fontes oficiais e histórico auditável no",
    staticFooter: "HTML estático, sem servidor em tempo de execução.",
    homeTitle: "Awesome LatAm VC · Diretório aberto de financiamento",
    homeDescription:
      "Diretório aberto e baseado em fontes de fundos e programas de financiamento para startups na América Latina.",
    heroKicker: "Informação aberta sobre financiamento na América Latina",
    heroTitle: "Encontre caminhos de capital realmente documentados.",
    heroBody:
      "Fundos de venture capital, aceleradoras, redes-anjo, plataformas de captação e programas públicos. Cada entrada permanece ligada ao Markdown canônico, às evidências oficiais e ao histórico Git.",
    browseCatalog: "Explorar o catálogo",
    inspectSource: "Consultar a fonte",
    snapshot: "Retrato atual",
    canonicalProfiles: "perfis canônicos",
    geographies: "Geografias",
    categories: "Categorias",
    categoryHeading: "Um catálogo, cinco caminhos para financiamento",
    categoryBody:
      "As contagens vêm dos arquivos canônicos no momento do build. Novos perfis aceitos aparecem automaticamente, sem copiar conteúdo para o site.",
    principlesHeading: "Feito para verificação, sem exageros",
    principles: [
      ["Markdown canônico", "O repositório permanece como fonte oficial."],
      [
        "Evidência estruturada",
        "Links oficiais e datas de verificação acompanham os perfis.",
      ],
      [
        "Estático por padrão",
        "Todas as páginas funcionam sem servidor em tempo de execução.",
      ],
    ],
    catalogTitle: "Catálogo de financiamento latino-americano · Awesome LatAm VC",
    catalogDescription:
      "Explore o catálogo canônico do Awesome LatAm VC por tipo de entidade.",
    catalogKicker: "Catálogo canônico",
    profileCount: (count: number) =>
      `${count} perfis, diretamente do repositório.`,
    catalogIntro:
      "Explore todas as entradas canônicas por tipo. Os corpos traduzidos chegam em lotes revisados; a identidade e os links das fontes permanecem estáveis.",
    jumpNavigation: "Ir para uma categoria do catálogo",
    profilePlural: "perfis",
    sourceLabel: "Ver Markdown canônico",
    directoryHeading: "Buscar e filtrar",
    searchLabel: "Buscar perfis",
    searchPlaceholder: "Nome, foco, estágio ou geografia",
    clearFilters: "Limpar busca e filtros",
    submitSearch: "Buscar",
    facetLabels: {
      entity_type: "Tipo de entidade",
      geography: "Geografia",
      stage: "Estágio",
      focus: "Foco",
    },
    resultCount: "{count} perfis",
    loadingResults: "Buscando perfis…",
    noResults: "Nenhum perfil corresponde a esta combinação de busca e filtros.",
    searchError:
      "A busca está temporariamente indisponível. Exibindo os resultados dos filtros locais.",
    noScript:
      "Todos os links de perfis continuam disponíveis abaixo. A busca e os filtros combinados exigem JavaScript.",
    browseCategories: "Explorar categorias",
    browseCountries: "Explorar países",
    profileSource: "Fonte canônica",
    profileHistory: "Histórico do arquivo",
    officialWebsite: "Site oficial",
    founderRoute: "Rota para fundadores",
    verifiedOn: "Verificado em",
    coverage: "Cobertura",
    stages: "Estágios",
    focuses: "Focos",
    categoryLandingTitle: (label: string) => label,
    categoryLandingDescription: (label: string) =>
      `Explore ${label.toLocaleLowerCase("pt-BR")} no catálogo do Awesome LatAm VC.`,
    countryLandingTitle: (country: string) =>
      `Diretório de financiamento para ${country}`,
    countryLandingDescription: (country: string) =>
      `Explore entidades de financiamento documentadas relacionadas a ${country}.`,
    categoryLabels: {
      fund: "Fundos de venture capital",
      accelerator: "Aceleradoras",
      angel_network: "Redes-anjo",
      funding_platform: "Plataformas de captação",
      public_program: "Programas públicos",
    } satisfies Record<Category, string>,
  },
  es: {
    languageName: "Español",
    languageNavigation: "Elegir idioma",
    skipLink: "Saltar al contenido",
    home: "Resumen",
    catalog: "Catálogo",
    editorial: "Metodología",
    editorialNavigation: "Páginas editoriales",
    lastReviewed: "Última revisión",
    viewSource: "Ver fuente en Markdown",
    translationNotice:
      "Esta página incluye contenido traducido automáticamente y revisado antes de su publicación.",
    suggestCorrection: "Sugiere una corrección.",
    breadcrumbNavigation: "Ruta de navegación",
    primaryNavigation: "Navegación principal",
    githubLabel: "GitHub",
    sourceFooter: "Datos abiertos, fuentes oficiales e historial auditable en",
    staticFooter: "HTML estático, sin servidor en tiempo de ejecución.",
    homeTitle: "Awesome LatAm VC · Directorio abierto de financiación",
    homeDescription:
      "Directorio abierto y respaldado por fuentes de fondos y programas de financiación para startups en América Latina.",
    heroKicker: "Información abierta sobre financiación en América Latina",
    heroTitle: "Encuentra caminos de capital realmente documentados.",
    heroBody:
      "Fondos de venture capital, aceleradoras, redes ángel, plataformas de financiación y programas públicos. Cada entrada sigue vinculada al Markdown canónico, la evidencia oficial y el historial Git.",
    browseCatalog: "Explorar el catálogo",
    inspectSource: "Consultar la fuente",
    snapshot: "Estado actual",
    canonicalProfiles: "perfiles canónicos",
    geographies: "Geografías",
    categories: "Categorías",
    categoryHeading: "Un catálogo, cinco caminos hacia la financiación",
    categoryBody:
      "Los recuentos provienen de los archivos canónicos durante el build. Los nuevos perfiles aceptados aparecen automáticamente sin copiar contenido al sitio.",
    principlesHeading: "Hecho para verificar, sin exageraciones",
    principles: [
      ["Markdown canónico", "El repositorio sigue siendo la fuente oficial."],
      [
        "Evidencia estructurada",
        "Los enlaces oficiales y las fechas de verificación acompañan los perfiles.",
      ],
      [
        "Estático por defecto",
        "Todas las páginas funcionan sin servidor en tiempo de ejecución.",
      ],
    ],
    catalogTitle: "Catálogo de financiación latinoamericana · Awesome LatAm VC",
    catalogDescription:
      "Explora el catálogo canónico de Awesome LatAm VC por tipo de entidad.",
    catalogKicker: "Catálogo canónico",
    profileCount: (count: number) =>
      `${count} perfiles, directamente desde el repositorio.`,
    catalogIntro:
      "Explora todas las entradas canónicas por tipo. Los cuerpos traducidos llegan en lotes revisados; la identidad y los enlaces de las fuentes permanecen estables.",
    jumpNavigation: "Ir a una categoría del catálogo",
    profilePlural: "perfiles",
    sourceLabel: "Ver Markdown canónico",
    directoryHeading: "Buscar y filtrar",
    searchLabel: "Buscar perfiles",
    searchPlaceholder: "Nombre, foco, etapa o geografía",
    clearFilters: "Limpiar búsqueda y filtros",
    submitSearch: "Buscar",
    facetLabels: {
      entity_type: "Tipo de entidad",
      geography: "Geografía",
      stage: "Etapa",
      focus: "Foco",
    },
    resultCount: "{count} perfiles",
    loadingResults: "Buscando perfiles…",
    noResults:
      "Ningún perfil coincide con esta combinación de búsqueda y filtros.",
    searchError:
      "La búsqueda no está disponible temporalmente. Se muestran los resultados de los filtros locales.",
    noScript:
      "Todos los enlaces de perfiles siguen disponibles abajo. La búsqueda y los filtros combinados requieren JavaScript.",
    browseCategories: "Explorar categorías",
    browseCountries: "Explorar países",
    profileSource: "Fuente canónica",
    profileHistory: "Historial del archivo",
    officialWebsite: "Sitio oficial",
    founderRoute: "Ruta para fundadores",
    verifiedOn: "Verificado el",
    coverage: "Cobertura",
    stages: "Etapas",
    focuses: "Focos",
    categoryLandingTitle: (label: string) => label,
    categoryLandingDescription: (label: string) =>
      `Explora ${label.toLocaleLowerCase("es")} en el catálogo de Awesome LatAm VC.`,
    countryLandingTitle: (country: string) =>
      `Directorio de financiación para ${country}`,
    countryLandingDescription: (country: string) =>
      `Explora entidades de financiación documentadas relacionadas con ${country}.`,
    categoryLabels: {
      fund: "Fondos de venture capital",
      accelerator: "Aceleradoras",
      angel_network: "Redes ángel",
      funding_platform: "Plataformas de financiación",
      public_program: "Programas públicos",
    } satisfies Record<Category, string>,
  },
} as const;

export type Locale = keyof typeof ui;

export function strings(locale: Locale) {
  return ui[locale];
}
