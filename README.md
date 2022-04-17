# How to use this match pattern and replace tool
This project works for BID-235, upgrading `github.com/urfave/cli` and `gopkg.in/urfave/cli.v1` to `	"github.com/urfave/cli/v2"`.
In the future, this project can be modified to run other chore-like jobs, which just required multiline based pattern matching.


## Setup

 ```
 virtualenv env
 source env/bin/activate
 pip install -r requirements.txt
 python -m app --help
 ```


# How to run this code
```shell
    # prod
    # go to cli.cfg
    # in 'folders', list the folders that needs to be migrated to v2
    # ensure no space between the folder names, otherwise it doesn't work
    python runner.py -p
    # then go to the src/tools folder
    make
    # make sure that the compile process does not generate any failures
    # test
    # first populate your own folders according to the `cli.cfg` test section. Specify your test root_path, test_input and test_output folders.
    python runner.py
```

 ## Packaging 

 Update `setup.py` with your details and then run `python setup.py upload` to package for distribution on PyPi.
