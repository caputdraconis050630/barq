package api

import (
	"encoding/json"
	"net/http"

	"github.com/caputdraconis050630/barq/internal/model"
)

func RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("/healthz", healthzHandler)
	mux.HandleFunc("/functions", FunctionHandler)
}

func healthzHandler(w http.ResponseWriter, r *http.Request) {
	w.WriteHeader(http.StatusOK)
	w.Write([]byte("OK"))
}

func FunctionHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodPost:
		var fn model.Function
		if err := json.NewDecoder(r.Body).Decode(&fn); err != nil {
			http.Error(w, "Invalid json", http.StatusBadRequest)
			return
		}

		w.WriteHeader(http.StatusCreated)
		w.Write([]byte("function registered"))
	default:
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
	}
}
