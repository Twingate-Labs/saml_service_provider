## Installation

---

### Python

- Set up python 3.10.1
    ```
    ~ $ brew install pyenv
    
    ~ $ pyenv install 3.10.1
    ```

### Poetry
- Managing dependency tool
    ```
    ~ $ brew install poetry
    ```


### OS package dependency

- `xmlsec1` - a requirement for [`pysaml2`](https://pysaml2.readthedocs.io/en/latest/install.html#install-pysaml2)
  ```
  ~ $ brew install libxmlsec1
  ```


## Setting up

---

- Clone the repository:

   ```sh
   ~ $ git clone git@github.com:inbalzelinger/saml_service_provider.git
   ~ $ cd saml_service_provider
   ```

- Set the local Python interpreter: 
    ```
    ~/saml_service_provider $ pyenv local 3.10.1
    ```

- Create and activate new virtual env.

    ```
    ~/saml_service_provider $ python3 -m venv .venv
    ~/saml_service_provider $ source .venv/bin/activate
    ```

- Install dependencies: 
   ```
   (.venv) ~/saml_service_provider $ poetry install
   ```


## Create SSO app on JumpCloud
***


Log in to JumpCloud as an Administrator --> go to SSO  --> press + to add an application --> chose custom SAML App

#### General Info

- Display label: `Sample_app`


- You can choose Logo and write a description

#### SSO

- IdP Entity ID:  `jumpcloud/twingate/sample-sp`


- SP Entity ID: `http://localhost:8000/sample_sp`


  **Note**: Those entity ids could be any string, but usually we will set then to an url.

- ACS URL: `http://127.0.0.1:8000/saml2/acs/`

    
- SAMLSubject's NameID: `email`

    
- SAMLSubject's NameID Format: `urn:oasis:names:tc:SAML:1.0:nameid-format-unspecified`

    
- Signature Algorithm: `RSA-SHA256`

    
- Sign assertion: keep unmarked


- Default RelayState: keep empty

    
- Login URL: `http://127.0.0.1:8000/saml2/login` 

    
- Declare Redirect Endpoint: keep unmarked

    
- IdP URL: `https://sso.jumpcloud.com/saml2/saml2`


#### User Groups

- Add a group of users that will get access to the app. 


#### Activate the app

  - Click **activate** to save and activate the connector.
  
#### Certificate

- Download the public certificate and private key pair `<cert>.pem`


- Open the `.pem` file that we just downloaded and copy its content. 


- We need the certificate to be in string format, we can use [onelogin SAML tools](https://www.samltool.com/format_x509cert.php) for that.


- Copy the cert in string format, paste it in our SP app in `saml.py`, `x509_cert="<change_it>`




## Check the application

---

#### Run the application

```shell
(.venv) ~/saml_service_provider $ python3 manage.py runserver
```

#### Access the application

- Access the login page the app in the browser:

  [http://localhost:8000/saml2/login](http://localhost:8000/saml2/login)


- We now redirected to the JumpCloud login page, 


- Login into JumpCloud with the user that has access to our app


- After the successful login to JumpCloud we will immediately redirected back to our SP acs url with a SAML response.

