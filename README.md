# Documentação -  Assistente Virtual [PIBIC]

Este é um projeto desenvolvido pelo discente Caio Cotrim Pereira, do curso de Sistemas de Informação do Instituto Federal da Bahia (IFBA) - Campus Vitória da Conquista, orientado pelo docente Dr. Leonardo Barreto Campos, em parceria com o Programa Institucional de Bolsas de Iniciação Científica [PIBIC] ofertado pelo CNPq.

---

## 1. Descrição Geral
O projeto consiste no desenvolvimento de um Assistente Virtual para o IFBA (Campus Vitória da Conquista) especializado em responder questionamentos e dúvidas sobre o contexto acadêmico da universidade - principalmente sobre os cursos superiores ofertados pela instituição: Química, Sistemas de Informação, Eng. Ambiental, Eng. Civil, Eng. Elétrica, Eng. Mecânica.

## 2 Sobre a Versões

#### 2.1 Versão 1.0
Como o próprio nome já diz, essa foi a primeira versão desenvolvida do Assistente Virtual. Nesta versão, utilizamos apenas uma base de dados: [arquivos do curso de Bacharelado em Sistemas de Informação](base-de-dados/dados-tratados/bsi/). Esta versão é simples, porém extremamente funcional para você que deseja implementar um Chatbot com apenas uma base de dados.

#### 2.2 Versão 1.1
Essa foi a segunda versão desenvolvida do Assistente Virtual. Neste momento, crescemos nossa base de dados para abranger documentos de todos os cursos de ensino superior ofertados pelo IFBA - Vitória da Conquista: [arquivos do curso de Bacharelado em Sistemas de Informação](../base-de-dados/dados-tratados/bsi/). Esta versão é um pouco mais robusta que a versão 1.0, nela foi necessário implementar uma base de dados para cada curso para que não haja erros na busca por similaridade semântica tendo em vista que os documentos acadêmicos possuem uma certa semelhança. Além disso, foi implementado também uma função para fazer o reconhecimento do curso que o usuário está se referindo. Essa função em questão é fundamental para fazer o filtro definir em qual base de dados será feita a busca.

#### 2.3 Versão 1.2
Essa foi a terceira versão desenvolvida do Assistente Virtual. Nesta etapa, houve uma evolução significativa na forma como o sistema interpreta as perguntas dos usuários. Diferente da versão 1.1, que utilizava regras fixas e palavras-chave para identificar o curso relacionado, a versão 1.2 passou a utilizar um modelo de linguagem (LLM) para realizar essa classificação de forma semântica.

Com essa mudança, o assistente se tornou mais inteligente e flexível, sendo capaz de compreender melhor variações na forma como os usuários escrevem suas perguntas, mesmo quando não utilizam termos exatos. A partir da classificação realizada pelo LLM, o sistema seleciona automaticamente a base de dados mais adequada para realizar a busca, reduzindo ambiguidades e melhorando a precisão das respostas.

#### 2.4 Versão 1.3
Essa foi a quarta versão desenvolvida do Assistente Virtual. Nesta versão, foram introduzidas melhorias importantes na etapa de recuperação de informações e no monitoramento do funcionamento do sistema, tornando a arquitetura mais próxima de aplicações reais.

Entre os principais avanços, destaca-se a implementação da segmentação de documentos (chunking), permitindo dividir textos longos em partes menores e mais relevantes para a busca semântica, o que melhora a qualidade dos resultados retornados. Além disso, foi implementado um sistema de registro de logs, possibilitando armazenar informações sobre cada interação, como perguntas, respostas, documentos recuperados e o curso classificado.

Essas melhorias tornam o sistema mais robusto, transparente e preparado para análises posteriores, contribuindo para a evolução contínua do assistente.

#### 2.5 Versão 1.4
Essa foi a quinta versão desenvolvida do Assistente Virtual. Nesta versão, o foco foi refinar a qualidade do contexto enviado ao LLM e ampliar o escopo de perguntas que o assistente consegue atender, mantendo toda a lógica em um único arquivo (`app.py`) com interface em Gradio.

