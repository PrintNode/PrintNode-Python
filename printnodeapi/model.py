
from collections import namedtuple

from .util import camel_to_underscore

def safe_tuple_populate(tuple_class, fields, defaults={}):
    """
    Instantiate a named tuple using *fields in a "safe" way. I.e. extra keys
    are ignored and missing keys are populated by defaults dict

    tuple_class :namedtuple/model
    fields :dict
    defaults :dict
    """

    assert issubclass(tuple_class, Model)
    assert isinstance(fields, dict)
    assert isinstance(defaults, dict)

    fk = set(fields.keys())
    tk = set(tuple_class._fields)

    # add in missing fields using defaults if present
    for key in (tk - fk):
        fields.setdefault(key, defaults.get(key))

    # remove any extra keys
    for key in (fk - tk):
        fields.pop(key)

    return tuple_class(**fields)


class ModelFactory:

    def create_account(self, account_dict):
        fields = self._underscore_keys(account_dict)
        fields.setdefault('api_keys', [])
        fields.setdefault('permissions', [])
        return safe_tuple_populate(Account, fields)

    def create_clients(self, clients_dict):
        return self._map(self.create_client, clients_dict)

    def create_latest_download(self, client_dict):
        fields = self._underscore_keys(client_dict)
        return safe_tuple_populate(Download, fields)

    def create_client(self, client_dict):
        fields = self._underscore_keys(client_dict)
        return safe_tuple_populate(Client, fields)

    def create_scales(self, scales_dict):
        return self._map(self.create_scale, scales_dict)

    def create_scale(self, scale_dict):
        fields = self._underscore_keys(scale_dict)
        return safe_tuple_populate(Scale, fields)

    def create_computers(self, computers_dict):
        return self._map(self.create_computer, computers_dict)

    def create_computer(self, computer_dict):
        fields = self._underscore_keys(computer_dict)
        del fields['jre']
        self._rename_field(fields, 'inet_6', 'inet6')
        return safe_tuple_populate(Computer, fields)

    def create_printers(self, printers_dict):
        return self._map(self.create_printer, printers_dict)

    def create_printer(self, printer_dict):
        fields = self._underscore_keys(printer_dict)
        fields['computer'] = self.create_computer(fields['computer'])
        if fields['capabilities']:
            fields['capabilities'] = self.create_capabilities(
                fields['capabilities'])
        return safe_tuple_populate(Printer, fields)

    def create_capabilities(self, capabilities_dict):
        fields = self._underscore_keys(capabilities_dict)
        return safe_tuple_populate(Capabilities, fields)

    def create_printjobs(self, printjobs_dict):
        return self._map(self.create_printjob, printjobs_dict)

    def create_printjob(self, printjob_dict):
        fields = self._underscore_keys(printjob_dict)
        fields['printer'] = self.create_printer(fields['printer'])
        fields.setdefault('content', None)
        fields.setdefault('pages', None)
        fields.setdefault('qty', 1)
        fields.setdefault('options', {})
        return safe_tuple_populate(PrintJob, fields)

    def create_states_map(self, states_dict_list):
        return self._map(self.create_states, states_dict_list)

    def create_states(self, states_dict):
        return self._map(self.create_state, states_dict)

    def create_state(self, state_dict):
        fields = self._underscore_keys(state_dict)
        return safe_tuple_populate(State, fields)

    def _underscore_keys(self, input_dict):
        return {
            camel_to_underscore(k): v
            for k, v in input_dict.items()}

    def _rename_field(self, obj_dict, old_name, new_name):
        assert new_name not in obj_dict
        obj_dict[new_name] = obj_dict[old_name]
        del obj_dict[old_name]

    def _map(self, f, iter):
        return list(map(f, iter))


class Model:
    pass


Account = namedtuple('Account', [
    'id',
    'firstname',
    'lastname',
    'email',
    'can_create_sub_accounts',
    'creator_email',
    'creator_ref',
    'child_accounts',
    'credits',
    'num_computers',
    'total_prints',
    'versions',
    'connected',
    'tags',
    'state',
    'api_keys',
    'permissions'])


class Account(Account, Model):
    pass


Computer = namedtuple('Computer', [
    'id',
    'name',
    'inet',
    'inet6',
    'hostname',
    'version',
    'create_timestamp',
    'state'])


class Computer(Computer, Model):
    pass


Printer = namedtuple('Printer', [
    'id',
    'computer',
    'name',
    'description',
    'capabilities',
    'default',
    'create_timestamp',
    'state'])


class Printer(Printer, Model):
    pass


PrintJob = namedtuple('PrintJob', [
    'id',
    'printer',
    'title',
    'content',
    'content_type',
    'pages',
    'qty',
    'options',
    'source',
    'expire_at',
    'create_timestamp',
    'state'])


class PrintJob(PrintJob, Model):
    pass

Scale = namedtuple('Scale', [
    'measurement',
    'mass',
    'product',
    'computer_id',
    'vendor_id',
    'port',
    'client_reported_create_timestamp',
    'device_name',
    'product_id',
    'vendor',
    'count',
    'age_of_data',
    'device_num',
    'ntp_offset'])


class Scale(Scale, Model):
    pass

Client = namedtuple('Client', [
    'id',
    'enabled',
    'edition',
    'version',
    'os',
    'filename',
    'filesize',
    'sha_1',
    'release_timestamp',
    'url'
    ])


class Client(Client, Model):
    pass

Download = namedtuple('Download', [
    'edition',
    'version',
    'os',
    'filename',
    'filesize',
    'sha_1',
    'release_timestamp',
    'url'
    ])


class Download(Download, Model):
    pass

State = namedtuple('State', [
    'print_job_id',
    'state',
    'message',
    'data',
    'client_version',
    'create_timestamp',
    'age'
    ])


class State(State, Model):
    pass

Capabilities = namedtuple('Capabilities', [
    'bins',
    'collate',
    'copies',
    'color',
    'dpis',
    'duplex',
    'extent',
    'medias',
    'nup',
    'papers',
    'printrate',
    'supports_custom_paper_size'
    ])


class Capabilities(Capabilities, Model):
    pass
