# shake

A top-down online real-time multiplayer shooter, written in python and javascript. Communication between client and server uses websockets.

## Development setup

This repo is shared by the `shake` game server and the `shake` game client, in folders named accordingly.

### Server (Python)

This project uses [pipenv](https://pipenv.pypa.io/en/latest/) to manage python dependencies, which can be installed with `pip install pipenv`. It is also expected that you be comfortable upgrading between different python versions, which means you should be familiar with using [pyenv](https://github.com/pyenv/pyenv). On MacOS you can install pyenv with `brew install pyenv`. The currently targeted python version for this project is committed into the repo at `.python-version`, which is automatically used by pyenv to detect the correct version of python to use for a particular project.

Once you've got pipenv and pyenv installed, you can run `pipenv install --dev` to setup a local development environment.

To launch the server, cd into the `server` folder and run `pipenv run python3 server.py`, or if you're in the virtual environment already (via `pipenv shell`) then you can simply run `python3 server.py` to start the server.

Your code should adhere to the style requirements as codified in `.pre-commit-config.yaml`. The easiest way to achieve this is to install [pre-commit](https://pre-commit.com/) by running `brew install pre-commit` and then run `pre-commit install` inside this repo. This will automatically run code formatters and linters whenever you try to commit. Your code should also pass mypy strict type checking in order to reduce the risk of bugs.

### Client (Javascript)

...
