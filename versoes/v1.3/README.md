## Documentação – Assistente Virtual  
## Versão 1.3
A versão 1.3 representa uma evolução estrutural da arquitetura desenvolvida na versão 1.2, introduzindo melhorias importantes no processo de recuperação de informações e no monitoramento do funcionamento do sistema.

Enquanto a versão anterior já utilizava um modelo de linguagem (LLM) para classificar semanticamente a pergunta do usuário e selecionar a base de dados correta, a **versão 1.3 introduz técnicas adicionais para melhorar a qualidade da recuperação de informações e permitir o acompanhamento do comportamento do sistema durante sua utilização.**

Entre as principais melhorias implementadas nesta versão destacam-se:
- **Segmentação de documentos (chunking) utilizando `RecursiveCharacterTextSplitter`, permitindo que textos longos sejam divididos em partes menores e semanticamente mais relevantes para a busca vetorial**.
- **Registro de logs das interações**, permitindo armazenar perguntas, respostas, documentos recuperados e o curso classificado.

Essas melhorias tornam o sistema mais robusto, com uma maior transparência no funcionamento do sistema, possibilitando análise posterior das respostas geradas pelo modelo. Isso o torna mais próximo de arquiteturas utilizadas em aplicações reais de Retrieval-Augmented Generation (RAG). 

---

# 2. Fluxo Geral do Projeto

O fluxo de funcionamento da versão 1.3 ocorre da seguinte forma:

1. O usuário envia uma pergunta pela interface do chat.
2. Um modelo de linguagem (LLM) classifica semanticamente a pergunta para identificar o curso relacionado.
3. O sistema seleciona automaticamente o retriever correspondente ao curso identificado.
4. O retriever realiza uma busca semântica no índice FAISS, recuperando os documentos mais relevantes.
5. Os documentos recuperados são organizados e concatenados para formar o contexto da resposta.
6. O contexto e a pergunta são enviados ao modelo de linguagem.
7. O LLM gera a resposta final baseada nas informações recuperadas.
8. A interação completa (pergunta, curso classificado, documentos recuperados e resposta) é registrada em um arquivo de log.
9. A resposta é exibida ao usuário na interface do Gradio.

---

# 3. Estrutura da Versão

## 3.1 Arquivos

