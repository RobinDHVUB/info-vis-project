# Information Visualization: Project

Project of Group 8 for the Information Visualization course at [VUB](www.vub.be).

## 0. Contact information

Monty Python and the Three WISE Men:

| Name                     | Student number | Email address                                                      |
| :----------------------- | :------------- | :----------------------------------------------------------------- |
| Robin De Haes            | 0565683        | [robin.de.haes@vub.be](mailto:robin.de.haes@vub.be)                |
| Wolf De Wulf             | 0546395        | [wolf.de.wulf@vub.be](mailto:wolf.de.wulf@vub.be)                  |
| Alexis François Verdoodt | 0545813        | [alexis.francois.verdoodt@vub.be](alexis.francois.verdoodt@vub.be) |

## 1. Data

Download the [preprocessed data](https://vub-my.sharepoint.com/:u:/g/personal/wolf_de_wulf_vub_be/EZ70UnZ1aPFAmXQS98Gt0PEB0kBJ_IjNMszrhueXSs_YnA?e=et2jxn) (7.1G) and extract it into `data/processed`.  
The code that was used to process the data can be found in [data/preprocessing](data/preprocessing).  
Note that, because of the size of the dataset (+85GB), all preprocessing was ran on the [VUB Hydra HPC](https://hpc.vub.be/).

## 2. Installation

### Create a Python virtual environment
```console
python -m venv env
```

### Activate the environment

*Linux*
```console
source env/bin/activate
```

To deactivate, use:
```console
deactivate
```

*Windows*
```console
.\\env\Scripts\activate
```

To deactivate, use:
```console
deactivate
```

### Install the requirements
```console
pip install -r requirements.txt
```

## 3. Usage

To boot the [Panel](https://panel.holoviz.org/) visualisation, use:

```console
panel serve visualisation/run.py
```

To stop the application, press `Ctrl-c`.  

## (4. For developers)

Use the above command with the ``--autoreload`` option to allow for live code updates.