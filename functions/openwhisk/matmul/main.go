package main

import (
	"fmt"
	"math/rand"
	"time"

	"gonum.org/v1/gonum/mat"
)

func generateRandomSquareMatrix(randomInstance *rand.Rand, dimensions int) *mat.Dense {
	data := make([]float64, dimensions*dimensions)
	for i := range data {
		data[i] = randomInstance.NormFloat64()
	}
	return mat.NewDense(dimensions, dimensions, data)
}

func Main(obj map[string]interface{}) map[string]interface{} {
	response := make(map[string]interface{})
	dimensions := 10
	if val, ok := obj["dimensions"].(float64); ok {
		dimensions = int(val)
	}

	seed := rand.NewSource(time.Now().UnixNano())
	randomInstance := rand.New(seed)
	matrix := mat.NewDense(dimensions, dimensions, nil)
	a := generateRandomSquareMatrix(randomInstance, dimensions)
	b := generateRandomSquareMatrix(randomInstance, dimensions)
	matrix.Mul(a, b)
	formatted := mat.Formatted(matrix, mat.Prefix(""), mat.Squeeze())

	response["result"] = fmt.Sprintf("%v", formatted)
	return response
}
