# Documentação – Assistente Virtual

## Versão 1.5

A versão **1.5** representa uma reformulação significativa da arquitetura desenvolvida na versão **1.3**, deixando de utilizar uma estrutura monolítica baseada em um único arquivo para adotar uma organização modular, mais escalável e de fácil manutenção.

Além da reorganização do código em diferentes módulos, esta versão introduz novos mecanismos que tornam o processo de recuperação de informações mais eficiente, reduzem o consumo de tokens enviados ao modelo de linguagem e ampliam as funcionalidades disponíveis ao usuário final.

Enquanto a versão **1.3** era composta por um único arquivo responsável por carregar a base de dados, realizar a classificação das perguntas, recuperar documentos, gerar respostas e disponibilizar uma interface via Gradio, a versão **1.5** distribui essas responsabilidades em arquivos independentes, separando as configurações do sistema, os prompts utilizados pelos modelos de linguagem, a lógica da arquitetura Retrieval-Augmented Generation (RAG) e a interface de comunicação com o usuário através da plataforma Telegram.

Essa reorganização segue princípios de modularização de software, tornando cada componente responsável por uma única função específica. Como consequência, o código torna-se mais organizado, reutilizável e facilita futuras expansões do projeto.

Além da reorganização estrutural, a versão 1.5 incorpora diversas melhorias na arquitetura RAG, permitindo um fluxo de processamento mais robusto e mais próximo de aplicações reais de Inteligência Artificial Generativa.

Entre as principais melhorias implementadas nesta versão destacam-se:

- **Modularização completa do projeto**, separando a aplicação em arquivos independentes responsáveis pelas configurações do sistema, definição dos prompts, processamento RAG e interface com o Telegram.

- **Persistência dos índices vetoriais FAISS**, evitando que toda a base vetorial precise ser reconstruída a cada inicialização do sistema, reduzindo significativamente o tempo de carregamento da aplicação.

- **Aumento da quantidade de documentos recuperados durante a busca vetorial**, permitindo que o sistema trabalhe inicialmente com um contexto mais amplo antes da etapa de filtragem.

- **Compressão automática do contexto**, utilizando um segundo modelo de linguagem responsável por remover apenas informações irrelevantes antes da geração da resposta final, reduzindo o número de tokens enviados ao modelo principal sem perda significativa de informações importantes.

- **Implementação de memória conversacional inteligente**, onde um modelo de linguagem decide automaticamente quando o histórico da conversa é realmente necessário para responder corretamente à pergunta do usuário, evitando o envio desnecessário de mensagens anteriores.

- **Estrutura preparada para reranqueamento (Reranking)** dos documentos recuperados, permitindo que um modelo de linguagem selecione apenas os documentos mais relevantes antes da geração da resposta. Embora essa funcionalidade permaneça temporariamente desativada durante os testes da versão 1.5, sua implementação já faz parte da arquitetura do sistema.

- **Envio automático do Projeto Pedagógico de Curso (PPC)** em formato PDF sempre que identificado que o usuário realizou uma solicitação relacionada ao documento.

- **Ampliação do sistema de logs**, registrando não apenas os documentos inicialmente recuperados, mas também os documentos efetivamente utilizados na geração da resposta, além do contexto comprimido enviado ao modelo principal.

- **Migração da interface de interação**, substituindo a interface web desenvolvida com Gradio por um bot integrado ao Telegram, permitindo maior acessibilidade e uma experiência de uso mais próxima de aplicações reais.

Com essas modificações, a versão 1.5 deixa de ser apenas uma prova de conceito baseada em Retrieval-Augmented Generation (RAG) e passa a incorporar diversas técnicas encontradas em arquiteturas modernas de sistemas conversacionais baseados em Grandes Modelos de Linguagem (Large Language Models – LLMs), incluindo mecanismos de otimização de contexto, gerenciamento inteligente de memória, persistência de índices vetoriais e separação das responsabilidades da aplicação.

Como resultado, o Assistente Virtual apresenta uma arquitetura mais eficiente, escalável e preparada para futuras evoluções, facilitando tanto sua manutenção quanto a incorporação de novas funcionalidades nas próximas versões do projeto.

---

---

# 2. Fluxo Geral do Projeto

A arquitetura da versão **1.5** segue o paradigma **Retrieval-Augmented Generation (RAG)**, porém incorpora diversos mecanismos adicionais responsáveis por otimizar a recuperação de informações, reduzir o consumo de tokens enviados ao modelo de linguagem e melhorar a organização interna da aplicação.

