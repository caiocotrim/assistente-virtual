## Scripts

Este diretório contém scripts auxiliares utilizados durante o desenvolvimento do projeto.

O script `pdf-para-jpg/script.py` automatiza a extração das ementas dos Projetos Pedagógicos de Curso (PPCs) em formato PDF, gerando uma imagem JPEG para cada componente curricular. O processo é adaptado à estrutura específica de cada PPC, identificando e separando corretamente as ementas dos cursos de Bacharelado em Sistemas de Informação, Engenharia Civil, Engenharia Elétrica, Engenharia Ambiental e Licenciatura em Química.

As imagens geradas são organizadas em diretórios por curso e utilizadas pelo assistente virtual para enviar a ementa correspondente quando solicitada pelo usuário, complementando as respostas geradas pelo sistema de Retrieval-Augmented Generation (RAG).