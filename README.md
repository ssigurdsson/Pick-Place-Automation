# Pick-Place-Automation

This python script enables automated Pick &amp; Place processing of unsorted components/devices using computer vision powered by the opencv library.

The script controls the software that accompanies the P&P machine, moving the microscope objective accross the plane in which the unsorted devices lie, registering the locations of each device and checking if the device is face-up or -down. The script then spits out files that may be uploaded to the P&P software for automated processing of the devices into ordered arrays.

As our devices are small, it's important that the script yields precise locations so that the precision is only limited by the components of the P&P machine.

The animation below demonstrate the computer-vision abilities of the script, as well as the resulting sorted devices (as processed by the P&P Machine).

![results](example_results.gif)

# Files & Folders

pick_n_place_automation.py: This is the script that generates the appropriate files for input into the P&P software.

testimage.png: This image may be used to test the functionality of the script.

processed_devices.png: This image shows a handful of sorted devices post-processing via the script.

example_results.gif: This animation shows the images generated as the microscope camera moves accross the device plane, demonstrating appropriate discrimination and localization of devices.

example_results: This folder contains the images displayed in the above .gif file.
