## **PrintNode API Client Python Library**

This is a Python library to interact with PrintNode's remote printing API. This client allows you to access the API's functions for quick use in Python scripts.

### Requirements

* Python 2.x or 3.x
* python-requests
* python-future

### Installation

This is installed as a module by executing `python3 setup.py install` with root permissions.

### Getting Started

The default constructor for the Library is a Gateway, which is constructed with at minimum of one key-word argument, that being an api-key.

```python
from printnodeapi.Gateway import Gateway
my_account_gateway = Gateway(apikey='my_api_key')
```

After creating a Gateway, you can access any requests as such:

```python
my_account_id = my_account_gateway.account.id
new_tag = my_account_gateway.ModifyTag("Likes","PrintNode")
```

### Initial Gateway Configuration

You can authenticate in 2 ways other than using an api-key:
```python
Gateway(email='email',password='password')
Gateway(clientkey='ckey')
```

The three below will authenticate with access to child accounts of a specific user:

```python
Gateway(apikey='api-key',child_email='c_email')
Gateway(apikey='api-key',child_ref='c_creator_ref')
Gateway(apikey='api-key',child_id='c_id')
```

### Gateway Methods
All of these will have the associated API doc next to them. Any of the argument types will be exactly the same as the attributes used in a normal request. Any "Objects" under type are represented as a `dict`, which will have the same representation as the JSON objects.


### Computers Library
This handles anything that is associated with a computer, such as Printers, PrintJobs, States (of PrintJobs) and Scales.

### Account lookup
https://www.printnode.com/docs/api/curl/#whoami

#### account(self)
Returns an Account object of the currently authenticated account.
```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
print(gateway.account.firstname)

'''
Results:
Mr
'''
```
### Computer lookup
https://www.printnode.com/docs/api/curl/#computers

#### computers(self, computer)
Given a set of computers, returns these computers. Given only one id, returns that computer.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
print(gateway.computers(computer=10027).name)

'''
Results:
5.2015-07-10 15:04:40.253763.TEST-COMPUTER
'''
```
### Printer lookup
https://www.printnode.com/docs/api/curl/#printers

#### printers(self, computer=None, printer=None)
There are four ways this can be run:

* *printer* & *computer* argument both None: Gives all printers attached to the account.
* *printer* str/int, *computer* None: Gives a printer found from either an id or the name of a printer, taken from all possible printers.
* *printer* None, *computer* int: Gives all printers attached to the computer given by an id.
* *printer* str/int, *computer* int: Gives a printer found from either an id or the name of a printer, taken only from printers attached to the computer specified by the computer's id.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
print(gateway.printers(printer=50120).name)
for printer in gateway.printers(computer=10027):
    print(printer.name)

'''
Results:
10027.3.TEST-PRINTER
10027.1.TEST-PRINTER
10027.2.TEST-PRINTER
10027.3.TEST-PRINTER
10027.4.TEST-PRINTER
10027.5.TEST-PRINTER
'''
```

### PrintJob lookup
https://www.printnode.com/docs/api/curl/#printjob-viewing

#### printjobs(self, computer=None, printer=None, printjob=None
There are five ways this can be run:

* No arguments : Returns all printjobs associated with the account.
* *computer* int : Returns all printjobs relative to printers associated with the computer specified by the argument *computer*.
* *printer* int : Returns all printjobs relative to the printer specificed by the argument *printer*.
* *computer* int, *printer* int : Returns all printjobs relative to the printer specified by the argument *printer* from printers with access to *computer*.
* *printjob* int : Returns specific printjob.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
printjob_id = gateway.printjobs(computer=10027)[0].id
print(gateway.printjobs(printer=50120)[0].id)
print(gateway.printjobs(printjob=printjob_id))

'''
Results:
251137
PrintJob(id=251127, printer=Printer(id=50118, computer=Computer(id=10027, name='5.2015-07-10 15:04:40.253763.TEST-COMPUTER', inet=None, inet6=None, hostname=None, version=None, create_timestamp='2015-07-10T15:04:40.253Z', state='created'), name='10027.1.TEST-PRINTER', description='description', capabilities={'capability_1': 'one', 'capability_2': 'two'}, default=True, create_timestamp='2015-07-10T15:04:40.253Z', state=None), title='50118.1.TEST-PRINTJOB', content_type='pdf_uri', source='API test endpoint', expire_at=None, create_timestamp='2015-07-10T15:04:40.253Z', state='new')
'''
```
### PrintJob creation
https://www.printnode.com/docs/api/curl/#printjob-creating

#### PrintJob(self, computer=None, printer=None, job_type='pdf', title='PrintJob',options=None,authentication=None,uri=None,base64=None,binary=None)
Only one of uri, base64 and binary can be chosen.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
print(gateway.PrintJob(printer=50120,options={"copies":2},uri="a.pdf"))

'''
Results:
PrintJob(id=251153, printer=Printer(id=50120, computer=Computer(id=10027, name='5.2015-07-10 15:04:40.253763.TEST-COMPUTER', inet=None, inet6=None, hostname=None, version=None, create_timestamp='2015-07-10T15:04:40.253Z', state='created'), name='10027.3.TEST-PRINTER', description='description', capabilities={'capability_1': 'one', 'capability_2': 'two'}, default=False, create_timestamp='2015-07-10T15:04:40.253Z', state=None), title='PrintJob', content_type='pdf_uri', source='PythonApiClient', expire_at=None, create_timestamp='2015-07-10T15:05:27.087Z', state='new')
'''
```
### State lookup

https://www.printnode.com/docs/api/curl/#printjob-states

