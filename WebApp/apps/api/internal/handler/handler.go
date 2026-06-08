package handler

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/Mdashe/anti-spamware/apps/api/internal/repository"
	"github.com/Mdashe/anti-spamware/apps/api/internal/response"
)

type Handler struct {
	repo *repository.Repository
}

func New(repo *repository.Repository) *Handler {
	return &Handler{repo: repo}
}

func (h *Handler) Register(mux *http.ServeMux) {
	mux.HandleFunc("GET /health", h.Health)
	mux.HandleFunc("GET /health/db", h.HealthDB)
	mux.HandleFunc("POST /api/v1/users", h.CreateUser)
	mux.HandleFunc("POST /api/v1/emails", h.CreateEmail)
	mux.HandleFunc("POST /api/v1/classifications", h.CreateClassification)
	mux.HandleFunc("POST /api/v1/rules", h.CreateRule)
}

func (h *Handler) Health(w http.ResponseWriter, r *http.Request) {
	response.JSON(w, http.StatusOK, map[string]string{"status": "ok"})
}

func (h *Handler) HealthDB(w http.ResponseWriter, r *http.Request) {
	if err := h.repo.Ping(r.Context()); err != nil {
		response.ServiceUnavailable(w, "database unavailable")
		return
	}
	response.JSON(w, http.StatusOK, map[string]string{"status": "ok", "database": "connected"})
}

type createUserRequest struct {
	Email string `json:"email"`
	Name  string `json:"name"`
}

func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) {
	var req createUserRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.BadRequest(w, "invalid JSON body")
		return
	}
	if req.Email == "" {
		response.BadRequest(w, "email is required")
		return
	}

	result, err := h.repo.InsertUser(r.Context(), req.Email, req.Name)
	if err != nil {
		response.ServiceUnavailable(w, "database error")
		return
	}
	response.FromProcResult(w, result.Status, result.ID, result.Message)
}

type createEmailRequest struct {
	UserID          int      `json:"user_id"`
	AccountID       int      `json:"account_id"`
	ProviderEmailID string   `json:"provider_email_id"`
	ThreadID        string   `json:"thread_id"`
	Subject         string   `json:"subject"`
	Sender          string   `json:"sender"`
	Recipients      []string `json:"recipients"`
	Snippet         string   `json:"snippet"`
	ReceivedAt      string   `json:"received_at"`
	CachedBody      string   `json:"cached_body"`
}

func (h *Handler) CreateEmail(w http.ResponseWriter, r *http.Request) {
	var req createEmailRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.BadRequest(w, "invalid JSON body")
		return
	}
	if req.UserID == 0 || req.AccountID == 0 || req.ProviderEmailID == "" {
		response.BadRequest(w, "user_id, account_id, and provider_email_id are required")
		return
	}

	receivedAt := time.Now().UTC()
	if req.ReceivedAt != "" {
		parsed, err := time.Parse(time.RFC3339, req.ReceivedAt)
		if err != nil {
			response.BadRequest(w, "received_at must be RFC3339 format (e.g. 2026-06-08T10:00:00Z)")
			return
		}
		receivedAt = parsed
	}

	result, err := h.repo.InsertEmail(
		r.Context(),
		req.UserID,
		req.AccountID,
		req.ProviderEmailID,
		req.ThreadID,
		req.Subject,
		req.Sender,
		req.Recipients,
		req.Snippet,
		receivedAt,
		req.CachedBody,
	)
	if err != nil {
		response.ServiceUnavailable(w, "database error")
		return
	}
	response.FromProcResult(w, result.Status, result.ID, result.Message)
}

type createClassificationRequest struct {
	EmailID       int     `json:"email_id"`
	Label         string  `json:"label"`
	Confidence    float64 `json:"confidence"`
	ModelVersion  string  `json:"model_version"`
	Source        string  `json:"source"`
}

func (h *Handler) CreateClassification(w http.ResponseWriter, r *http.Request) {
	var req createClassificationRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.BadRequest(w, "invalid JSON body")
		return
	}
	if req.EmailID == 0 || req.Label == "" {
		response.BadRequest(w, "email_id and label are required")
		return
	}
	if req.Source == "" {
		req.Source = "model"
	}

	result, err := h.repo.InsertClassification(
		r.Context(),
		req.EmailID,
		req.Label,
		req.Confidence,
		req.ModelVersion,
		req.Source,
	)
	if err != nil {
		response.ServiceUnavailable(w, "database error")
		return
	}
	response.FromProcResult(w, result.Status, result.ID, result.Message)
}

type createRuleRequest struct {
	UserID          int    `json:"user_id"`
	Name            string `json:"name"`
	ConditionType   string `json:"condition_type"`
	ConditionValue  string `json:"condition_value"`
	Action          string `json:"action"`
	Enabled         *bool  `json:"enabled"`
}

func (h *Handler) CreateRule(w http.ResponseWriter, r *http.Request) {
	var req createRuleRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		response.BadRequest(w, "invalid JSON body")
		return
	}
	if req.UserID == 0 || req.Name == "" || req.ConditionType == "" || req.ConditionValue == "" || req.Action == "" {
		response.BadRequest(w, "user_id, name, condition_type, condition_value, and action are required")
		return
	}

	enabled := true
	if req.Enabled != nil {
		enabled = *req.Enabled
	}

	result, err := h.repo.InsertRule(
		r.Context(),
		req.UserID,
		req.Name,
		req.ConditionType,
		req.ConditionValue,
		req.Action,
		enabled,
	)
	if err != nil {
		response.ServiceUnavailable(w, "database error")
		return
	}
	response.FromProcResult(w, result.Status, result.ID, result.Message)
}
