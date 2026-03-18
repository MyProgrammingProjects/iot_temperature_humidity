
## Create a root CA
I first need to create an internal root certificate authority (CA) and a self-signed root CA certificate to serve as the trust anchor from which I can create other certificates for testing. The files used to create and maintain the internal root CA are stored in a folder structure that is initialized as part of this process. Perform the following steps to:

- Create and initialize the folders and files used by the root CA
- Create a configuration file used by OpenSSL to configure the root CA and the certificates created with it
- Generate a self-signed CA certificate that serves as the root CA certificate


```bash

mkdir rootca
cd rootca
mkdir certs db private
chmod 700 private
touch db/index
openssl rand -hex 16 > db/serial
echo 1001 > db/crlnumber

```


Create a text file named `rootca.conf` in the `rootca` directory created in the previous step. Open that file in a text editor, then copy and save the OpenSSL configuration settings into it.

This file provides OpenSSL with the values needed to configure the test root CA. In this example, the file configures a root CA called `rootca` using the directories and files created in the previous steps. The file also provides configuration settings for:

- The CA policy used by the root CA for certificate Distinguished Name (DN) fields
- Certificate requests created by the root CA
- X.509 extensions applied to root CA certificates, subordinate CA certificates, and client certificates issued by the root CA


__Note__

The `home` attribute in the `ca_default` section is set to `../rootca` because this configuration file is also used when creating the certificate for the subordinate CA. The specified relative path allows OpenSSL to navigate from the subordinate CA folder back to the root CA folder during that process.


In the Bash window, run the following command to generate a certificate signing request (CSR) in the `rootca` directory and generate a private key in the `rootca/private` directory. For more information about the OpenSSL `req` command, see the `openssl-req` manual page in the OpenSSL documentation.




```bash
openssl req -new -config rootca.conf -out rootca.csr -keyout private/rootca.key

```

You will be prompted to enter a PEM pass phrase, as shown in the following example, for the private key file. Enter and confirm a pass phrase to generate the private key and CSR.



```bash
Enter PEM pass phrase:
Verifying - Enter PEM pass phrase:
-----

```

Confirm that the CSR file `rootca.csr` is present in the `rootca` directory and that the private key file `rootca.key` is present in the `private` subdirectory before continuing.


In the Bash window, run the following command to create a self-signed root CA certificate. The command applies the `ca_ext` configuration file extensions to the certificate. These extensions indicate that the certificate is for a root CA and can be used to sign certificates and certificate revocation lists (CRLs). For more information about the OpenSSL `ca` command, see the `openssl-ca` manual page in the OpenSSL documentation.




```bash
openssl ca -selfsign -config rootca.conf -in rootca.csr -out rootca.crt -extensions ca_ext

```

You will be prompted to provide the PEM pass phrase, as shown in the following example, for the private key file.



```bash
Using configuration from rootca.conf
Enter pass phrase for ../rootca/private/rootca.key:
```


After providing the pass phrase, OpenSSL generates a certificate and then prompts you to sign and commit it for the root CA. Specify `y` for both prompts to generate the self-signed certificate for the root CA.


```bash
Using configuration from rootca.conf
Enter pass phrase for ../rootca/private/rootca.key:
Check that the request matches the signature
Signature ok
Certificate Details:
    {Details omitted from output for clarity}
Certificate is to be certified until Mar  9 17:43:12 2036 GMT (3650 days)
Sign the certificate? [y/n]:


1 out of 1 certificate requests certified, commit? [y/n]
Write out database with 1 new entries
Data Base Updated

Sign the certificate? [y/n]:


1 out of 1 certificate requests certified, commit? [y/n]
Write out database with 1 new entries
Data Base Updated

```

After OpenSSL updates the certificate database, confirm that both the certificate file `rootca.crt` is present in the `rootca` directory and the PEM certificate file (`.pem`) is present in the `rootca/certs` directory. The name of the `.pem` file matches the serial number of the root CA certificate.


## Create a subordinate CA

After creating the internal root CA, the next step is to create a subordinate CA to use as an intermediate CA for signing client certificates for the devices. In theory, this is not strictly required, because the root CA certificate can be uploaded to the IoT hub and used directly to sign client certificates. However, using a subordinate CA more closely simulates a recommended production environment, where the root CA is kept offline. A subordinate CA can also sign other subordinate CAs, creating a hierarchy of intermediate CAs as part of a certificate chain of trust. In a production environment, that chain of trust enables delegated signing authority for devices.

