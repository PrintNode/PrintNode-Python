import pytest
import requests
import mock
import string
import random
import re
import time

from fixtures import *

from printnodeapi.gateway import Gateway
from printnodeapi.model import Computer, Printer, PrintJob, State, Account, Scale
from printnodeapi.auth import Auth

def setup_module(module):
    gateway = create_gateway()
    gateway.TestDataGenerate()

def teardown_module(module):
    gateway = create_gateway()
    gateway.TestDataDelete()

@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_scales(gateway):
    scales = gateway.scales(0)
    for scale in scales:
        assert isinstance(scale, Scale)

@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_all_printers(gateway):
    printers = gateway.printers()
    computers = gateway.computers()
    computer_names = []
    for computer in computers:
        computer_names.append(computer.name)

    for printer in printers:
        time.sleep(0.5)
        assert isinstance(printer, Printer)
        assert printer.computer.name in computer_names


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_query_printers_by_computer(gateway):

    for computer in gateway.computers():
        printers = gateway.printers(computer=computer.id)
        for printer in printers:
            assert printer.computer.id == computer.id
            assert printer.computer.name == computer.name

    assert [] == gateway.printers(computer=-1)


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_query_printers_by_printer_id(gateway):
    all_printers = gateway.printers()
    for printer in all_printers:
        time.sleep(0.5)
        assert printer == gateway.printers(printer=printer.id)
        assert printer == gateway.printers(
            computer=printer.computer.id,
            printer=printer.id)

    with pytest.raises(LookupError):
        gateway.printers(printer=-1)


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_query_printers_by_printer_name(gateway):
    for printer in gateway.printers():
        time.sleep(0.5)
        actual_printers = gateway.printers(printer=printer.name)
        assert printer in actual_printers


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_query_printers_by_invalid_printer_name_returns_empty(gateway):
    assert [] == gateway.printers(printer='fakeprinter')


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_all_printjobs(gateway):
    all_printjobs = gateway.printjobs()
    computers = gateway.computers()
    computer_names = []
    for computer in computers:
        computer_names.append(computer.name)
    for printjob in all_printjobs:
        assert isinstance(printjob, PrintJob)
        assert isinstance(printjob.printer, Printer)
        assert printjob.printer.computer.name in computer_names


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_printjobs_of_printer(gateway):
    all_printjobs = gateway.printjobs()
    printers = gateway.printers()
    for printer in printers:
        time.sleep(0.5)
        expected = sorted(
            pj
            for pj in all_printjobs
            if pj.printer.id == printer.id)
        actual = sorted(gateway.printjobs(printer=printer.id))
        assert expected == actual


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_get_specific_printjob(gateway):
    all_printjobs = gateway.printjobs()
    for expected_printjob in all_printjobs:
        time.sleep(0.5)
        actual = gateway.printjobs(printjob=expected_printjob.id)
        assert expected_printjob == actual


@pytest.mark.parametrize("gateway", [(create_gateway())])
def test_submit_printjob(gateway):
    printer = gateway.printers()[0]
    printjob = gateway.PrintJob(printer=printer.id, uri='somewhere')
    assert isinstance(printjob, PrintJob)
    assert printer == printjob.printer
    assert 'PrintJob' == printjob.title
    assert 'pdf_uri' == printjob.content_type
    assert 'PythonApiClient' == printjob.source
    state = gateway.states(printjob.id)
    assert isinstance(state[0][0], State)
    printjob = gateway.PrintJob(printer=printer.id, binary='010101010')
    assert isinstance(printjob, PrintJob)