De forma geral, o funcionamento do sistema ocorre conforme o fluxo apresentado a seguir:

1. O usuário envia uma mensagem ao Assistente Virtual através do bot do Telegram.

2. A aplicação recebe a mensagem e identifica o usuário responsável pela conversa, recuperando automaticamente o histórico daquela sessão.

3. Um modelo de linguagem (LLM) realiza a **classificação semântica da pergunta**, identificando automaticamente qual curso ou categoria institucional está relacionada ao questionamento.

4. Após a classificação, o sistema seleciona o **retriever correspondente** ao curso identificado.

5. Antes da recuperação dos documentos, o sistema verifica se a mensagem corresponde a uma solicitação do **Projeto Pedagógico de Curso (PPC)**. Caso seja identificado um pedido de envio do documento, o arquivo PDF correspondente é localizado e preparado para envio ao usuário.

6. Caso a pergunta não corresponda a uma solicitação de PPC, o retriever realiza uma busca semântica no índice vetorial FAISS, recuperando os documentos mais relevantes relacionados ao questionamento.

7. Os documentos recuperados são organizados para formar o contexto inicial que será utilizado durante a geração da resposta.

8. Opcionalmente, um segundo modelo de linguagem executa a etapa de **compressão automática do contexto**, removendo apenas informações consideradas irrelevantes para a pergunta atual, mantendo intactas listas, tabelas, datas, nomes próprios e demais informações necessárias para a geração da resposta.

9. Em paralelo, outro modelo de linguagem analisa o histórico da conversa para decidir automaticamente se as mensagens anteriores são realmente necessárias para responder corretamente à pergunta atual.

10. Caso o histórico seja considerado relevante, ele é formatado e enviado juntamente com o contexto recuperado. Caso contrário, apenas a pergunta atual e o contexto recuperado são utilizados.

11. O contexto (original ou comprimido), o histórico (quando necessário) e a pergunta do usuário são enviados ao modelo principal de linguagem.

12. O modelo gera a resposta utilizando exclusivamente as informações presentes no contexto recuperado, evitando a utilização de conhecimento externo ao sistema.

13. Todas as informações da execução são registradas em um arquivo de log, incluindo:
    - pergunta realizada pelo usuário;
    - curso classificado;
    - documentos inicialmente recuperados;
    - documentos efetivamente utilizados;
    - contexto comprimido enviado ao modelo;
    - resposta gerada pelo assistente.

14. A resposta é enviada ao usuário através do Telegram.

15. Caso exista um arquivo PDF associado à solicitação realizada, o documento também é enviado automaticamente ao usuário após a resposta textual.

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

Observa-se que, diferentemente das versões anteriores, a arquitetura da versão **1.5** passa a utilizar múltiplos modelos de linguagem especializados em tarefas distintas ao longo do fluxo de processamento.

Enquanto o modelo principal permanece responsável pela geração da resposta final, outros modelos atuam em tarefas específicas, como a classificação do curso, a decisão de utilização da memória conversacional e a compressão automática do contexto. Essa divisão de responsabilidades reduz a complexidade de cada etapa, melhora a qualidade das respostas geradas e diminui a quantidade de informações desnecessárias enviadas ao modelo principal.

Outra mudança importante introduzida nesta versão é a persistência dos índices vetoriais FAISS. Nas versões anteriores, os embeddings eram reconstruídos sempre que a aplicação era iniciada. Na versão 1.5, os índices passam a ser armazenados em disco e reutilizados nas próximas execuções, reduzindo significativamente o tempo de inicialização do sistema.

Essa combinação de classificação semântica, recuperação vetorial, compressão automática de contexto, gerenciamento inteligente de memória e persistência dos índices aproxima a arquitetura desenvolvida de soluções modernas empregadas em sistemas baseados em Retrieval-Augmented Generation (RAG), tornando o Assistente Virtual mais eficiente, escalável e preparado para futuras evoluções.

---

# 3. Estrutura da Versão

Uma das principais mudanças introduzidas na versão **1.5** foi a reorganização completa da estrutura do projeto.

Enquanto as versões anteriores concentravam praticamente toda a lógica da aplicação em um único arquivo (`app.py`), esta versão adota uma arquitetura modular, separando cada responsabilidade em arquivos independentes. Essa organização segue princípios de engenharia de software, como separação de responsabilidades (_Separation of Concerns_), facilitando a manutenção, reutilização de código e implementação de novas funcionalidades.

