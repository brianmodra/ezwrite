## Getting started

I'm developing on a Mac. I don't have instructions here fopr other environments yet. I will add for Windows and Linux later.

Note that I did not use pyenv. I used the MacOS Python3 https://docs.python.org/3/using/mac.html

I installed using those instructions, then added python and python3 aliases in my ~/.zshrc to point to the actual installed python. E.g. (it may be different for you)
```
alias python /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
alias python3 /Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
alias pip pip3
```

installed venv and pykka:
(See also https://pykka.readthedocs.io/stable/)

```
python -m pip install --upgrade pip setuptools virtualenv
export PATH=/Library/Frameworks/Python.framework/Versions/3.13/bin:$PATH
```
(I also added /Library/Frameworks/Python.framework/Versions/3.13/bin to the PATH in ~/.zshrc).
```
mkdir -p .venv
python -m venv .venv
source .venv/bin/activate
pip install pykka
pip install mypy
pip install types-PyYAML types-requests
pip install pylint
pip install pytest
pip install pycycle
pip install "mcp[cli]"
pip insyall rdflib
```
