package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"io"
	"log"
	r "math/rand"
	"time"
)

func init() {
	r.New(r.NewSource(time.Now().UnixNano()))
}

const letterBytes = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

func randomString(length int) string {
	b := make([]byte, length)
	for i := range b {
		b[i] = letterBytes[r.Intn(len(letterBytes))]
	}
	return string(b)
}

func encrypt(key []byte, message string) (encoded string, err error) {
	//Create byte array from the input string
	plainText := []byte(message)

	//Create a new AES cipher using the key
	block, err := aes.NewCipher(key)

	//IF NewCipher failed, exit:
	if err != nil {
		return
	}

	//Make the cipher text a byte array of size BlockSize + the length of the message
	cipherText := make([]byte, aes.BlockSize+len(plainText))

	//iv is the ciphertext up to the blocksize (16)
	iv := cipherText[:aes.BlockSize]
	if _, err = io.ReadFull(rand.Reader, iv); err != nil {
		return
	}

	//Encrypt the data:
	stream := cipher.NewCFBEncrypter(block, iv)
	stream.XORKeyStream(cipherText[aes.BlockSize:], plainText)

	//Return string encoded in base64
	return base64.RawStdEncoding.EncodeToString(cipherText), err
}

func decrypt(key []byte, secure string) (decoded string, err error) {
	//Remove base64 encoding:
	cipherText, err := base64.RawStdEncoding.DecodeString(secure)

	//If DecodeString failed, exit:
	if err != nil {
		return
	}

	//Create a new AES cipher with the key and encrypted message
	block, err := aes.NewCipher(key)

	//If NewCipher failed, exit:
	if err != nil {
		return
	}

	//IF the length of the cipherText is less than 16 Bytes:
	if len(cipherText) < aes.BlockSize {
		err = errors.New("Ciphertext block size is too short!")
		return
	}

	iv := cipherText[:aes.BlockSize]
	cipherText = cipherText[aes.BlockSize:]

	//Decrypt the message
	stream := cipher.NewCFBDecrypter(block, iv)
	stream.XORKeyStream(cipherText, cipherText)

	return string(cipherText), err
}

func Main(obj map[string]interface{}) map[string]interface{} {
	log.Println(obj)
	//mylength := obj["length"].(string)
	randomStringLength := 10
	if val, ok := obj["length"].(float64); ok {
		randomStringLength = int(val)
	}

	iterations := 2
	if val, ok := obj["iterations"].(float64); ok {
		iterations = int(val)
	}

	// randomStringLength, err := strconv.Atoi(length)
	// if err != nil {
	// 	return map[string]interface{}{"error": err.Error()}
	// }

	// iterations, err := strconv.Atoi(iter)

	// if err != nil {
	// 	return map[string]interface{}{"error": err.Error()}
	// }

	message := randomString(randomStringLength)
	results := []map[string]string{}

	for i := 0; i < iterations; i++ {
		cipherKey := []byte("\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,")
		encrypted, err := encrypt(cipherKey, message)
		if err != nil {
			log.Println(err)
			return map[string]interface{}{"error": err.Error()}
		}

		decrypted, err := decrypt(cipherKey, encrypted)
		if err != nil {
			log.Println(err)
			return map[string]interface{}{"error": err.Error()}
		}

		results = append(results, map[string]string{
			"encrypted": encrypted,
			"decrypted": decrypted,
		})
	}
	log.Println(message)
	return map[string]interface{}{
		"message": message,
		"results": results,
	}

}
