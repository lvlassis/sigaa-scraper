# Gerando páginas de teste

Os testes de integração rodam sobre páginas HTML reais do SIGAA, armazenadas em `tests/pages/`. Cada página é acompanhada de um arquivo YAML de mesmo nome com os valores esperados — o *test oracle* — que você preenche após validar manualmente o HTML.

## 1. Baixe a página

```bash
make pages
```

O comando autentica com os cookies do `.env`, baixa a página discente, aplica a oclusão de dados pessoais e salva o arquivo em `tests/pages/discente-<data-hora>.html`.

## 2. Valide o HTML gerado

Abra o arquivo e confirme que o conteúdo está correto e que nenhum dado pessoal real ficou exposto.

## 3. Gere o oracle YAML

```bash
make oracle
```

O comando roda o scraper na página e gera automaticamente `tests/pages/discente-<data-hora>.yaml` com todos os valores extraídos. Páginas que já possuem um YAML são ignoradas por padrão; use `--force` para sobrescrever:

```bash
python tests/generate_oracle.py --force
```

## 4. Revise o oracle gerado

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

## 5. Execute os testes

```bash
make tests
```

O pytest detecta automaticamente todos os pares `.html` + `.yaml` em `tests/pages/` e os parametriza como casos de teste independentes. Adicionar uma nova página não requer nenhuma alteração no código de testes.

---

## Oclusão de dados pessoais e IDs de banco de dados

Antes de salvar, `make pages` substitui automaticamente dados pessoais e identificadores internos do banco do SIGAA por valores fixos e genéricos, tornando o arquivo seguro para ser commitado e compartilhado.

Os valores abaixo são os que aparecerão nos fixtures de teste — use-os como referência ao escrever oracles YAML ou casos de teste adicionais.

### Dados pessoais do discente

| Campo | Valor nos fixtures |
|---|---|
| Nome completo | `JOAO JOAQUIM JOSE` |
| Nome no título da página | `JOAO JOAQUIM JOSE` |
| Número de matrícula | `040028922` |
| Username do e-mail (parte antes do `@`) | `aluno_anonimo` |
| Nome completo dos autores de tópicos do fórum | `AUTOR ANONIMO` |
| Login dos autores de tópicos do fórum | `autor_anonimo` |

### IDs e tokens de banco de dados

| Dado original | Campo / Contexto | Valor nos fixtures |
|---|---|---|
| PK do discente/usuário | `<input name="id">` no form de navegação | `000000` |
| PK do arquivo de foto | `idArquivo=` na URL de foto do perfil | `0` |
| Token de acesso à foto | `key=` na URL de foto do perfil | `00000000000000000000000000000000` |
| PK do usuário nos links de chat | `idusuario=` nas URLs de chat | `00000000` |
| PK do curso (URL pública) | `portal.jsf?id=` no menu | `0` |
| PK das turmas matriculadas | `linha_`, `idchat=`, `idTurma=`, `'id':'...'`, `<input name="idTurma">` | `1000000`, `2000000`, `3000000`, `4000000` (ordem de aparição na página) |
| PK das mensagens do fórum | `'idForumMensagem':'...'` nos links de tópicos | `10000000`, `20000000`, … (ordem de aparição) |
| PK de atividades/tarefas | `'id':'...'` nos links de atividades | `100000000`, `200000000`, … (ordem de aparição) |
| Hostname do servidor de aplicação | texto do rodapé (`srv-app4.ufg.br.srv4inst1`) | `srv-redacted` |
