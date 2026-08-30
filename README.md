# Agente Financeiro com IA para Classificação de Extratos Bancários

Um projeto em Python para análise inteligente de extratos bancários com Gemini, pensado para demonstrar fluxo real de ingestão, limpeza de dados e classificação automática de transações financeiras.

## Visão geral

Este projeto lê extratos CSV exportados do NuBank, prepara as transações em lotes e envia cada lote para o Gemini com um schema estruturado de resposta. A proposta é reduzir ruído nos prompts, organizar a saída em JSON e criar uma base sólida para a próxima etapa: persistência em banco SQL para consumo no Power BI.

## Por que este projeto existe

Este repositório foi criado como um estudo prático de agentes e automação com IA aplicada a dados financeiros. A ideia é mostrar, de forma objetiva, como transformar dados bancários brutos em uma estrutura útil para análise, categorização e visualização.

## O que o projeto faz hoje

- Lê todos os arquivos CSV dentro da pasta `extratos/`.
- Normaliza e limpa descrições bancárias para reduzir ruído no prompt.
- Agrupa transações em lotes para envio ao modelo.
- Consulta o Gemini com resposta estruturada em JSON.
- Consolida os resultados de saída em arquivos JSON.
- Prepara a base para a futura carga em SQL e uso no Power BI.

## Stack usada

- **Python**
- **Google Gemini SDK (`google-genai`)**
- **Pydantic**
- **python-dotenv**
- **CSV / JSON** para ingestão e persistência intermediária

## Arquitetura em alto nível

```mermaid
flowchart LR
    A[CSVs do NuBank] --> B[Batcher]
    B --> C[Limpeza e normalização]
    C --> D[Montagem de lotes]
    D --> E[Gemini]
    E --> F[JSON de saída]
    F --> G[Persistência local]
    G --> H[Futuro: banco SQL]
    H --> I[Power BI]
```

## Estrutura do projeto

```text
Simple AI Agent/
├── extratos/
│   └── arquivos CSV do NuBank
├── saida/
│   └── arquivos JSON gerados na execução
├── src/
│   ├── batcher.py
│   └── main.py
└── README.md
```

## Como funciona

1. O `Batcher` carrega os CSVs da pasta `extratos/`.
2. As descrições são normalizadas e limpas para deixar o prompt mais enxuto.
3. As transações são divididas em lotes.
4. Cada lote é enviado ao Gemini com um schema de resposta bem definido.
5. A resposta retorna em JSON estruturado.
6. O resultado é salvo localmente para uso posterior.

## Como executar

### 1. Criar e ativar o ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Instalar dependências

```powershell
pip install google-genai pydantic python-dotenv
```

### 3. Configurar a chave da API

Crie um arquivo `.env` na raiz do projeto:

```env
GEMINI_API_KEY=sua_chave_aqui
```

### 4. Colocar os extratos na pasta correta

Adicione os CSVs exportados do NuBank dentro de `extratos/`.

### 5. Executar o projeto

```powershell
python src/main.py
```

## Exemplo de saída esperada

Cada lote gera um JSON com transações classificadas, algo neste formato:

```json
{
  "lote": 1,
  "transacoes": [
    {
      "data": "02/04/2026",
      "valor": 5.49,
      "categoria": "Alimentação",
      "estabelecimento": "COMERCIAL ABC DA HORTALICA",
      "justificativa": "Pagamento associado a compra em estabelecimento comercial."
    }
  ]
}
```

## Roadmap

- [x] Leitura dos CSVs do NuBank
- [x] Limpeza e preparação de descrições para o prompt
- [x] Processamento em lotes
- [x] Classificação via Gemini
- [x] Geração de JSON de saída
- [ ] Persistir a saída em banco SQL
- [ ] Estruturar o banco para consumo no Power BI
- [ ] Criar arquivo final elegível para análise no Power BI
- [ ] Melhorar observabilidade, logs e retentativas

## Próximo passo planejado

A próxima evolução do projeto será converter os JSONs de saída em um banco SQL. Isso vai facilitar consultas, histórico, rastreabilidade e integração com o Power BI para criação de dashboards.

## Observações técnicas

- O projeto está focado em um fluxo realista de classificação financeira.
- A leitura dos CSVs foi projetada especificamente para o modelo emitido pelo banco NuBank
- A estrutura foi pensada para ser fácil de expandir.
- O resultado final pretende servir tanto como estudo de IA aplicada quanto como uma ferramenta de uso pessoal.

