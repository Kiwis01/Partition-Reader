# Partition-Reader

This code was made with standard python libraries, imports are "argparse, hashlib, os, json".
To run the code you can execute the makefile by entering "make" on the terminal or referencing the makfile directly "make makefile". Then an executable "./boot_info" will be available to use.

# Usage 
"./boot_info -f file.raw -o 123 73 234"
--f {filename} --o {offsets}

# Description 
This code can calculate MD5 hash and SHA 256 SHA hash values and store them into a designated txt file with the name of the raw file in between the hash and .txt, ex. "MD5-{filename}.txt". 

After that the code will check if the entered file -f has a GPT or MBR partition, then it will parse different partition trees depending on that.

If it detects the ID byte is "ee" or "EE" then it will parse a GPT partition tree, otherwise, it will be an MBR tree.

GPT tree shows the partitions GUID type, First and Last LBA address in both hex and decimal values. As well as the Partition name decoded to Romani characters (ASCII).

MBR tree shows the ID of the partition and extracts the type of partition by comparing the JSON file containing each ID and their corresponding partition, then it also prints the 16 bytes starting from the offset that was entered in the -o argument (For this we used the LBA * 512 + offsets to find the 16 bytes in the offset regarding the position of the start LBA address). It also outputs the ASCII translation of the 16 bytes.

# Testing
I uploaded two "raw" files for testing purposes, feel free to use any file you want. 
