# Information Visualisation: Project

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

The visualisation is dockerised and thus the only requirements needed to run it are docker [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

## 3. Usage

To boot the application, navigate to the [webapp](webapp) folder and run the following:

```console
docker-compose up
```

Make sure that the docker daemon is running.

To stop the application, press `Ctrl-c`.  
Note that this does not completely remove the docker containers.  
To clean up the docker containers completely, run the following:

```console
docker-compose rm
```

## (4. For developers)

When changes are made to the docker container's settings or when packages are added to their `requirements.txt` files, the containers need to be rebuilt.  
To do so, firstly, clean up dangling containers/images/volumes:

```console
docker system prune -a
docker volume prune
```

Afterwards, rebuild:

```console
docker-compose up --build --rm
```

Lastly, when docker or docker-compose complains about permissions, try running with administrator/root privileges.