O primeiro avanço é a criação de uma base de dados **geral**, voltada a perguntas que não se referem a nenhum curso específico, como informações institucionais, calendário acadêmico, eventos, matrícula e biblioteca. Com isso, o classificador baseado em LLM passou a reconhecer seis categorias (os cinco cursos e a categoria *geral*) e a direcionar a busca para a base mais adequada. Além disso, os índices vetoriais (FAISS) de cada base passaram a ser salvos em disco: na primeira execução eles são criados e, nas seguintes, apenas carregados, reduzindo bastante o tempo de inicialização e o custo com embeddings.

Também foi implementada uma etapa de **reranqueamento**. A busca semântica passou a recuperar mais documentos (k = 8) e, em seguida, o LLM seleciona os 3 trechos mais relevantes para compor o contexto da resposta, reduzindo ruídos no prompt. Outra melhoria foi o uso inteligente da **memória da conversa**: antes de responder, o LLM decide se a pergunta atual depende do histórico (por exemplo, quando o usuário diz "esse curso" ou "também"), e o histórico só é enviado ao modelo quando realmente necessário. Por fim, o assistente passou a reconhecer quando o usuário solicita o **PPC** (Projeto Pedagógico do Curso) e, nesse caso, devolve o PDF do curso identificado, e os logs passaram a registrar tanto os documentos recuperados quanto os documentos efetivamente utilizados na resposta.

#### 2.6 Versão 1.5
Essa foi a sexta versão desenvolvida do Assistente Virtual e a que apresenta a maior reestruturação do projeto até o momento. Nesta versão, o código deixou de ser um único arquivo e passou a ser organizado em módulos com responsabilidades bem definidas, além de ganhar novos canais de atendimento (Telegram e WhatsApp), cache semântico, compressão de contexto e envio de ementas.

A **arquitetura modular** é composta pelos seguintes arquivos:
- `config.py`: concentra as configurações do sistema, como modelos de linguagem, embeddings, parâmetros de chunking e o dicionário `CURSOS`, que reúne, para cada curso, o nome, as pastas de dados, o índice vetorial, o PPC em PDF e a pasta de ementas. Os índices FAISS e os retrievers de todas as bases são criados a partir dessa estrutura.
- `prompts.py`: reúne todos os prompts utilizados (classificação do curso, memória, rerank, resposta principal, compressão de contexto e identificação de ementas).
- `rag.py`: contém o pipeline principal do assistente, com a função `responder`, responsável por orquestrar todas as etapas.
- `semantic_cache.py`: implementa o cache semântico.
- `telegram.py` e `whatsapp.py`: são as interfaces de comunicação com o usuário.

No pipeline de recuperação, o chunking foi ajustado para segmentos maiores (4000 caracteres, com sobreposição de 500) e com separadores específicos para documentos acadêmicos (como *DOCENTES*, *DISCIPLINAS*, *EMENTA* e *OBJETIVOS*), preservando melhor tabelas e listas extraídas dos PDFs. Foi adicionada também a **compressão de contexto**: um LLM auxiliar filtra os trechos recuperados, removendo apenas informações irrelevantes e preservando nomes, listas completas, números e datas, antes de enviar o contexto ao modelo principal. Essa etapa pode ser ativada ou desativada pela configuração `USAR_COMPRESSAO_CONTEXTO`. Nesta versão, o rerank foi desativado, e os modelos passaram a ser definidos explicitamente (`gpt-4.1-mini`).

O **cache semântico** armazena as perguntas já respondidas, organizadas por curso, em arquivos JSON (`respostas/<curso>/resp-<curso>.json`). A partir desses arquivos, um índice FAISS é reconstruído automaticamente, e novas perguntas são comparadas por similaridade com as já existentes. Quando a distância fica abaixo do limiar definido, a resposta salva é retornada imediatamente, sem passar pelo restante do pipeline, o que reduz o tempo de resposta e o custo com chamadas ao LLM.

Outra novidade é o envio de **ementas de disciplinas**. Quando o usuário solicita a ementa de uma disciplina, o LLM extrai o nome citado, o sistema busca por similaridade de texto entre os nomes dos arquivos de imagem da pasta de ementas do curso e, caso haja ambiguidade entre candidatos próximos, o LLM escolhe o arquivo que corresponde exatamente à disciplina pedida. O envio do PPC em PDF foi mantido.

