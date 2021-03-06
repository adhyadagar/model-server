[![CodeFactor](https://www.codefactor.io/repository/github/aiforgoodsimulator/model-server/badge)](https://www.codefactor.io/repository/github/aiforgoodsimulator/model-server)
[![codecov](https://codecov.io/gh/AIforGoodSimulator/model-server/branch/dev/graph/badge.svg?token=TK647J6ZUC)](https://codecov.io/gh/AIforGoodSimulator/model-server)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)
[![Testing](https://github.com/AIforGoodSimulator/model-server/workflows/AIforGood%20ModelServer%20Tests/badge.svg)](https://github.com/AIforGoodSimulator/model-server/actions?query=workflow%3A%22AIforGood+ModelServer+test+workflow%22)
[![Dev-Build-Deploy](https://github.com/AIforGoodSimulator/model-server/workflows/DEV%20Build%20Deploy/badge.svg)](https://github.com/AIforGoodSimulator/model-server/actions?query=workflow%3A%22DEV+Build+Deploy%22)
[![UAT-Build-Deploy](https://github.com/AIforGoodSimulator/model-server/workflows/UAT%20Build%20Deploy/badge.svg)](https://github.com/AIforGoodSimulator/model-server/actions?query=workflow%3A%22UAT+Build+Deploy%22)



### Install 

To start install required packages with 

    pip install -r requirements.txt
    
or first create and activate virtual environment

* On macOS and Linux:

        python3 -m venv env
        source env/bin/activate
        pip install -r requirements.txt
        
* On Windows:

        py -m venv env
        .\env\Scripts\activate
        pip install -r requirements.txt


Go to root of the repo and run (or configure corresponding env. vars)

* Windows: 
    
        set PYTHONPATH=%PYTHONPATH%;.
    
* Linux:

        export PYTHONPATH="${PYTHONPATH}:."
    
    
Copy the .env.default file to .env :

* Windows: 
    
  Command line :

        cp .env.default .env

  Windows explorer :

        Copy the .env.default and rename it to .env
    
* Linux:

        cp .env.default .env

You also need to fill in the .env variable REDIS_URL with the details of the REDIS server.  You can fill in the information with the details of a local REDIS instance or request the development REDIS parameters from :

    [pardf](https://github.com/pardf)

    [kariso2000](https://github.com/kariso2000)

    [billlyzhaoyh](https://github.com/billlyzhaoyh)

    [titorenko](https://github.com/titorenko)

    [TensorMan](https://github.com/TensorMan)
    
### Command line execution 
    
To get commandline help:
    
    python ai4good/runner/console_runner.py -h
    
    
Example execution (default camp is used):

    python ai4good/runner/console_runner.py --profile custom --save_plots --save_report
    
CSV Report is  saved in fs/reports, plots are in fs/figs, model result cache in fs/model_results.

Parameters are in fs/params + profile configuration in code right now, but to move to some kind of database in the future.


### Webapp

Webapp can be started from PyCharm by running server.py main method or from terminal:

    waitress-serve --port 8050 --host 0.0.0.0 ai4good.webapp.server:flask_app
    
Note waitress is for local development only and gunicorn is used for production deployment. 
    
### Azure deployment

First add azure remote

    git remote add azure https://ai4good-sim2.scm.azurewebsites.net:443/ai4good-sim2.git
    
 Note down deployment credentials from Deployment Center/Deployment Credentials on Azure portal for AI4Good-Sim2 app service.
 
 Now just do 
    
    git push azure master

enter credentials when prompted.
    
### Docker

Change directory

    cd model-server

Build:

    docker build -t model-server .

Test:

    docker run model-server python -m unittest discover -s ai4good/ -p "test_*.py"

Run Example:

    docker run model-server python ai4good/runner/console_runner.py --profile custom --save_plots --save_report

Container Command Line:

    docker run -it model-server /bin/bash

### Design overview

Model-server consists of following top level packages:

* models - various COVID-19 models and model registry
* params - parameter storage and retrieval
* runner - console runner
* webapp - web application runner / viewer

    #### models
    Every model needs to implement ai4good.models.model.Model abstract base class and basically just needs
    to implement run(params) method, where params object can be chosen by the model itself and usually 
    contains general parameters, camp specific parameters and model profile parameters. Model profiles
    are there to investigate and compare various regimes of the model and to help user to select best
    intervention scenario that mitigates COVID-19 spread.

    Model also responsible to provide hash of it's own parameter object so that model results can cached. 
    This functionality of saving/retrieving model result is provided by ModelResultStore and currently 
    stored on filesystem.  

    Model result is represented by ModelResult object which effectively just a free-from dictionary and
    can include some precomputed aggregations to speed up result rending later.
  
    #### params
    Provides abstract interface to parameter storage which is at the moment is based on csv files 
    stored on local file system.  


    #### runner

    Contains console runner that can run a model for single profile or all profiles/camps in a batch.
    Also contains console_utils to list currently cached models with human readable names.


    #### webapp

    Web application is built with dash/plotly and runs on Azure via gunicorn with multiple workers. There is also Redis
    instance used to store some shared state, such as models currently executing and also hosting some page cache. There is
    also cache on local disk that is used to store larger amounts of data. Webapp has model runner page and report pages.
    Report page is model specific and allows to compare various intervention scenarios.  


### Tests
use run_tests cmd/sh to execute all tests

### Instances

Difference instances of model server are available:

* Production - for end-users (docker)
* Non-production - for development and testing (docker) 
* Others - as backup and virtual environment deployment (e.g. DigitalOcean droplets)

    #### Production
    http://ai4good-sim2.azurewebsites.net/sim/run_model

    #### Non-production
    http://ai4good-uat.azurewebsites.net/sim/run_model (UAT)

    http://ai4good-dev.azurewebsites.net/sim/run_model (DEV)

    #### Others

    * Local address: http://localhost:8050/sim/run_model (private instance)

    * Python Server - Waitress Python

      Waitress is meant to be a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones which live in the Python standard library. It runs on CPython on Unix and Windows under Python 2.7+ and Python 3.5+. It is also known to run on PyPy 1.6.0 on UNIX. It supports HTTP/1.0 and HTTP/1.1.

    * How to run: 

    ```
    sudo apt update
    sudo apt install python3-pip
    git clone https://github.com/AIforGoodSimulator/model-server.git
    cd model-server
    pip3 install -r requirements.txt
    apt install python3-waitress
    waitress-serve --port 8050 --host your_host_ip ai4good.webapp.server:flask_app
    ```
### CI/CD Workflow 

The following workflow should be used for development:

* Run local tests, once all tests pass commit your branch to github

* Your commit will run the tests on Github using actions. You can view the tests running under the 'Actions' menu item above.

* Once your tests pass create a pull request to the 'dev' branch and merge.  Tests will be run again and the dev branch will be deployed to the dev server.

* You can view your changes on : (Note build and deployment can take 5+ minutes) 

    http://ai4good-dev.azurewebsites.net/sim/run_model (DEV)


* Now create a pull request to the 'uat' branch. This pull request can be merged by the people below.
* You can view your changes on : (Note build and deployment can take 5+ minutes) 
* This is the branch the testing team will do UAT testing on.

    http://ai4good-uat.azurewebsites.net/sim/run_model (UAT)

* The pull to 'Master' branch will happen manually once UAT has been accepted.  This pull request can be merged by the following people :

    [pardf](https://github.com/pardf)

    [kariso2000](https://github.com/kariso2000)

    [billlyzhaoyh](https://github.com/billlyzhaoyh)

    [titorenko](https://github.com/titorenko)

    [TensorMan](https://github.com/TensorMan)


* Deploy to PROD server with master branch is currently manual.

* You can also view web tests running on our Zalenium instance :

    http://51.132.48.142/dashboard/#

Please contact [kariso2000](https://github.com/kariso2000) on slack for userid and password.

### FAQ
Will the web server be a separate container?
**Yes**

Where do we intend to save the Results and Graphs? Volume/NFS?
**Bucket Storage**

Are we going to run this on ACI via docker context? or AKS?
**AKS**

How will new models and their dependencies be added/integrated into the model server?
**Model server is just a framework you can have inception file to run your model on that model server. all commands are in github documentation already.**

Or will this just become the base image to build a multistage container for new models?
**Yes**

Orca is not available via pip and requires some dependency management. Alternatives?
**Which container or AKS does not have orca available. need to know the name.**
        
