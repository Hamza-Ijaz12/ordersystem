# utils.py
import gnupg

def encrypt_message(public_key_path, message):
    gpg = gnupg.GPG()
   
    with open(public_key_path, 'rb') as f:
        key_data = f.read()
    public_key = gpg.import_keys(key_data)

    if not public_key.results or 'fingerprint' not in public_key.results[0]:
        return "Error importing public key"

    fingerprint = public_key.results[0]['fingerprint']
    
    # Encrypt the message 
    encrypted_data = gpg.encrypt(message, fingerprint,always_trust=True)
    if encrypted_data.ok:
        
        return str(encrypted_data)
    else:
        print('Encrypted message:', encrypted_data.status)
        return str(encrypted_data.status)

    



def decrypt_message( encrypted_message, passphrase,private_key_path):
    gpg = gnupg.GPG()
    with open(private_key_path, 'rb') as f:
        key_data = f.read()
    private_key = gpg.import_keys(key_data)

    if not private_key.results or 'fingerprint' not in private_key.results[0]:
        return "Error importing public key"

    fingerprint = private_key.results[0]['fingerprint']
    
    print('-------',passphrase)
    decrypted_data = gpg.decrypt(encrypted_message, passphrase=passphrase)

    if decrypted_data.ok:
        
        return str(decrypted_data)
    else:
        print('Encrypted message:', decrypted_data.status)
        decrypted_data=False
        return decrypted_data