Por fim, a resposta do pipeline passou a ser retornada em formato estruturado (texto, arquivo e tipo do arquivo), permitindo que cada canal envie texto, PDF ou imagem da forma adequada. Os canais disponíveis são:
- **Telegram** (`telegram.py`): bot com os comandos `/start` e `/help`, que mantém um histórico separado para cada conversa.
- **WhatsApp** (`whatsapp.py`): integração via [Evolution API](https://github.com/EvolutionAPI/evolution-api), implementada como um servidor Flask que recebe os eventos por *webhook*. Ignora mensagens de grupos e do próprio bot e permite restringir o atendimento a uma lista de números autorizados.

Os logs também foram ampliados e passaram a registrar o contexto comprimido enviado ao modelo.

---

## 3. Estrutura do Projeto

### 3.1 Pastas
A organização de pastas do projeto segue uma estrutura simples e objetiva, facilitando a manutenção e expansão futura:
- [**base-de-dados**](../base-de-dados/): Diretório que armazena o conteúdo da base de dados do projeto. Este diretório é divido em duas pastas: [dados-brutos](../base-de-dados/dados-brutos/) e [dados-tratados](../base-de-dados/dados-tratados/).

    - [**dados-brutos**](../base-de-dados/dados-brutos/): Essa pasta se refere aos dados brutos de cada curso. Arquivos como *PDF*, *DOCX*, *DOC*, *TXT*... são armazenados aqui. A pasta **dados-brutos** é dividida em subpastas responsáveis por armazenar os dados não tratados de cada curso em questão. A partir da versão 1.5, cada curso também possui uma subpasta **ementas**, que armazena as imagens (*JPG*) das ementas de cada disciplina.

        - **subpastas de dados-brutos**:
            - [**ambiental**](./base-de-dados/dados-brutos/ambiental/): Aqui estão armazenados os arquivos referentes ao curso de Bacharelado em Engenharia Ambiental.

            - [**bsi**](./base-de-dados/dados-brutos/bsi/): Aqui estão armazenados os arquivos referentes ao curso de Bacharelado em Sistemas de Informação.

            - [**civil**](./base-de-dados/dados-brutos/civil/): Aqui estão armazenados os arquivos referentes ao curso de Bacharelado em Engenharia Civil.

            - [**eletrica**](./base-de-dados/dados-brutos/eletrica/): Aqui estão armazenados os arquivos referentes ao curso de Bacharelado em Engenharia Elétrica.

            - [**quimica**](./base-de-dados/dados-brutos/quimica/): Aqui estão armazenados os arquivos referentes ao curso de Licenciatura em Química.

    - [**dados-tratados**](../base-de-dados/dados-tratados/): Essa pasta se refere aos dados tratados de cada curso. Apenas arquivos de TXT são armazenados aqui. Isso acontece pois facilita a comunicação com o LLM, tendo em vista que parte desses arquivos serão enviados como prompt e o LLM se comunica melhor com textos limpos e segmentados. A pasta **dados-tratados** é dividida em subpastas responsáveis por armazenar os dados de cada curso em questão.

        - **subpastas de dados-tratados**:
            - [**ambiental**](./base-de-dados/dados-tratados/ambiental/): Aqui estão armazenados os arquivos de texto referentes ao curso de Bacharelado em Engenharia Ambiental.

            - [**bsi**](./base-de-dados/dados-tratados/bsi/): Aqui estão armazenados os arquivos de texto referentes ao curso de Bacharelado em Sistemas de Informação.

            - [**civil**](./base-de-dados/dados-tratados/civil/): Aqui estão armazenados os arquivos de texto referentes ao curso de Bacharelado em Engenharia Civil.

            - [**eletrica**](./base-de-dados/dados-tratados/eletrica/): Aqui estão armazenados os arquivos de texto referentes ao curso de Bacharelado em Engenharia Elétrica.

            - [**quimica**](./base-de-dados/dados-tratados/quimica/): Aqui estão armazenados os arquivos de texto referentes ao curso de Licenciatura em Química.

            - [**geral**](./base-de-dados/dados-tratados/geral/): Aqui estão armazenados os arquivos de texto com informações que não pertencem a um curso específico, como dados institucionais, calendário acadêmico, matrícula e biblioteca (a partir da versão 1.4).

- [**versoes**](/versoes/): Contém as implementações completas de cada versão do Assistente Virtual. 
    - [**v1.0**](/versoes/v1.0/) - Versão: Inicial - Apenas 1 curso. 
    - [**v1.1**](/versoes/v1.1/) - Versão: Expandida - Abrange mais de 1 curso.
    - [**v1.2**](/versoes/v1.2/) - Versão: LLM - Utiliza mais o LLM do que nas versões anteriores.
    - [**v1.3**](/versoes/v1.3/) - Versão: Chunking e Log - Utiliza chunking para maior acertividade do RAG e log para um melhor monitoramento das interações. 
    - [**v1.4**](/versoes/v1.4/) - Versão: Rerank e Memória - Adiciona a base geral, reranqueamento de documentos, uso seletivo do histórico e envio do PPC.
    - [**v1.5**](/versoes/v1.5/) - Versão: Modular e Multicanal - Arquitetura modular, cache semântico, compressão de contexto, envio de ementas e integração com Telegram e WhatsApp.

- [**artigo-cientifico**](/artigo-cientifico/): Contém o artigo científico produzido a partir do desenvolvimento deste projeto, escrito pelo discente com a orientação do docente Dr. Leonardo Barreto Campos.

- **logs**: Pasta criada automaticamente a partir da versão 1.3, onde ficam os registros das interações (`logs.jsonl`).

---
## 4. Como Executar

Siga os passos abaixo para rodar qualquer versão do projeto localmente.

1. Instale as dependências necessárias. No seu ambiente Python, instale os pacotes usados pelo projeto:
```python
pip install gradio langchain python-dotenv
```
Para as versões **v1.4 e v1.5**, instale também os pacotes de busca vetorial e integração com a OpenAI:
```python
pip install langchain-community langchain-openai langchain-text-splitters faiss-cpu
```
Para a versão **v1.5**, instale ainda os pacotes dos canais de atendimento:
```python
pip install python-telegram-bot flask requests
```

2. Configure suas chaves de acesso. Crie um arquivo chamado `.env` na **raiz do seu projeto** e adicione sua chave da OpenAI seguindo este padrão:
```python
OPENAI_API_KEY=xxxx 
(Substitua `xxxx` pela sua chave real)
```
Na versão **v1.5**, adicione também as variáveis do canal que você pretende utilizar:
```python
# Telegram
TELEGRAM_TOKEN=xxxx

# WhatsApp (Evolution API)
EVOLUTION_URL=http://localhost:8080
EVOLUTION_API_KEY=xxxx
EVOLUTION_INSTANCE=assistente-ifba
NUMEROS_PERMITIDOS=5577999999999,5577888888888
(`NUMEROS_PERMITIDOS` é opcional: apenas dígitos, com DDI+DDD. Se ficar vazio, o assistente responde a todos.)
```

3. Acesse a pasta da versão que você quer executar. No terminal, navegue até a versão desejada. Por exemplo, para executar a versão **v1.1**:
```python
cd assistente-virtual/versoes/v1.1/
```

4. Inicie o aplicativo. Dentro da pasta da versão escolhida, execute:
```python
python app.py
```
O servidor local irá iniciar e expor um link. Clique no link que abrirá uma interface no seu navegador e o assistente estará pronto para uso.

5. Executando a versão **v1.5**. Esta versão não possui o arquivo `app.py`: o assistente é iniciado pelo canal de atendimento desejado. Dentro da pasta `assistente-virtual/versoes/v1.5/`, execute:
```python
# Para o Telegram
python telegram.py

# Para o WhatsApp (o servidor Flask ficará disponível em http://0.0.0.0:5000/webhook)
python whatsapp.py
```
No caso do WhatsApp, configure o *webhook* da sua instância na Evolution API para apontar para o endereço `/webhook` do servidor, escutando o evento `messages.upsert`.
