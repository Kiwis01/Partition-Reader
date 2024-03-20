all:
	dos2unix boot_info.py
	cp boot_info.py boot_info
	chmod +x boot_info
	
clean:
	rm boot_info
	
