# Documentação – Assistente Virtual

## Versão 1.5

A versão **1.5** representa uma reformulação da arquitetura desenvolvida nas versões anteriores, deixando de ser uma palicação monolítica, onde tudo se concentrava em um único arquivo para se adequar a organização modular.

Além da reorganização, esta versão introduz novos mecanismos que tornam todo o processo de recuperação de informação mais eficiente e ampliam a as funcionalidades disponíveis ao usuário final.

Enquanto as versões **1.3** e **1.4** (essa, por sua vez, descontinuada) eram compostas por um único arquivo responsável por carregar a base de dados, realizar a classificação de perguntas, recuperar documentos, gerar respostas e disponibilizar uma interface via Gradio, a versão **1.5** distribui essas funcionalidades em arquivos independentes, separando as configurações do sistema, prompts utilizados, lógica do Retrieval-Augmented Generation (RAG) e a interface de comunicação com o usuário final através do Telegram.

Essa reorganização segue a base de modularização de software, onde cada componente é responsável por uma única função específica. Dessa forma, o código torna-se mais organizado, reutilizável e facilita futuras expansões do projeto.

Como foi dito, além da reorganização, foram também implementadas melhorias:

- **Persistência dos índices vetoriais FAISS**, envitando que toda a base vetorial precise ser reconstruída a cada inicialização do sistema, reduzindo significativamente o temp de carregamento da aplicação.

- **Aumento da quantidade de documentos recuperados durante busca vetorial**, o que permite o modelo trabalhar com um maior contexto mais amplo antes da etapa de filtragem.

- **Compressão automática do contexto**, onde após receber o maior contexto possível, seleciona apenas as informações relevantes em relação à mensagem do usuário para que o modelo possa gerar a melhor resposta possível.

- **Implementação de memória conversacional inteligente**, aqui um modelo de linguagem vai decidir quando o histórico da conversa é realmente necessário para responder corretamente a dúvida do usuário, evitando envio desnecessário de mensagens anteriores.

- **Estrutura de reranqueamento (Reranking)** dos documentos recuperados, permitindo que o modelo de linguagem selecione apenas os documentos mais relevantes antes da geração da resposta.

- **Envio automático de PDFs** sempre que identificado que o usuário realizou uma solicitação relacionada a um documento PDF da base de dados.

- **Ampliação do sistema de logs**, registrando não apenas os documentos inicialmente recuperados, mas também os documentos efetivamente utilizados na geração da resposta e o contexto comprimido.

- **Migração de interface de interação**, substituindo a interface web do Gradio por um bot integrado ao Telegram.

Com essas modificações, a versão 1.5 passa a incorporar diversas técnicas encontradas em arquiteturas modernas de sistemas conversacionais baseados em Grandes Modelos de Linguagem (Large Language Models – LLMs).

---

# 2. Fluxo Geral do Projeto

De forma geral, o funcionamento do sistema ocorre conforme o fluxo apresentado a seguir:

1. O usuário envia uma mensagem ao Assistente Virtual através do Telegram

2. A aplicação recebe a mensagem e identifica o usuário responsável pela conversa, recuperando automaticamente o histórico daquela sessão.

3. Um LLM realiza a **classficação semântica da pergunta**, identificando qual curso ou categoria intitucional está relacionada ao questionamento.

4. Após a classificação, o sistema seleciona o **retriever correspondente** ao curso identificado.

5. Antes da recuperação dos documentos, o sistema verifica se a mensagem corresponde a uma solicitação de envio de arquivo. Caso corresponda, o arquivo será enviado.

6. Caso não corresponda, o sistema realiza uma busca semântica no índice vetorial, recuperando os documentos mais relevantes relacionados ao questionamento.

7. Os documentos recuperados são organizados para formar o contexto inicial que será utilizado durante a geração da resposta.

8. Um segundo modelo entra em ação para realizar a etapa de **compressão de contexto**, onde, daquele contexto inicial, ele vai selecionar as partes que realmente tenham haver com a mensagem do usuário.

9. Em paralelo, outro modelo analise o histórico da conversa para decidir se as mensagens anteriores são realmente necessárias para responder a pergunta at
   ua.

10. Caso o histórico seja relevante, ele é formatado e enviado juntamente com o contexto recuperado. Caso não seja, apenas a pergunta atual e o contexto recuperado são utilizados.

11. O contexto, o histórico (caso necessário) e a pergunta do usuário são enviados ao modelo principal de linguagem.

12. O modelo gera a resposta utilizando exclusivamente as respostas enviadas anteriormente

13. Todas as informações da execução são registradas em log:
    - pergunta do usuário;
    - curso classificado;
    - documentos recuperados inicialmente;
    - documentos efetivamente utilizados;
    - contexto comprimido;
    - resposta gerada pelo modelo;

14. A resposta do modelo é retornada ao telegram

---

## Fluxo resumido da arquitetura

