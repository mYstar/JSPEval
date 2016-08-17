"""Used to generate a valid xml-file to use in the JspEvaluator
"""
import sys
import os
import getopt
import gzip
import numpy
from numpy import random
from lxml import etree
import ruamel.yaml


XML_HEADER = '<?xml version="1.0" encoding="UTF-8" ?>'


def randfloat(xmin, xmax):
    """Generates a random float number between xmin (inclusive) and xmax
    (exclusive).

    :xmin: lower end of the random interval
    :xmax: higher end of the random interval
    :returns: a random float number

    """
    return random.rand() * (xmax - xmin) + xmin


def read_yaml(filename):
    """Reads a YAML file and generates a parameter dictionary from it.

    :filename: the name (and possibly the path) of the file to process.
    :returns: the raw file content and a dictionary with all parameters
    contained in the file.
    """
    try:
        file = open(filename, "r")
        content = file.read()

        return content, ruamel.yaml.load(content, ruamel.yaml.RoundTripLoader)
    except IOError:
        print("The file: ", filename, " could not be opened.", sep="")
    except ruamel.yaml.parser.ParserError:
        print("The file: ", filename, " is no valid yaml file.", sep="")


def read_peres(filename):
    """Reads a file in the Dauzere Peres et. al format and generates a
    list of value-lists from it.

    :filename: the name (and possibly the path) of the file to process.
    :returns: a list containing a list of all values for every line in the
    file.
    """
    try:
        values = []
        for line in open(filename, "r"):
            values.append(line.split(' ')[:-1])

        return values
    except IOError:
        print("The file: ", filename, " could not be opened.", sep="")


def validate(params):
    """validates the correctness of the parameter dictionary.

    :params: the parameter dictionary, that is read from a yaml file.
    :returns: a boolean value. True if all parameters are set and are in their
    limits, False otherwise.

    """
    # greater or equal 0
    gezero = ["weight", "release_time", "deadline", "duration", "setuptimes"]
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
              "weight", "setuptimes", "deadline"]
    for pname in geprev:
        if params[pname][0] > params[pname][1]:
            raise ValueError("Parameter: {} has wrong ordered values."
                             .format(pname))

    # special requirements
    if params["allowed_machines"][1] > params["machines"]:
        raise ValueError(
            "Parameter: allowed_machines is greater than machines.")

    return True


