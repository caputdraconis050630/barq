package model

type Function struct {
	FuncID     string `json:"func_id"`
	Runtime    string `json:"runtime"`
	Entrypoint string `json:"entrypoint"`
	Code       string `json:"code"`
}
