# Testing using curl command

### Adding user 

```bash
curl -H "Content-Type: application/json" -X POST -d '{ "token": "JCS39VlJ3EzS29YsYUdnrOWu", "CreateUserSSH": { "username": "xyz", "ssh-key": "AAAAB3NzaC1y6zvpeP1xKmPAJtE32F+kIvFs6nFmhcqgzbAkSnZ8S54mL+BsI1OB98AwF6RFn9CmYN1QIgw9OOsxalZyQGfFr== teste@teste-laptop"}}' http://127.0.0.1:8080/add/user
```

### Deleting user

```bash
curl -H "Content-Type: application/json" -X POST -d '{ "token": "JCS39VlJ3EzS29YsYUdnrOWu", "DeleteUserSSH": { "username": "xyz"}}' http://127.0.0.1:8080/add/user
```

### Python Example for adding user and ssk-pub key
```python
import json, requests

url = 'http://127.0.0.1:8080/add/user'

data = {
    "token": "JCS39VlJ3ELIez2KBMMzS29YsYUdnrOWu",
    "CreateUserSSH": {
        "username": "xyz",
        "ssh-key": "AAAAB3NzaC1y6zvqgzbAkS1QIgw9OOsxalZyQGfFr== teste@teste-laptop"
    }
}

resp = requests.post(url=url, json=data)
data = json.loads(resp.text)

print data

```
```python
import json, requests

url = 'http://127.0.0.1:8080/add/user'

data = {
    "token": "JCS39VlJ3ELIez2KBMMzS29YsYUdnrOWu",
    "CreateUserSSH": {
        "username": "xyz",
        "ssh-key": [ "AAAAB3NzaC1y6zvqgzbAkS1QIgw9OOsxalZyQGfFr== teste@teste-laptop" ]
    }
}

resp = requests.post(url=url, json=data)
data = json.loads(resp.text)

print data

```
### Python Example for adding another ssh-pub key to the user
```python
import json, requests

url = 'http://127.0.0.1:8080/add/sshpubkey'

data = {
    "token": "JCS39VlJ3ELIez2KBMMzS29YsYUdnrOWu",
    "AddSshKey": {
        "username": "xyz",
        "ssh-key": "AAAAB3NzaC1y6zvqgzbAkS1QIgw9OOsxalZyQGfFr== teste@teste-laptop"
    }
}

resp = requests.post(url=url, json=data)
data = json.loads(resp.text)

print data

```

```python
import json, requests

url = 'http://127.0.0.1:8080/add/sshpubkey'

data = {
    "token": "JCS39VlJ3ELIez2KBMMzS29YsYUdnrOWu",
    "AddSshKey": {
        "username": "xyz",
        "ssh-key": [ "AAAAB3NzaC1y6zvqgzbAkS1QIgw9OOsxalZyQGfFr== teste@teste-laptop" ]
    }
}

resp = requests.post(url=url, json=data)
data = json.loads(resp.text)

print data

```