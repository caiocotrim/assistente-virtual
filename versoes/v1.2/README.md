# Documentação – Assistente Virtual  
## Versão 1.2


## 1. Sobre a Versão 1.2
Esta é a terceira versão desenvolvida do Assistente Virtual e representa uma evolução significativa em relação à versão 1.1.  
Enquanto a versão anterior realizava o reconhecimento do curso por meio de regras fixas e verificações manuais de palavras-chave, a **versão 1.2 introduz o uso de um modelo de linguagem (LLM) para realizar a classificação semântica da pergunta do usuário**, tornando o sistema mais inteligente, flexível e escalável.

Nesta versão, o próprio LLM é responsável por interpretar a mensagem do usuário e identificar a qual curso ela se refere (ou se trata de uma pergunta geral). A partir dessa classificação, o assistente seleciona automaticamente a base de dados correta para realizar a busca semântica, reduzindo ambiguidades e melhorando a precisão das respostas.

---

## 2. Fluxo Geral do Projeto
1. Usuário envia uma mensagem com sua dúvida.
2. Um LLM classifica semanticamente a pergunta e identifica o curso relacionado (ou categoria geral).
3. O sistema seleciona automaticamente o retriever correspondente ao curso identificado.
4. O retriever busca documentos relevantes no FAISS da base selecionada.
5. O prompt é preenchido com o contexto recuperado + pergunta do usuário.
6. O LLM gera a resposta final.
7. O Gradio exibe a resposta no navegador.

---

## 3. Estrutura da Versão

