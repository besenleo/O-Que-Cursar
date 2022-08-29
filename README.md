# O Que Cursar

## Configurando seu ambiente

Instale Python 3.9 ou superior  e PostgreSQL 12 ou superior na maquina que rodará o site.

Faça o download ou clone o repositorio usando Git ou GitHub Desktop.

Após isso, realize os passos para instalar as dependencias necessarias. Para fins de desenvolvimento, recomendamos utilizar um virtual enviroment (explicado no proximo tópico).

- Siga os passos para criar seu ambiente virtual (caso pretenda contribuir com o desenvolvimento)
- Entre no diretorio do projeto:
```
cd O-Que-Cursar
```
- Valide se o Python instalado esta na versão recomendada:
```
python --version
```
- Faça o upgrade do pip e setuptools para pegar as dependencias
```
pip install --upgrade pip setuptools
```
- Instale as dependencias como definidas no arquivo `setup.py`:
```
pip install .
```

## Usando Virtual Enviroments

Caso pretenda contribuir com o desenvolvimento, é altamente recomendado que você crie um ambiente virtual usando o Python, que será usado para instalar a dependencias e evitar conflitos com outros projetos.

Para isso basta, seguir o seguintes passos:

-  Entre no diretorio do projeto:
```
cd O-Que-Cursar
```
- Valide se o Python instalado esta na versão recomendada:
```
python --version
```
- Instale o `virtualenv` usando o pip
```
pip install virtualenv
```
- Crie um novo ambiente na pasta do projeto
```
virtualenv venv
```
- Ative o ambiente virtual antes de instalar as dependencias:
```
no Windows: venv\Scripts\activate
```

Realize esses passos antes de instalar as dependencias do projeto e defina o sua IDE de escolha para usar esse ambiente virtual criado. Quando você for usar a linha de comando lembre-se de rodar o comadando para ativar o ambiente virtual.