Com essa divisão, cada arquivo passa a desempenhar uma função específica dentro da arquitetura do Assistente Virtual, reduzindo o acoplamento entre os componentes e tornando o projeto mais organizado e escalável.

---

## 3.1 Arquivos

A versão 1.5 é composta pelos seguintes arquivos principais:

- [**app.py**](./app.py)

  Arquivo responsável pela interface de comunicação com o usuário através do Telegram. Nele são implementados os comandos do bot, o gerenciamento do histórico de conversas de cada usuário, o tratamento das mensagens recebidas e o envio das respostas geradas pelo sistema.

- [**config.py**](./config.py)

  Responsável por centralizar todas as configurações da aplicação. Neste arquivo são definidos os modelos de linguagem utilizados, os parâmetros de segmentação dos documentos (_chunking_), as configurações da base vetorial, os caminhos da base de dados, os cursos disponíveis e o carregamento dos índices FAISS.

- [**prompts.py**](./prompts.py)

  Contém todos os prompts utilizados pelos modelos de linguagem durante o funcionamento do sistema. Cada prompt possui uma finalidade específica, como classificação do curso, decisão sobre utilização da memória, compressão de contexto, reranqueamento dos documentos e geração da resposta final.

- [**rag.py**](./rag.py)

  Implementa toda a arquitetura Retrieval-Augmented Generation (RAG) do Assistente Virtual. Neste arquivo encontram-se as funções responsáveis pela classificação das perguntas, recuperação dos documentos, montagem do contexto, compressão do contexto, utilização da memória conversacional, geração das respostas e registro dos logs da aplicação.

Essa separação torna cada componente independente, permitindo que futuras modificações sejam realizadas em um único módulo sem necessidade de alterar toda a aplicação.

---

## 3.2 Tecnologias Utilizadas

O desenvolvimento da versão **1.5** utiliza diversas tecnologias relacionadas à Inteligência Artificial, Recuperação de Informação, Processamento de Linguagem Natural e desenvolvimento de aplicações conversacionais.

As principais tecnologias empregadas são descritas a seguir.

### Python

Linguagem de programação utilizada para implementar toda a lógica da aplicação. Sua vasta disponibilidade de bibliotecas voltadas para Inteligência Artificial, além da simplicidade de integração com APIs externas, tornou-a a linguagem escolhida para o desenvolvimento do projeto.

---

### LangChain

Framework utilizado para estruturar toda a arquitetura baseada em Retrieval-Augmented Generation (RAG).

Na versão 1.5 o LangChain é utilizado para:

- construção dos prompts;
- integração com os modelos de linguagem da OpenAI;
- criação das cadeias (_chains_);
- carregamento da base documental;
- geração de embeddings;
- integração com o FAISS.

Sua utilização permite organizar o fluxo de processamento da aplicação de maneira modular e de fácil manutenção.

---

### OpenAI API

Responsável por disponibilizar os modelos de linguagem utilizados pelo Assistente Virtual.

Na versão 1.5 diferentes modelos desempenham funções distintas dentro da arquitetura.

Entre elas destacam-se:

- classificação do curso relacionado à pergunta;
- decisão automática de utilização da memória conversacional;
- compressão automática do contexto;
- reranqueamento dos documentos recuperados (estrutura já implementada);
- geração da resposta final ao usuário.

Essa abordagem permite distribuir diferentes tarefas entre modelos especializados, reduzindo a complexidade de cada etapa do processamento.

---

### OpenAI Embeddings

Utilizado para transformar os documentos textuais em representações vetoriais (_embeddings_), possibilitando a realização de buscas semânticas através do índice FAISS.

Os embeddings permitem que o sistema encontre documentos semanticamente semelhantes à pergunta do usuário, mesmo quando diferentes palavras ou expressões são utilizadas.

---

### FAISS

Biblioteca responsável pela criação dos índices vetoriais utilizados durante a recuperação de documentos.

Nesta versão, além da busca vetorial propriamente dita, o FAISS passa a oferecer persistência dos índices em disco. Dessa forma, sempre que a aplicação é iniciada, os índices previamente criados são reutilizados, evitando que todos os embeddings precisem ser reconstruídos novamente.

