package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"io"
	"log"
	r "math/rand"
	"net/http"
	"os"
	"strconv"
	"time"
	spinhttp "github.com/fermyon/spin/sdk/go/v2/http"
)

func init() {
	//r.Seed(time.Now().UnixNano())
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

func init() {
	spinhttp.Handle(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=\"UTF-8\"")
		randomStringLength, err := strconv.Atoi(r.URL.Query().Get("length"))
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Fprintln(w, "Cannot parse length query string parameter")
			return
		}
		iterations, err := strconv.Atoi(r.URL.Query().Get("iterations"))
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Fprintln(w, "Cannot parse iterations query string parameter")
			return
		}

		message := randomString(randomStringLength)

		fmt.Fprintln(w, fmt.Sprintf("CLEAR TEXT MESSAGE:%s\n\n", message))
		for i := 0; i < iterations; i++ {
			cipherKey := []byte("\xa1\xf6%\x8c\x87}_\xcd\x89dHE8\xbf\xc9,") //16 bit key for AES-128
			encrypted, err := encrypt(cipherKey, message)
			//If the encryption failed:
			if err != nil {
				//Print error message:
				log.Println(err)
				os.Exit(-2)
			}

			//Print the key and cipher text:
			fmt.Fprintln(w, fmt.Sprintf("\tENCRYPTED: %s", encrypted))
			//Decrypt the text:
			decrypted, err := decrypt(cipherKey, encrypted)

			//If the decryption failed:
			if err != nil {
				log.Println(err)
				os.Exit(-3)
			}

			//Print re-decrypted text:
			fmt.Fprintln(w, fmt.Sprintf("\tDECRYPTED: %s\n\n", decrypted))
		}
	})
}

func main() {}
