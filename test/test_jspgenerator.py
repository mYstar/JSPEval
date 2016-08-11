""" Tests for the JSP generator script
"""
import pytest
from lxml import objectify
from lxml import etree
from numpy import random
import jspgenerator


# ---- fixtures ----
@pytest.fixture(scope="module",
                params=["yaml/example.yaml"])
def example_xml(request):
    # read the model and build objects from it
    _, yaml = jspgenerator.read_yaml(request.param)
    return yaml


# ---- tests ----
def test_all_parameters_are_read(example_xml):
    assert len(example_xml.keys()) == 9


@pytest.mark.parametrize("filename", [
    pytest.mark.xfail(raises=Exception)("jspgenerator.py"),
    pytest.mark.xfail(raises=Exception)("non_existing.txt"),
])
def test_dont_read_wrong_files(filename):
    jspgenerator.read_yaml(filename)


def test_validates_correctly(example_xml):
    assert jspgenerator.validate(example_xml)


@pytest.mark.parametrize("filename", [
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_allowed_machines.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_deadline.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_duration.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_jobs.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_lotsize.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_machines.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_operations.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_release.yaml"),
    pytest.mark.xfail(raises=ValueError)
    ("test/yaml/wrong_setup.yaml")
])
def test_invalidates_wrong_parameters(filename):
    _, param = jspgenerator.read_yaml(filename)
    jspgenerator.validate(param)


def test_model_is_generated_correctly(example_xml):
    for _ in range(10):
        seed = random.randint(4294967295)
        root = jspgenerator.generate_random_xmltree(example_xml, seed)
        o_root = objectify.fromstring(etree.tostring(root))

        assert len(o_root.machine) == 5
        assert len(o_root.job) == 4

        jobcount = 0
        max_joblen = 0.0
        for o_job in o_root.job:
            assert len(o_job.operation) > 1
            assert len(o_job.operation) < 6

            joblen = 0
            for o_op in o_job.operation:
                assert float(o_op.op_duration.text) >= 5.0
                assert float(o_op.op_duration.text) <= 35.0
                joblen += float(o_op.op_duration.text)
                assert len(o_op.allowed_machine) > 1
                assert len(o_op.allowed_machine) < 6
                jobcount += 1

            assert float(o_job.deadline.text) >= 1.5 * joblen
            assert float(o_job.deadline.text) <= 2.0 * joblen
            assert int(o_job.lotsize.text) >= 1
            assert int(o_job.lotsize.text) <= 10

            if max_joblen < joblen:
                max_joblen = joblen

        for o_job in o_root.job:
            assert float(o_job.starttime.text) <= 0.5 * max_joblen

        assert len(o_root.setuptimes.setuptime) == jobcount * jobcount


def test_convert_peres_fileformat():

    params = jspgenerator.read_peres("test/peres.txt")
    root = jspgenerator.generate_peres_xmltree(params)
    o_root = objectify.fromstring(etree.tostring(root))

    assert len(o_root.job) == 3
    assert len(o_root.machine) == 3
    assert not hasattr(o_root.setuptimes, 'setuptime')

    # check the jobs
    assert int(o_root.job[0].starttime) == 0
    assert int(o_root.job[1].starttime) == 5
    assert int(o_root.job[2].starttime) == 10

    assert int(o_root.job[0].deadline) == 10
    assert int(o_root.job[1].deadline) == 15
    assert int(o_root.job[2].deadline) == 20

    assert int(o_root.job[0].lotsize) == 1
    assert int(o_root.job[1].lotsize) == 2
    assert int(o_root.job[2].lotsize) == 3

    assert len(o_root.job[0].operation) == 3
    assert len(o_root.job[1].operation) == 3
    assert len(o_root.job[2].operation) == 3

    assert float(o_root.job[0].operation[0].op_duration) == 2.0
    assert o_root.job[0].operation[0].allowed_machine == 'm0'
    assert float(o_root.job[0].operation[1].op_duration) == 3.0
    assert o_root.job[0].operation[1].allowed_machine == 'm1'
    assert float(o_root.job[0].operation[2].op_duration) == 2.0
    assert o_root.job[0].operation[2].allowed_machine == 'm2'

    assert float(o_root.job[1].operation[0].op_duration) == 1.5
    assert o_root.job[1].operation[0].allowed_machine == 'm2'
    assert float(o_root.job[1].operation[1].op_duration) == 2.5
    assert o_root.job[1].operation[1].allowed_machine == 'm1'
    assert float(o_root.job[1].operation[2].op_duration) == 3.5
    assert o_root.job[1].operation[2].allowed_machine == 'm0'

    assert float(o_root.job[2].operation[0].op_duration) == 1.1
    assert o_root.job[2].operation[0].allowed_machine == 'm1'
    assert float(o_root.job[2].operation[1].op_duration) == 1.2
    assert o_root.job[2].operation[1].allowed_machine == 'm0'
    assert float(o_root.job[2].operation[2].op_duration) == 1.3
    assert o_root.job[2].operation[2].allowed_machine == 'm2'
