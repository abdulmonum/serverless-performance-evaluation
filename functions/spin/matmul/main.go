package main

import (
	"fmt"
	"math/rand"
	"net/http"
	"strconv"
	"time"

	spinhttp "github.com/fermyon/spin/sdk/go/v2/http"
	"gonum.org/v1/gonum/mat"
)

func generateRandomSquareMatrix(randomInstance *rand.Rand, dimensions int) *mat.Dense {
	data := make([]float64, dimensions*dimensions)
	for i := range data {
		data[i] = randomInstance.NormFloat64()
	}
	return mat.NewDense(dimensions, dimensions, data)
}

func init() {
	spinhttp.Handle(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "text/plain; charset=\"UTF-8\"")
		dimensions, err := strconv.Atoi(r.URL.Query().Get("dimensions"))
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Fprintln(w, "Cannot parse dimensions query string parameter")
			return

		}
		seed := rand.NewSource(time.Now().UnixNano())
		randomInstance := rand.New(seed)
		matrix := mat.NewDense(dimensions, dimensions, nil)
		a := generateRandomSquareMatrix(randomInstance, dimensions)
		b := generateRandomSquareMatrix(randomInstance, dimensions)
		matrix.Mul(a, b)
		formatted := mat.Formatted(matrix, mat.Prefix(""), mat.Squeeze())
		fmt.Fprintln(w, formatted)

	})
}

func main() {}
