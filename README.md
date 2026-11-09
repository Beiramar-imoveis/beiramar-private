# Beiramar Private

Site da Beiramar Private, a frente de alto padrão da Beiramar Imóveis no Plano Piloto (Noroeste e Quadra 500 do Sudoeste).
Site estático (HTML, CSS e JS), sem WordPress, pronto para o GitHub Pages.

## Estrutura

| Pasta / arquivo | O que é |
|---|---|
| `dados/empreendimentos.json` | **Fonte de tudo**: regiões, números do Noroeste e os 12 empreendimentos (textos, metragens, status, fichas, endereço, mapa) |
| `dados/traducoes-en.json` | **Versão em inglês** dos textos dos empreendimentos, regiões e números (mesmos slugs) |
| `dados/blog/`, `dados/privacidade.html` e `dados/privacidade-en.html` | Artigos do blog (só em português) e política de privacidade nos dois idiomas |
| `ferramentas/gerar_site.py` | Gera todas as páginas a partir dos dados |
| `css/private.css` | Identidade visual e componentes (inclui os grafismos) |
| `js/private.js` | Menu, filtros, carrossel, galeria e formulário |
| `js/consentimento.js` | Aviso de cookies (LGPD) e carregamento do Analytics/Clarity |
| `imagens/empreendimentos/<slug>/` | `capa.webp` + fotos da galeria `01.webp`, `02.webp`… (versões `-p` são as reduzidas) |
| `imagens/site/` | Imagens institucionais e a logo original (`logo-beiramar-private.png`, sem alterações) |

As páginas `index.html` de cada pasta são **geradas**: edite os dados e rode o gerador, não o HTML.

## Idiomas

O site é gerado em português (raiz) e em inglês (`/en/`), com os mesmos modelos de página. O seletor PT/EN no
cabeçalho leva para a mesma página no outro idioma, e as páginas trazem as marcações `hreflang` para o Google.
Ao incluir ou editar um empreendimento, atualize também o trecho correspondente em `dados/traducoes-en.json`;
o que faltar lá aparece em português na versão em inglês. O blog e a landing page do Amaze Sunside existem só em português.

## Como atualizar

1. Edite `dados/empreendimentos.json` (para tirar um empreendimento do ar sem apagar: `"ativo": false`).
2. Fotos novas: coloque em `imagens/empreendimentos/<slug>/` como `capa.webp`, `01.webp`, `02.webp`… (1600 px de largura) e as versões reduzidas `-p.webp` (760 px). Ajuste `"galeria"` com a quantidade de fotos.
3. Rode:

```bash
python3 ferramentas/gerar_site.py
```

4. Faça o commit e o push. O GitHub Pages publica em seguida.

## Identidade visual

- **Cores:** Preto Private `#131415` e Branco Private `#FDFDFD` (sem branco puro), alternados por seção com a classe `.tema-claro`, mais cinzas neutros.
- **Tipografia:** DM Sans (mesma família dos sites do Grupo). Destaques em **Didot Italic** (`fontes/didot-italic.woff2`), a mesma dos posts.
- **Grafismos, como elementos independentes (CSS):**
  - `.moldura`: contorno fino com o canto em L deslocado no ângulo superior direito (proporções medidas na assinatura original). Variações: `.moldura--inferior`, `.moldura--canto`; ajuste com `--m-linha`, `--m-canto`, `--m-larg`, `--m-alt`.
  - `.faixas`: degradê em faixas que funde a foto no preto, aplicado por máscara sobre qualquer imagem limpa. Direções: `--esq` (padrão), `--dir`, `--topo`, `--base`.
  - `.listras`: faixas horizontais translúcidas sobre fotos e fundos claros.
  - `.bloco-preto`: números em blocos pretos, como nos cards “Os números não mentem”.

## Formulário de contato

Envia para o Web3Forms (mesmo serviço do site do Grupo); a chave em `ferramentas/gerar_site.py` (`WEB3FORMS_KEY`) define o e-mail que recebe os contatos. Depois do envio, o visitante vai para `/obrigado/`, que oferece continuar a conversa no WhatsApp com a mensagem já preenchida.

## Endereços antigos

Os endereços do WordPress (`/yard/`, `/azzure-beiramar-private/`, `/quadra500/` etc.) redirecionam para os novos (`/empreendimentos/yard/`, `/quadra-500/`). Essas pastas são criadas pelo gerador; a lista fica em `dados/.redirecionamentos`.

## Publicação

1. Prévia: em **Settings → Pages**, publique a branch desejada (pasta raiz). O site abre em `https://beiramar-imoveis.github.io/beiramar-private/`.
2. Domínio: quando aprovado, crie o arquivo `CNAME` com `beiramarprivate.com.br` e aponte o DNS do domínio para o GitHub Pages.
