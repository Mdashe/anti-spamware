package response

import (
	"encoding/json"
	"net/http"
	"strings"
)

type Success struct {
	ID      int    `json:"id"`
	Message string `json:"message"`
}

type ErrorBody struct {
	Error string `json:"error"`
}

func JSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(body)
}

func FromProcResult(w http.ResponseWriter, status int, id *int, message string) {
	if status == 1 && id != nil {
		JSON(w, http.StatusCreated, Success{ID: *id, Message: message})
		return
	}

	msg := strings.ToLower(message)
	switch {
	case strings.Contains(msg, "already exists"):
		JSON(w, http.StatusConflict, ErrorBody{Error: message})
	case strings.Contains(msg, "does not exist"), strings.Contains(msg, "invalid user"):
		JSON(w, http.StatusBadRequest, ErrorBody{Error: message})
	default:
		JSON(w, http.StatusUnprocessableEntity, ErrorBody{Error: message})
	}
}

func BadRequest(w http.ResponseWriter, message string) {
	JSON(w, http.StatusBadRequest, ErrorBody{Error: message})
}

func InternalError(w http.ResponseWriter, message string) {
	JSON(w, http.StatusInternalServerError, ErrorBody{Error: message})
}

func ServiceUnavailable(w http.ResponseWriter, message string) {
	JSON(w, http.StatusServiceUnavailable, ErrorBody{Error: message})
}