Os principais arquivos presentes na versão são:
- [**app.py**](app.py): Arquivo principal que contém toda a lógica do Assistente Virtual (explicado no [Tópico 4 – Desenvolvimento](#4-desenvolvimento)).

---

## 3.2 Tecnologias Utilizadas

O projeto utiliza tecnologias voltadas para Inteligência Artificial, Recuperação de Informação e Processamento de Linguagem Natural:

- **Python**  
  Linguagem de programação utilizada para desenvolver toda a lógica do projeto.

- **LangChain**  
  Framework utilizado para estruturar o pipeline de processamento do assistente virtual, incluindo criação de prompts, integração com modelos de linguagem e encadeamento de tarefas.

- **OpenAI API**  
  Utilizada para acessar modelos de linguagem responsáveis pela classificação das perguntas e geração das respostas.

- **FAISS**  
  Biblioteca de busca vetorial responsável por indexar e recuperar embeddings de forma eficiente.

- **Gradio**  
  Biblioteca utilizada para criar uma interface web simples que permite testar o assistente virtual diretamente no navegador.

- **dotenv**  
  Utilizado para carregar variáveis de ambiente, incluindo a chave da API da OpenAI.

---

# 4. Desenvolvimento

O desenvolvimento do projeto foi realizado através da linguagem de programação `Python` e do framework `LangChain`, organizando o fluxo de processamento conforme a arquitetura Retrieval-Augmented Generation (RAG).

---

# 4.1 app.py

O arquivo [`app.py`](./app.py) contém toda a implementação da versão 1.3 do Assistente Virtual.

A seguir é apresentada uma explicação detalhada das principais partes do código.

---

## 4.1.1 Importação de Bibliotecas

```python
import gradio
import json

from dotenv import load_dotenv
from datetime import datetime

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
```

### Explicação

*Explicação:* Como citado anteriormente, foi utilizado o framework `LangChain` para o desenvolvimento do projeto. Para isso, importamos do próprio framework três "módulos" diferentes, sendo eles: core, community e openai. 

1. **langchain_core:** Classes e componentes fundamentais do framework. Desse módulo foi utilizado o `ChatPromptTemplate` (*responsável por definir um prompt padrão para ser utilizado ao entrar em contato com um modelo de IA*), e `RunnablePassthrough` (*responsável por permitir que a função receba o input no próximo passo*).

2. **langchain_community:** Classes e componentes que foram desenvolvidos e mantidos pela comunidade open source do framework. Desse módulo foi utilizado o `FAISS` (*biblioteca para busca vetorial, onde armazena vetores - textos embedados - e faz busca semântica*), `DirectoryLoader` (*percorre todos os arquivos de um diretório utilizando um loader para cada*), `TextLoader ` (*abre e carrega um arquivo de texto*).

3. **langchain_openai:** Integração oficial do LangChain com a OpenAI. Desse módulo foi utilizado `OpenAIEmbeddings` (*responsável por embedar - transformar o conteúdo dos arquivos da base de dados em vetores numéricos*), `ChatOpenAI` (*responsável por realizar chamadas ao modelo de linguagem da OpenAI*).

 - OBS: Além dessas importações, foi utilizado também o `dotenv`, responsável por carregar e utilizar a minha chave API da OpenAI de forma segura e o `gradio` para utilizar uma interface de conversação pelo navegador.

### Outras bibliotecas
- **dotenv**: Carrega a chave da API da OpenAI armazenada no arquivo `.env`.  
- **json**: Utilizado para registrar logs das interações do sistema.  
- **datetime**: Utilizado para registrar o momento exato de cada interação.  
- **gradio**: Utilizado para criar a interface de chat acessível pelo navegador.

---

## 4.1.2 Segmentação de Documentos (Chunking)

**Uma das principais melhorias introduzidas na versão 1.3 é a utilização de segmentação de documentos**, também conhecida como `chunking`.

```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200
)
```

Após o carregamento:

```python
docs_txt_bsi = text_splitter.split_documents(docs_txt_bsi)
```

### Explicação

*Explicação:* **Documentos muito longos podem** `dificultar` **a recuperação de trechos relevantes** durante a busca semântica.

O `RecursiveCharacterTextSplitter` divide textos em partes menores chamadas *chunks*.

- **chunk_size = 1200** → tamanho máximo do trecho  
- **chunk_overlap = 200** → sobreposição entre trechos  

**Isso melhora significativamente a precisão da busca.**

---

## 4.1.3 Criação das Bases Vetoriais

```python
loader_bsi = DirectoryLoader("../../base-de-dados/dados-tratados/bsi", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_bsi = loader_bsi.load()

loader_civil = DirectoryLoader("../../base-de-dados/dados-tratados/civil", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_civil = loader_civil.load()

loader_ambiental = DirectoryLoader("../../base-de-dados/dados-tratados/ambiental", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_ambiental = loader_ambiental.load()

loader_eletrica = DirectoryLoader("../../base-de-dados/dados-tratados/eletrica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_eletrica = loader_eletrica.load()

loader_quimica = DirectoryLoader("../../base-de-dados/dados-tratados/quimica", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_quimica = loader_quimica.load()

loader_geral = DirectoryLoader("../../base-de-dados/dados-tratados/geral", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt_geral = loader_geral.load()

embeddings = OpenAIEmbeddings()

faiss_bsi = FAISS.from_documents(docs_txt_bsi, embeddings)
faiss_civil = FAISS.from_documents(docs_txt_civil, embeddings)
faiss_ambiental = FAISS.from_documents(docs_txt_ambiental, embeddings)
faiss_eletrica = FAISS.from_documents(docs_txt_eletrica, embeddings)
faiss_quimica = FAISS.from_documents(docs_txt_quimica, embeddings)
faiss_geral = FAISS.from_documents(docs_txt_geral, embeddings)

retriever_bsi = faiss_bsi.as_retriever()
retriever_civil = faiss_civil.as_retriever()
retriever_ambiental = faiss_ambiental.as_retriever()
retriever_eletrica = faiss_eletrica.as_retriever()
retriever_quimica = faiss_quimica.as_retriever()
retriever_geral = faiss_geral.as_retriever()
``` 
*Explicação:* Após a importação das bibliotecas, se fez necessário a preparação dos dados. Tendo em vista que nessa versão foi utilizado dados de cursos diferentes, criamos uma base de dados para cada curso, para que não haja erro por similaridade semântica entre os documentos. 

Para isso, utilizamos o `DirectoryLoader` para encontrar os arquivos da nossa [base de dados tratada](/base-de-dados/dados-tratados/) de cada curso (e o **geral**, que serve como fonte para responder dúvidas que não se relacionam a nenhum curso) e o parâmetro `loader_cls=TextLoader` define que cada arquivo encontrado será carregado por meio do TextLoader, tendo em vista que os arquivos são **.txt**. Com os conteúdos dos arquivos encontrados, fizemos a utilização do método `.load()` na variável `loader` para retornar o conteúdo desses arquivos como documentos na variável `docs_txt`. 

Na segunda etapa, inicializamos `OpenAIEmbeddings()` na variável `embeddings`, que representa o modelo responsável por gerar os vetores numéricos a partir dos textos. 

Em seguida, criamos as variáveis `faiss_bsi`, `faiss_civil`, `faiss_eletrica`, `faiss_ambiental`, `faiss_geral`, `faiss_quimica` que corresponde aos nossos índices vetoriais `FAISS`. Nelas, utilizamos `FAISS.from_documents()` para gerar os embeddings dos documentos presentes em `docs_txt` de cada curso usando o modelo da OpenAI da variável `embeddings` e, ao mesmo tempo, armazenar esses vetores no índice `FAISS`. 

Por fim, utilizamos o método `as_retriever()` nas variáveis `retriever` de cada curso para adicionar um mecanismo de busca semântica no nosso índice vetorial (`FAISS`) e retornar documentos relacionados com a chave de busca. Ou seja, o trecho `retriever = base_vetores.as_retriever()` é responsável por receber um texto de entrada (um input, por exemplo) e buscar documentos com a semântica parecida no `FAISS`. Vale ressaltar que quando **não é definido** um limite de documentos retornados pela busca, o `as_retriever()` retorna 4 documentos por padrão.
- OBS: O `retriever` não responde textos de entrada, apenas assimila e recupera documentos relevantes relacionados ao input por meio de busca semântica.

---

## 4.1.4 Classificação Semântica do Curso

```python
prompt_curso="""
Você é um classificador de perguntas acadêmicas do IFBA – Campus Vitória da Conquista.

Sua tarefa é identificar a qual curso a pergunta do usuário se refere.
Considere linguagem natural, abreviações e sinônimos comuns usados por estudantes.

Classifique a pergunta em APENAS UMA das categorias abaixo:

- bsi: Bacharelado em Sistemas de Informação  
Exemplos de termos relacionados:
"bsi", "sistemas de informação", "curso de ti", "computação", "sistemas"

- engenharia_civil: Engenharia Civil  
Exemplos:
"civil", "engenharia civil", "curso de civil"

- engenharia_ambiental: Engenharia Ambiental  
Exemplos:
"ambiental", "engenharia ambiental", "meio ambiente"

- engenharia_eletrica: Engenharia Elétrica  
Exemplos:
"elétrica", "engenharia elétrica", "curso de elétrica"

- licenciatura_quimica: Licenciatura em Química  
Exemplos:
"química", "licenciatura em química", "curso de química"

- geral: Use APENAS se a pergunta não se referir a nenhum curso específico.
Exemplos:
informações institucionais, campus, calendário acadêmico, eventos, matrícula, biblioteca.

REGRAS IMPORTANTES:
- Se o curso estiver implícito na pergunta, escolha o curso correspondente.
- NÃO peça esclarecimentos.
- NÃO explique sua resposta.
- NÃO invente categorias.
- Responda SOMENTE com um dos rótulos abaixo:
bsi  
engenharia_civil  
engenharia_ambiental  
engenharia_eletrica  
licenciatura_quimica  
geral  

Pergunta do usuário:
{question}
"""
```
*Explicação:* Esse prompt instrui o modelo a atuar exclusivamente como um classificador, retornando apenas um rótulo que identifica o curso relacionado à pergunta ou a categoria geral.
A função abaixo interpreta a resposta do LLM e retorna automaticamente o retriever correspondente:
```python
prompt_curso_definido = ChatPromptTemplate.from_template(prompt_curso)

def classificar_retriever(pergunta):
    chain_curso = prompt_curso_definido | llm
    resposta = chain_curso.invoke({"question": pergunta})
    resposta_formatada = resposta.content.strip().lower()

    if resposta_formatada == "bsi":
        return retriever_bsi, "bsi"
    elif resposta_formatada == "engenharia_civil":
        return retriever_civil, "engenharia_civil"
    elif resposta_formatada == "engenharia_ambiental":
        return retriever_ambiental, "engenharia_ambiental"
    elif resposta_formatada == "engenharia_eletrica":
        return retriever_eletrica, "engenharia_eletrica"
    elif resposta_formatada == "licenciatura_quimica":
        return retriever_quimica, "licenciatura_quimica"
    elif resposta_formatada == "geral":
        return retriever_geral, "geral"
```
---

## 4.1.5 Prompt para Resposta do LLM
```python
prompt_padrao="""
Você é um assistente virtual acadêmico especializado em fornecer informações sobre os cursos oferecidos pelo Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista. 
Utilize as informações fornecidas para responder às perguntas dos usuários de forma clara e precisa.

Contexto: {context}
Pergunta: {question}
"""
prompt = ChatPromptTemplate.from_template(prompt_padrao)

```
*Explicação:* **Esse é o prompt que será enviado ao LLM para gerar a resposta para o questionamento do usuário**. No prompt vamos passar ao LLM um `contexto`, que será os documentos relacionados à dúvida do usuário recuperados pelo retriever e a `question`, que nada mais é do que a própria dúvida do usuário. Com o prompt definido, utilizamos a função `ChatPromptTemplate.from_template(prompt_padrao)` com o prompt como parâmetro para o definirmos dentro do padrão que o LLM busca receber.

---

## 4.1.6 Função 'responder'

```python
def responder(mensagem, historico):

    resultado = classificar_retriever(mensagem)
    if not resultado:
        return "Desculpe, não consegui identificar a sua pergunta. Por favor, caso sua dúvida seja relacionada a algum curso, especifique o curso para que eu possa ajudar melhor. Caso não seja, reformule melhor a sua pergunta."
    
    retriever, curso_classificado = resultado

    docs_recuperados = retriever.invoke(mensagem)

    contexto = "\n\n".join([doc.page_content for doc in docs_recuperados])

    chain = ({"context": contexto, "question": RunnablePassthrough()} | prompt | llm)
    resposta = chain.invoke(mensagem)

    log = {
        "timestamp": datetime.now().isoformat(),
        "pergunta": mensagem,
        "curso_classificado": curso_classificado,
        "documentos_recuperados": [
            {
                "conteudo": doc.page_content[:500],
                "metadata": doc.metadata
            }
            for doc in docs_recuperados
        ],
        "resposta": resposta.content
    }

    with open("../../logs/logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

    return resposta.content
```
*Explicação:* A função **def_responder** inicia-se com a atribuição de uma variável `resultado`, onde ela será igual ao retorno da função **classificar_retriever** com a mensagem do usuário como **parâmetro** para a função. Ou seja, a variável `resultado` contém o local onde o retriever será feito e o curso que esse retriever se relaciona. Como exposto, é de se perceber que a variável conterá dois conteúdos: `o retriever correspondente` e `o curso`. Para uma melhor organização, declaramos mais duas variáveis, para cada conteúdo da variável `resultado`: `retriever` e `curso_classificado`, que correspondem ao primeiro e segundo conteúdo, respectivamente. Com as variáveis `retriever` e `curso_classificado` definidas, inicializamos mais uma variável: `docs_recuperados`, que nada mais é do que os documentos que são recuperados pela função `retriever.invoke(mensagem)`, onde realiza a busca no local definido utilizando a **mensagem** do usuário como parâmetro de busca. Com os documentos recuperados devidamente armazenados, criamos o `contexto`, que nada mais é do que um texto que armazena o conteúdo de todos os documentos recuperados em um mesmo local. Com tudo isso definido, passamos para a execução da cadeia do **LangChain**, onde `chain = ({"context": contexto, "question": RunnablePassthrough()} | prompt | llm)`. Com a chain definida e tudo no seu devido lugar, onde `context` = `contexto` (texto que armazena o conteúdo dos documentos recuperados), `question` = `RunnablePassthrough()` (aqui definimos que a question será passada como parâmetro quando a função `chain` for acionada), `prompt` = prompt definido no passo [**4.1.5 Prompt para Resposta do LLM**](#415-prompt-para-resposta-do-llm), `llm` = `ChatOpenAI()` onde é de fato chamado a API da OpenAI. Após estruturação da chain, definimos a variável `resposta` como o retorno do chamado da `chain` passando a mensagem do usuário como parâmetro: `resposta = chain.invoke(mensagem)`. Com a chain executada e seu retorno definido na variável `resposta`, criamos o `log` para armazenar todas as informações daquela execução específica, onde no log definimos: `timestamp` como horário e data da interação, `pergunta` como mensagem do usuário, `curso_classificado` como a que curso/retriever pertence aquela mensagem, `documentos_recuperados` como um array que vai armazenar o `conteudo` (os primeiros 500 caracteres) e o `metadata` (que é informações adicionais do documento, como origem, caminho do arquivo) de cada documento recuperado dentro de `docs_recuperados`, e a resposta do `LLM`. Com o `log` definido, criamos uma função para abrir o arquivo **log.json** em seu respectivo caminho dentro do repositório e sobrescrevê-lo adicionando as informações definidas no log da interação mais recente. Por fim, a função `def responder` retorna a resposta do LLM que está armazenada no caminho `resposta.content`

## 4.1.7 Interface de Interação
```python
interface = gradio.ChatInterface(fn=responder, type="messages")
interface.launch()
```
*Explicação:* Aqui chamamos a função `ChatInterface()` para que a interface de chat padrão do `Gradio` seja criada e com a função `def responder()` como parâmetro para que a função possa ser acionada para cada mensagem recebida no chat. Por fim, é utilizado o método `interface.launch()` para que a interface do `Gradio` seja disponibilizada em um servidor HTTP local, o que permite testes do projeto no navegador. 

---