"""Used to generate a valid xml-file to use in the JspEvaluator
"""
import sys
import os
import getopt
import numpy
from numpy import random
from lxml import etree
import ruamel.yaml


XML_HEADER = '<?xml version="1.0" encoding="UTF-8" ?>'


def read_yaml(filename):
    """Reads a YAML file and generates a parameter dictionary from it.

    :filename: the name (and possibly the path) of the file to process.
    :returns: the raw file content and a dictionary with all parameters
    contained in the file.
    by the file.
    """
    try:
        file = open(filename, "r")
        content = file.read()

        return content, ruamel.yaml.load(content, ruamel.yaml.RoundTripLoader)
    except IOError:
        print("The file: ", filename, " could not be opened.", sep="")
    except ruamel.yaml.parser.ParserError:
        print("The file: ", filename, " is no valid yaml file.", sep="")


def validate(params):
    """validates the correctness of the parameter dictionary.

    :params: the parameter dictionary, that is read from a yaml file.
    :returns: a boolean value. True if all parameters are set and are in their
    limits, False otherwise.

    """
    # greater or equal 0
    gezero = ["release_time", "deadline", "duration", "setuptimes"]
    for pname in gezero:
        try:
            if params[pname] < 0:
                raise ValueError("Parameter: {} less than 0.".format(pname))
        except TypeError:
            if params[pname][0] < 0:
                raise ValueError("Parameter: {} less than 0.".format(pname))

    # greater than 0
    geone = ["machines", "jobs", "lotsize", "operations", "allowed_machines"]
    for pname in geone:
        try:
            if params[pname] <= 0:
                raise ValueError("Parameter: {} less than 1.".format(pname))
        except TypeError:
            if params[pname][0] <= 0:
                raise ValueError("Parameter: {} less than 1.".format(pname))

    # greater or equal to previous value
    geprev = ["operations", "duration", "allowed_machines",
              "setuptimes", "deadline"]
    for pname in geprev:
        if params[pname][0] > params[pname][1]:
            raise ValueError("Parameter: {} has wrong ordered values."
                             .format(pname))

    # special requirements
    if params["allowed_machines"][1] > params["machines"]:
        raise ValueError(
            "Parameter: allowed_machines is greater than machines.")

    return True


def generate_xmltree(params, seed):
    """Generates a xml-tree that represents a jspmodel, that is randomly
    generated in the limits of the parameters.

    :params: a dictionary, that contains all the parameters
    :returns: an objectified xml-tree

    """
    # set the seed
    random.seed(seed)

    # intialize an element factory
    root = etree.Element(
        "jsp-model",
        xmlns="http://www.htw-dresden.de/JSPeval",
        nsmap={"xsi": "http://www.w3.org/2001/XMLSchema-instance"})

    # generate the machines
    machines = []
    for mnum in range(params["machines"]):
        mname = "m{}".format(mnum)
        etree.SubElement(root, "machine", machine_id=mname)
        machines.append(mname)

    # generate jobs
    generate_jobs(root, params, machines)

    # generate setuptimes
    e_stimes = etree.SubElement(root, "setuptimes")
    for e_op1 in root.iter("operation"):
        for e_op2 in root.iter("operation"):
            e_st = etree.SubElement(e_stimes, "setuptime")
            etree.SubElement(e_st, "from_operation").text = \
                e_op1.attrib["operation_id"]
            etree.SubElement(e_st, "to_operation").text = \
                e_op2.attrib["operation_id"]
            smin = params["setuptimes"][0]
            smax = params["setuptimes"][1]
            setuptime = random.rand() * (smax - smin) + smin
            etree.SubElement(e_st, "setup_duration").text = \
                "{:.2f}".format(setuptime)

    return root


