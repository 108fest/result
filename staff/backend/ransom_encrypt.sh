#!/bin/bash
echo "[*] Initiating Astra DB Encryption Protocol..."
sleep 1
echo "[*] Generating RSA-4096 encryption keys..."
sleep 1
echo "[*] Encrypting tables..."
HASH=$(echo "Astra_DB_Encrypted_$(date)" | md5sum | awk '{print $1}')
echo "[+] Database successfully encrypted!"
echo "[+] Ransom hash: $HASH"
echo "[+] FLAG: CTF{SST1_RCE_R4ns0mw4r3_M4st3r}"