#### states(self, printjob_set)
Given a set of printjobs as a string (check https://www.printnode.com/docs/api/curl/#parameters for examples), returns a list of object type State. As each PrintJob can have many states, `states()` is a list of PrintJobs that each have a list of States.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
printjob_id = gateway.printjobs(computer=10027)[0].id
print(gateway.states(printjob_id)[0][0].state)

'''
Results:
new
'''
```

### Accounts Library
This handles anything to do with accounts, such as Account creation, deletion and modificaiton, api-key handling, tag handling and Client handling.

### Tag lookup
https://www.printnode.com/docs/api/curl/#account-tagging

#### tag(self, tagname)
Given a *tagname*, returns the value of that tag.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
print(gateway.tag("Likes"))

'''
Results:
Everything!
'''
```
### Tag modification
#### ModifyTag(self, tagname, tagvalue)
Given a *tagname* and *tagvalue*, either creates a tag with specifed value if *tagname* doesn't exist, otherwise changes the value.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
gateway.ModifyTag("Likes","PrintNode")
print(gateway.tag("Likes"))

'''
Results:
PrintNode
'''
```

### Tag deletion
#### DeleteTag(self, tagname)
Given a *tagname*, deletes that tag. Returns True on successful deletion.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
gateway.ModifyTag("Likes","PrintNode")
gateway.DeleteTag("Likes")
print(gateway.account.tags)

'''
Results:
[]
'''
```

### Account creation
https://www.printnode.com/docs/api/curl/#account-creation

#### CreateAccount(self, firstname, lastname, email, password, creator_ref=None, api_keys=None, tags=None)
Creates an account with the specified values. The last three are optional.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"}
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
print(new_account_gateway.account.firstname)
new_account_gateway.DeleteAccount()

'''
Results:
A
'''
```

### Account deletion
https://www.printnode.com/docs/api/curl/#account-deletion

#### DeleteAccount(self)
Deletes the child account that is currently authenticated. Accounts can only be deleted if authenticated by a parent account's api-key and a reference to the child account being deleted (e.g the child account's id)
```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"}
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
new_account_gateway.DeleteAccount()
print(new_account["Account"]["id"] in gateway.account.child_accounts)

'''
Results:
False
'''
```

### Account modification
https://www.printnode.com/docs/api/curl/#account-modification

#### ModifyAccount(self, firstname=None, lastname=None, password=None, email=None, creator_ref=None)
Given one or more arguments, changes the account details specified by the arguments.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"}
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
new_account_gateway.ModifyAccount(firstname="B")
print(new_account_gateway.account.firstname)
new_account_gateway.DeleteAccount()

'''
Results:
B
'''
```
### Api-key lookup
https://www.printnode.com/docs/api/curl/#account-apikeys

#### apikey(self, api_key)
Returns value of api-key specified by the argument.
```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"},
    api_keys=["Production"]
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
print(new_account_gateway.api_key("Production"))
new_account_gateway.DeleteAccount()

'''
Results:
5a272ed7406d351be86f25be388810dc83b8f52d
'''
```
### API Key Creation
#### CreateApikey(self, api_key)
Creates an api-key with the api-key's reference given by the argument.

```python
from printnodeapi import Gateway

gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"},
    api_keys=["Production"]
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
new_account_gateway.CreateApiKey("Development")
print(new_account_gateway.account.api_keys)
new_account_gateway.DeleteAccount()

'''
Results:
{'Development': '123SecretAPIKey', 'Production': '456SecretAPIKey'}
'''
```
### API Key Deletion
#### DeleteApikey(self, api_key)
Deletes api-key specified by the argument.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"},
    api_keys=["Production"]
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
new_account_gateway.DeleteApiKey("Production")
print(new_account_gateway.account.api_keys)
new_account_gateway.DeleteAccount()

'''
Results:
[]
'''
```

### Client Key creation
https://www.printnode.com/docs/api/curl/#account-delegated-auth

#### clientkey(self, uuid, edition, version)
Generates a clientkey for the account.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
new_account = gateway.CreateAccount(
    firstname="A",
    lastname="Person",
    password="password",
    email="aperson@emailprovider.com",
    tags={"Likes":"Something"},
    api_keys=["Production"]
    )
new_account_gateway = Gateway(url='https://api.printnode.com',apikey='secretAPIKey',child_id=new_account["Account"]["id"])
new_clientkey = new_account_gateway.clientkey(
    uuid="0a756864-602e-428f-a90b-842dee47f57e",
    edition="printnode",
    version="4.7.2")
print(new_clientkey)
new_account_gateway.DeleteAccount()

'''
Results:
ck-nwa2SSvSGl1YR5zrHDVVgfdpJ8JLfVCvwaCWj8dQXmZW
'''
```
### Download client lookup
https://www.printnode.com/docs/api/curl/#account-download-management

#### clients(self, client_ids = None, os = None)
This has three different outcomes:

* *os* and *client_ids* both None: Returns all clients available for the current account.
* *os* str and *client_ids* None: Returns the most recent version for given OS ("windows" or "osx" only)
* *os* None and *client_ids* str: Given a set of ids (e.g "11-15"), return all clients in that set.

Having both set will default to showing the most recent version for the os argument.

```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
for client in gateway.clients(client_ids="11-12"):
    print(client.id)
print(gateway.clients(os="windows").os)

'''
Results:
12
11
windows
'''
```

### Download client controlling
#### ModifyClientDownloads(self, client_id, enabled)
Given a set of ids and either True or False, sets whether the clients are enabled or not. Returns a list of modified clients.
```python
from printnodeapi import Gateway

gateway=Gateway(url='https://api.printnode.com',apikey='secretAPIKey')
gateway.ModifyClientDownloads(11,False)
print(gateway.clients(client_ids=11)[0].enabled)

'''
Results:
False
'''
```
