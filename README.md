# Information Visualization: Visualising a Multi-Modal Neuroimaging Dataset

Project of Group 8 for the Information Visualization course at [vub](www.vub.be).

## 0. Contact information

Monty Python and the Three WISE Men:

| Name                     | Student number | Email address                                                      |
| :----------------------- | :------------- | :----------------------------------------------------------------- |
| Robin De Haes            | 0565683        | [robin.de.haes@vub.be](mailto:robin.de.haes@vub.be)                |
| Wolf De Wulf             | 0546395        | [wolf.de.wulf@vub.be](mailto:wolf.de.wulf@vub.be)                  |
| Alexis François Verdoodt | 0545813        | [alexis.francois.verdoodt@vub.be](alexis.francois.verdoodt@vub.be) |

## 1. Installation

The visualisation is dockerised and thus to run it you need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

## 2. Usage

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

## (3. For developers)

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
