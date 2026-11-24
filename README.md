# Penumbra

**Disciplina:** Introdução à Inteligência Artificial (IMD3001)  
**Semestre:** 2026.2  
**Professor:** André Fonseca  
**Turma:** [T01]

## Integrantes do Grupo
* Ana Paula Evangelista Melo Freitas (20250041027)
* Larissa de Araújo Barreto (20240004155)
* Luigson Gesse de Oliveira Pereira (20250031209)
* Maria Helena Varela Kizerlla Guanaes (20250033713)

## Descrição do Projeto

Em um cenário pós-apocalíptico, um agente combina lógica e probabilidade para guardar um abrigo e decidir, em até 6 passos, se a criatura que se aproxima é humano ou monstro. Cada criatura é sorteada e, a cada passo, é revelada uma nova pista, que pode ser genérica, ambígua ou específica. O jogo tem 4 níveis com 3 criaturas cada; a cada nível a névoa aumenta, e o agente só enxerga a criatura quando ela já está perto da porta. Deixar um monstro entrar ou matar 3 humanos acaba o jogo.

O agente é híbrido: regras lógicas cuidam do que é certo (uma pista específica prova o tipo da criatura) e do que se anula (por exemplo, roupa suja explica cheiro forte), e a inferência bayesiana (Naive Bayes) junta as demais pistas numa chance de ser monstro. Ele mata ou deixa entrar assim que essa chance passa da taxa de garantia; se chegar ao 6º passo sem garantia, escolhe a ação de menor custo esperado. O projeto foi desenvolvido em Python, com pandas (leitura do catálogo de características), Streamlit (interface) e pytest (testes).

## Guia de Instalação e Execução

### 1. Instalação das Dependências
Certifique-se de ter o **Python 3.10** ou mais recente instalado. Clone o repositório e instale as bibliotecas listadas no `requirements.txt`:

```bash
# Clone o repositório
git clone https://github.com/paulamelof/Penumbra.git

# Entre na pasta do projeto
cd Penumbra

# (Opcional) Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### 2. Como Executar

Execute o comando abaixo no terminal, a partir da raiz do projeto, para iniciar o servidor local:

```bash
streamlit run app.py
```

A interface abre em http://localhost:8501. Na barra lateral, escolha a dificuldade, o nível inicial, as garantias e a seed, e clique em **Iniciar jogo**. Na aba **Jogo**, use **Próximo passo**, **Rodar criatura** ou **Automático** para acompanhar as decisões do agente; na aba **Experimentos**, rode as simulações e baixe os resultados em CSV.

### 3. Como Rodar os Testes

```bash
python -m pytest
```

## Estrutura dos Arquivos

  * `data/caracteristicas.csv`: catálogo das 23 características (tipo, lado, probabilidades e qual ambígua cada atenuante anula).
  * `src/modelos.py`: tipos compartilhados entre os módulos (`Caracteristica`, `Percepcao`, `Acao`, `Resultado`).
  * `src/catalogo.py`: lê e valida o CSV com pandas.
  * `src/base_conhecimento.py`: monta as regras de certeza, as regras de anulação e o fator de cada característica a partir do catálogo.
  * `src/ambiente.py`: criatura, passos, névoa e sorteio das pistas.
  * `src/inferencia.py`: regras de certeza e anulação e cálculo da chance (Naive Bayes).
  * `src/agente.py`: decisão do agente e explicação passo a passo.
  * `src/metricas.py`: simulações e resumo dos experimentos.
  * `tests/`: testes automatizados (pytest).
  * `app.py`: interface em Streamlit.

## Resultados e Demonstração

[Adicionar prints da interface e os gráficos da aba Experimentos: acurácia por nível de névoa e por dificuldade, passos até decidir e o experimento da garantia de matar (70%, 80%, 90% e 99%).]

## Referências

  * RUSSELL, S.; NORVIG, P. *Inteligência Artificial: Uma Abordagem Moderna*. Capítulos 2 (agentes inteligentes), 7 (agentes lógicos) e 12 (quantificação da incerteza).
  * *No, I'm not a Human* (Trioskaz / CRITICAL REFLEX, 2025), jogo que inspirou o projeto.
  * Documentação do pandas: https://pandas.pydata.org/docs/
  * Documentação do Streamlit: https://docs.streamlit.io/
  * Documentação do pytest: https://docs.pytest.org/
