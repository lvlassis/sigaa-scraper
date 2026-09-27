# Contribuindo

## Configurando o ambiente

**1. Clone o repositório e prepare o ambiente:**

```bash
git clone https://github.com/lvlassis/sigaa-scraper.git
cd sigaa-scraper
make setup
source .venv/bin/activate
```

**2. Configure os cookies no arquivo `.env`:**

Crie um `.env` na raiz do projeto com o valor completo do header `Cookie` de uma sessão autenticada no SIGAA (veja como obtê-lo no [Quick Start](quickstart.md)):

```bash
SIGAA_COOKIES="_ufg_br_sess=...; JSESSIONID=..."
```

**3. Execute os testes:**

```bash
make tests
```

---

## Gerando páginas de teste

Os testes de integração rodam sobre páginas HTML reais do SIGAA com dados anonimizados. Veja o guia completo em [Gerando páginas de teste](fixtures.md).