O processamento da versão 1.5 pode ser representado pela sequência abaixo:

```text
Usuário
    │
    ▼
Telegram Bot
    │
    ▼
Recebimento da pergunta
    │
    ▼
Classificação semântica do curso (LLM)
    │
    ▼
Seleção do Retriever correspondente
    │
    ├──────────────► Pedido de PPC?
    │                     │
    │                     ├── Sim ──► Localiza PDF ──► Envia documento
    │                     │
    │                     └── Não
    ▼
Busca vetorial (FAISS)
    │
    ▼
Recuperação dos documentos
    │
    ▼
Montagem do contexto
    │
    ▼
Compressão automática do contexto (LLM)
    │
    ▼
Decisão de uso da memória (LLM)
    │
    ▼
Prompt Principal
(Contexto + Histórico + Pergunta)
    │
    ▼
Modelo GPT-4.1-mini
    │
    ▼
Resposta
    │
    ▼
Registro de Logs
    │
    ▼
Envio da resposta ao Telegram
```

---

# 3. Estrutura da Versão

## 3.1 Arquivos

Os principais arquivos presentes na versão são:

- [**app.py**](./app.py): Arquivo responsável pela interface de comunicação com o usuário através do **Telegram**. Nele são implementados os comandos do bot, gerenciamento do histórico de conversas, tratamento das mensagens recebidas e envio das respostas geradas pelo sistema.

- [**config.py**](./config.py): Responsável por centralizar todas as configurações da aplicação. Neste arquivo são definidos os modelos de linguagem utilizados, os parâmetros de segmentação dos documentos (_chunking_), as configurações da base vetorial, os caminhos da base de dados, os cursos disponíveis e o carregamento dos indíces FAISS.

- [**prompts.py**](./prompts.py): Contém todos os prompts utilizados pelos modelos de linguagem durante o funcionamento do sistema.

- [**rag.py**](./rag.py): Implementa toda a arquitetura Retrieval-Augmented Generation (RAG) do Assistente Virtual. Aqui encontram-se as funções responsáveis pela classificação das perguntas, recuperação dos documentos, montagem do contexto, compressão do contexto, utilização da memória conversacional, geração das repostas e registro dos logs da aplicação.

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

# 4.1 config.py

O arquivo [`config.py`](./config.py) concentra todas as configurações globais do Assistente Virtual. Sua principal responsabilidade é preparar o ambiente antes que o sistema comece a responder às perguntas dos usuários, centralizando parâmetros, modelos de linguagem, bases vetoriais e retrievers.

## Carregamento das variáveis de ambiente

Inicialmente, o sistema realiza o carregamento das variáveis de ambiente utilizando a biblioteca `dotenv`. Nessa etapa são recuperadas as informações sensíveis, como os tokens e chaves de APIs.

## Configuração da estratégia de Chunking

Nas versões anteriores, os documentos eram divididos utilizando apenas um tamanho fixo de caracteres. Já na **v1.5**, o `RecursiveCharacterTextSplitter` passou a utilizar separadores personalizados, priorizando a divisão dos textos em limites semanticamente relevantes, como títulos de seções, listas de disciplinas e ementas.

Além disso, os parâmetros de segmentação também foram alterados para:

- **chunk_size = 4000**
- **chunk_overlap = 500**

Essa configuração permite preservar melhor o contexto de documentos longos, reduzindo a fragmentação de informações importantes durante a recuperação semântica.

## Inicialização dos modelos de linguagem

Outra melhoria implementada foi a separação dos modelos utilizados pelo sistema.

Enquanto versões anteriores utilizavam um único modelo para todas as tarefas, a **v1.5** define dois modelos distintos:

- **LLM principal:** responsável pela geração das respostas do usuário;
- **LLM compressor:** utilizado exclusivamente para filtrar o contexto recuperado antes do envio ao modelo principal.

## Persistência dos índices vetoriais

Em versões anteriores, sempre que o sistema era inicializado, todos os documentos precisavam ser carregados, transformados em embeddings e novamente indexados pelo FAISS. Esse processo aumentava significativamente o tempo de incialização do programa.

Na versão 1.5, antes de criar um novo índice vetorial, o sistema verifica se há mudanças nos dados ou se os dados são compatíveis com o que já existe nos índices. Caso não exista alteração, o índice é carregado automaticamente, eliminando a necessidade de reconstrução. Somente quando o índice ainda não foi criado ou caso exista alteração nos dados, o índice legado é apagado e um novo atualizado é criado e salvo para reutilizações futuras.

## Criação automática de retrievers

Por fim, após o carregamento ou criação dos índices vetoriais, o sistema instancia automaticamente um _retriever_ para cada curso disponível.

Todos os retrievers são armazenados em uma estrutura única de dados, permitindo que o módulo responsável pelo processamento das perguntas selecione dinamicamente o retriever correspondente ao curso identificado durante a etapa de classificação semântica.
