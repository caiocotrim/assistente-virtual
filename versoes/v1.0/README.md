### 1 Sobre a Versão 1.0
Como o próprio nome já diz, essa foi a primeira versão desenvolvida do Assistente Virtual. Neste momento, utilizamos apenas uma base de dados: [arquivos do curso de Bacharelado em Sistemas de Informação](../base-de-dados/dados-tratados/bsi/). Esta versão é simples, porém extremamente funcional para você que deseja implementar um Chatbot com apenas uma base de dados. 

---

## 2. Fluxo Geral do Projeto
1. Usuário envia uma mensagem informando a dúvida.
2. Retriever busca documentos relevantes no FAISS.
3. Prompt é preenchido com contexto + pergunta e enviado ao LLM.
4. LLM gera a resposta.
5. Gradio exibe a resposta no navegador.
---
## 3. Estrutura da Versão

### 3.1 Arquivos
Os principais arquivos presentes na versão são:
- [**app.py**](app.py): Arquivo principal que contém toda a lógica do Assistente Virtual (explicado no [Tópico 3 - Desenvolvimento](#3-desenvolvimento)). 

### 3.2 Tecnologias Utilizadas
O projeto faz uso de tecnologias voltadas a IA e processamento de linguagem natural:

- **Python**: Linguagem de programação utilizada para o desenvolvimento do projeto.

- **LangChain**: Framework utilizado para estruturar a pipeline do Assistente Virtual, manipular embeddings, construir prompts e integrar com modelos de linguagem

- **OpenAI API**: Plataforma que fornece o modelo de linguagem utilizado pelo Assistente Virtual.

- **FAISS**: Ferramenta de busca vetorial responsável por indexar e recuperar embeddings de forma eficiente.

- **Gradio**: Biblioteca que permite criar interfaces simples para teste e interação com o assistente via navegador.

---

## 4. Desenvolvimento
O desenvolvimento do projeto foi realizado através da linguagem de programação `Python` e o framework `LangChain`.

### 4.1 app.py
Este arquivo ([app.py](./app.py)) concentra o código-fonte da versão e toda a lógica por trás do funcionamento do Assistente Virtual. 
**Abaixo seguirá a explicação detalhada do código:**

#### 4.1.1 Importação de bibliotecas
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

3. **langchain_openai:** Integração oficial do LangChain com a OpenAI. Desse módulo foi utilizado `OpenAIEmbeddings` (*responsável por embedar - transformar o conteúdo dos arquivos da base de dados em vetores númericos*), `ChatOpenAI` (*abre um chat de conversa com um modelo do ChatGPT*).

 - OBS: Além dessas importações, foi utilizado também o `dotenv`, responsável por carregar e utilizar a minha chave API da OpenAI de forma segura e o `gradio` para utilizar uma interface de conversação pelo navegador.

#### 4.1.2 Preparação de dados
```python
loader = DirectoryLoader("base-de-dados/txt-files/bsi", glob="*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
docs_txt = loader.load()

embeddings = OpenAIEmbeddings()
base_vetores = FAISS.from_documents(docs_txt, embeddings)
retriever = base_vetores.as_retriever()
```
*Explicação:* Após a importação das bibliotecas, se fez necessário a preparação dos dados. Para isso, utilizamos o `DirectoryLoader` para encontrar os arquivos da nossa [base de dados](./base-de-dados/txt-files/bsi/) e o parâmetro `loader_cls=TextLoader` define que cada arquivo encontrado será carregado por meio do TextLoader, tendo em vista que os arquivos são **.txt**. Com os conteúdos dos arquivos encontrados, fizemos a utilização do método `.load()` na variável `loader` para retornar o conteúdo desses arquivos como documentos na variável `docs_txt`. Na segunda etapa, inicializamos `OpenAIEmbeddings()` na variável `embeddings`, que representa o modelo responsável por gerar os vetores numéricos a partir dos textos. Em seguida, criamos a variável `base_vetores`, que corresponde ao nosso índice vetorial `FAISS`. Nela, utilizamos `FAISS.from_documents()` para gerar os embeddings dos documentos presentes em `docs_txt` usando o modelo da OpenAI da variável `embeddings` e, ao mesmo tempo, armazenar esses vetores no índice `FAISS`. Por fim, utilizamos o método `as_retriever()` na variável `base_vetores` para adicionar um mecanismo de busca semântica no nosso índice vetorial (`FAISS`). Ou seja, o trecho `retriever = base_vetores.as_retriever()` é responsável por receber um texto de entrada (um input, por exemplo) e buscar documentos com a semântica parecida no `FAISS`. 
- OBS: O `retriever` não responde textos de entrada, apenas assimila e recupera documentos relevantes relacionados ao input por meio de busca semântica.

#### 4.1.3 Utilização de LLM
```python
llm = ChatOpenAI()

prompt_padrao="""
Você é um assistente virtual acadêmico especializado em fornecer informações sobre os cursos oferecidos pelo Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista. 
Utilize as informações fornecidas para responder às perguntas dos usuários de forma clara e precisa.

Contexto: {context}
Pergunta: {question}
"""
prompt = ChatPromptTemplate.from_template(prompt_padrao)

chain = ({"context": retriever, "question": RunnablePassthrough()} | prompt | llm)
```
*Explicação:* Após a preparação dos dados, partimos para a parte final: comunicação com o modelo de linguagem da OpenAI. Aqui, iniciamos com a criação de uma variável denominada `llm` onde inicializamos nela a função `ChatOpenAI()`, responsável por inicializar o modelo de linguagem da OpenAI no formato de chat. Dando sequência, criamos um prompt para ser enviado ao modelo de linguagm, armazenamos em uma variável (`prompt_padrao`) e, através do método `ChatPromptTemplate`, definimos esse prompt como prompt padrão, onde sempre que a API da OpenAI for solicitada e um chat for aberto, esse prompt será encaminhado. Após isso, definimos uma `chain`, que nada mais é do que uma sequência de passos utlizados pelo framework para automatizar o fluxo de trabalho. Essa `chain` é inicializada com um **context** cedido pelo `retriever` (*onde vai pegar o input do usuário, relacionar com até 4 arquivos semelhantes semanticamente falando e enviar como contexto ao modelo de linguagem*), uma **question** (*onde utilizamos o RunnablePassthrough pois o input não é algo estático e pré-definido, e sim enviado pelo usuário*), o **prompt** (*que é o prompt padrão citado anteriormente acrescentado do **context** passado pelo retriever e da **question** que é o input do usuário*) e o **llm** (*que é quando o prompt preenchido é enviado ao modelo de linguagem inicializado em um chat através do método `ChatOpenAI()`*). 

#### 4.1.4 Chat e Interface Gradio
```python
def responder(mensagem, historico): 
    retorno_chain = chain.invoke(mensagem)
    resposta = retorno_chain.content
    return resposta

interface = gradio.ChatInterface(fn=responder)
interface.launch()
```
*Explicação:* Por fim, após estruturar a preparação dos dados e o LLM, criamos uma função para utilizar a interface `Gradio` como ambiente de teste no navegador. Essa interface é bastante simples de implementar e utilizar, mas para isso, precisamos seguir algumas regras padrão. A primeira regra é que a função que será chamada pelo método `ChatInterface()` deve conter dois parâmetros: *`mensagem`* e *`historico`*. O parâmetro *`mensagem`* diz respeito a mensagem do usuário, já o parâmetro *`historico`* é o próprio histórico da troca de mensagens que ocorreu no chat `Gradio`, porém, sua captação é acontecida de forma automática pela biblioteca. Após a definição dos parâmetros, definimos a variável `retorno_chain` como `chain.invoke(mensagem)`, pois, através do `RunnablePassthrough` implementado na `chain`, a mensagem enviada pelo usuário será alocada justamente em `question` (conforme foi visto no tópico [**3.1.3 Utilização de LLM**](#313-utilização-de-llm)). Depois definimos outra variável, a `resposta`, onde ela recebe `retorno_chain.content` (isso acontece pois a chain vai retornar diversas informações na variável criada anteriormente (`retorno_chain`), e a informação que aloca a resposta do LLM é o `content`, por isso a variável que vai guardar a resposta tem que ser definida através do `retorno_chain.content`). Depois disso, a função retorna a resposta do LLM. Após a definição da função `def responder()`, partimos para a implementação do chat utilizado `Gradio`. Esse último passo é bem simples, basta utilizar o método `ChatInterface()` para que a interface de chat padrão do `Gradio` seja criada e com a função `def responder()` como parâmetro para que a função possa ser acionada para cada mensagem recebida no chat. Por fim, é utilizado o método `interface.launch()` para que a interface do `Gradio` seja disponibilizada em um servidor HTTP local, o que permite testes do projeto no navegador. 