Similar to the root CA, the files used to create and maintain the subordinate CA are stored in a folder structure that is initialized as part of this process. Perform the following steps:

Return to the base directory that contains the `rootca` directory. In this example, both the root CA and the subordinate CA are located in the same base directory.

```bash
cd ..

```


In the Bash window, run the following commands one at a time.

This step creates a directory structure and support files for the subordinate CA, similar to the structure created for the root CA in the previous section.


```bash
mkdir subca
cd subca
mkdir certs db private
chmod 700 private
touch db/index
openssl rand -hex 16 > db/serial
echo 1001 > db/crlnumber

```

Create a text file named `subca.conf` in the `subca` directory created in the previous step. Open that file in a text editor, then copy and save the OpenSSL configuration settings into it.

As with the configuration file for the test root CA, this file provides OpenSSL with the values needed to configure the test subordinate CA. You can create multiple subordinate CAs to support different testing scenarios or environments.



In the Bash window, run the following command to generate a private key and a certificate signing request (CSR) in the subordinate CA directory.


```bash
openssl req -new -config subca.conf -out subca.csr -keyout private/subca.key

```



You will be prompted to enter a PEM pass phrase, as shown in the following example, for the private key file. Enter and confirm a pass phrase to generate the private key and CSR.



```bash
Enter PEM pass phrase:
Verifying - Enter PEM pass phrase:
-----
```

Confirm that the CSR file `subca.csr` is present in the subordinate CA directory and that the private key file `subca.key` is present in the `private` subdirectory before continuing.

In the Bash window, run the following command to create a subordinate CA certificate in the subordinate CA directory. The command applies the `sub_ca_ext` configuration file extensions to the certificate. These extensions indicate that the certificate is for a subordinate CA and can also be used to sign certificates and certificate revocation lists (CRLs). Unlike the root CA certificate, this certificate is not self-signed. Instead, it is signed by the root CA certificate, establishing a certificate chain similar to what would be used in a public key infrastructure (PKI). The subordinate CA certificate is then used to sign client certificates for testing the devices.


```bash
openssl ca -config ../rootca/rootca.conf -in subca.csr -out subca.crt -extensions sub_ca_ext

```


You will be prompted to enter the pass phrase, as shown in the following example, for the private key file of the root CA. After you enter the pass phrase, OpenSSL generates and displays the certificate details, then prompts you to sign and commit the certificate for the subordinate CA. Specify `y` for both prompts.



```bash
Using configuration from rootca.conf
Enter pass phrase for ../rootca/private/rootca.key:
Check that the request matches the signature
Signature ok
Certificate Details:
    {Details omitted from output for clarity}
Certificate is to be certified until Mar  9 17:52:13 2036 GMT (3650 days)
Sign the certificate? [y/n]:


1 out of 1 certificate requests certified, commit? [y/n]
Write out database with 1 new entries
Data Base Updated

```

After OpenSSL updates the certificate database, confirm that the certificate file `subca.crt` is present in the subordinate CA directory and that the PEM certificate file (`.pem`) is present in the `rootca/certs` directory. The name of the `.pem` file matches the serial number of the subordinate CA certificate.


## Register your subordinate CA certificate in your IoT hub


Register the subordinate CA certificate in the IoT hub so that it can be used to authenticate devices during registration and connection. The following steps describe how to upload and automatically verify the subordinate CA certificate in the IoT hub.

In the Azure portal, navigate to the IoT hub and select `Certificates` from the resource menu under `Security settings`.

Select `Add` from the command bar to add a new CA certificate.

Enter a display name for the subordinate CA certificate in the `Certificate name` field.

Select the PEM certificate file (`.pem`) for the subordinate CA certificate from the `rootca/certs` directory and upload it in the `.pem` or `.cer` field.

Check the box next to `Set certificate status to verified on upload`.

Select `Save`.

The uploaded subordinate CA certificate should appear with its status set to `Verified` on the `Certificates` tab.


## Create a client certificate for a device

This is done in the same folder as `subca`.


After creating the subordinate CA, you can create client certificates for the devices. The files and folders created for the subordinate CA are used to store the CSR, private key, and certificate files for each client certificate.

