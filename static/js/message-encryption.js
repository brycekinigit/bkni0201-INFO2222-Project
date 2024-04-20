function encodeText(message) {
    let encoder = new TextEncoder();
    return encoder.encode(message);
}

function decodeText(message) {
    let encoder = new TextDecoder();
    return encoder.decode(message);
}

async function encryptText(message, key, iv) {
    return await crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv,
        },
        key,
        encodeText(message)
    );
}

async function decryptText(encryptedData, key, iv) {
    let result =  await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: iv,
        },
        key,
        encryptedData);
    return decodeText(result)
}

async function keyToJSON(key){
    let keyJSON = await crypto.subtle.exportKey(
        'jwk',
        key
    );
    return keyJSON;
}

async function keyFromJSON(keyJSON){
    let key = await crypto.subtle.importKey(
        'jwk',
        keyJSON,
        { name: 'AES-GCM' },
        true,
        ['encrypt', 'decrypt']
    );
    return key;
}

async function aesKeyFromPassword(password, salt) {
    const keySalt = new TextEncoder().encode(salt)
    const keyData = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(password),
        "PBKDF2",
        false,
        ["deriveBits", "deriveKey"],
    );
    const messageKey = await crypto.subtle.deriveKey(
        {
            name: "PBKDF2",
            salt: keySalt,
            iterations: 100000,
            hash: "SHA-256",
        },
        keyData,
        { name: "AES-GCM", length: 256 },
        true,
        ["encrypt", "decrypt"],
    );
    console.log("KEY: ", typeof messageKey);
    return messageKey;
}

// The following code is based on the documentation found at
// https://developer.mozilla.org/en-US/docs/Web/API/SubtleCrypto/deriveKey#pbkdf2
// Under the public domain
// Not adapted to this yet

// derives a shared secret for both users
function deriveSecretKey(privateKey, publicKey) {
    return window.crypto.subtle.deriveKey(
        {
            name: "ECDH",
            public: publicKey,
        },
        privateKey,
        {
            name: "AES-GCM",
            length: 256,
        },
        false,
        ["encrypt", "decrypt"],
    );
}

// NOTE: ECDH (eliptic curve diffie hellman) seems more secure than regular diffie hellman, so probably good to use

async function agreeSharedSecretKey() {
    // Generate 2 ECDH key pairs: one for Alice and one for Bob
    // In more normal usage, they would generate their key pairs
    // separately and exchange public keys securely

    // Generates a key pair
    let alicesKeyPair = await window.crypto.subtle.generateKey(
        {
            name: "ECDH",
            namedCurve: "P-384",
        },
        false,
        ["deriveKey"],
    );

    let bobsKeyPair = await window.crypto.subtle.generateKey(
        {
            name: "ECDH",
            namedCurve: "P-384",
        },
        false,
        ["deriveKey"],
    );

    // Alice then generates a secret key using her private key and Bob's public key.
    let alicesSecretKey = await deriveSecretKey(
        alicesKeyPair.privateKey,
        bobsKeyPair.publicKey,
    );

    // Bob generates the same secret key using his private key and Alice's public key.
    let bobsSecretKey = await deriveSecretKey(
        bobsKeyPair.privateKey,
        alicesKeyPair.publicKey,
    );

    console.log("Alice's key: " + alicesSecretKey);
    console.log("Bob's key: " + bobsSecretKey);

    // Alice can then use her copy of the secret key to encrypt a message to Bob.
}