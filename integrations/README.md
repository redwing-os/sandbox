# Vector Integrations

## SAP Integration Guide

First install SAP NetWeaver Remote Function Call (RFC) Software Development Kit (SDK).

Log in to SAP Marketplace by using the following URL:

`http://service.sap.com`

Click `SAP Support Portal`.

Enter your Service Marketplace user name and password.

Click `Software Downloads` and expand the `Support Packages and Patches` link.

Click `Browse our Download` Catalog, and then click `Additional Components`.

Click `SAP NetWeaver RFC SDK`, and then click `SAP NetWeaver RFC SDK`.

Attention: From `SAP agent V8.1.4.0.20` onwards, you must download `SAP NetWeaver RFC SDK 7.50 PL11` libraries only.

Select the operating system where you have the SAP agent.

Download the `*.SAR` file on your computer.

To extract the SAP Netweaver RFC SDK `*.SAR` file by using the `SAPCAR` utility that is provided by SAP, run the following command:

```
sapcar -xvf SAP NetWeaver RFC SDK File Name.SAR
```

## SAP Python Dependencies 

```
pip install cython
```

PyRFC Download Link.

```
https://github.com/SAP/PyRFC/releases
```

For the purposes of Sandbox we have gone ahead and pre-installed one for MacOSX, arm64-based systems. 

```
https://github.com/SAP/PyRFC/releases/download/v3.3/pyrfc-3.3-cp310-cp310-macosx_13_0_arm64.whl
```

To Install from `.whl` file locally

```
pip install pyrfc-3.3-cp310-cp310-macosx_13_0_arm64.whl
```