Essa melhoria reduz significativamente o tempo de inicialização da aplicação.

---

### python-telegram-bot

Biblioteca utilizada para implementar o bot do Telegram.

Ela é responsável por:

- receber mensagens enviadas pelos usuários;
- tratar comandos do bot;
- enviar respostas textuais;
- enviar arquivos PDF;
- manter a comunicação entre os usuários e o Assistente Virtual.

A substituição da interface desenvolvida com Gradio pela integração com o Telegram torna o sistema mais acessível e mais próximo de uma aplicação real.

---

### python-dotenv

Biblioteca utilizada para carregar variáveis de ambiente armazenadas no arquivo `.env`.

Sua utilização evita que informações sensíveis, como a chave da API da OpenAI e o token do bot do Telegram, sejam inseridas diretamente no código-fonte, aumentando a segurança da aplicação.

---

### JSON

Utilizado para registrar os logs de execução do sistema.

Cada interação realizada pelo usuário é armazenada em formato JSON Lines (`.jsonl`), permitindo registrar informações importantes como a pergunta realizada, os documentos recuperados, o contexto utilizado e a resposta gerada pelo modelo.

Esse mecanismo facilita análises posteriores sobre o comportamento do Assistente Virtual.

---

### Pathlib

Biblioteca utilizada para manipulação de caminhos de arquivos e diretórios de maneira independente do sistema operacional.

Sua utilização torna o projeto mais portável, permitindo que os caminhos internos sejam resolvidos corretamente em diferentes ambientes de execução.

---

### OS

Utilizada para operações relacionadas ao sistema operacional, incluindo verificação da existência de arquivos, criação automática de diretórios e carregamento de variáveis de ambiente.

Também é utilizada durante o carregamento e persistência dos índices vetoriais e no envio automático dos arquivos PDF dos Projetos Pedagógicos de Curso.

---

Observa-se que a versão **1.5** amplia significativamente o conjunto de tecnologias utilizadas em relação às versões anteriores.

Além das bibliotecas tradicionalmente empregadas em sistemas RAG, esta versão incorpora ferramentas voltadas para persistência de índices, gerenciamento de arquivos, integração com plataformas de mensagens instantâneas e otimização do processamento dos modelos de linguagem, resultando em uma arquitetura mais robusta, modular e preparada para futuras expansões.

---

# 4. Desenvolvimento

O desenvolvimento da versão **1.5** foi realizado utilizando a linguagem de programação **Python** e o framework **LangChain**, organizando o Assistente Virtual em uma arquitetura modular baseada no paradigma **Retrieval-Augmented Generation (RAG)**.

Diferentemente da versão 1.3, onde praticamente toda a implementação encontrava-se concentrada em um único arquivo (`app.py`), a versão 1.5 distribui as responsabilidades da aplicação em módulos independentes. Cada arquivo passou a desempenhar uma função específica dentro da arquitetura, tornando o código mais organizado, reutilizável e de fácil manutenção.

Essa reorganização também facilita futuras evoluções do projeto, permitindo adicionar novas funcionalidades sem a necessidade de modificar toda a estrutura da aplicação.

A implementação da versão 1.5 está organizada conforme os seguintes módulos:

- **config.py:** responsável pelas configurações gerais da aplicação, carregamento dos documentos, criação e persistência dos índices vetoriais, configuração dos modelos de linguagem e definição dos retrievers.

- **prompts.py:** responsável por armazenar todos os prompts utilizados pelos modelos de linguagem durante as diferentes etapas do processamento.

- **rag.py:** implementa toda a arquitetura Retrieval-Augmented Generation (RAG), incluindo classificação das perguntas, recuperação de documentos, gerenciamento da memória conversacional, compressão do contexto, geração das respostas e registro dos logs.

- **app.py:** implementa a interface de comunicação através do Telegram, realizando o gerenciamento das mensagens enviadas pelos usuários e integrando o bot à arquitetura RAG desenvolvida.

Nas próximas seções será apresentada uma descrição detalhada de cada um desses arquivos, explicando o funcionamento de suas principais funções e a finalidade de cada componente utilizado durante o processamento das perguntas.

---

# 4.1 `config.py` – Configuração e Inicialização do Sistema

O arquivo [`config.py`](./config.py) concentra todas as configurações globais do Assistente Virtual. Sua principal responsabilidade é preparar o ambiente antes que o sistema comece a responder às perguntas dos usuários, centralizando parâmetros, modelos de linguagem, bases vetoriais e retrievers.

