# CheckList ABNT NBR ISO 9241-11:2021

Trabalho de Graduação do curso Analise e Desenvolvimento de Sistemas, da faculdade Estadual Fatec Arthur de Azevedo.

## Inicializando o backend

Entre na pasta mova seu terminal para pasta app
Execute o comando no bash: ```python -m venv .venv```
Para habilitar o ambiente virtual, no bash execute ```source .venv/Scripts/activate```
Após habilitar o ambiente virtual, execute o comando ```python.exe -m pip install --upgrade pip``` para atualizar o pip
Após atualizar o ambiente pip, execute o comando no bash ```pip install -r requirements.txt``` para realizar o download das dependencias.

### Inicializando o servidor
Utilize o comando no bash ```flask --app server run``` este comando irá habilitar o servidor local host

### Inicializando o servidor modo debug
Utilize o comando no bash ```flask --app server run --debug``` este comando irá habilitar o servidor local host no modo debug.