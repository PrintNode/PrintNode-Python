from printnodeapi.model import Computer, Model, Printer, PrintJob, Scale, State
from future.types import newbytes
import json
import base64 as base_64
import sys


class Computers:

    def __init__(self, auth, factory):
        self._auth = auth
        self._factory = factory

    def get_computers(self, computer=None):
        if self._is_multi_query(computer):
            results = self._auth.get('/computers')
            computers = self._factory.create_computers(results)
            if isinstance(computer, str):
                return [c for c in computers if c.name == computer]
            else:
                return computers
        else:
            computer_id = self._get_computer_id(computer)
            results = self._auth.get('/computers/{}'.format(computer_id))
            if len(results) == 0:
                raise LookupError(
                    'computer not found with ID {}'.format(computer_id))
            assert len(results) == 1
            computers = self._factory.create_computers(results)
            return computers[0]

    def get_scales(self, computer, dev_name=None, dev_num=None):
        url = '/computer/'+str(computer)+'/scales'
        if dev_name is not None:
            url = url+'/'+dev_name
            if dev_num is not None:
                url = url+'/'+str(dev_num)
        if dev_num is not None and dev_name is None:
            temp_str = 'Device num stated without name - nothing found.'
            raise LookupError(temp_str)
        scales = self._factory.create_scales(self._auth.get(url))
        return scales

    def get_states(self, pjob_set=None):

        pjob_set = str(pjob_set)+"/" if pjob_set else ""
        states = self._factory.create_states_map(
            self._auth.get("/printjobs/"+pjob_set+"states"))

        return states

    def get_printers(self, computer=None, printer=None):
        """queries API for printers.
        the printer argument can be:
        * id of the printer, in which case a single printer is returned
        * name of the printer, in which case a single printer is returned
        * unspecified in which case a list of all printers is returned
        the computer argument can be:
        * id of the computer in which case only printers that are attached
        to that computer are returned
        * unspecified in which case all printers attached to the account
        are considered.
        raises LookupError if querying for a specific printer
        that doesn't exist
        """

        if self._is_multi_query(printer):
            computer_ids = ','.join(map(str, self._get_computer_ids(computer)))
            url = '/computers/{}/printers'.format(computer_ids)
            printers = self._factory.create_printers(self._auth.get(url))
            assert all(isinstance(p, Printer) for p in printers)
            if isinstance(printer, str):
                return [p for p in printers if p.name == printer]
            else:
                return printers
        else:
            printer_id = self._get_printer_id(printer)
            results = self._auth.get('/printers/{}'.format(printer_id))
            printers = self._factory.create_printers(results)
            assert all(isinstance(p, Printer) for p in printers)
            if len(printers) == 0:
                raise LookupError('no printer with ID {}'.format(printer_id))
            return printers[0]

    def get_printjobs(self, computer=None, printer=None, printjob=None):
        if self._is_multi_query(printjob):
            if computer is None and printer is None:
                url = '/printjobs'
                printjobs = self._factory.create_printjobs(self._auth.get(url))
                if isinstance(printjob, str):
                    return [pj for pj in printjobs if pj.title == printjob]
                else:
                    return printjobs
            else:
                printers = self.get_printers(
                    computer=computer,
                    printer=printer)
                if self._is_multi_query(printer):
                    if len(printers) == 0:
                        return []
                else:
                    printers = [printers]
                printer_ids = [p.id for p in printers]
                printer_url = ','.join(map(str, printer_ids))
                url = '/printers/{}/printjobs'.format(printer_url)
                printjobs = self._factory.create_printjobs(self._auth.get(url))

                if isinstance(printjob, str):
                    return [pj for pj in printjobs if pj.title == printjob]
                else:
                    return printjobs
        else:
            printjob_id = self._get_printjob_id(printjob)
            results = self._auth.get('/printjobs/{}'.format(printjob_id))
            printjobs = self._factory.create_printjobs(results)
            if len(printjobs) == 0:
                raise LookupError('no printjob with ID {}'.format(printjob_id))
            return printjobs[0]

    # could use the default printer if none is provided
    def submit_printjob(
            self,
            computer=None,
            printer=None,
            job_type='pdf',  # PDF|RAW
            title='PrintJob',
            options=None,
            authentication=None,
            uri=None,
            base64=None,
            binary=None):
        printers = self.get_printers(computer=computer, printer=printer)
        assert isinstance(printers, (list, Printer))
        if isinstance(printers, list):
            if len(printers) == 0:
                raise LookupError('printer not found')
            elif len(printers) > 1:
                printer_ids = ','.join(p.id for p in printers)
                msg = 'multiple printers match destination: {}'.format(
                    printer_ids)
                raise LookupError(msg)
            printer_id = printers[0].id
        else:
            printer_id = printers.id

        if job_type not in ['pdf', 'raw', 'binary']:
            raise ValueError('only support job_type of pdf or raw')
        if len([x for x in [uri, base64, binary] if x is not None]) != 1:
            raise ValueError('one and only one of the following parameters '
                             'is needed: uri, base64, or binary')

        if binary is not None:
            if sys.version_info[0] < 3:
                binary_bytes = newbytes(binary)
            else:
                if isinstance(binary, str):
                    binary_bytes = binary.encode('latin-1')
                else:
                    binary_bytes = binary
            base64 = base_64.b64encode(binary_bytes)
            base64 = base64.decode('utf-8')

        printjob_data = {
            'printerId': printer_id,
            'title': title,
            'contentType': job_type + '_' + ('uri' if uri else 'base64'),
            'content': uri or base64,
            'source': 'PythonApiClient'}

        if authentication is not None:
            printjob_data.update({"authentication": authentication})

        if options is not None:
            printjob_data.update({"options": options})

        printjob_id = self._auth.post('/printjobs', printjob_data)

        return printjob_id

    def _native(self, obj):
        if hasattr(obj, '__native__'):
            return obj.__native__()
        else:
            return obj

    def _get_computer_ids(self, computer):
        if isinstance(computer, int):
            return [computer]
        elif isinstance(computer, Computer):
            return [computer.id]
        elif computer is None or isinstance(computer, str):
            computers = [
                self._factory.create_computer(comp)
                for comp in self._auth.get('/computers')]
            if isinstance(computer, str):
                computers = [
                    comp
                    for comp in computers
                    if comp.name == computer]
            return [c.id for c in computers]
        else:
            raise TypeError('computer: "{}"'.format(type(computer)))

    def _get_computer_id(self, computer):
        return self._get_model_id(computer, Computer)

    def _get_printer_id(self, printer):
        return self._get_model_id(printer, Printer)

    def _get_printjob_id(self, printjob):
        return self._get_model_id(printjob, PrintJob)

    def _get_model_id(self, model, model_type):
        if isinstance(model, int):
            return model
        elif isinstance(model, model_type):
            return model.id
        else:
            raise TypeError(str(type(model)))

    def _get_printer_ids(self, printer):
        if isinstance(printer, int):
            return [printer]
        elif isinstance(printer, Printer):
            return [Printer.id]
        elif printer is None or isinstance(printer, str):
            printers = {
                self._factory.create_printer(printer_dict)
                for printer_dict in self._auth.get('/printer')}
            if isinstance(printer, str):
                printers = {
                    p for p in printers if p.name == printer}
            return printers
        else:
            raise TypeError('printer: "{}"'.format(type(printer)))

    def _is_multi_query(self, obj):
        if obj is None:
            return True
        elif isinstance(obj, int):
            return False
        elif isinstance(obj, str):
            return True
        elif isinstance(obj, Model):
            return False
        else:
            raise TypeError('type "{}" unsupported'.format(type(obj)))

    def _get_printer_by_name(self, printer_name, computer_id=None):
        assert isinstance(printer_name, str)
        assert not computer_id or isinstance(computer_id, int)
        printers = self.get_printers(computer=computer_id)
        return [
            printer
            for printer in printers
            if printer.name == printer_name]


class LookupFailedError(RuntimeError):

    def __init__(self, obj_name, field, value):
        msg = 'Failed to find a matching {} with {} of {}'.format(
            obj_name,
            field,
            value)
        super(RuntimeError, self).__init__(msg)

        self.obj_name = obj_name
        self.field = field
        self.value = value