Diferentemente da versão 1.3, onde toda essa configuração estava concentrada em um único arquivo (`app.py`), a versão 1.5 adota uma arquitetura modular. Essa reorganização torna o código mais limpo, facilita futuras manutenções e permite que diferentes componentes reutilizem as mesmas configurações sem duplicação de código.

As principais responsabilidades deste módulo são apresentadas a seguir.

---

## Carregamento das variáveis de ambiente

Inicialmente, o sistema realiza o carregamento das variáveis de ambiente utilizando a biblioteca `dotenv`. Nessa etapa são recuperadas informações sensíveis, como o token de autenticação do bot do Telegram e a chave da API da OpenAI, evitando que esses dados fiquem expostos diretamente no código-fonte.

Além disso, é utilizado o módulo `pathlib` para localizar automaticamente o diretório raiz do projeto, permitindo que os arquivos sejam encontrados corretamente independentemente do sistema operacional utilizado.

---

## Configuração da estratégia de Chunking

Uma das principais modificações desta versão foi a atualização da estratégia de segmentação dos documentos.

Na versão 1.3, os documentos eram divididos utilizando apenas um tamanho fixo de caracteres. Já na versão 1.5, o `RecursiveCharacterTextSplitter` passou a utilizar separadores personalizados, priorizando a divisão dos textos em limites semanticamente relevantes, como títulos de seções, listas de disciplinas, ementas e demais estruturas presentes nos Projetos Pedagógicos dos Cursos (PPCs).

Além disso, os parâmetros de segmentação também foram alterados para:

- **chunk_size = 4000**
- **chunk_overlap = 500**

Essa configuração permite preservar melhor o contexto de documentos longos, reduzindo a fragmentação de informações importantes durante a recuperação semântica.

---

## Inicialização dos modelos de linguagem

Outra melhoria implementada foi a separação dos modelos utilizados pelo sistema.

Enquanto versões anteriores utilizavam um único modelo para todas as tarefas, a versão 1.5 define dois modelos distintos:

- **LLM principal**, responsável pela geração das respostas ao usuário;
- **LLM compressor**, utilizado exclusivamente para filtrar o contexto recuperado antes do envio ao modelo principal.

Essa separação torna a arquitetura mais flexível, permitindo substituir futuramente qualquer um dos modelos de forma independente, sem alterar o restante do sistema.

---

## Centralização das informações dos cursos

Outra alteração importante foi a criação de uma estrutura única contendo todas as informações referentes aos cursos disponíveis no sistema.

Cada curso possui seu nome, diretório contendo os documentos tratados, o local onde seu índice vetorial é armazenado e, quando existente, o caminho para o respectivo Projeto Pedagógico do Curso (PPC).

Essa organização elimina estruturas repetidas existentes na versão anterior e facilita a inclusão de novos cursos no futuro, sendo necessário apenas adicionar uma nova entrada na estrutura de configuração.

---

## Persistência dos índices vetoriais

Uma das principais evoluções da versão 1.5 foi a implementação da persistência dos índices vetoriais.

Na versão 1.3, toda vez que o sistema era iniciado, todos os documentos precisavam ser carregados, transformados em embeddings e novamente indexados no FAISS. Esse processo aumentava significativamente o tempo de inicialização da aplicação.

Na versão 1.5, antes de criar um novo índice vetorial, o sistema verifica se ele já existe em disco. Caso exista, o índice é carregado diretamente, eliminando a necessidade de reconstrução. Somente quando o índice ainda não foi criado é que os documentos são processados e um novo índice é gerado e salvo para reutilizações futuras.

Essa modificação reduz significativamente o tempo de inicialização da aplicação e torna a execução do sistema mais eficiente.

---

## Criação automática dos retrievers

Por fim, após o carregamento ou criação dos índices vetoriais, o sistema instancia automaticamente um _retriever_ para cada curso disponível.

Todos os retrievers são armazenados em uma estrutura única de dados, permitindo que o módulo responsável pelo processamento das perguntas selecione dinamicamente o retriever correspondente ao curso identificado durante a etapa de classificação semântica.

Além disso, cada retriever foi configurado para recuperar até **8 documentos** (`k = 8`), ampliando a quantidade de contexto disponível para as etapas posteriores de processamento, como a compressão automática do contexto e a geração da resposta final.