The client certificate must have its Subject Common Name (CN) set to the same value as the device ID used when registering the corresponding device in Azure IoT Hub. So if you register a device called `device_1` in IoT Hub, then the certificate Common Name must also be `device_1`.



In the Bash window, make sure you are still in the `subca` directory.

Run the following commands one at a time, replacing the placeholder with a name for the IoT device, for example `DEVICE_NAME`. This step creates the private key and CSR for the client certificate.

It creates a 2048-bit RSA private key and then generates a certificate signing request (CSR) using that key.



```bash

openssl genpkey -out private/DEVICE_NAME.key -algorithm RSA -pkeyopt rsa_keygen_bits:2048
openssl req -new -key private/DEVICE_NAME.key -out DEVICE_NAME.csr


```



When prompted, provide the certificate details as shown in the following example.

__The only prompt that requires a specific value is the Common Name__, which must match the device name used in the previous step. The other fields can be skipped or filled with arbitrary values.

After entering the certificate details, OpenSSL generates and displays the request details.


```bash
-----
Country Name (2 letter code) [XX]:.
State or Province Name (full name) []:.
Locality Name (eg, city) [Default City]:.
Organization Name (eg, company) [Default Company Ltd]:.
Organizational Unit Name (eg, section) []:
Common Name (eg, your name or your server hostname) []:'DEVICE_NAME'
Email Address []:

Please enter the following 'extra' attributes
to be sent with your certificate request
A challenge password []:
An optional company name []:

```


Confirm that the CSR file is present in the subordinate CA directory and that the private key file is present in the `private` subdirectory before continuing.

In the Bash window, run the following command, replacing the device name placeholder with the same name used in the previous steps.

This step creates a client certificate in the subordinate CA directory. The command applies the `client_ext` configuration file extensions to the certificate. These extensions indicate that the certificate is a client certificate and cannot be used as a CA certificate. The client certificate is signed by the subordinate CA certificate.



```bash
openssl ca -config subca.conf -in <DEVICE_NAME>.csr -out <DEVICE_NAME>.crt -extensions client_ext

```



You will be prompted to enter the pass phrase, as shown in the following example, for the private key file of the subordinate CA. After entering the pass phrase, OpenSSL generates and displays the certificate details, then prompts you to sign and commit the client certificate for the device. Specify `y` for both prompts.


```bash
Using configuration from subca.conf
Enter pass phrase for ../subca/private/subca.key:
Check that the request matches the signature
Signature ok
Certificate Details:
    {Details omitted from output for clarity}
Certificate is to be certified until Mar  9 19:14:51 2036 GMT (3650 days)
Sign the certificate? [y/n]:


1 out of 1 certificate requests certified, commit? [y/n]
Write out database with 1 new entries
Data Base Updated

```


After OpenSSL updates the certificate database, confirm that the certificate file for the client certificate is present in the subordinate CA directory and that the PEM certificate file (`.pem`) is present in the `certs` subdirectory of the subordinate CA directory. The name of the `.pem` file matches the serial number of the client certificate.




## Tricky Part
After following all of those steps, I still could not make authentication work. Not even ChatGPT helped at first. After more searching, I found a post that said: "In MicroPython certificates have to be in DER format, not PEM."

```bash
openssl pkey -in private/DEVICE_NAME.key -out private/DEVICE_NAME.der -outform DER
openssl x509 -in certs/DEVICE_NAME.pem -out certs/DEVICE_NAME.der -outform DER
```

After doing that, everything worked as expected and I started to see data flowing into the database.




I set all my certificates to be valid for 3,650 days because I intend to use this system for as long as possible and do not want to revisit authentication issues unnecessarily. In fact, the system has been running for a while and I have already validated the resilience requirements. However, the certificates originally had a shorter duration and, after the system had been running successfully for some time, data suddenly stopped being sent. Fortunately, because I had logs, I found the following message:

```text
b' \x02\x00\x05' MQTTException raised: 5
```

With some help from ChatGPT, I found the explanation. After checking the certificate details, I discovered that the certificates had expired.

```text
MQTTException: 5 from umqtt.robust / umqtt.simple corresponds to an MQTT CONNACK return code = 5, which means:

Connection Refused - Not Authorized
```
