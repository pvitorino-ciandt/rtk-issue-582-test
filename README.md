# Reprodução Local — RTK Issue #582

> RTK Hook aumenta custos do Claude Code em 18%
> Ref: https://github.com/rtk-ai/rtk/issues/582

## Pré-requisitos

- **Python 3.8+**
- **Claude Code CLI** instalado (`claude`)
- **jq** instalado (`brew install jq` / `apt install jq`)
- **RTK** instalado (ver abaixo)

## 1. Instalar o RTK

```bash
# macOS
brew install rtk

# Linux
curl -fsSL https://github.com/rtk-ai/rtk/releases/latest/download/install.sh | sh

# Ou via cargo (ATENÇÃO: use --git para não pegar o pacote errado)
cargo install --git https://github.com/rtk-ai/rtk

# Verificar instalação
rtk --version    # deve mostrar 0.28+ 
rtk gain         # deve funcionar (se der erro, instalou o pacote errado)
```

## 2. Instalar dependências Python

```bash
cd rtk-test-582
pip install -r requirements.txt
```

## 3. Verificar o bug do pytest (sem Claude)

```bash
# Sem CI — todos os testes passam
pytest test_example.py -v
# → 6 passed

# Com CI=true — 3 erros (o bug real)
CI=true pytest test_example.py -v
# → 3 errors: NameError: name 'true' is not defined
```

## 4. Configurar o hook RTK

```bash
# Criar diretórios necessários
mkdir -p ~/.claude/hooks ~/.claude/bin

# Copiar os scripts
cp rtk-rewrite.sh ~/.claude/hooks/
cp toggle-rtk ~/.claude/bin/
chmod +x ~/.claude/hooks/rtk-rewrite.sh
chmod +x ~/.claude/bin/toggle-rtk

# Adicionar ao PATH (se necessário)
export PATH="$HOME/.claude/bin:$PATH"

# Habilitar o RTK
toggle-rtk

# Verificar que o hook está registrado
jq '.hooks.PreToolUse[] | select(.matcher == "Bash") | .hooks[] | select(.command | contains("rtk-rewrite.sh"))' ~/.claude/settings.json
```

## 5. Teste A/B com o Claude Code

O prompt para ambos os testes é o mesmo:

```
Tests failed in CI. The error log is in @ci_log_synthetic.txt and the test file is @test_example.py. Help me debug and fix the issue.
```

### Teste 1: COM RTK (habilitado)

```bash
# Garantir que RTK está habilitado
toggle-rtk  # (se necessário)

# Iniciar sessão limpa do Claude Code
claude

# Colar o prompt acima
# Esperar o Claude completar
# Verificar custos:
/cost

# ANOTAR: output tokens, custo total, duração
```

### Teste 2: SEM RTK (desabilitado)

```bash
# Desabilitar RTK
toggle-rtk

# Iniciar sessão limpa do Claude Code
claude

# Colar o MESMO prompt
# Esperar o Claude completar
# Verificar custos:
/cost

# ANOTAR: output tokens, custo total, duração
```

## 6. O que medir e comparar

| Métrica            | RTK OFF | RTK ON | Δ esperado |
|--------------------|---------|--------|------------|
| Output tokens      |         |        | ~+50%      |
| Input tokens       |         |        | ~-80%      |
| Custo total ($)    |         |        | ~+18%      |
| Duração            |         |        | ~+26%      |
| Tool calls extras  |         |        | ~+1-2      |

**Resultado esperado da issue:** A economia de input tokens NÃO compensa o aumento de output tokens, resultando em custo total MAIOR com RTK.

## 7. Testes adicionais sugeridos

### Testar com diferentes níveis de compressão

```bash
# Comparar outputs manualmente
cat test_example.py          # output raw
rtk read test_example.py     # compressão padrão
rtk read test_example.py -l aggressive  # só assinaturas

cat ci_log_synthetic.txt     # log raw
rtk read ci_log_synthetic.txt  # log comprimido
```

### Testar o cenário Playwright (issue #690)

Se tiver um projeto com testes E2E, repetir o teste A/B com:
```bash
# Sem RTK
npx playwright test --reporter=list

# Com RTK
rtk playwright test --reporter=list
```

### Testar output de comandos que falham vs sucedem

```bash
# Comando que sucede — RTK deveria comprimir
rtk git status

# Comando que falha — RTK NÃO deveria comprimir
CI=true rtk test pytest test_example.py
# Verificar: o output de falha está completo ou cortado?
```

## 8. Dados para o levantamento

Ao final dos testes, documentar:

1. **Tabela comparativa** com as métricas acima
2. **Exemplos concretos** de output raw vs comprimido (screenshots ou copiar/colar)
3. **Casos onde a compressão atrapalhou** — o Claude pediu mais info? Fez tool calls extras? 
4. **Casos onde a compressão ajudou** — comandos onde a saída era realmente ruído
5. **Proposta**: quais comandos deveriam ser comprimidos e quais não

## Estrutura dos arquivos

```
rtk-test-582/
├── README.md              ← Este arquivo
├── test_example.py        ← Teste com o bug do pytest skipif
├── ci_log_synthetic.txt   ← Log de erro simulando CI
├── requirements.txt       ← Dependências (só pytest)
├── rtk-rewrite.sh         ← Hook que reescreve comandos
└── toggle-rtk             ← Script para habilitar/desabilitar RTK
```

## Meus testes
Com o toggle-rtk ativado
<img width="964" height="286" alt="image" src="https://github.com/user-attachments/assets/3bba8e6e-1220-4060-b636-a05d4e7f30ae" />

Com o toggle-rtk desativa
<img width="968" height="290" alt="image" src="https://github.com/user-attachments/assets/750da759-fa13-4125-926e-565aab8a9213" />



