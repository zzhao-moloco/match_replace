# How to use this match pattern and replace tool
This project works for BID-235, upgrading `github.com/urfave/cli` and `gopkg.in/urfave/cli.v1` to `	"github.com/urfave/cli/v2"`.
In the future, this project can be modified to run other chore-like jobs, which just required multiline based pattern matching.


# How to run this code
```shell
    # prod
    python runner.py -p
    # then go to the src/tools folder
    make
    # make sure that the compile process does not generate any failures
    # test
    # first populate your own folders according to the `cli.cfg` test section. Specify your test root_path, test_input and test_output folders.
    python runner.py
```