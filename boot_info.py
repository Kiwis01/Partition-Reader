#!/usr/bin/env python3
import argparse
import hashlib
import os
import json

# Function to calculate MD5 hash value
def calculate_md5(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        md5_hash = hashlib.md5(data).hexdigest()
    return md5_hash

# Function to calculate SHA-256 hash value
def calculate_sha256(file_path):
    with open(file_path, 'rb') as f:
        data = f.read()
        sha256_hash = hashlib.sha256(data).hexdigest()
    return sha256_hash
    
# Function to extract file partitions
def get_partition_scheme(disk):

    # Loading the partition json file provided to find the partition file based on id
    with open('PartitionTypes.json', 'r') as f:
        partition_types = json.load(f)

    # LBA list  
    lbs = []
    for i in range(3):
        file_id = disk[450 + i*16]
        # Identify partition type by using the json
        description = next((p["desc"] for p in partition_types if str(p["hex"]).lower() == file_id.lower()), None)
        start_sector = ''.join(disk[457+i*16 : 453+i*16 : -1])
        size_file = ''.join(disk[461+i*16 : 457+i*16 : -1])
        if description:
            # Print Partitions types, start LBA, size
            print(f"({file_id}), {description} , {int(start_sector, 16)*512}, {int(size_file, 16)*512}")
            # Saving the LBA values for parse_mbr
            lbs.append(int(start_sector, 16)*512)
        else:
            print(f"No description found for file_id: {file_id}")
    return lbs
   
# Function to check if the partition is of type GPT or MBR and returns string 
def check_partition_type(disk):
    # Checking value of partition id, ee = GPT, and returning str value for reference later
    if disk[450] == "ee" or disk[450] == "EE":
        return "gpt"
    else:
        return "mbr"
  
# Function to parse MBR partition table
def parse_mbr(hexlist, offsets):
    # Save the lba to find the offest of the partition 
    lbs = get_partition_scheme(hexlist)
    for part in range(3):
        print(f"Partition number: {part+1}")
        byte_list = ' '.join(hexlist[lbs[part] + offsets[part] : lbs[part] + offsets[part] + 16])
        print(f"16 bytes of boot record from offset {str(offsets[part]).zfill(3)}: {byte_list}")
        # Converting all bytes into ascii from the offset, replacing 0 with .
        ascii_chars = '  '.join(chr(int(byte, 16)) if 32 <= int(byte, 16) <= 126 else '.' for byte in hexlist[lbs[part] + offsets[part]:lbs[part] + offsets[part]+16])
        print(f"ASCII:                                    {ascii_chars}")
    print("\n")
    return

# Function to parse GPT partition table
def parse_gpt(hexlist):
    for i in range(4):
        # Simple math for the initial index of each partition 
        part_guid_index = 1024 + i * 128
        start_index = 1055 + i * 128
        part_name_ind = 1080 + i * 128

        # Concatenating all bytes, little endian order
        start_lba = ''.join(hexlist[start_index+8:start_index:-1])
        end_lba = ''.join(hexlist[start_index+16:start_index+8:-1])
        start_lba_dec= int(start_lba,16)
        end_lba_dec = int(end_lba,16)
        part_name_hex = ''.join(hexlist[part_name_ind:part_name_ind+72])
        part_name_bytes = bytes.fromhex(part_name_hex)
        part_name_ascii = part_name_bytes.decode('utf-16-le')  

        # Printing out all parameters
        print(f"Partition number: {i+1}")
        print(f"Partition Type GUID :{''.join(hexlist[part_guid_index:part_guid_index+16])}")
        print(f"Starting LBA address in hex: {hex(start_lba_dec)}")
        print(f"ending LBA address in hex: {hex(end_lba_dec)}")
        print(f"starting LBA address in Decimal: {start_lba_dec}")
        print(f"ending LBA address in Decimal: {end_lba_dec}")
        print(f"Partition name: {part_name_ascii}")
        print("\n")
    return

# Function to parse GPT partition table
def main():
    parser = argparse.ArgumentParser(description='Boot Info Analyzer')
    parser.add_argument('-f', '--file', type=str, help='Path to the raw image file')
    parser.add_argument('-o', '--offsets', type=int, nargs='+', help='Offset values for partitions')
    args = parser.parse_args()

    if args.file:
        # 1 Calculate hash values
        md5_hash = calculate_md5(args.file)
        sha256_hash = calculate_sha256(args.file)
        filename = os.path.basename(args.file)
        hexlist = []

        # Write hash values to files
        with open(f'MD5-{filename}.txt', 'w') as fmd:
            fmd.write(md5_hash)

        with open(f'SHA-256-{filename}.txt', 'w') as fsha:
            fsha.write(sha256_hash)
            
        # 2 & 3 Open image in read only and print tables
        with open(args.file, 'rb') as f:
            # Limit the input hex characters to 8000000, if we read the whole file autograder times out
            file_content = f.read(8000000)
            
            # Debugging statement
            if not file_content:
                print("File is empty.")
                return
                
            # Decoding hex values and storing them in a list 
            file_hex = file_content.hex()
            hexlist = [file_hex[i:i+2] for i in range(0, len(file_hex), 2)] 
            
            # Checking if the file is type GPT or MBR
            if check_partition_type(hexlist) == "mbr":
                parse_mbr(hexlist, args.offsets)
            else:
                parse_gpt(hexlist)
    return 
        
if __name__ == "__main__":
    main()