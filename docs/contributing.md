# Contribuição

## Configurando o ambiente

**1. Clone o repositório e crie o ambiente virtual:**

```bash
git clone https://github.com/lvlassis/sigaa-scraper.git
cd sigaa-scraper
python -m venv .venv
source .venv/bin/activate
```

**2. Instale as dependências do projeto e de desenvolvimento:**

```bash
pip install -e ".[dev]"
```

**3. Configure os cookies no arquivo `.env`:**

Crie um `.env` na raiz do projeto com o valor completo do header `Cookie` de uma sessão autenticada no SIGAA (veja como obtê-lo no [Quick Start](quickstart.md)):

```bash
SIGAA_COOKIES="_ufg_br_sess=...; JSESSIONID=..."
```

**4. Execute os testes:**

```bash
make tests
```

---

## Gerando páginas de teste

Os testes de integração rodam sobre páginas HTML reais do SIGAA, armazenadas em `tests/pages/`. Cada página é acompanhada de um arquivo YAML de mesmo nome com os valores esperados — o *test oracle* — que você preenche após validar manualmente o HTML.

### 1. Baixe a página

```bash
make pages
```

O comando autentica com os cookies do `.env`, baixa a página discente, aplica a oclusão de dados pessoais e salva o arquivo em `tests/pages/discente-<data-hora>.html`.

### 2. Valide o HTML gerado

Abra o arquivo e confirme que o conteúdo está correto e que nenhum dado pessoal real ficou exposto.

### 3. Gere o oracle YAML

```bash
make oracle
```

O comando roda o scraper na página e gera automaticamente `tests/pages/discente-<data-hora>.yaml` com todos os valores extraídos. Páginas que já possuem um YAML são ignoradas por padrão; use `--force` para sobrescrever:

```bash
python tests/generate_oracle.py --force
```

### 4. Revise o oracle gerado

O YAML gerado é um **ponto de partida**, não uma verdade absoluta. Abra-o e confirme que os valores extraídos são os corretos. O arquivo segue esta estrutura:

```yaml
nome: JOAO JOAQUIM JOSE
matricula: '040028922'
curso: ENGENHARIA DE COMPUTAÇÃO
# ... demais campos escalares ...

turmas:
  count: 4
  items:
    - nome: COMPILADORES 1
      local: Sala 201 - CAE
      horario: 35N23

atividades:
  count: 2
  items: [...]

atualizacoes_turma:
  count: 10
  items: [...]

topicos_forum:
  count: 6
  items: [...]
```

Você pode remover campos ou seções inteiras do YAML — itens ausentes são simplesmente ignorados nos testes.

### 5. Execute os testes

```bash
make tests
```

O pytest detecta automaticamente todos os pares `.html` + `.yaml` em `tests/pages/` e os parametriza como casos de teste independentes. Adicionar uma nova página não requer nenhuma alteração no código de testes.

### Oclusão de dados pessoais

Antes de salvar, `make pages` substitui automaticamente os dados pessoais por valores genéricos, tornando o arquivo seguro para ser commitado e compartilhado. Os campos ocultados são:

| Dado original | Substituído por |
|---|---|
| Nome completo do discente | `JOAO JOAQUIM JOSE` |
| Nome no título da página | `JOAO JOAQUIM JOSE` |
| Número de matrícula | `040028922` |
| Username do e-mail (parte antes do `@`) | `aluno_anonimo` |
| ID interno do discente nos links de chat | `00000000` |
| Nome completo dos autores de tópicos do fórum | `AUTOR ANONIMO` |
| Login dos autores de tópicos do fórum | `autor_anonimo` |