def generate_random_xmltree(params, seed):
    """Generates a xml-tree that represents a jspmodel, that is randomly
    generated in the limits of the parameters.

    :params: a dictionary, that contains all the parameters
    :seed: the seed to use for the RNG
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
            setuptime = randfloat(
                params["setuptimes"][0],
                params["setuptimes"][1])
            etree.SubElement(e_st, "setup_duration").text = \
                "{:.2f}".format(setuptime)

    return root


def generate_peres_xmltree(params):
    """Generates a xml-tree that represents a jspmodel, that is build from the
    parameters in peres et al format.

    :params: a list, that contains all the parameters
    :returns: an objectified xml-tree

    """
    # intialize an element factory
    root = etree.Element(
        "jsp-model",
        xmlns="http://www.htw-dresden.de/JSPeval",
        nsmap={"xsi": "http://www.w3.org/2001/XMLSchema-instance"})

    # generate the machines
    machines = []
    for mnum in range(int(params[0][1])):
        mname = "m{}".format(mnum)
        etree.SubElement(root, "machine", machine_id=mname)
        machines.append(mname)

    # generate jobs
    for jnum in range(int(params[0][0])):
        jname = "j{}".format(jnum)
        e_job = etree.SubElement(root, "job", job_id=jname)

        # starttime element
        etree.SubElement(e_job, "starttime").text = params[jnum + 1][0]
        # create deadline element
        etree.SubElement(e_job, "deadline").text = params[jnum + 1][1]
        # generate the weight
        etree.SubElement(e_job, "weight").text = params[jnum + 1][2]
        # generate the lotsize
        etree.SubElement(e_job, "lotsize").text = "1"

        # operations
        for onum in range(int(params[jnum + 1][3])):
            e_op = etree.SubElement(
                e_job,
                "operation",
                operation_id="j{}_o{}".format(jnum, onum))

            # generate op duration
            etree.SubElement(e_op, "op_duration").text = \
                params[jnum + 1][onum * 2 + 5]

            # allowed machine
            etree.SubElement(
                e_op,
                "allowed_machine"
                ).text = machines[int(params[jnum + 1][onum * 2 + 4]) - 1]

    # generate setuptimes
    etree.SubElement(root, "setuptimes")

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
        # generate the weight
        weight = randfloat(
            params["weight"][0],
            params["weight"][1])
        etree.SubElement(e_job, "weight").text = str(weight)
        # generate the lotsize
        lotsize = random.randint(1, params["lotsize"] + 1)
        etree.SubElement(e_job, "lotsize").text = str(lotsize)

        # generate operations
        joblengths[jname] = generate_operations(e_job, jnum, params, machines)

        # generate the deadline
        dmin = (1 + params["deadline"][0]) * joblengths[jname]
        dmax = (1 + params["deadline"][1]) * joblengths[jname]
        deadline = randfloat(dmin, dmax)

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
        duration = randfloat(
            params["duration"][0],
            params["duration"][1])
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


def process_yaml(files, output_dir, seed, compression):
    """processes all the steps to generate models from the yaml-files.

    :files: the yaml files containing the parameters
    :output_dir: the directory to output the models to
    :seed: the seed to use
    :compression: flag - whether to use compression for the output files
    :returns: None

    """
    # iterate over all parameter files
    for param_file in files:
        # get the parameters
        paramstring, param = read_yaml(param_file)
        validate(param)

        # generate the xml
        xmltree = generate_random_xmltree(param, seed)

        # write the result
        out_filename = "{}/{}.xml".format(
            output_dir,
            param_file.split('.')[0].split('/')[-1])

        content = "{}\n<!--\nseed: {}\n{}\n-->\n{}".format(
            XML_HEADER,
            seed,
            paramstring,
            etree.tostring(xmltree, pretty_print=True).decode("utf8"))

        if compression:
            out_filename = "{}.gz".format(out_filename)
            out_file = gzip.open(out_filename, "wb")
            content = content.encode()
        else:
            out_file = open(out_filename, "w")

        out_file.write(content)


def convert_peres(files, output_dir, compression):
    """converts the peres et al formatted files to the xml format.

    :files: the peres files containing the model parameters
    :output_dir: the directory to output the models to
    :compression: flag - whether to use compression for the output files
    :returns: None

    """
    # iterate over all peres files
    for peres_file in files:
        # get the values
        values = read_peres(peres_file)

        # generate the xml
        xmltree = generate_peres_xmltree(values)

        # write the result
        out_filename = "{}/{}.xml".format(
            output_dir,
            peres_file.split('.')[0].split('/')[-1])

        content = "{}\n{}".format(
            XML_HEADER,
            etree.tostring(xmltree, pretty_print=True).decode("utf8"))

        if compression:
            out_filename = "{}.gz".format(out_filename)
            out_file = gzip.open(out_filename, "wb")
            content = content.encode()
        else:
            out_file = open(out_filename, "w")

        out_file.write(content)


def main():
    """controls the generation of the xml-file(s).

    :returns: None

    """
    usage_string = \
        "usage: python3 jspgenerator.py-[hdsocf] <parameters.yaml, ...>"

    # read the given parameters
    try:
        options, files = getopt.getopt(
            sys.argv[1:],
            "hdcs:o:f:",
            ["help", "compression", "use-directories",
             "seed=", "output-dir=", "format="])
    except getopt.GetoptError:
        print(usage_string)
        sys.exit(1)

    # generate seed (this is max uint32)
    seed = random.randint(4294967295)

    # set the source dir as the output dir
    if ('-d', '') in options:
        output_dir = files[0]
    else:
        output_dir = os.path.dirname(files[0])

    # compression flag
    compression = False

    # default format
    fmt = "yaml"

    for opt, arg in options:
        if opt in ("-h", "--help"):
            print(usage_string)
            sys.exit()
        elif opt in ("-d", "--use-directory"):
            files = get_yaml_files(files[0])
        elif opt in ("-s", "--seed"):
            seed = numpy.uint32(arg)
        elif opt in ("-o", "--output-dir"):
            output_dir = arg
        elif opt in ("-c", "--compression"):
            compression = True
        elif opt in ("-f", "--format"):
            if arg == "peres":
                fmt = arg

    if fmt == "peres":
        convert_peres(files, output_dir, compression)
    else:
        process_yaml(files, output_dir, seed, compression)


if __name__ == "__main__":
    main()
