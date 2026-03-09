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

---

## 3. Estrutura do Projeto

### 3.1 Pastas
A organização de pastas do projeto segue uma estrutura simples e objetiva, facilitando a manutenção e expansão futura:
- [**base-de-dados**](../base-de-dados/): Diretório que armazena o conteúdo da base de dados do projeto. Este diretório é divido em duas pastas: [dados-brutos](../base-de-dados/dados-brutos/) e [dados-tratados](../base-de-dados/dados-tratados/).

    - [**dados-brutos**](../base-de-dados/dados-brutos/): Essa pasta se refere aos dados brutos de cada curso. Arquivos como *PDF*, *DOCX*, *DOC*, *TXT*... são armazenados aqui. A pasta **dados-brutos** é dividida em subpastas responsáveis por armazenar os dados não tratados de cada curso em questão.

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

- [**versoes**](/versoes/): Contém as implementações completas de cada versão do Assistente Virtual. 
    - [**v1.0**](/versoes/v1.0/): Versão inicial. 
    - [**v1.1**](/versoes/v1.0/): Versão expandida. 

---
## 4. Como Executar

Siga os passos abaixo para rodar qualquer versão do projeto localmente.

1. Instale as dependências necessárias. No seu ambiente Python, instale os pacotes usados pelo projeto:
```python
pip install gradio langchain python-dotenv
```

2. Configure sua API Key. Crie um arquivo chamado `.env` na **raiz do seu projeto** e adicione sua chave da OpenAI seguindo este padrão:
```python
OPENAI_API_KEY=xxxx 
(Substitua `xxxx` pela sua chave real)
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

