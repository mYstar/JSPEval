# JSPEval
Evaluator for the multicriterial Job Shop Problem in Python 

The documentation is written with zim.
As of now a dump will be in [documentation](doc/JSP_Evaluator.html).

## Example script

An Example how to use the Evaluator is in `example.py`. The parts it contains are described down below:

### Import

Nothing to see here. You will probably need all 3 imports.

```python
from jspeval import JspEvaluator
from jspmodel import JspModel
from jspsolution import JspSolution
```

### Model

The model has to be instanciated. This is done by reading an xml-file that describes the JSP. Other examples for these xml files can be found in `test/`. 

```python
model = JspModel("xml/example.xml")
```

The xml-schema that describes the form of the xml-files can be found in `xml/model.xsd`. If you want to verify your own xml-file this can be done by:

```bash
xmllint --schema xml/model.xsd your_model.xml
```

### Solutions

Solutions should be instanciated manually by:

```python
custom_solution = JspSolution(model, [0.0, 0.25, 0.75, 0.5])
```

The length of the array has to match the number of operations in the specified model. The array values correspond to priority values in the permutation based encoding described further in [documentation](doc/JSP_Evaluator). Your optimization algorithm should generate these arrays probably.
For testing purposes there is an option to generate random solutions:

```python
random_solution = model.get_random_solution()
```

### Evaluation

The instanciation of the evaluator is straightforward:

```python
evaluator = JspEvaluator(model)
```

To generate the metrics 3 steps have to be performed:

1. generate a machine assignment
2. calculate a schedule
3. calculate the metrics

This code does all this:

```python
# generate the machine assignment
assign = evaluator.build_machine_assignment(solution)

# calculate the schedule
sched = evaluator.execute_schedule(assign)

# calculate the metrics
metrics = evaluator.get_metrics(assign, sched)
```

After this the `metrics` variable contains a dictionary, that has an entry with the name of every metric currently implemented and the corresponding value assigned to it.

# JSPGenerator

This is a little script used to generate jsp models from config parameter files written in yaml. ([example](yaml/example.yaml)) It can be used as:

```shell
./jspgenerator.py -o output/ yaml/example.yaml
```

Also, there is a way to convert Peres et. al. formatted files to the xml-format, like this.

```shell
./jspgenerator.py -f peres -o output/ data/JSP_instances/Taillard/tai01.txt 
```

For more information, please refer to the man-page via:

```shell
man ./jspgenerator.1
```
