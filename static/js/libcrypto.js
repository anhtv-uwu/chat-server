// Generate RSA keypair 

function arrayBufferToBase64( buffer ) {
    var binary = '';
    var bytes = new Uint8Array( buffer );
    var len = bytes.byteLength;
    for (var i = 0; i < len; i++) {
        binary += String.fromCharCode( bytes[ i ] );
    }
    return window.btoa( binary );
}

function generateKeys() {
    const rsaKeyPair = forge.pki.rsa.generateKeyPair({ bits: 2048 });
    const privateKey = forge.pki.privateKeyToPem(rsaKeyPair.privateKey);
    const publicKey = forge.pki.publicKeyToPem(rsaKeyPair.publicKey);

    return [privateKey, publicKey];
}

// Encrypt message
function encrypt(message, publicKey) {
    const key = forge.random.getBytesSync(32);
    const iv = forge.random.getBytesSync(16);
    var cipher = forge.cipher.createCipher('AES-CBC', key);
    cipher.start({iv: iv});
    cipher.update(forge.util.createBuffer(message));
    cipher.finish();
    // Convert binary encoded ciphertext to Base64 encoded
    var encrypted = cipher.output;
    var encoded = forge.util.encode64(encrypted.getBytes());
    publicKey = forge.pki.publicKeyFromPem(publicKey).encrypt(forge.util.encode64(key));
    
    return forge.util.encode64(publicKey) + '.' + forge.util.encode64(iv) + '.' + encoded;
}

// Decrypt 
function decrypt(encryptedMessage, privateKey) {
    const [publicKey, iv, encrypted] = encryptedMessage.split('.');
    const key = forge.pki.privateKeyFromPem(privateKey).decrypt(forge.util.decode64(publicKey));
    var decipher = forge.cipher.createDecipher('AES-CBC', forge.util.decode64(key));
    decipher.start({iv: forge.util.decode64(iv)});
    decipher.update(forge.util.createBuffer(forge.util.decode64(encrypted)));
    decipher.finish();
    return decipher.output.toString();
    
}
  
 

var privkey, pubkey;
[privkey, pubkey] = generateKeys();


