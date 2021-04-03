# Let's play soccer
### Course CSL7040: Artificial Intelligent II
#### Submitted by: Hiren Chalodiya

### How to set up

- Make sure your system have `python 3.8` (as specified in `Pipfile`)
  - If your system does not have `python 3.8` then you may get error while installing dependencies. In such case, change
    `python_version` in `Pipfile`
    
- Install `pipenv` if your system does not have
  - ```pip install pipenv```
    
- Setup virtual environment
  - ```pipenv install```
  - If found error while installing dependency `sympy`, run following commands
  - ```
    pipenv uninstall sympy
    pipenv install sympy
    ``` 
    
### How to run

- Run following command
  - ```python main.py```