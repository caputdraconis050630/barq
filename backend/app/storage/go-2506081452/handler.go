package main

import (
	"fmt"
	"os"
	"encoding/json"
)

type Event struct {
	Name string `json:"name"`
}

func main() {
	eventJson := os.Getenv("EVENT")
	var e Event
	_ = json.Unmarshal([]byte(eventJson), &e)
	name := e.Name
	if name == "" {
		name = "world"
	}
	fmt.Printf("Hello %s from Go!\n", name)
}