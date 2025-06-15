# CBM
The full name of CBM is Companion Board Module, which is a program placed on the RPi used to send data integrated with information from the RPi camera and Fly Controller to the Ground Control Station (GCS) via TCP.



## Tutorial: 
Please refer to the following two PDF documents:
- PDF1 outlines the hardware equipment that should be prepared, and how to use the code from this repository to enable the functions to work.
- PDF2 describes the prerequisites for testing before using the Fly Controller to retrieve the data.
- PDF3 describes the installation steps of the picamera packages before using the Arducam camera with RPi. (by Yang-Zhi)

## Requirements

Both software environments on CBM and GCS use `Python version 3.10.1`.
* packages on CBM:
  * MAVProxy   1.8.71
  * numpy      2.2.2
  * pymavlink  2.4.42
  * multiprocess 0.70.17
    
* packages on GCS:  
  * piexif     1.1.3

## Result
This video shows the real-time status of GCS receiving image information.
