# Pick-Place-Automation

This python script enables automated Pick &amp; Place processing of unsorted components/devices using computer vision enabled by the opencv library.

The script controls the software that accompanies the P&P machine, moving the microscope camera accross the plane in which the unsorted devices lie, registering the locations of each device and checking whether that device is face-up or -down. The script then spits out files that may be uploaded to the P&P software for automated processing of the devices into ordered arrays.

As our devices are small, it's important that the software yields precise locations so that the precision is only limited by the components of the P&P machine.

# Files & Folders

PnP_auto.py: This is the script that generates the appropriate files for input into the P&P software.

testimage.png: This image may be used to test the functionality of the script.

processed_devices.png: This image shows a handful of sorted devices post-processing via the script.

example_results.gif: This animation shows the images generated as the microscope camera moves accross the device plane, demonstrating appropriate discrimination and localization of devices.

example_results: This folder contains the images displayed in the above .gif file.
