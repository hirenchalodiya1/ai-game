# Reinforcement Learning

## Requirement
- ![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)
- Tkinter (python 3.x supported version)

## Help
- Run command
    - ```
      python3 main.py -h
      ```
- Important parameter
    - `-n` Number of games
    - `-x` Number of training episode
    - `-p` Print path information
    - `-z` Zoom window
  
## Run
```
python3 main.py -n 1001 -x 1000
```

## Layout

- Add layout in `layouts` folder
- Add `-l <layout_file_name>` parameter for particular layout
- `S` Start Position
- `G` Possible goal position
  - At the start of the game, goal position will be randomly selected
- `P` Power Position
- `p` Go to power
- `R` Restart
- `%` Wall
