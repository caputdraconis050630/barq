package main

import (
	"log"
	"net/http"

	"github.com/caputdraconis050630/barq/internal/api"
)

func main() {
	mux := http.NewServeMux()
	api.RegisterRoutes(mux)

	log.Println("Server listening on port :8080")
	err := http.ListenAndServe(":8080", mux)
	if err != nil {
		log.Fatalf("Server failed: %v", err)
	}
}
