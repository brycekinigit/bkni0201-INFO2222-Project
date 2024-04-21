function encodeText(message) {
    let encoder = new TextEncoder();
    return encoder.encode(message);
}

function decodeText(message) {
    let encoder = new TextDecoder();
    return encoder.decode(message);
}

async function encryptText(message, key, iv) {
    let result = await crypto.subtle.encrypt(
        {
            name: "AES-GCM",
            iv: iv,
        },
        key,
        encodeText(message)
    );
    return result;
    // return decodeText(result);
}

async function decryptText(encryptedData, key, iv) {
    let result =  await crypto.subtle.decrypt(
        {
            name: "AES-GCM",
            iv: iv,
        },
        key,
        // encodeText(encryptedData));
        encryptedData,
    );
    return decodeText(result);
}

async function keyToJSON(key){
    let keyJSON = await crypto.subtle.exportKey(
        'jwk',
        key
    );
    return keyJSON;
}

async function keyFromJSON(keyJSON, uses){
    let key = await crypto.subtle.importKey(
        'jwk',
        keyJSON,
        { name: 'AES-GCM' },
        true,
        uses
    );
    return key;
}

async function aesKeyFromPassword(password, salt) {
    const keySalt = new TextEncoder().encode(salt)
    const keyData = await crypto.subtle.importKey(
        "raw",
        new TextEncoder().encode(password),
        "PBKDF2",
        true,
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
    return crypto.subtle.deriveKey(
        {
            name: "ECDH",
            public: publicKey,
        },
        privateKey,
        {
            name: "AES-GCM",
            length: 256,
        },
        true,
        ["encrypt", "decrypt"],
    );
}

// NOTE: ECDH (eliptic curve diffie hellman) seems more secure than regular diffie hellman, so probably good to use