### 3.1 Arquivos
Os principais arquivos presentes na versão são:
- [**app.py**](app.py): Arquivo principal que contém toda a lógica do Assistente Virtual (explicado no [Tópico 4 – Desenvolvimento](#4-desenvolvimento)).

### 3.2 Tecnologias Utilizadas
O projeto faz uso de tecnologias voltadas a IA e processamento de linguagem natural:

- **Python**: Linguagem de programação utilizada para o desenvolvimento do projeto.
- **LangChain**: Framework utilizado para estruturar a pipeline do Assistente Virtual, construção de prompts, integração com modelos de linguagem e encadeamento de tarefas.
- **OpenAI API**: Plataforma que fornece o modelo de linguagem utilizado tanto para classificação de perguntas quanto para geração das respostas.
- **FAISS**: Ferramenta de busca vetorial responsável por indexar e recuperar embeddings de forma eficiente.
- **Gradio**: Biblioteca que permite criar interfaces simples para teste e interação com o assistente via navegador.

---

## 4. Desenvolvimento
O desenvolvimento do projeto foi realizado através da linguagem de programação `Python` e do framework `LangChain`.

### 4.1 app.py
Este arquivo ([app.py](./app.py)) concentra todo o código-fonte da versão 1.2 e a lógica completa do funcionamento do Assistente Virtual.  
A seguir será apresentada a explicação detalhada do código.

---

### 4.1.1 Importação de bibliotecas
```python
import gradio

from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

load_dotenv()
```
*Explicação:* Como citado anteriormente, foi utilizado o framework `LangChain` para o desenvolvimento do projeto. Para isso, importamos do próprio framework três "módulos" diferentes, sendo eles: core, community e openai. 

1. **langchain_core:** Classes e componentes fundamentais do framework. Desse módulo foi utilizado o `ChatPromptTemplate` (*responsável por definir um prompt padrão para ser utilizado ao entrar em contato com um modelo de IA*), e `RunnablePassthrough` (*responsável por permitir que a função receba o input no próximo passo*).

2. **langchain_community:** Classes e componentes que foram desenvolvidos e mantidos pela comunidade opensource do framework. Desse módulo foi utilizado o `FAISS` (*biblioteca para busca vetorial, onde armazena vetores - textos embedados - e faz busca semântica*), `DirectoryLoader` (*percorre todos os arquivos de um diretório utilizando um loader para cada*), `TextLoader ` (*abre e carrega um arquivo de texto*).

3. **langchain_openai:** Integração oficial do LangChain com a OpenAI. Desse módulo foi utilizado `OpenAIEmbeddings` (*responsável por embedar - transformar o conteúdo dos arquivos da base de dados em vetores númericos*), `ChatOpenAI` (*reponsável por realizar chamadas ao modelo de linguagem da OpenAI*).

 - OBS: Além dessas importações, foi utilizado também o `dotenv`, responsável por carregar e utilizar a minha chave API da OpenAI de forma segura e o `gradio` para utilizar uma interface de conversação pelo navegador.

### 4.1.1 Importação de bibliotecas
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

Por fim, utilizamos o método `as_retriever()` nas variáveis `retriever` de cada curso para adicionar um mecanismo de busca semântica no nosso índice vetorial (`FAISS`) e retornar documentos relacionados com a chave de busca. Ou seja, o trecho `retriever = base_vetores.as_retriever()` é responsável por receber um texto de entrada (um input, por exemplo) e buscar documentos com a semântica parecida no `FAISS`. Vale ressaltar que quando **não é definido** um limite de documentos retornardos pela busca, o `as_retriever()` retorna 4 documentos por padrão.
- OBS: O `retriever` não responde textos de entrada, apenas assimila e recupera documentos relevantes relacionados ao input por meio de busca semântica.

### 4.1.3 Classificação semântica do curso utilizando LLM
* **Uma das principais inovações da versão 1.2 é a utilização de um modelo de linguagem para classificar semanticamente a pergunta do usuário.**
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
        return retriever_bsi
    elif resposta_formatada == "engenharia_civil":
        return retriever_civil
    elif resposta_formatada == "engenharia_ambiental":
        return retriever_ambiental
    elif resposta_formatada == "engenharia_eletrica":
        return retriever_eletrica
    elif resposta_formatada == "licenciatura_quimica":
        return retriever_quimica
    elif resposta_formatada == "geral":
        return retriever_geral
```
* **Com isso, elimina-se a dependência de regras fixas baseadas em palavras-chave, tornando o sistema mais robusto e adaptável à linguagem natural dos usuários.**

### 4.1.4 Utilização de LLM para geração da resposta
Após a definição do retriever adequado, utiliza-se um prompt padrão para geração da resposta final:
```python
prompt_padrao = """
Você é um assistente virtual acadêmico especializado em fornecer informações sobre os cursos oferecidos pelo Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista.
Utilize as informações fornecidas para responder às perguntas dos usuários de forma clara e precisa.

Contexto: {context}
Pergunta: {question}
"""
```
Esse prompt recebe o contexto recuperado pelo FAISS e a pergunta do usuário, garantindo que as respostas sejam fundamentadas nos documentos da base de dados.

### 4.1.5 Chat e Interface Gradio
```python
def responder(mensagem, historico):

    retriever = classificar_retriever(mensagem)
    if not retriever:
        return "Desculpe, não consegui identificar à sua pergunta. Por favor, reformule a pergunta ou especifique o curso."

    chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)
    resposta = chain.invoke(mensagem)
    return resposta.content

interface = gradio.ChatInterface(fn=responder)
interface.launch()
```
*Explicação:* A função `responder` representa o núcleo lógico do chatbot, sendo responsável por `processar a mensagem enviada pelo usuário`, `identificar o contexto adequado` e `gerar uma resposta utilizando um modelo de linguagem (LLM)`. Essa função é utilizada diretamente pela interface de chat do `Gradio`, funcionando como o ponto central de interação entre o usuário e o sistema. Ao receber uma mensagem, a função realiza inicialmente a **identificação do contexto mais apropriado por meio de um mecanismo de classificação**, que determina qual retriever deve ser utilizado. **O retriever é responsável por fornecer as informações relevantes** que servirão de base para a geração da resposta. **Essa etapa é fundamental para garantir que o modelo de linguagem trabalhe com dados coerentes com a pergunta realizada**, aumentando a precisão e a relevância das respostas. Caso não seja possível identificar um contexto válido, a função retorna imediatamente uma mensagem informando que a pergunta não pôde ser compreendida corretamente, solicitando ao usuário que reformule a questão ou forneça mais detalhes. Esse tratamento evita respostas genéricas ou inconsistentes e melhora a experiência de uso do chatbot. **Com o contexto definido, é construída uma cadeia de execução** (`chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)`) **que organiza o fluxo de dados entre o contexto recuperado, a pergunta original do usuário e o modelo de linguagem**. A mensagem do usuário é preservada integralmente e combinada com o contexto por meio de um template de prompt, que estrutura essas informações de forma adequada para interpretação pelo LLM. Em seguida, o `modelo de linguagem é acionado para gerar a resposta final`. **Após a execução dessa cadeia, o conteúdo textual da resposta gerada é extraído e retornado pela função, sendo exibido diretamente na interface de chat**. Todo esse processo ocorre de forma transparente para o usuário, que apenas visualiza a resposta final no chat. A integração com o `Gradio` permite que essa função seja chamada automaticamente a cada nova mensagem enviada, viabilizando uma interface conversacional simples e interativa. **No geral, essa abordagem segue o paradigma de Retrieval-Augmented Generation (RAG)**, no qual a geração de respostas é enriquecida por informações previamente recuperadas, resultando em respostas mais precisas, contextualizadas e alinhadas ao domínio específico da aplicação.

