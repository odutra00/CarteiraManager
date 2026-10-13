# CarteiraManager V2.0

Gerenciador de Carteiras de Ativos (B3), Cálculo de IRPF (Mensal Swing Trade, Day-Trade e DIRPF Anual) e Indicadores de Mercado.

Reativado e totalmente refatorado com arquitetura modular, **PyQt6**, **yfinance** e suporte ao **Python 3.12+**.

---

## 🚀 Principais Funcionalidades

1. **Gestão de Operações e Custódia**:
   - Cadastro e histórico completo de compras e vendas (Mercado à Vista, Opções, Fracionário, FII, ETF, BDR).
   - Cálculo automático de **Preço Médio (PM)** considerando custos e taxas da B3 (Instrução Normativa RFB nº 1.585/2015).
   - Acompanhamento de quantidade consolidada e posição de custódia em tempo real.
   - Detecção automática de operações **Day-Trade**.

2. **Visão da Carteira & Gráfico de Alocação**:
   - Cards com métricas consolidadas: Total Investido (Custo), Valor de Mercado Atual, Lucro/Prejuízo (R$) e Rentabilidade Global (%).
   - Tabela detalhada de ativos em custódia com cotação atualizada, resultado e percentual de alocação.
   - Gráfico de Pizza / Donut interativo (Matplotlib) com a composição da carteira.
   - Atualização de cotações em tempo real via Yahoo Finance (`yfinance`).

3. **Apuração de IRPF & DARF**:
   - **Operações Comuns (Swing Trade)**:
     - Isenção automática para meses com volume de vendas de ações $\le$ R$ 20.000,00.
     - Alíquota de 15% sobre o lucro líquido para meses com vendas $>$ R$ 20.000,00.
     - Cálculo do IRRF retido na fonte (dedo-duro de 0,005%).
     - **Compensação contínua de prejuízos acumulados** de meses anteriores.
     - Cálculo exato do valor da DARF a recolher.
   - **Day Trade**:
     - Alíquota de 20% sobre o ganho líquido (sem faixa de isenção).
     - IRRF retido na fonte de 1% e compensação de prejuízos anteriores de Day Trade.
   - **Declaração Anual (DIRPF)**:
     - Total de Rendimentos Isentos e Não Tributáveis (Código 20) para a declaração de ajuste anual.
     - Total de Ganhos Líquidos Tributáveis mês a mês.
     - Total de IRRF retido no ano para dedução na DIRPF.
     - Saldo de prejuízos acumulados a transportar para o ano seguinte.

4. **Gráfico de Desempenho vs IBOV**:
   - Evolução normalizada da rentabilidade (Base 1.0) comparando a Carteira com o índice Ibovespa (`^BVSP`) e ativos individuais.
   - Compatível com as versões mais recentes do Pandas e Matplotlib.

5. **Indicadores de Mercado**:
   - Busca em tempo real de múltiplos fundamentalistas (P/L, P/VP, Dividend Yield, LPA, Beta, Mín/Máx 52 semanas).

6. **Importação e Exportação CSV**:
   - Importação e exportação com detecção automática de delimitadores (`;` ou `,`) e codificação (UTF-8, ANSI).

---

## 🛠️ Requisitos e Instalação

O projeto utiliza o ambiente virtual configurado. Para executar:

```bash
# 1. Ativar o ambiente virtual
source ~/myPython/bin/activate

# 2. Instalar dependências (caso necessário)
pip install -r requirements.txt

# 3. Executar o programa
python main.py
```

### Comandos de Linha de Comando (CLI)

O `main.py` também oferece utilitários via terminal:

```bash
# Recalcular todos os preços médios e posições do banco de dados
python main.py --recalculate

# Importar uma planilha de operações
python main.py --import-csv PlanilhaOperacoesTeste.csv

# Exportar as operações atuais para CSV
python main.py --export-csv MinhaCarteira.csv
```

---

## 🧪 Execução de Testes Automatizados

O projeto conta com suíte de testes unitários e de integração com `pytest`:

```bash
pytest tests/ -v
```

---

## 📂 Estrutura do Projeto

```
CarteiraManager/
├── core/                       # Regras de negócio e camada de dados (desacoplada da UI)
│   ├── models.py               # Dataclasses tipadas (Operacao, PosicaoConsolidada, ResumoIRPF)
│   ├── database.py             # Acesso seguro ao SQLite (STOCKS.db)
│   ├── portfolio_service.py    # Cálculo de Preço Médio, Day-Trade e Consolidação
│   ├── tax_service.py          # Apuração fiscal de IRPF e DIRPF
│   ├── market_data.py          # Integração resiliente com yfinance e cache local
│   └── csv_service.py          # Importador e exportador de planilhas CSV
├── ui/                         # Interface Gráfica Moderna (PyQt6)
│   ├── app.py                  # Janela principal e menus (MainWindow)
│   └── widgets/                # Componentes das abas
│       ├── operations_tab.py   # Cadastro e tabela de operações
│       ├── portfolio_tab.py    # Carteira consolidada e gráfico Donut
│       ├── performance_tab.py  # Gráfico de rentabilidade normalizada vs IBOV
│       ├── tax_tab.py          # Painel de apuração de IRPF e DARF
│       └── indicators_tab.py   # Consulta de fundamentos de ativos
├── tests/                      # Testes automatizados (pytest)
├── STOCKS.db                   # Banco de dados SQLite persistente
├── requirements.txt            # Dependências Python
└── main.py                     # Ponto de entrada do programa
```