def generate_jobs(root, params, machines):
    """generates jobs into the xml-tree root node.

    :root: the root of the xml tree
    :params: the params from the yaml file
    :machines: an list of available machines
    :returns: the root of the resulting tree

    """
    # go through all jobs
    joblengths = {}
    for jnum in range(params["jobs"]):
        jname = "j{}".format(jnum)
        e_job = etree.SubElement(root, "job", job_id=jname)

        # starttime element
        etree.SubElement(e_job, "starttime")
        # create deadline element
        e_deadl = etree.SubElement(e_job, "deadline")
        # generate the lotsize
        lotsize = random.randint(1, params["lotsize"] + 1)
        etree.SubElement(e_job, "lotsize").text = str(lotsize)

        # generate operations
        joblengths[jname] = generate_operations(e_job, jnum, params, machines)

        # generate the deadline
        dmin = (1 + params["deadline"][0]) * joblengths[jname]
        dmax = (1 + params["deadline"][1]) * joblengths[jname]
        deadline = random.rand() * (dmax - dmin) + dmin

        e_deadl.text = "{:.2f}".format(deadline)

    # generate the starting times
    max_jobduration = max(joblengths.values())
    for e_job in root.iter("job"):
        starttime = random.rand() * params["release_time"] * max_jobduration
        e_job.find('starttime').text = "{:.2f}".format(starttime)

    return root


def generate_operations(e_job, jnum, params, machines):
    """generates the operations for an e_job xml node according to the params.

    :e_job: the job-node to append the operations to
    :params: the parameters read from the yaml-file
    :machines: a list of available machines
    :returns: the total duration of the job

    """
    job_duration = 0
    numop = random.randint(
        params["operations"][0],
        params["operations"][1] + 1)
    for onum in range(numop):
        e_op = etree.SubElement(
            e_job,
            "operation",
            operation_id="j{}_o{}".format(jnum, onum))

        # generate op duration
        dmin = params["duration"][0]
        dmax = params["duration"][1]
        duration = random.rand() * (dmax - dmin) + dmin
        etree.SubElement(e_op, "op_duration").text = \
            "{:.2f}".format(duration)

        job_duration += duration

        # generate machine list
        numma = random.randint(
            params["allowed_machines"][0],
            params["allowed_machines"][1])
        mlist = random.choice(machines, numma, replace=False)

        for manum in range(numma):
            etree.SubElement(
                e_op,
                "allowed_machine"
                ).text = mlist[manum]

    return job_duration


def get_yaml_files(directory):
    """Looks for YAML files in a particular directory.

    :directory: the directory to be searched for YAML files.
    :returns: a list of all YAML files in directory

    """
    yaml_files = []
    for file in os.listdir(directory):
        if file.endswith(".yaml"):
            yaml_files.append("{}/{}".format(directory, file))

    return yaml_files


def main():
    """controls the generation of the xml-file(s).

    :returns: None

    """
    # read the given parameters
    try:
        options, files = getopt.getopt(
            sys.argv[1:],
            "hds:o:",
            ["help", "use-directories", "seed=", "output-dir="])
    except getopt.GetoptError:
        print("usage: python3 jspgenerator.py",
              "[-h, -d, -s, -o] <parameters.yaml, ...>")
        sys.exit(1)

    # generate seed (this is max uint32)
    seed = random.randint(4294967295)

    # set the source dir as the output dir
    if ('-d', '') in options:
        output_dir = files[0]
    else:
        output_dir = os.path.dirname(files[0])

    for opt, arg in options:
        if opt in ("-h", "--help"):
            print("usage: python3 jspgenerator.py",
                  "[-h, -d, -s, -o] <parameters.yaml, ...>")
            sys.exit()
        elif opt in ("-d", "--use-directory"):
            files = get_yaml_files(files[0])
        elif opt in ("-s", "--seed"):
            seed = numpy.uint32(arg)
        elif opt in ("-o", "--output-dir"):
            output_dir = arg

    # iterate over all parameter files
    for param_file in files:
        # get the parameters
        paramstring, param = read_yaml(param_file)
        validate(param)

        # generate the xml
        xmltree = generate_xmltree(param, seed)

        # write the result
        out_filename = "{}/{}.xml".format(
            output_dir,
            param_file.split('.')[0].split('/')[-1])
        out_file = open(out_filename, "w")
        out_file.write("{}\n<!--\nseed: {}\n{}\n-->\n{}".format(
            XML_HEADER,
            seed,
            paramstring,
            etree.tostring(xmltree, pretty_print=True).decode("utf8")))


if __name__ == "__main__":
    main()
